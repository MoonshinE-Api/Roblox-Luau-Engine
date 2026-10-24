"""Compare bootstrap boundaries, stack initialization, and strings with original bytes.

f_luaopen is deliberately not executed: the protected-runner boundary records its
arguments and supplies test statuses. This validates preinitialization and control
flow, NOT a working Lua VM, garbage collector, or real exception unwinding.
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
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--out', type=Path, default=Path(__file__).parent/'evidence/bootstrap.json')
    args = parser.parse_args()
    project = Path(__file__).parent
    report = json.loads((project/'evidence/recovery.json').read_text(encoding='utf-8'))
    dll = C.CDLL(str((project/'vm0735.dll').resolve()))
    dll.oracle_dependency.argtypes, dll.oracle_dependency.restype = [C.c_uint], U
    dll.oracle_set_callback.argtypes = [C.c_uint, U]
    dll.recovered_stringhash.argtypes, dll.recovered_stringhash.restype = [U,U], C.c_uint32
    dll.recovered_newstate_boundary.argtypes, dll.recovered_newstate_boundary.restype = [U]*5, U
    dll.recovered_stack_init.argtypes, dll.recovered_stack_init.restype = [U]*3, None
    deps = [dll.oracle_dependency(i) for i in range(5)]
    # Guard both sides of all buffers; 16-byte alignment is required by original movaps.
    block, info, stack = [C.create_string_buffer(size+32) for size in [19424,384,720]]
    block_address, info_address, stack_address = [C.addressof(buf)+16 for buf in [block,info,stack]]
    assert block_address % 16 == 0
    ctx = {'events': [], 'fail': False, 'status': 0, 'memory_requests': 0}

    @C.CFUNCTYPE(U,U,U,U,U)
    def allocate(userdata, pointer, old_size, size):
        ctx['events'].append(['allocate', userdata, pointer, old_size, size])
        return 0 if ctx['fail'] else block_address

    @C.CFUNCTYPE(U,U,U,C.c_ubyte)
    def newmemory(parent, size, category):
        ctx['events'].append(['newmemory', parent, size, category])
        ctx['memory_requests'] += 1
        return info_address if ctx['memory_requests'] == 1 else stack_address

    @C.CFUNCTYPE(C.c_int,U,U,U)
    def protected(state, function, userdata):
        ctx['events'].append(['protected_boundary', state, function, userdata])
        return ctx['status']

    @C.CFUNCTYPE(None,U)
    def close(state):
        ctx['events'].append(['cleanup_boundary', state])

    callbacks = [allocate,newmemory,protected,close]  # Keep callbacks alive.
    for slot, callback in enumerate(callbacks):
        dll.oracle_set_callback(slot, C.cast(callback, C.c_void_p).value)
    hooks = {
        int(report['functions']['luaM_new_']['address'],16): deps[1],
        int(report['functions']['luaD_rawrunprotected']['address'],16): deps[2],
        int(report['functions']['close_state']['address'],16): deps[3],
    }
    # The repeated direct call in newstate is the __bzero import stub. Verify the
    # binary stub shape before replacing its private mapping; it is not a VM body.
    bzero = {int(c['target'],16) for c in report['functions']['lua_newstate']['calls']
             if 'target' in c and not c.get('symbols')}
    assert len(bzero) == 1
    bzero_address = bzero.pop()
    hooks[bzero_address] = deps[4]
    randomizer = random.Random(7351131)
    counts = {'stringhash':0, 'newstate_preinit':0, 'stack_init':0}
    string_vectors = []
    with MachO(args.binary) as binary:
        assert binary.read(bzero_address,2) == b'\xff\x25', 'Unexpected import-stub encoding'
        with Original(binary,report,dll,hooks=hooks) as original:
            # Keep tested entry point bytes unchanged, despite replacing dependencies.
            for name in ['lua_newstate','stack_init','luaS_hash']:
                function = report['functions'][name]
                mapped = C.string_at(original.functions[name]+original.slide, function['size'])
                assert hashlib.sha256(mapped).hexdigest() == function['sha256']
            opener = int(report['functions']['f_luaopen']['address'],16)+original.slide
            for length in list(range(100)) + [127,128,255,256,1023,1024,4095,4096]*16:
                data = randomizer.randbytes(length)
                # Include unaligned addresses to check the actual x86 string path.
                source = C.create_string_buffer(b'X'+data+b'Z')
                address = C.addressof(source)+1
                expected = original.call_u('luaS_hash',address,length) & 0xffffffff
                actual = dll.recovered_stringhash(address,length)
                assert expected == actual, ('stringhash',length,expected,actual)
                counts['stringhash'] += 1
                if length in [0,31,32,33,43,44]:
                    string_vectors.append({'length':length,'input_hex':data.hex(),'hash':actual})

            for case in range(96):
                before = randomizer.randbytes(len(block))
                userdata = randomizer.getrandbits(64)
                ctx['fail'] = case % 4 == 0
                ctx['status'] = [0,2,4,7][(case // 4) % 4]
                if case == 0: ctx['fail'] = False  # Explicit success case.
                results = []
                for recovered in [False,True]:
                    C.memmove(C.addressof(block),before,len(block))
                    ctx['events'] = []
                    if recovered:
                        answer = dll.recovered_newstate_boundary(deps[0],userdata,opener,deps[2],deps[3])
                    else:
                        answer = original.call_u('lua_newstate',deps[0],userdata)
                    results.append((answer,block.raw,list(ctx['events'])))
                expected,actual = results
                assert expected == actual, ('newstate_preinit',case,
                    next((i for i,(a,b) in enumerate(zip(expected[1],actual[1])) if a!=b),None),
                    expected[2],actual[2])
                assert block.raw[:16] == before[:16] and block.raw[-16:] == before[-16:]
                expected_events = [['allocate',userdata,0,0,19424]]
                if not ctx['fail']:
                    expected_events.append(['protected_boundary',block_address,opener,0])
                    if ctx['status']: expected_events.append(['cleanup_boundary',block_address])
                assert actual[2] == expected_events
                assert actual[0] == (block_address if not ctx['fail'] and ctx['status']==0 else 0)
                counts['newstate_preinit'] += 1

            for case in range(96):
                baseline = [randomizer.randbytes(len(buf)) for buf in [block,info,stack]]
                parent = randomizer.getrandbits(64)
                results = []
                for recovered in [False,True]:
                    for buf,raw in zip([block,info,stack],baseline): C.memmove(C.addressof(buf),raw,len(raw))
                    ctx['events'],ctx['memory_requests'] = [],0
                    if recovered: dll.recovered_stack_init(block_address,parent,deps[1])
                    else: original.call_u('stack_init',block_address,parent)
                    results.append(([buf.raw for buf in [block,info,stack]],list(ctx['events'])))
                assert results[0] == results[1], ('stack_init',case)
                category = baseline[0][18]
                assert results[1][1] == [['newmemory',parent,384,category],['newmemory',parent,720,category]]
                for buf,before in zip([block,info,stack],baseline):
                    assert buf.raw[:16] == before[:16] and buf.raw[-16:] == before[-16:]
                # Check recovered primitives on the stack that original initialization produced.
                assert original.call('lua_gettop',block_address) == 0
                original.call('lua_pushnumber',block_address,number=42.5)
                assert original.call('lua_gettop',block_address) == 1
                assert original.call('lua_type',block_address,argument=1) == 3
                assert struct.unpack_from('<d',stack,32)[0] == 42.5
                counts['stack_init'] += 1
            result = {
                'counts':counts, 'total_differential_cases':sum(counts.values()),
                'string_vectors':string_vectors,
                'entry_bytes_match_original':True, 'buffer_canaries_verified':True,
                'stack_allocations':[384,720], 'stack_slots':45, 'call_info_entries':8,
                'main_block_bytes':19424,
                'dependency_replacements':{
                    'luaM_new_':'test-owned fixed buffers; original small-block allocator not executed',
                    'luaD_rawrunprotected':'records f_luaopen address; supplies test statuses; does not invoke f_luaopen',
                    'close_state':'records cleanup request; original GC/free path not executed',
                    '__bzero':'ABI-compatible Rust zero fill'},
                'limits':['Not a fully initialized VM','No tables, strings, GC, allocator page lists or real unwinding',
                          'No compilation, bytecode loading, script execution or Engine API yet'],
            }
            args.out.write_text(json.dumps(result,indent=2),encoding='utf-8')
            print(json.dumps(result,indent=2))


if __name__ == '__main__': main()
