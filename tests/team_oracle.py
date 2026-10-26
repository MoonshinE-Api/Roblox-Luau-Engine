"""Compare color lookup, neutral filtering and counts with native build 735.

Three dependency bridges return borrowed fixture class descriptors/Players.
The five compared bodies remain unchanged; no C++ objects are constructed.
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

FIXTURE=ROOT/'tests/fixtures/team_functions.json'
DEPENDENCIES={0x100a5c2be:'fixture Team descriptor',0x10072f0fa:'fixture Player descriptor',
              0x1010b1d88:'fixture Players service'}


def extract(binary):
    from capstone import Cs,CS_ARCH_X86,CS_MODE_64,CS_OP_IMM,CS_OP_MEM,CS_GRP_JUMP
    from capstone.x86 import X86_REG_RIP
    cs=Cs(CS_ARCH_X86,CS_MODE_64);cs.detail=True;functions={};dependencies=set()
    for name,address in Original.ENGINE_TEAMS.items():
        code=binary.function_bytes(address);references=set()
        for ins in cs.disasm(code,address):
            if (ins.mnemonic=='call' or ins.group(CS_GRP_JUMP)) and ins.operands[0].type==CS_OP_IMM:
                target=ins.operands[0].imm
                if not address<=target<address+len(code) and target not in Original.ENGINE_TEAMS.values():
                    assert target in DEPENDENCIES,(name,hex(target));dependencies.add(target)
            for op in ins.operands:
                if op.type==CS_OP_MEM and op.mem.base==X86_REG_RIP:references.add(ins.address+ins.size+op.mem.disp)
        functions[name]={'address':hex(address),'size':len(code),'sha256':hashlib.sha256(code).hexdigest(),
                         'data_references':[hex(a) for a in sorted(references)]}
    assert dependencies==DEPENDENCIES.keys()
    report={'functions':functions,'adapted_dependencies':{hex(a):DEPENDENCIES[a] for a in sorted(dependencies)},
        'source':'v8datamodel/Teams.c',
        'comparison':'Five unchanged bodies; borrowed vectors, class-range descriptors and null reference controllers.',
        'limits':'Fixture service/descriptor lookup is bridged. No native membership events, network joins, automatic assignment, object construction or ownership destruction executed.'}
    FIXTURE.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


def native_cases(path,extract_metadata):
    rng=random.Random(735184);rows=[]
    colors=[1,21,23,24,194,1004,1024]
    dll=C.CDLL(str(ROOT/'vm0735.dll'));U=C.c_size_t
    dll.oracle_set_callback.argtypes=[C.c_uint,U]
    dll.oracle_dependency.argtypes=[C.c_uint];dll.oracle_dependency.restype=U
    descriptor=C.create_string_buffer(448);other=C.create_string_buffer(448)
    struct.pack_into('<HH',descriptor,440,100,0);struct.pack_into('<HH',other,440,200,0)
    service=C.create_string_buffer(256);player_service=C.create_string_buffer(256)
    @C.CFUNCTYPE(U,U,U,U,U)
    def get_descriptor(*unused):return C.addressof(descriptor)
    @C.CFUNCTYPE(U,U,U,C.c_ubyte)
    def get_players(*unused):return C.addressof(player_service)
    dll.oracle_set_callback(0,C.cast(get_descriptor,C.c_void_p).value)
    dll.oracle_set_callback(1,C.cast(get_players,C.c_void_p).value)
    hooks={address:dll.oracle_dependency(1 if 'service' in label else 0) for address,label in DEPENDENCIES.items()}
    def vector(records,player=False):
        objects=[];entries=(U*max(2,2*len(records)))()
        for index,(color,neutral,valid) in enumerate(records):
            obj=C.create_string_buffer(912 if player else 208);objects.append(obj)
            struct.pack_into('<Q',obj,24,C.addressof(descriptor if valid else other))
            struct.pack_into('<I',obj,872 if player else 184,color)
            if player:struct.pack_into('B',obj,900,neutral)
            entries[2*index]=C.addressof(obj)
        begin=C.addressof(entries);end=begin+16*len(records)
        return objects,entries,(U*3)(begin,end,end)
    with MachO(path) as binary:
        report=extract(binary) if extract_metadata else json.loads(FIXTURE.read_text())
        with Original(binary,report,dll,hooks=hooks,enabled=report['functions']) as native:
            for _ in range(320):
                definitions=[(rng.choice(colors),False,rng.random()>.15) for _ in range(rng.randrange(13))]
                members=[(rng.choice(colors),rng.random()<.35,rng.random()>.15) for _ in range(rng.randrange(18))]
                team_objects,team_entries,team_vector=vector(definitions)
                player_objects,player_entries,player_vector=vector(members,True)
                struct.pack_into('<Q',service,120,C.addressof(team_vector))
                struct.pack_into('<QQ',service,200,C.addressof(team_vector),0)
                struct.pack_into('<Q',player_service,120,C.addressof(player_vector))
                output=(U*2)();native.call3('teams_snapshot',C.addressof(output),C.addressof(service),0)
                assert list(output)==[C.addressof(team_vector),0]
                before=bytes(service);native.call('teams_rebalance',C.addressof(service));assert bytes(service)==before
                addresses=[C.addressof(obj) for obj in team_objects]
                queries=[]
                probe=C.create_string_buffer(912)
                for color in colors:
                    found=native.call3('teams_lookup',C.addressof(service),color,0)
                    index=addresses.index(found)+1 if found else 0
                    expected=next((i+1 for i,row in enumerate(definitions) if row[2] and row[0]==color),0)
                    count=native.call3('teams_count',C.addressof(service),color,0)
                    assert index==expected and count==sum(valid and not neutral and c==color for c,neutral,valid in members)
                    struct.pack_into('<I',probe,872,color)
                    for neutral in (False,True):
                        struct.pack_into('B',probe,900,neutral)
                        actual=native.call3('teams_from_player',C.addressof(service),C.addressof(probe),0)
                        assert actual==(0 if neutral else found)
                    queries.append([color,index,count])
                rows.append([[list(item) for item in definitions],[list(item) for item in members],queries])
    return rows


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--binary',type=Path,default=Path('D:/Release-RobloxStudioApp/RobloxStudio.app/Contents/MacOS/RobloxStudio'))
    parser.add_argument('--extract',action='store_true');args=parser.parse_args()
    rows=native_cases(args.binary,args.extract)
    runtime=Runtime(args.binary)
    try:
        runtime.open_libraries()
        with tempfile.TemporaryDirectory(prefix='team-oracle-') as directory:
            work=Path(directory)
            execute_source(runtime,ROOT,bootstrap(ROOT,{'side':'server','noPlayer':True,'duration':0}),work,'bootstrap')
            source='''local players,teams=game:GetService('Players'),game:GetService('Teams')
for case,row in ROWS do
    local objects,records={},{}
    for i,definition in row[1] do
        local object=Instance.new(if definition[3] then 'Team' else 'Folder')
        objects[i]=object
        if definition[3] then object.AutoAssignable=false;object.TeamColor=BrickColor.new(definition[1]) end
        object.Parent=teams
    end
    for _,definition in row[2] do
        local object=Instance.new(if definition[3] then 'Player' else 'Folder')
        if definition[3] then object.TeamColor=BrickColor.new(definition[1]) end
        object.Parent=players
        if definition[3] then object.Neutral=definition[2] end
        table.insert(records,object)
    end
    local probe=Instance.new('Player',players)
    for _,query in row[3] do
        probe.Neutral=true;probe.TeamColor=BrickColor.new(query[1]);probe.Neutral=false
        assert(probe.Team==objects[query[2]],'Native team lookup mismatch '..case)
        probe.Neutral=true;assert(probe.Team==nil)
        local team=objects[query[2]]
        if team then assert(#team:GetPlayers()==query[3],'Native team count mismatch '..case) end
    end
    local snapshot=teams:GetTeams();local expected=0
    for _,definition in row[1] do if definition[3] then expected+=1 end end
    assert(#snapshot==expected);table.clear(snapshot);assert(#teams:GetTeams()==expected)
    teams:RebalanceTeams()
    probe:Destroy()
    for _,record in records do record:Destroy() end
    for _,object in objects do object:Destroy() end
end
return true
'''.replace('ROWS',lua_literal(rows))
            assert execute_source(runtime,ROOT,source,work,'team-comparison')==[True]
    finally:runtime.close()
    assert not runtime.owned and not runtime.backing_errors
    print('ORIGINAL TEAM LOOKUP, COUNTS, NEUTRAL FILTER, SNAPSHOT AND REBALANCE CHECKS PASSED',len(rows),len(rows)*7*4)


if __name__=='__main__':main()
