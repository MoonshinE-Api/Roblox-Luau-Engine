"""Experimental execution of the user's local original Luau VM text in Windows.

The native Rust reconstruction remains separately testable. This image adapter
currently supports successful VM paths and a small set of host C imports. It is
not a sandbox; scripts and bytecode must be trusted. No Studio app is launched.
"""
import ctypes as C
import json
from pathlib import Path
import struct

from macho import MachO
from original import Original

U=C.c_size_t


class Runtime:
    def __init__(self,binary_path,memory_mb=256):
        root=Path(__file__).parent
        self.dll=C.CDLL(str((root/'vm0735.dll').resolve()))
        self.dll.oracle_dependency.argtypes,self.dll.oracle_dependency.restype=[C.c_uint],U
        self.dll.oracle_set_callback.argtypes=[C.c_uint,U]
        self.dll.recovered_sizeclassconfig.argtypes=[U]
        self.dll.oracle_stack_guard.restype=U
        self.dll.host_rune_locale.restype=U
        self.dll.oracle_install_crash_reporter.restype=U
        self.dll.oracle_install_crash_reporter()
        self.dll.host_import_address.argtypes,self.dll.host_import_address.restype=[C.c_char_p,U],U
        def host(name):
            encoded=name.encode()
            return self.dll.host_import_address(encoded,len(encoded))
        self.binary=MachO(binary_path)
        report=json.loads((root/'evidence/vm_core.json').read_text(encoding='utf-8'))
        config=C.create_string_buffer(1192)
        self.dll.recovered_sizeclassconfig(C.addressof(config))
        def symbol(name):
            return next(int(a,16) for a,names in report['reference_symbols'].items() if name in names)
        overrides={symbol('__ZL16kSizeClassConfig'):config.raw}
        pointers=self.binary.import_pointers()
        for address,name in pointers.items():
            if name=='___stack_chk_guard': overrides[address]=struct.pack('<Q',self.dll.oracle_stack_guard())
            if name=='__DefaultRuneLocale': overrides[address]=struct.pack('<Q',self.dll.host_rune_locale())
        adapters={'___bzero':4,'_memset':5,'_memcpy':6,'_memcmp':7,'_strlen':8,'_memmove':9}
        hooks={int(address,16):self.dll.oracle_dependency(adapters[call['import']])
               for address,call in report['external_calls'].items() if call['import'] in adapters}
        self.host_imports={}
        for address,call in report['external_calls'].items():
            if call['import']:
                pointer=host(call['import'])
                if pointer:
                    hooks[int(address,16)]=pointer
                    self.host_imports[call['import']]=pointer
        hooks[int(report['functions']['__Z20luaD_rawrunprotectedP9lua_StatePFvS0_PvES1_']['address'],16)]=host('luaD_rawrunprotected')
        hooks[int(report['functions']['__Z10luaD_throwP9lua_Statei']['address'],16)]=host('luaD_throw')
        self.image=Original(self.binary,report,self.dll,hooks=hooks,enabled=report['functions'],
                            data_overrides=overrides,core=True,auto_rebase=True,data_padding=1,writable_data=True)
        self.functions={}
        for name,function in report['functions'].items():
            self.functions[name]=int(function['address'],16)+self.image.slide
        self.owned={}
        self.memory_used=0
        self.memory_limit=memory_mb*1024*1024
        self.backing_errors=[]
        @C.CFUNCTYPE(U,U,U,U,U)
        def backing(userdata,pointer,old_bytes,new_bytes):
            if pointer:
                old=self.owned.get(pointer)
                if old is None or len(old)!=old_bytes:
                    self.backing_errors.append(('allocation ownership mismatch',pointer,old_bytes))
                    return 0
            if new_bytes==0:
                if pointer:self.owned.pop(pointer);self.memory_used-=old_bytes
                return 0
            if self.memory_used-old_bytes+new_bytes>self.memory_limit:return 0
            memory=C.create_string_buffer(new_bytes)
            address=C.addressof(memory)
            if pointer:
                C.memmove(address,pointer,min(old_bytes,new_bytes));self.owned.pop(pointer)
            self.owned[address]=memory
            self.memory_used+=new_bytes-old_bytes
            return address
        self.backing=backing
        self.dll.oracle_set_callback(0,C.cast(backing,C.c_void_p).value)
        self.allocator=self.dll.oracle_dependency(0)
        self.state=self.image.call_u('__Z12lua_newstatePFPvS_S_mmES_',self.allocator,0)
        if not self.state:raise RuntimeError('Original lua_newstate failed')

    def open_libraries(self):
        self.image.call('__Z13luaL_openlibsP9lua_State',self.state)
        self.logs=[]
        self.output_errors=[]
        @C.CFUNCTYPE(C.c_int,U,U,U)
        def output(state,unused1,unused2):
            # Receive preformatted strings only. Lua callbacks/errors must not
            # transfer control across the Python interpreter's own stack frames.
            values=self.stack(state)
            text='\t'.join(str(v) for v in values)
            self.logs.append(text)
            try:print(text,flush=True)
            except Exception as error:self.output_errors.append(str(error))
            return 0
        self.output=output
        self.dll.oracle_set_callback(2,C.cast(output,C.c_void_p).value)
        self.set_cfunction('__host_print',self.dll.oracle_dependency(10))
        self.dll.host_setup_proxy.argtypes=[U]*3
        self.dll.host_setup_proxy(self.functions['__Z21lua_newuserdatataggedP9lua_Statemi'],
                                  self.functions['__Z15lua_createtableP9lua_Stateii'],
                                  self.functions['__Z16lua_setmetatableP9lua_Statei'])
        self.dll.host_setup_random.argtypes=[U]*4
        self.dll.host_setup_random(*(self.functions[name] for name in (
            '__Z12lua_tobufferP9lua_StateiPm','__Z13lua_tonumberxP9lua_StateiPi',
            '__Z14lua_pushnumberP9lua_Stated','__Z11lua_pushnilP9lua_State')))
        from http_runtime import HttpRuntime
        self.http=HttpRuntime()
        self.dll.host_setup_http.argtypes=[U]*4
        self.dll.host_setup_http(C.cast(self.http.dispatch,C.c_void_p).value,
            self.functions['__Z13lua_tolstringP9lua_StateiPm'],
            self.functions['__Z15lua_pushlstringP9lua_StatePKcm'],self.functions['__Z9luau_loadP9lua_StatePKcS2_mi'])
        for name in ('__host_proxy','__host_random','__host_brickcolor','__host_datetime','__host_sleep','__host_http','__host_guid','__host_loadbytecode'):
            encoded=name.encode()
            self.set_cfunction(name,self.dll.host_import_address(encoded,len(encoded)))

    def set_cfunction(self,name,pointer):
        if not pointer:raise ValueError(f'Missing native callback for {name}')
        key=C.create_string_buffer(name.encode())
        self.image.call5('__Z17lua_pushcclosurekP9lua_StatePFiS0_EPKciPFiS0_iE',self.state,pointer,C.addressof(key),0,0)
        self.image.call3('__Z12lua_setfieldP9lua_StateiPKc',self.state,0xffffd8ee,C.addressof(key))

    def publish_top(self,name):
        """Move an already loaded closure from the VM stack into a global slot."""
        key=C.create_string_buffer(name.encode())
        self.image.call3('__Z12lua_setfieldP9lua_StateiPKc',self.state,0xffffd8ee,C.addressof(key))

    def load(self,bytecode,name=b'@standalone'):
        data=C.create_string_buffer(bytecode)
        chunkname=C.create_string_buffer(name)
        status=self.image.call5('__Z9luau_loadP9lua_StatePKcS2_mi',self.state,C.addressof(chunkname),C.addressof(data),len(bytecode),0)
        if status:raise RuntimeError(f'luau_load returned {status}; stack={self.stack()}')

    def execute(self):
        return self.image.call5('__Z9lua_pcallP9lua_Stateiii',self.state,0,0xffffffff,0,0)

    def stack(self,state=None):
        state=state or self.state
        base=C.c_size_t.from_address(state+56).value
        top=C.c_size_t.from_address(state+88).value
        result=[]
        for address in range(base,top,16):
            tag=C.c_uint32.from_address(address+12).value
            if tag==0:value=None
            elif tag==1:value=bool(C.c_int.from_address(address).value)
            elif tag==3:value=C.c_double.from_address(address).value
            elif tag==4:value=C.c_int64.from_address(address).value
            elif tag==6:
                string=C.c_size_t.from_address(address).value
                length=C.c_uint32.from_address(string+20).value
                value=C.string_at(string+24,length).decode('utf-8','replace')
            else:value=f'<tag {tag} at {C.c_size_t.from_address(address).value:#x}>'
            result.append(value)
        return result

    def close(self):
        if getattr(self,'http',None):self.http.close()
        if getattr(self,'state',0):
            self.image.call('__Z9lua_closeP9lua_State',self.state)
            self.state=0
        self.image.close();self.binary.close()


def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--binary',type=Path,required=True)
    parser.add_argument('bytecode',type=Path)
    parser.add_argument('--libraries',action='store_true')
    args=parser.parse_args()
    runtime=Runtime(args.binary)
    print(json.dumps({'state':hex(runtime.state),'slide':hex(runtime.image.slide),'phase':'initialized'}),flush=True)
    if args.libraries:
        runtime.open_libraries()
        print('Standard libraries initialized.',flush=True)
    runtime.load(args.bytecode.read_bytes())
    print(json.dumps({'phase':'loaded','stack':runtime.stack()}),flush=True)
    status=runtime.execute()
    print(json.dumps({'phase':'executed','status':status,'stack':runtime.stack(),'backing_errors':runtime.backing_errors}),flush=True)
    runtime.close()
    assert not runtime.owned,('Leaked backing allocations',len(runtime.owned))
    print('Original VM closed; backing allocations balanced.',flush=True)


if __name__=='__main__':main()
