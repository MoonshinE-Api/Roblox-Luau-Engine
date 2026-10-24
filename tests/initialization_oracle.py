"""Full successful f_luaopen vs reconstructed objects/allocator, not an interpreter.

No VM dependencies are replaced. Only four C imports and caller-owned backing
allocation are adapted. GC tracing feature flag is explicitly disabled in both.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argparse
import ctypes as C
import hashlib
import json
from pathlib import Path
import struct

from macho import MachO
from original import Original

U = C.c_size_t


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--binary',type=Path,required=True)
    parser.add_argument('--out',type=Path,default=Path(__file__).resolve().parents[1]/'data/initialization.json')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    report = json.loads((root/'data/recovery.json').read_text(encoding='utf-8'))
    dll = C.CDLL(str((root/'vm0735.dll').resolve()))
    dll.oracle_dependency.argtypes,dll.oracle_dependency.restype = [C.c_uint],U
    dll.oracle_set_callback.argtypes = [C.c_uint,U]
    dll.recovered_sizeclassconfig.argtypes = [U]
    dll.recovered_newstate_boundary.argtypes,dll.recovered_newstate_boundary.restype = [U]*5,U
    dll.recovered_open_successpath.argtypes,dll.recovered_open_successpath.restype = [U]*4,None
    dll.recovered_intern.argtypes,dll.recovered_intern.restype = [U]*3,U
    deps = [dll.oracle_dependency(i) for i in range(9)]
    config = C.create_string_buffer(1192)
    dll.recovered_sizeclassconfig(C.addressof(config))
    def symbol(name):
        return next(int(address,16) for address,names in report['reference_symbols'].items() if name in names)
    types,events = symbol('_luaT_typenames'),symbol('_luaT_eventname')
    dummy = symbol('_luaH_dummynode')
    overrides = {symbol('__ZL16kSizeClassConfig'):config.raw,
                 symbol('__ZN5FFlag16LuauGcTraceUdataE'):b'\0'}
    hooks = {0x1088229aa:deps[4],0x1088230e2:deps[6],0x1088230dc:deps[7],0x1088236a6:deps[8]}
    enabled = Original.ALLOWED | Original.BOUNDARY | Original.ALLOCATOR | Original.INITIALIZER
    block = C.create_string_buffer(19424+32)
    address = C.addressof(block)+16
    pools = [C.create_string_buffer(32768+32) for _ in range(160)]
    pages = [C.addressof(pool)+16 for pool in pools]
    ctx = {'used':0,'events':[],'live':{},'bad':[],'main_pending':False}

    @C.CFUNCTYPE(U,U,U,U,U)
    def backing(userdata,pointer,old_bytes,new_bytes):
        ctx['events'].append([userdata,pointer,old_bytes,new_bytes])
        if ctx['main_pending']:
            ctx['main_pending'] = False
            if (pointer,old_bytes,new_bytes)!=(0,0,19424): ctx['bad'].append('Unexpected main allocation')
            return address
        if pointer and ctx['live'].get(pointer)!=old_bytes:
            ctx['bad'].append('Size/liveness mismatch'); return 0
        if new_bytes==0:
            if pointer: del ctx['live'][pointer]
            return 0
        if new_bytes>32768 or ctx['used']>=len(pages):
            ctx['bad'].append('Backing capacity exceeded'); return 0
        page = pages[ctx['used']]
        ctx['used']+=1
        ctx['live'][page] = new_bytes
        if pointer:
            C.memmove(page,pointer,min(old_bytes,new_bytes)); del ctx['live'][pointer]
        return page

    @C.CFUNCTYPE(C.c_int,U,U,U)
    def stop_at_open(state,function,userdata): return 0

    @C.CFUNCTYPE(None,U)
    def unexpected_close(state): ctx['bad'].append('Unexpected cleanup path')

    callbacks = [backing,None,stop_at_open,unexpected_close]
    for slot,callback in enumerate(callbacks):
        if callback: dll.oracle_set_callback(slot,C.cast(callback,C.c_void_p).value)

    with MachO(args.binary) as binary, Original(binary,report,dll,hooks=hooks,enabled=enabled,
               data_overrides=overrides,pointer_arrays={types:14,events:21}) as original:
        for name in enabled:
            f=report['functions'][name]
            assert hashlib.sha256(C.string_at(original.functions[name]+original.slide,f['size'])).hexdigest()==f['sha256']
        relocated_types,relocated_events = types+original.slide,events+original.slide
        relocated_dummy = dummy+original.slide

        def reset():
            C.memset(C.addressof(block),0xa5,len(block))
            for pool in pools: C.memset(C.addressof(pool),0xcd,len(pool))
            ctx.update(used=0,events=[],live={},bad=[],main_pending=True)
            assert dll.recovered_newstate_boundary(deps[0],0x7351131,0,deps[2],deps[3])==address

        def snapshot():
            assert not ctx['bad'],ctx['bad']
            sizes=[e[3] for e in ctx['events'][1:] if e[3]]
            assert len(sizes)==ctx['used']
            assert block.raw[:16]==bytes([0xa5])*16 and block.raw[-16:]==bytes([0xa5])*16
            for pool,size in zip(pools,sizes):
                assert pool.raw[:16]==bytes([0xcd])*16 and pool.raw[16+size:32+size]==bytes([0xcd])*16
            return block.raw,[C.string_at(p,size) for p,size in zip(pages,sizes)],list(ctx['events'])

        snapshots=[]
        # Deliberately exercise the actual original initializer, not a replacement.
        for recovered in [False,True]:
            reset()
            if recovered: dll.recovered_open_successpath(address,relocated_dummy,relocated_types,relocated_events)
            else: original.call_u('f_luaopen',address,0)
            snapshots.append(snapshot())
        if snapshots[0]!=snapshots[1]:
            a,b=snapshots
            print('STATE DIFFERENCES',[(i,x,y) for i,(x,y) in enumerate(zip(a[0],b[0])) if x!=y][:20],flush=True)
            print('PAGE DIFFERENCES',[(page,[(i,x,y) for i,(x,y) in enumerate(zip(xb,yb)) if x!=y][:10])
                  for page,(xb,yb) in enumerate(zip(a[1],b[1])) if xb!=yb][:8],flush=True)
            print('BACKING EVENTS',a[2],b[2],flush=True)
            raise AssertionError('Full successful initialization differs')
        global_address=address+128
        string_count=C.c_uint32.from_address(global_address+12).value
        type_names=[]
        for i in range(14):
            string=C.c_size_t.from_address(global_address+1088+i*8).value
            type_names.append(C.string_at(string+24).decode())
        event_names=[]
        for i in range(21):
            string=C.c_size_t.from_address(global_address+920+i*8).value
            event_names.append(C.string_at(string+24).decode())
        assert original.call('lua_gettop',address)==0
        original.call('lua_pushnumber',address,number=42.0)
        assert original.call('lua_gettop',address)==1
        # Intern repeated/embedded-NUL/long strings, force table growth and collisions.
        strings=[b'',b'x\0y',b'hello',b'hello']+[f'key_{i}'.encode() for i in range(180)]+[b'z'*1024]
        intern_results=[]
        for recovered in [False,True]:
            reset()
            dll.recovered_open_successpath(address,relocated_dummy,relocated_types,relocated_events)
            values=[]
            for data in strings:
                buffer=C.create_string_buffer(data)
                value=dll.recovered_intern(address,C.addressof(buffer),len(data)) if recovered else original.call3('luaS_newlstr',address,C.addressof(buffer),len(data))
                assert C.string_at(value+24,len(data))==data
                values.append(value)
            assert values[2]==values[3]
            intern_results.append((values,snapshot()))
        assert intern_results[0]==intern_results[1], 'Interning/resizing/collisions differ'
        result={'full_successful_f_luaopen_bytes_match':True,'vm_dependencies_replaced':[],
                'gc_trace_userdata_flag':False,'original_code_hashes_verified':len(enabled),
                'intern_operations':len(strings),'initial_interned_strings':string_count,
                'initial_type_names':type_names,'initial_event_names':event_names,
                'initialized_fields':['stack','global table','registry','string hash table','fixed type/event/error strings','GC threshold'],
                'memory_snapshot_includes':['main state','all backing pages','allocation/free events','buffer canaries'],
                'limits':['Successful initialization only; OOM/unwinding pending','Not yet a bytecode interpreter or Engine API',
                          'GC allocation exists; tracing collection is not restored']}
        args.out.write_text(json.dumps(result,indent=2),encoding='utf-8')
        print(json.dumps(result,indent=2))


if __name__=='__main__': main()
