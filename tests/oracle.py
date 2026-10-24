"""Differential test: original Mach-O bytes via SysV ABI vs reconstructed Rust."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argparse
import ctypes
import json
from pathlib import Path
import random
import struct

from macho import MachO
from original import Original


def state_from(data, count, capacity):
    slots = ctypes.create_string_buffer(data, len(data))
    state, info = ctypes.create_string_buffer(256), ctypes.create_string_buffer(32)
    values = ctypes.addressof(slots)
    struct.pack_into('<Q', state, 56, values)
    struct.pack_into('<Q', state, 80, ctypes.addressof(info))
    struct.pack_into('<Q', state, 88, values+count*16)
    struct.pack_into('<Q', info, 0, values+capacity*16)
    return state, info, slots


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--report', type=Path, default=Path(__file__).resolve().parents[1]/'data/recovery.json')
    parser.add_argument('--dll', type=Path, default=Path(__file__).resolve().parents[1]/'vm0735.dll')
    parser.add_argument('--out', type=Path, default=Path(__file__).resolve().parents[1]/'data/differential.json')
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding='utf-8'))
    dll = ctypes.CDLL(str(args.dll.resolve()))
    functions = {}
    for name in ['gettop','absindex','settop','type','toboolean','pushnil','pushnumber','pushboolean']:
        fn = getattr(dll, 'recovered_'+name)
        fn.restype = ctypes.c_int
        fn.argtypes = [ctypes.c_void_p] + ([ctypes.c_double] if name == 'pushnumber' else [ctypes.c_int] if name in {'absindex','settop','type','toboolean','pushboolean'} else [])
        functions[name] = fn
    randomizer = random.Random(7351131)
    counts = {name: 0 for name in functions}
    with MachO(args.binary) as binary, Original(binary, report, dll) as original:
        for case in range(160):
            capacity = randomizer.randrange(1, 129)
            count = randomizer.randrange(capacity)
            raw = bytearray(randomizer.randbytes((capacity+8)*16))
            for index in range(capacity+8): struct.pack_into('<I', raw, index*16+12, randomizer.randrange(11))
            for name, native in functions.items():
                native_state, native_info, native_slots = state_from(bytes(raw), count, capacity)
                original_state, original_info, original_slots = state_from(bytes(raw), count, capacity)
                argument = randomizer.choice([1, count+1, count+20] + ([-1, -count] if count else []))
                if name == 'settop': argument = randomizer.choice([0, capacity, randomizer.randrange(capacity+1), -count-1, -1])
                if name == 'absindex': argument = randomizer.choice([1, -1, -count, -10000, -10002, 123])
                number = randomizer.choice([0.0, -0.0, 1.5, -123.75, float('inf'), float('-inf')])
                if name == 'pushboolean': argument = randomizer.choice([0, 1, -1, -2147483648, 2147483647])
                original_args = {'argument': argument} if name in {'absindex','settop','type','toboolean','pushboolean'} else {'number': number} if name == 'pushnumber' else {}
                answer = original.call('lua_'+name, ctypes.addressof(original_state), **original_args)
                native_args = [ctypes.addressof(native_state)] + ([number] if name == 'pushnumber' else [argument] if name in {'absindex','settop','type','toboolean','pushboolean'} else [])
                recovered = native(*native_args)
                if name in {'gettop','absindex','type','toboolean'}:
                    answer = ctypes.c_int32(answer).value
                    assert answer == recovered, (case, name, count, argument, answer, recovered)
                else:
                    assert recovered == 0, (case, name, 'unexpected native capacity error')
                    original_top = struct.unpack_from('<Q', original_state, 88)[0] - ctypes.addressof(original_slots)
                    recovered_top = struct.unpack_from('<Q', native_state, 88)[0] - ctypes.addressof(native_slots)
                    assert original_top == recovered_top, (case, name, 'top mismatch')
                    assert original_slots.raw == native_slots.raw, (case, name, 'stack bytes mismatch')
                counts[name] += 1
        output = ctypes.create_string_buffer(bytes([0xA5])*128, 128)
        original.call('setupCompiler', ctypes.addressof(output))
        initializer = []
        for offset in range(0, 128, 8):
            value = struct.unpack_from('<Q', output, offset)[0]
            if value != 0xA5A5A5A5A5A5A5A5:
                address = value-original.slide
                entry = {'offset': offset, 'original_image_address': hex(address),
                         'symbols': report['reference_symbols'].get(hex(address), [])}
                try: entry['string'] = binary.string(address)
                except (ValueError, UnicodeDecodeError): pass
                initializer.append(entry)
        by_offset = {item['offset']: item for item in initializer}
        assert by_offset[16]['string'] == 'Vector3' and by_offset[24]['string'] == 'new' and by_offset[32]['string'] == 'Vector3'
        assert sorted(by_offset) == [16,24,32,48,56,64,72,80]
        state, info, slots = state_from(bytes(32), 1, 1)
        assert functions['pushnil'](ctypes.addressof(state)) == -1
        result = {'cases_per_function': counts, 'total_differential_cases': sum(counts.values()),
            'native_capacity_guard_verified': True, 'original_setupCompiler_pointer_writes': initializer,
            'method': 'Unmodified original function bytes mapped in-process; Rust Windows-to-SysV ABI bridge; comparison with reconstructed Rust DLL',
            'memory': 'Read-only original data pages; RX original code pages; no persistent binary changes',
            'limits': ['fixed-capacity synthetic state', 'no allocator/GC/pseudo-index paths', 'not a full initialized Luau VM']}
        args.out.write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(json.dumps(result, indent=2))


if __name__ == '__main__': main()
