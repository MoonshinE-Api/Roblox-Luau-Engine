"""Compare clock clamping, second quantization and day wrapping with original code."""
import argparse
import ctypes as C
import hashlib
import json
from pathlib import Path
import random
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from macho import MachO
from original import Original
from run import bootstrap,execute_source,lua_literal
from vm_runtime import Runtime

FIXTURE=ROOT/'tests/fixtures/lighting_functions.json'


def extract(binary):
    from capstone import Cs,CS_ARCH_X86,CS_MODE_64,CS_OP_IMM,CS_OP_MEM,CS_GRP_JUMP
    from capstone.x86 import X86_REG_RIP
    cs=Cs(CS_ARCH_X86,CS_MODE_64);cs.detail=True;functions={}
    for name,address in Original.ENGINE_ENVIRONMENT.items():
        code=binary.function_bytes(address);references=set()
        for ins in cs.disasm(code,address):
            if (ins.mnemonic=='call' or ins.group(CS_GRP_JUMP)) and ins.operands[0].type==CS_OP_IMM:
                assert address<=ins.operands[0].imm<address+len(code),'Unexpected time dependency'
            for op in ins.operands:
                if op.type==CS_OP_MEM and op.mem.base==X86_REG_RIP:references.add(ins.address+ins.size+op.mem.disp)
        functions[name]={'address':hex(address),'size':len(code),'sha256':hashlib.sha256(code).hexdigest(),
                         'data_references':[hex(a) for a in sorted(references)]}
    report={'functions':functions,'source':'v8datamodel/Lighting.c',
            'comparison':'Unchanged float32 clock conversion and signed duration normalization functions.'}
    FIXTURE.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--binary',type=Path,default=Path('D:/Release-RobloxStudioApp/RobloxStudio.app/Contents/MacOS/RobloxStudio'))
    parser.add_argument('--extract',action='store_true')
    args=parser.parse_args()
    dll=C.CDLL(str(ROOT/'vm0735.dll'))
    dll.original_call_clock.argtypes=[C.c_size_t,C.c_void_p,C.c_float];dll.original_call_clock.restype=None
    rng=random.Random(73514)
    hours=[float('nan'),float('inf'),-float('inf'),-1,0,0.0001,0.5,12.34567,23.99999,24,25]
    hours.extend(rng.uniform(-100,100) for _ in range(600))
    minutes=[-1500,-1440,-0.03,-0.001,0,0.001,0.03,1440,1500,2147483647/60,2147483648/60]
    minutes.extend(rng.uniform(-1e7,1e7) for _ in range(400))
    for _ in range(512):
        seconds=rng.randrange(-2147483648,2147483648)
        minutes.extend([seconds/60,(seconds+0.000001)/60])
    rows=[];minute_rows=[]
    with MachO(args.binary) as binary:
        report=extract(binary) if args.extract else json.loads(FIXTURE.read_text())
        with Original(binary,report,dll,enabled=report['functions']) as original:
            for value in hours:
                raw,normalized=C.c_int64(),C.c_int64()
                dll.original_call_clock(original.functions['lighting_clock']+original.slide,C.byref(raw),value)
                original.call3('lighting_time_normalize',C.addressof(normalized),0,C.addressof(raw))
                rows.append([value,normalized.value/1e6])
            for value in minutes:
                raw=C.c_int64(int(value*60000000));normalized=C.c_int64()
                original.call3('lighting_time_normalize',C.addressof(normalized),0,C.addressof(raw))
                minute_rows.append([value,normalized.value/1e6])
    runtime=Runtime(args.binary)
    try:
        runtime.open_libraries()
        with tempfile.TemporaryDirectory(prefix='lighting-clock-') as directory:
            work=Path(directory)
            execute_source(runtime,ROOT,bootstrap(ROOT,{'side':'server','duration':0}),work,'bootstrap')
            source='''local light=game:GetService('Lighting')
for index,row in HOURS do
    light.ClockTime=row[1]
    assert(math.abs(light:GetMinutesAfterMidnight()*60-row[2])<1e-7,'Clock mismatch '..index..': '..(light:GetMinutesAfterMidnight()*60)..' ~= '..row[2])
end
for index,row in MINUTES do
    light:SetMinutesAfterMidnight(row[1])
    assert(math.abs(light:GetMinutesAfterMidnight()*60-row[2])<1e-7,'Minute mismatch '..index..': '..(light:GetMinutesAfterMidnight()*60)..' ~= '..row[2])
end
return true
'''.replace('HOURS',lua_literal(rows)).replace('MINUTES',lua_literal(minute_rows))
            assert execute_source(runtime,ROOT,source,work,'clock-comparison')==[True]
    finally:runtime.close()
    assert not runtime.owned and not runtime.backing_errors
    print('ORIGINAL LIGHTING CLOCK AND DAY NORMALIZATION CHECKS PASSED',len(rows),len(minute_rows))


if __name__=='__main__':main()
