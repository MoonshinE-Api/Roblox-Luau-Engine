"""Compare float32 health views and state-enable reads with native build 735."""
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

FIXTURE=ROOT/'tests/fixtures/humanoid_functions.json'


def extract(binary):
    from capstone import Cs,CS_ARCH_X86,CS_MODE_64,CS_OP_IMM,CS_OP_MEM,CS_GRP_JUMP
    from capstone.x86 import X86_REG_RIP
    cs=Cs(CS_ARCH_X86,CS_MODE_64);cs.detail=True;functions={};unexecuted=[]
    for name,address in Original.ENGINE_HUMANOID.items():
        code=binary.function_bytes(address);references=set()
        for ins in cs.disasm(code,address):
            if (ins.mnemonic=='call' or ins.group(CS_GRP_JUMP)) and ins.operands[0].type==CS_OP_IMM:
                target=ins.operands[0].imm
                if not address<=target<address+len(code):
                    assert name=='humanoid_state_enabled',(name,hex(target))
                    unexecuted.append(hex(target))
            for op in ins.operands:
                if op.type==CS_OP_MEM and op.mem.base==X86_REG_RIP:references.add(ins.address+ins.size+op.mem.disp)
        functions[name]={'address':hex(address),'size':len(code),'sha256':hashlib.sha256(code).hexdigest(),
                         'data_references':[hex(a) for a in sorted(references)]}
    report={'functions':functions,'unexecuted_invalid_state_logging':unexecuted,
        'source':'humanoid/Humanoid.part001.c; humanoid/Humanoid.part002.c',
        'comparison':'Unchanged transformHealthCallback and getStateTransitionEnabled bodies.',
        'limits':'Borrowed scalar/flag fixtures only; no rigs, locomotion, damage, death state machine, ownership or native events executed.'}
    FIXTURE.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


def native_cases(path,extract_metadata):
    rng=random.Random(735408)
    samples=[-float('inf'),-1e30,-1,-0.0,0,1e-30,1,99.25,100,100.5,1e30,float('inf'),float('nan')]
    cases=[(maximum,value) for maximum in (0,1e-20,1,100,250,float('inf')) for value in samples]
    cases.extend((10**rng.uniform(-6,10),rng.uniform(-1e10,1e10)) for _ in range(1600))
    enum=json.loads((ROOT/'data/enum_catalog.json').read_text())['enums']['HumanoidStateType']
    states=[(name,value) for name,value in enum.items() if value<17]
    health=[];flags=[]
    dll=C.CDLL(str(ROOT/'vm0735.dll'));dll.original_call_scalar_f32.argtypes=[C.c_size_t,C.c_size_t,C.c_float]
    dll.original_call_scalar_f32.restype=C.c_float
    with MachO(path) as binary:
        report=extract(binary) if extract_metadata else json.loads(FIXTURE.read_text())
        with Original(binary,report,dll,enabled=report['functions']) as original:
            buffer=C.create_string_buffer(2304)
            for maximum,value in cases:
                maximum=C.c_float(maximum).value;value=C.c_float(value).value
                struct.pack_into('<f',buffer,408,maximum)
                result=dll.original_call_scalar_f32(original.functions['humanoid_health_view']+original.slide,C.addressof(buffer),value)
                health.append([maximum,value,result])
            for _ in range(120):
                row=[]
                for name,value in states:
                    expected=rng.randrange(2)
                    C.c_uint8.from_address(C.addressof(buffer)+2196+value).value=expected
                    native=original.call3('humanoid_state_enabled',C.addressof(buffer),value,0)&255
                    assert native==expected
                    row.append([name,bool(native)])
                flags.append(row)
    return health,flags


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--binary',type=Path,default=Path('D:/Release-RobloxStudioApp/RobloxStudio.app/Contents/MacOS/RobloxStudio'))
    parser.add_argument('--extract',action='store_true')
    args=parser.parse_args();health,flags=native_cases(args.binary,args.extract)
    runtime=Runtime(args.binary)
    try:
        runtime.open_libraries()
        with tempfile.TemporaryDirectory(prefix='humanoid-oracle-') as directory:
            work=Path(directory)
            execute_source(runtime,ROOT,bootstrap(ROOT,{'side':'server','duration':0}),work,'bootstrap')
            source='''local humanoid=Instance.new('Humanoid')
for index,row in HEALTH do
    humanoid.MaxHealth=row[1];humanoid.Health=row[2]
    local expected,actual=row[3],humanoid.Health
    assert(expected==actual or expected~=expected and actual~=actual,'Native health view mismatch '..index..': '..actual..' ~= '..expected)
end
for _,row in FLAGS do
    for _,entry in row do
        local state=Enum.HumanoidStateType[entry[1]]
        humanoid:SetStateEnabled(state,entry[2])
        assert(humanoid:GetStateEnabled(state)==entry[2])
    end
end
humanoid:Destroy();return true
'''.replace('HEALTH',lua_literal(health)).replace('FLAGS',lua_literal(flags))
            assert execute_source(runtime,ROOT,source,work,'humanoid-comparison')==[True]
    finally:runtime.close()
    assert not runtime.owned and not runtime.backing_errors
    print('ORIGINAL HUMANOID FLOAT32 HEALTH AND STATE FLAG CHECKS PASSED',len(health),sum(map(len,flags)))


if __name__=='__main__':main()
