"""Compare roster algorithms with unchanged native build 735 functions.

Fixtures provide borrowed, null-controller player pointers. MigrateUserIdAccessors
is enabled to read the stored global ID directly. These tests do not execute
native connection, reference-count destruction, account, or avatar lifecycle code.
"""
import argparse
import ctypes as C
import hashlib
import json
from pathlib import Path
import random
import struct
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from macho import MachO
from original import Original
from run import bootstrap,execute_source,lua_literal
from vm_runtime import Runtime

FIXTURE=ROOT/'tests/fixtures/player_functions.json'
FLAG=0x10d7f6ee8
UNEXECUTED={0x100729224,0x108822734,0x10005edfc,0x10881e396}


def extract(binary):
    from capstone import Cs,CS_ARCH_X86,CS_MODE_64,CS_OP_IMM,CS_OP_MEM,CS_GRP_JUMP
    from capstone.x86 import X86_REG_RIP
    cs=Cs(CS_ARCH_X86,CS_MODE_64);cs.detail=True;functions={};unexecuted=set()
    for name,address in Original.ENGINE_PLAYERS.items():
        code=binary.function_bytes(address);references=set()
        for ins in cs.disasm(code,address):
            if (ins.mnemonic=='call' or ins.group(CS_GRP_JUMP)) and ins.operands[0].type==CS_OP_IMM:
                target=ins.operands[0].imm
                if not address<=target<address+len(code) and target not in Original.ENGINE_PLAYERS.values():
                    assert target in UNEXECUTED,(name,hex(target))
                    unexecuted.add(hex(target))
            for op in ins.operands:
                if op.type==CS_OP_MEM and op.mem.base==X86_REG_RIP:references.add(ins.address+ins.size+op.mem.disp)
        functions[name]={'address':hex(address),'size':len(code),'sha256':hashlib.sha256(code).hexdigest(),
                         'data_references':[hex(a) for a in sorted(references)]}
    report={'functions':functions,'unexecuted_targets':sorted(unexecuted),'flag_override':{hex(FLAG):1},
        'source':'v8datamodel/Players.c; rbx/PlayersProp.c; std::shared_ptr<Player> destructor',
        'comparison':'Four unchanged native bodies; borrowed vector/player fixtures with null reference controllers.',
        'limits':'MigrateUserIdAccessors enabled. No account/domain-ID translation, actual connection setup, ownership destruction or character simulation.'}
    FIXTURE.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


def native_cases(path,extract_metadata):
    rng=random.Random(735592)
    identifiers=[0,-1,1,2,2147483647,2147483648,10**12,-10**12,2**52-1]
    rows=[]
    dll=C.CDLL(str(ROOT/'vm0735.dll'))
    with MachO(path) as binary:
        report=extract(binary) if extract_metadata else json.loads(FIXTURE.read_text())
        with Original(binary,report,dll,enabled=report['functions'],data_overrides={FLAG:b'\x01'}) as original:
            for _ in range(800):
                ids=[rng.choice(identifiers) if rng.random()<.6 else rng.randrange(-10**12,10**12) for _ in range(rng.randrange(31))]
                objects=[C.create_string_buffer(224) for _ in ids]
                addresses=[C.addressof(obj) for obj in objects]
                entries=(C.c_size_t*max(2,2*len(ids)))()
                for index,value in enumerate(ids):
                    struct.pack_into('<q',objects[index],208,value)
                    entries[index*2]=addresses[index]
                begin=C.addressof(entries);end=begin+len(ids)*16
                vector=(C.c_size_t*3)(begin,end,end)
                service=C.create_string_buffer(640)
                struct.pack_into('<QQ',service,592,C.addressof(vector),0)
                count=original.call('players_count',C.addressof(service)+192)
                snapshot=(C.c_size_t*2)()
                original.call3('players_snapshot',C.addressof(snapshot),C.addressof(service),0)
                assert list(snapshot)==[C.addressof(vector),0] and count==len(ids)
                queries=[]
                values=[rng.randrange(-10**12,10**12),*(ids[index] for index in (0,len(ids)//2,-1))] if ids else [0,1,-1,2**52-1]
                for value in values:
                    output=(C.c_size_t*2)()
                    original.call3('players_lookup',C.addressof(output),C.addressof(service),value)
                    assert output[1]==0
                    found=addresses.index(output[0])+1 if output[0] else 0
                    assert found==(ids.index(value)+1 if value in ids else 0)
                    queries.append([value,found])
                rows.append([ids,count,queries])
    return rows


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--binary',type=Path,default=Path('D:/Release-RobloxStudioApp/RobloxStudio.app/Contents/MacOS/RobloxStudio'))
    parser.add_argument('--extract',action='store_true')
    args=parser.parse_args();rows=native_cases(args.binary,args.extract)
    runtime=Runtime(args.binary)
    try:
        runtime.open_libraries()
        with tempfile.TemporaryDirectory(prefix='player-roster-oracle-') as directory:
            work=Path(directory)
            execute_source(runtime,ROOT,bootstrap(ROOT,{'side':'server','noPlayer':True,'duration':0}),work,'bootstrap')
            source='''local players=game:GetService('Players')
for case,row in ROWS do
    local objects={}
    for index,id in row[1] do
        local player=Instance.new('Player');player.UserId=id;player.Parent=players;objects[index]=player
    end
    assert(players.NumPlayers==row[2],case)
    local snapshot=players:GetPlayers();assert(#snapshot==#objects)
    for index,object in snapshot do assert(object==objects[index]) end
    for _,query in row[3] do
        assert(players:GetPlayerByUserId(query[1])==objects[query[2]],'Native player lookup mismatch '..case)
    end
    for _,object in objects do object:Destroy() end
    assert(players.NumPlayers==0)
end
return true
'''.replace('ROWS',lua_literal(rows))
            assert execute_source(runtime,ROOT,source,work,'player-comparison')==[True]
    finally:runtime.close()
    assert not runtime.owned and not runtime.backing_errors
    print('ORIGINAL PLAYER ROSTER LOOKUP, COUNT AND SNAPSHOT CHECKS PASSED',len(rows),sum(len(row[2]) for row in rows))


if __name__=='__main__':main()
