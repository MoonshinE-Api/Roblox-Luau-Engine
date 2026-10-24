"""Original nongarbage allocator/page paths vs reconstructed Rust, with real metadata.

Only the backing allocator and C memset cross the OS boundary. No Lua allocation
function is replaced. OOM/exception and freeing paths are outside this check.
"""
import argparse
import ctypes as C
import hashlib
import json
from pathlib import Path
import random
import struct

from macho import MachO
from original import Original

U = C.c_size_t


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--binary',type=Path,required=True)
    parser.add_argument('--out',type=Path,default=Path(__file__).parent/'data/allocator.json')
    args = parser.parse_args()
    project = Path(__file__).parent
    report = json.loads((project/'data/recovery.json').read_text(encoding='utf-8'))
    dll = C.CDLL(str((project/'vm0735.dll').resolve()))
    dll.oracle_dependency.argtypes,dll.oracle_dependency.restype = [C.c_uint],U
    dll.oracle_set_callback.argtypes = [C.c_uint,U]
    dll.recovered_sizeclassconfig.argtypes,dll.recovered_sizeclassconfig.restype = [U],None
    dll.recovered_allocate_successpath.argtypes,dll.recovered_allocate_successpath.restype = [U,U,C.c_ubyte],U
    dll.recovered_stack_init.argtypes,dll.recovered_stack_init.restype = [U,U,U],None
    dll.recovered_allocation_entry.restype = U
    dll.recovered_free.argtypes,dll.recovered_free.restype = [U,U,U,C.c_ubyte],None
    dll.recovered_realloc_successpath.argtypes,dll.recovered_realloc_successpath.restype = [U,U,U,U,C.c_ubyte],U
    deps = [dll.oracle_dependency(i) for i in range(7)]
    rng = random.Random(7351131)
    config_buffer = C.create_string_buffer(1192+32)
    config_address = C.addressof(config_buffer)+16
    memset_call = report['functions']['SizeClassConfig']['calls']
    assert len(memset_call)==1
    memset_address = int(memset_call[0]['target'],16)
    with MachO(args.binary) as binary:
        assert binary.read(memset_address,2) == b'\xff\x25'
        with Original(binary,report,dll,hooks={memset_address:deps[5]},enabled={'SizeClassConfig'}) as original:
            for case in range(32):
                baseline = rng.randbytes(len(config_buffer))
                C.memmove(C.addressof(config_buffer),baseline,len(baseline))
                original.call('SizeClassConfig',config_address)
                expected = config_buffer.raw
                C.memmove(C.addressof(config_buffer),baseline,len(baseline))
                dll.recovered_sizeclassconfig(config_address)
                assert config_buffer.raw == expected, ('SizeClassConfig',case)
                assert config_buffer.raw[:16]==baseline[:16] and config_buffer.raw[-16:]==baseline[-16:]
            config_bytes = C.string_at(config_address,1192)
        config_location = next(int(address,16) for address,names in report['reference_symbols'].items()
                               if '__ZL16kSizeClassConfig' in names)
        block = C.create_string_buffer(19424+32)
        address = C.addressof(block)+16
        pools = [C.create_string_buffer(32768+32) for _ in range(96)]
        pages = [C.addressof(buf)+16 for buf in pools]
        ctx = {'used':0,'events':[],'notified':[],'bad':[],'live':{}}

        @C.CFUNCTYPE(U,U,U,U,U)
        def backing(userdata,pointer,old_bytes,new_bytes):
            ctx['events'].append([userdata,pointer,old_bytes,new_bytes])
            if pointer and ctx['live'].get(pointer) != old_bytes:
                ctx['bad'].append('Backing allocation size/liveness mismatch')
                return 0
            if new_bytes==0:
                if pointer: del ctx['live'][pointer]
                return 0
            if (not pointer and old_bytes) or new_bytes>32768 or ctx['used']>=len(pages):
                ctx['bad'].append('Unexpected backing allocation')
                return 0
            page = pages[ctx['used']]
            ctx['used']+=1
            ctx['live'][page] = new_bytes
            if pointer:
                C.memmove(page,pointer,min(old_bytes,new_bytes))
                del ctx['live'][pointer]
            return page

        @C.CFUNCTYPE(C.c_int,U,U,U)
        def notify(state,old_bytes,new_bytes):
            ctx['notified'].append([state,old_bytes,new_bytes])
            return 0

        dll.oracle_set_callback(0,C.cast(backing,C.c_void_p).value)
        dll.oracle_set_callback(2,C.cast(notify,C.c_void_p).value)
        initial = bytearray(bytes([0xa5])*16+bytes(19424)+bytes([0xa5])*16)
        for offset,value in [(48,address+128),(184,deps[0]),(192,0x7351131),
                             (216,19424),(11456,19424),(1464,deps[2])]:
            struct.pack_into('<Q',initial,offset+16,value)
        initial[18] = 7
        scenarios = [
            ('all_small_sizes',[(size,size%256) for size in range(1,1025)]),
            ('page_exhaustion',[(size,3) for size in [384]*180+[720]*180+[8]*2100]),
            ('direct_allocations',[(size,255) for size in [0,1025,1026,2048,4096,8192,32768]]),
        ]
        results = []
        enabled = Original.ALLOCATOR | {'stack_init','lua_gettop','lua_pushnumber','lua_type'}
        memcpy_calls = {int(call['target'],16) for call in report['functions']['luaM_realloc_']['calls']
                        if 'target' in call and not call.get('symbols')}
        assert len(memcpy_calls)==1
        memcpy_address = memcpy_calls.pop()
        assert binary.read(memcpy_address,2)==b'\xff\x25'
        with Original(binary,report,dll,enabled=enabled,hooks={memcpy_address:deps[6]},
                      data_overrides={config_location:config_bytes}) as original:
            for name in enabled:
                function = report['functions'][name]
                assert hashlib.sha256(C.string_at(original.functions[name]+original.slide,function['size'])).hexdigest() == function['sha256']

            def reset():
                C.memmove(C.addressof(block),bytes(initial),len(initial))
                for pool in pools: C.memset(C.addressof(pool),0xcd,len(pool))
                ctx.update(used=0,events=[],notified=[],bad=[],live={})

            def snapshot():
                assert not ctx['bad'],ctx['bad']
                sizes = [event[3] for event in ctx['events'] if event[3]]
                assert len(sizes)==ctx['used']
                for pool,size in zip(pools,sizes):
                    raw = pool.raw
                    assert raw[:16]==bytes([0xcd])*16 and raw[16+size:32+size]==bytes([0xcd])*16
                assert block.raw[:16]==bytes([0xa5])*16 and block.raw[-16:]==bytes([0xa5])*16
                return (block.raw,[C.string_at(page,size) for page,size in zip(pages,sizes)],
                        list(ctx['events']),list(ctx['notified']))

            for label,requests in scenarios:
                answers = []
                for recovered in [False,True]:
                    reset()
                    values = []
                    for size,category in requests:
                        value = dll.recovered_allocate_successpath(address,size,category) if recovered else original.call3('luaM_new_',address,size,category)
                        assert value or size==0
                        values.append(value)
                    answers.append((values,snapshot()))
                assert answers[0]==answers[1], ('allocator',label)
                expected_total = 19424+sum(size for size,_ in requests)
                assert struct.unpack_from('<Q',block,16+216)[0]==expected_total
                assert ctx['notified']==[[address,0,size] for size,_ in requests]
                results.append({'scenario':label,'allocations':len(requests),'backing_requests':len(ctx['events']),
                                'total_requested_bytes_including_main_block':expected_total})

            # Fill and exhaust pages, free blocks from different linked pages, reuse
            # free-list entries, resize across class/direct boundaries, and drain all.
            sizes = [384]*60+[720]*45+[8,16,56,64,240,256,480,512,1024,1025,2048,0]
            operations = [('alloc',i,size) for i,size in enumerate(sizes)]
            freed = set(range(0,len(sizes),3))
            operations += [('free',i,0) for i in sorted(freed)]
            operations += [('alloc',len(sizes)+i,384) for i in range(25)]
            resized = [i for i in range(len(sizes)) if i not in freed][::5]
            operations += [('resize',i,size) for i,size in zip(resized,[0,8,31,384,720,1024,1025,2048,4096]*3)]
            lifecycle_results = []
            for recovered in [False,True]:
                reset()
                owned,values = {},[]
                for action,ident,size in operations:
                    category = ident%256
                    if action=='alloc':
                        pointer = dll.recovered_allocate_successpath(address,size,category) if recovered else original.call3('luaM_new_',address,size,category)
                        owned[ident] = (pointer,size)
                    else:
                        old_pointer,old_size = owned.pop(ident)
                        if action=='free':
                            if recovered: dll.recovered_free(address,old_pointer,old_size,category)
                            else: original.call5('luaM_free_',address,old_pointer,old_size,category,0)
                            values.append(('free',ident))
                            continue
                        prefix = C.string_at(old_pointer,min(old_size,size))
                        pointer = dll.recovered_realloc_successpath(address,old_pointer,old_size,size,category) if recovered else original.call5('luaM_realloc_',address,old_pointer,old_size,size,category)
                        assert C.string_at(pointer,min(old_size,size))==prefix, ('realloc payload',ident)
                        if size: owned[ident] = (pointer,size)
                    assert pointer or size==0
                    if size: C.memset(pointer,(ident*37+11)%256,size)
                    values.append((action,ident,pointer,size))
                for ident,(pointer,size) in sorted(owned.items()):
                    if recovered: dll.recovered_free(address,pointer,size,ident%256)
                    else: original.call5('luaM_free_',address,pointer,size,ident%256,0)
                lifecycle_results.append((values,snapshot()))
                assert not ctx['live'], 'Backing pages were not fully released'
                assert struct.unpack_from('<Q',block,16+216)[0]==19424
                assert C.string_at(address+128+144,336)==bytes(336), 'Page-list head leaked'
            assert lifecycle_results[0]==lifecycle_results[1], 'Allocation/free/realloc lifecycle differs'

            stack_results = []
            for recovered in [False,True]:
                reset()
                if recovered: dll.recovered_stack_init(address,address,dll.recovered_allocation_entry())
                else: original.call_u('stack_init',address,address)
                stack_results.append(snapshot())
            assert stack_results[0]==stack_results[1], 'Integrated stack/allocator initialization differs'
            assert original.call('lua_gettop',address)==0
            original.call('lua_pushnumber',address,number=123.5)
            assert original.call('lua_gettop',address)==1
            stack_address = struct.unpack_from('<Q',block,16+64)[0]
            assert C.c_double.from_address(stack_address+16).value==123.5
            # Free the two real stack buffers and verify ownership is balanced.
            original.call_u('freestack',address,address)
            assert not ctx['live']
            assert struct.unpack_from('<Q',block,16+216)[0]==19424
            size_count = struct.unpack_from('<I',config_bytes,1188)[0]
            result = {
                'sizeclass_constructor_cases':32,'sizeclass_count':size_count,
                'sizeclasses':list(struct.unpack_from('<'+'I'*size_count,config_bytes)),
                'allocation_comparisons':sum(item['allocations'] for item in results),
                'scenarios':results,'integrated_stack_initialization_with_actual_allocator':True,
                'page_and_state_bytes_match':True,'allocation_notifications_match':True,
                'buffer_canaries_verified':True,'original_allocator_dependencies_replaced':[],
                'lifecycle_operations_before_final_drain':len(operations),
                'free_reuse_resize_payload_and_final_page_release_verified':True,
                'host_adapters':['caller-supplied successful backing allocator','memset for isolated config constructor','memcpy'],
                'limits':['No garbage-collected object allocator yet','Original Lua OOM exception path is not implemented',
                          'Still no fully initialized global tables or running scripts'],
            }
            args.out.write_text(json.dumps(result,indent=2),encoding='utf-8')
            print(json.dumps(result,indent=2))


if __name__=='__main__': main()
