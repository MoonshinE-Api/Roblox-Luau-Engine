"""Map a bounded slice of the local x64 image and call it through a SysV ABI bridge.

This does not launch Roblox, perform process injection, resolve OS imports, or run
initializers. Bootstrap tests must supply explicit dependency bridges; they stop
before full VM initialization. Primitive/hash tests use unmodified dependencies.
"""
import ctypes
import hashlib
import struct


class Original:
    ALLOWED = frozenset({'lua_absindex', 'lua_gettop', 'lua_settop', 'lua_type',
                         'lua_toboolean', 'lua_pushnil', 'lua_pushnumber',
                         'lua_pushboolean', 'setupCompiler', 'luaS_hash'})
    BOUNDARY = frozenset({'stack_init', 'lua_newstate'})
    ALLOCATOR = frozenset({'luaM_new_', 'newblock', 'newpage', 'newclasspage', 'SizeClassConfig',
                           'luaM_free_', 'luaM_realloc_', 'freeblock', 'freepage', 'freeclasspage', 'freestack'})
    INITIALIZER = frozenset({'luaM_newgco_', 'luaM_freegco_', 'luaS_resize', 'luaS_newlstr',
                             'luaT_init', 'luaH_new', 'setarrayvector', 'setnodevector',
                             'luaO_log2', 'f_luaopen', 'luaD_rawrunprotected'})
    ENGINE_RANDOM = {'random_seed':0x1041ae236,'random_number':0x1041ae41a,
                     'random_range':0x1041ae49e,'random_integer':0x1041ae5e0,
                     'random_next':0x1041ae6b2,'random_float':0x1041ae336}
    ENGINE_BRICK = {'brick_closest':0x102a45390,'brick_constructor':0x102a4544e}
    ENGINE_DATE = {'datetime_unix':0x102a7555c,'datetime_get_rep':0x1008806a0,
                   'datetime_counted_ctor':0x1000e319c,'datetime_subtract':0x10006ead8,
                   'datetime_gregorian':0x10006f690,'datetime_tick_count':0x100312d1c,
                   'datetime_duration_minus':0x1000e28a4}
    ENGINE_PHYSICAL = {'physical_min_density':0x102a91528,'physical_constructor':0x104936ea8,
                       'material_index':0x1002931e4,'physical_unit_inertia':0x100cde5a4}
    ENGINE_REGION = {'region_init':0x102a91e80,'region_constructor':0x102a91eea,
                     'region_min':0x102a91fee,'region_max':0x102a9201a,
                     'region_is_nan_inf':0x103206e00,'region_expand':0x104645e3e}
    ENGINE_ROTATION = {'rotation_yxz':0x10321337e,'rotation_xyz':0x103214450,
                       'rotation_xzy':0x10321454c,'rotation_yzx':0x103214642,
                       'rotation_zxy':0x10321473e,'rotation_zyx':0x10321483a,
                       'rotation_look_along':0x103203538}
    ENGINE_ENVIRONMENT = {'lighting_clock':0x104b3cfee,'lighting_time_normalize':0x104b3ce48}
    def __init__(self, binary, report, dll, hooks=None, enabled=None, data_overrides=None, pointer_arrays=None,
                 core=False, auto_rebase=False, data_padding=0, writable_data=False):
        self.dll, self.binary = dll, binary
        self.api = ctypes.WinDLL('kernel32', use_last_error=True)
        self.api.VirtualAlloc.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_uint32, ctypes.c_uint32]
        self.api.VirtualAlloc.restype = ctypes.c_void_p
        self.api.VirtualProtect.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)]
        self.api.VirtualProtect.restype = ctypes.c_int
        self.api.VirtualFree.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_uint32]
        self.api.VirtualFree.restype = ctypes.c_int
        self.api.FlushInstructionCache.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]
        self.api.FlushInstructionCache.restype = ctypes.c_int
        self.api.GetCurrentProcess.restype = ctypes.c_void_p
        hooks = hooks or {}
        self.enabled = frozenset(enabled) if enabled is not None else self.ALLOWED | (self.BOUNDARY if hooks else frozenset())
        reviewed_engine=self.ENGINE_RANDOM | self.ENGINE_BRICK | self.ENGINE_DATE | self.ENGINE_PHYSICAL | self.ENGINE_REGION | self.ENGINE_ROTATION | self.ENGINE_ENVIRONMENT
        permitted = self.ALLOWED | self.BOUNDARY | self.ALLOCATOR | self.INITIALIZER | reviewed_engine.keys()
        for name in self.enabled & reviewed_engine.keys():
            if int(report['functions'][name]['address'],16)!=reviewed_engine[name]:
                raise ValueError('Unexpected reviewed engine function address')
        if core:
            if report.get('range') != ['0x1031ce278','0x1031fc453']: raise ValueError('Unexpected VM interval')
            if report.get('cold_range') not in (None,['0x108629482','0x108629af0']): raise ValueError('Unexpected VM cold interval')
            def reviewed_vm(function):
                address=int(function['address'],16)
                end=address+function['size']
                return (0x1031ce278<=address<end<=0x1031fc453 or
                        (report.get('cold_range') and 0x108629482<=address<end<=0x108629af0))
            if any(not reviewed_vm(report['functions'][name]) for name in self.enabled):
                raise ValueError('Function is outside the Luau VM interval')
        elif not self.enabled <= permitted:
            raise ValueError('Function is outside the reviewed execution set')
        data_overrides = data_overrides or {}
        pointer_arrays = pointer_arrays or {}
        pages, code_pages = set(), set()
        self.functions = {}
        for name, function in report['functions'].items():
            if name not in self.enabled: continue
            address, length = int(function['address'], 16), function['size']
            assert hashlib.sha256(binary.read(address, length)).hexdigest() == function['sha256']
            self.functions[name] = address
            for page in range(address & ~4095, address+length, 4096):
                pages.add(page); code_pages.add(page)
            for ref in function['data_references']:
                page=int(ref,16)&~4095
                for candidate in range(page-data_padding*4096,page+(data_padding+1)*4096,4096):
                    if any(s['address']<=candidate<s['address']+s['size'] for s in binary.segments if s['name']!='__PAGEZERO'):
                        pages.add(candidate)
        hook_slots = {}
        for address, pointer in hooks.items():
            if not pointer: raise ValueError('Missing dependency bridge')
            stub = binary.read(address,6)
            if stub[:2] == b'\xff\x25':
                slot = address+6+struct.unpack_from('<i',stub,2)[0]
                hook_slots[address] = slot
                for page in range(slot & ~4095,slot+8,4096): pages.add(page)
            for page in range(address & ~4095, address+(6 if address in hook_slots else 12), 4096):
                pages.add(page); code_pages.add(page)
        for address, data in data_overrides.items():
            if not any(s['address'] <= address and address+len(data) <= s['address']+s['size']
                       for s in binary.segments if s['name'] != '__PAGEZERO'):
                raise ValueError('Data initialization is outside the original image')
            for page in range(address & ~4095, address+len(data), 4096): pages.add(page)
        arrays = {}
        for address,count in pointer_arrays.items():
            pointers = struct.unpack('<'+'Q'*count,binary.read(address,count*8))
            arrays[address] = pointers
            for page in range(address & ~4095,address+count*8,4096): pages.add(page)
            for pointer in pointers:
                length = len(binary.string(pointer).encode('utf-8'))+1
                for page in range(pointer & ~4095,pointer+length,4096): pages.add(page)
        rebases=[]
        if auto_rebase:
            for address in binary.rebase_addresses():
                pointer=struct.unpack('<Q',binary.read(address,8))[0]
                rebases.append((address,pointer))
            # Library registration tables contain string pointers whose targets
            # need not appear in any instruction's RIP-relative operands.
            # Two levels cover the VM's static library records without recursively
            # traversing unrelated engine descriptor graphs sharing a data page.
            for _ in range(2):
                extra=set()
                for address,pointer in rebases:
                    if (address & ~4095) not in pages: continue
                    section=next((s for s in binary.sections if s['address']<=pointer<s['address']+s['size']),None)
                    if section and not section['flags'] & 0x80000400:
                        extra.add(pointer & ~4095)
                extra-=pages
                if not extra:break
                pages.update(extra)
                if len(pages)>8192:raise ValueError('VM data graph exceeded bounded mapping capacity')
        self.image_start = min(pages)
        self.image_size = max(pages) + 4096 - self.image_start
        # Reserve address space; commit only the small set of code/data pages.
        self.base = self.api.VirtualAlloc(None, self.image_size, 0x2000, 0x01)
        if not self.base: raise ctypes.WinError(ctypes.get_last_error())
        self.slide = self.base - self.image_start
        try:
            for page in sorted(pages):
                mapped = page + self.slide
                if not self.api.VirtualAlloc(mapped, 4096, 0x1000, 0x04): raise ctypes.WinError(ctypes.get_last_error())
                for segment in binary.segments:
                    if segment['address'] <= page < segment['address']+segment['size']:
                        size = min(4096, max(0, segment['address']+segment['file_size']-page))
                        if size:
                            offset = segment['offset']+page-segment['address']
                            ctypes.memmove(mapped, binary.data[offset:offset+size], size)
                        break
                else: raise ValueError(f'Page is not backed by image: {page:#x}')
            if auto_rebase:
                for address,original_pointer in rebases:
                    if (address & ~4095) not in pages or ((address+7)&~4095) not in pages: continue
                    pointer=ctypes.c_uint64.from_address(address+self.slide)
                    if pointer.value: pointer.value+=self.slide
            # Only dependency entry points in this disposable test mapping are replaced.
            # The file and bytes of the functions under comparison remain unchanged.
            for address, pointer in hooks.items():
                if address in hook_slots:
                    ctypes.memmove(hook_slots[address]+self.slide,struct.pack('<Q',pointer),8)
                else:
                    ctypes.memmove(address+self.slide, b'\x48\xb8'+struct.pack('<Q', pointer)+b'\xff\xe0', 12)
            for address, data in data_overrides.items():
                ctypes.memmove(address+self.slide, data, len(data))
            for address,pointers in arrays.items():
                relocated = struct.pack('<'+'Q'*len(pointers),*(p+self.slide for p in pointers))
                ctypes.memmove(address+self.slide,relocated,len(relocated))
            for page in sorted(pages):
                mapped = page + self.slide
                previous = ctypes.c_uint32()
                writable=writable_data and any(s['name']=='__DATA' and s['address']<=page<s['address']+s['size'] for s in binary.segments)
                protection = 0x20 if page in code_pages else 0x04 if writable else 0x02
                if not self.api.VirtualProtect(mapped, 4096, protection, ctypes.byref(previous)):
                    raise ctypes.WinError(ctypes.get_last_error())
            if not self.api.FlushInstructionCache(self.api.GetCurrentProcess(), self.base, self.image_size):
                raise ctypes.WinError(ctypes.get_last_error())
        except BaseException:
            self.close(); raise
        for name, types in [('original_call0', [ctypes.c_size_t, ctypes.c_void_p]),
                            ('original_call_i', [ctypes.c_size_t, ctypes.c_void_p, ctypes.c_int]),
                            ('original_call_n', [ctypes.c_size_t, ctypes.c_void_p, ctypes.c_double]),
                            ('original_call_u', [ctypes.c_size_t, ctypes.c_size_t, ctypes.c_size_t]),
                            ('original_call3', [ctypes.c_size_t]*4),
                            ('original_call5', [ctypes.c_size_t]*6)]:
            function = getattr(dll, name)
            function.argtypes, function.restype = types, ctypes.c_size_t

    def call(self, name, state, argument=None, number=None):
        if name not in self.enabled: raise ValueError('This original function is not enabled for isolated execution')
        address = self.functions[name] + self.slide
        if number is not None: return self.dll.original_call_n(address, state, number)
        if argument is not None: return self.dll.original_call_i(address, state, argument)
        return self.dll.original_call0(address, state)

    def call_u(self, name, first, second):
        if name not in self.enabled: raise ValueError('Function is not enabled')
        return self.dll.original_call_u(self.functions[name]+self.slide, first, second)

    def call3(self, name, a, b, c):
        if name not in self.enabled: raise ValueError('Function is not enabled')
        return self.dll.original_call3(self.functions[name]+self.slide,a,b,c)

    def call5(self, name, a, b, c, d, e):
        if name not in self.enabled: raise ValueError('Function is not enabled')
        return self.dll.original_call5(self.functions[name]+self.slide,a,b,c,d,e)

    def close(self):
        if self.base:
            self.api.VirtualFree(self.base, 0, 0x8000)
            self.base = None

    def __enter__(self): return self
    def __exit__(self, *_): self.close()
