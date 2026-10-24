"""Read-only access to the supplied x86_64 Mach-O. No binary rewriting/loading."""
import bisect
import mmap
import struct


class MachO:
    def __init__(self, path):
        self.file = open(path, "rb")
        self.data = mmap.mmap(self.file.fileno(), 0, access=mmap.ACCESS_READ)
        assert self.data[:4] == b"\xcf\xfa\xed\xfe", "Expected thin little-endian Mach-O 64"
        assert struct.unpack_from("<I", self.data, 4)[0] == 0x1000007, "Expected x86_64"
        self.segments, self.sections, self.symtab = [], [], None
        self.indirect = None
        self.rebase_stream = None
        commands, command_bytes = struct.unpack_from("<II", self.data, 16)
        cursor, starts = 32, None
        for _ in range(commands):
            command, size = struct.unpack_from("<II", self.data, cursor)
            assert size >= 8 and cursor + size <= 32 + command_bytes
            if command == 0x19:
                name = self.data[cursor+8:cursor+24].split(b"\0")[0].decode()
                va, virtual_size, offset, file_size = struct.unpack_from("<4Q", self.data, cursor+24)
                self.segments.append(dict(name=name, address=va, size=virtual_size, offset=offset, file_size=file_size))
                count = struct.unpack_from("<I", self.data, cursor+64)[0]
                for index in range(count):
                    at = cursor + 72 + index * 80
                    section_name = self.data[at:at+16].split(b"\0")[0].decode()
                    address, length, file_offset = struct.unpack_from("<QQI", self.data, at+32)
                    flags,reserved1,reserved2 = struct.unpack_from('<III',self.data,at+64)
                    self.sections.append(dict(name=section_name, segment=name, address=address, size=length, offset=file_offset,
                                              flags=flags,indirect_start=reserved1,stub_size=reserved2))
            elif command == 2:
                self.symtab = struct.unpack_from("<4I", self.data, cursor+8)
            elif command == 0x26:
                starts = struct.unpack_from("<II", self.data, cursor+8)
            elif command == 0xb:
                self.indirect = struct.unpack_from('<II',self.data,cursor+56)
            elif command in (0x22,0x80000022):
                self.rebase_stream = struct.unpack_from('<II',self.data,cursor+8)
            cursor += size
        assert self.symtab
        self.sorted_segments=sorted(self.segments,key=lambda s:s['address'])
        self.segment_addresses=[s['address'] for s in self.sorted_segments]
        self.starts = []
        if starts:
            at, length = starts
            end = at + length
            address = next(segment["address"] for segment in self.segments if segment["name"] == "__TEXT")
            while at < end:
                delta, shift = 0, 0
                while True:
                    byte = self.data[at]; at += 1
                    delta |= (byte & 0x7F) << shift
                    if byte < 128: break
                    shift += 7
                    assert shift < 64 and at < end
                if delta == 0: break
                address += delta
                self.starts.append(address)

    def read(self, address, length):
        index=bisect.bisect_right(self.segment_addresses,address)-1
        if index>=0:
            segment=self.sorted_segments[index]
            if address+length<=segment['address']+segment['file_size']:
                offset=segment['offset']+address-segment['address']
                return self.data[offset:offset+length]
        for section in self.sections:
            if section["address"] <= address and address + length <= section["address"] + section["size"]:
                # Exclude zero-fill sections by requiring a backed file range.
                offset = section["offset"] + address - section["address"]
                if section["offset"] and offset + length <= len(self.data):
                    return self.data[offset:offset+length]
        for segment in self.segments:
            if segment["address"] <= address and address + length <= segment["address"] + segment["file_size"]:
                offset = segment["offset"] + address - segment["address"]
                return self.data[offset:offset+length]
        raise ValueError(f"Unbacked binary address {address:#x} (+{length})")

    def string(self, address, limit=512):
        result = bytearray()
        for i in range(limit):
            byte = self.read(address + i, 1)
            if byte == b"\0": return result.decode("utf-8")
            result.extend(byte)
        raise ValueError("Unterminated string")

    def function_bytes(self, address):
        index = bisect.bisect_right(self.starts, address)
        assert index < len(self.starts) and address in self.starts
        end = self.starts[index]
        assert 0 < end - address < 1000000
        return self.read(address, end-address)

    def symbols(self):
        offset, count, strings, string_bytes = self.symtab
        for i in range(count):
            name_offset, kind, section, description, address = struct.unpack_from("<IBBHQ", self.data, offset+i*16)
            if kind & 0xE0 or not name_offset or name_offset >= string_bytes: continue
            start = strings + name_offset
            end = self.data.find(b"\0", start, min(start+8192, strings+string_bytes))
            if end != -1:
                yield self.data[start:end], address, kind, section

    def import_stubs(self):
        return self.indirect_symbols({8})

    def import_pointers(self):
        return self.indirect_symbols({6,7})

    def indirect_symbols(self, types):
        if self.indirect is None: return {}
        offset,count = self.indirect
        symoffset,symcount,strings,stringbytes = self.symtab
        result = {}
        for section in self.sections:
            if section['flags'] & 0xff not in types: continue
            stride = section['stub_size'] if section['flags'] & 0xff == 8 else 8
            assert stride > 0
            for i in range(section['size']//stride):
                index = struct.unpack_from('<I',self.data,offset+(section['indirect_start']+i)*4)[0]
                if index & 0xc0000000: continue
                assert index < symcount
                name_offset = struct.unpack_from('<I',self.data,symoffset+index*16)[0]
                start = strings+name_offset
                end = self.data.find(b'\0',start,strings+stringbytes)
                result[section['address']+i*stride] = self.data[start:end].decode()
        return result

    def rebase_addresses(self):
        if not self.rebase_stream: return
        cursor,size=self.rebase_stream
        end=cursor+size
        segment,offset,kind=0,0,1
        def uleb():
            nonlocal cursor
            value,shift=0,0
            while True:
                assert cursor<end
                byte=self.data[cursor];cursor+=1
                value|=(byte&127)<<shift
                if byte<128:return value
                shift+=7
                assert shift<64
        while cursor<end:
            byte=self.data[cursor];cursor+=1
            opcode,imm=byte&0xf0,byte&15
            if opcode==0:return
            if opcode==0x10:kind=imm
            elif opcode==0x20:segment,offset=imm,uleb()
            elif opcode==0x30:offset+=uleb()
            elif opcode==0x40:offset+=imm*8
            elif opcode in (0x50,0x60,0x70,0x80):
                count=imm if opcode==0x50 else 1 if opcode==0x70 else uleb()
                skip=uleb() if opcode in (0x70,0x80) else 0
                assert kind==1,'Only pointer64 rebasing is supported'
                for _ in range(count):
                    yield self.segments[segment]['address']+offset
                    offset+=8+skip
            else:raise ValueError(f'Unknown rebase opcode: {byte:#x}')

    def close(self):
        self.data.close(); self.file.close()

    def __enter__(self): return self
    def __exit__(self, *_): self.close()
