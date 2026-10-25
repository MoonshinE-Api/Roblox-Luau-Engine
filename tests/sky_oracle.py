"""Compare sky directions with unchanged original LightingParameters code."""
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

FIXTURE=ROOT/'tests/fixtures/sky_functions.json'
ADAPTED={'_cos','___sincosf_stret','___cxa_guard_acquire','___cxa_guard_release'}
UNEXECUTED={'___stack_chk_fail','__Unwind_Resume'}


def extract(binary):
    from capstone import Cs,CS_ARCH_X86,CS_MODE_64,CS_OP_IMM,CS_OP_MEM,CS_GRP_JUMP
    from capstone.x86 import X86_REG_RIP
    cs=Cs(CS_ARCH_X86,CS_MODE_64);cs.detail=True
    functions={};external={};unexecuted={};imports=binary.import_stubs()
    for name,address in Original.ENGINE_SKY.items():
        code=binary.function_bytes(address);references=set()
        for ins in cs.disasm(code,address):
            if (ins.mnemonic=='call' or ins.group(CS_GRP_JUMP)) and ins.operands[0].type==CS_OP_IMM:
                target=ins.operands[0].imm
                if not address<=target<address+len(code) and target not in Original.ENGINE_SKY.values():
                    symbol=imports.get(target)
                    assert symbol in ADAPTED|UNEXECUTED,(hex(target),symbol)
                    (external if symbol in ADAPTED else unexecuted)[hex(target)]={'import':symbol}
            for op in ins.operands:
                if op.type==CS_OP_MEM and op.mem.base==X86_REG_RIP:references.add(ins.address+ins.size+op.mem.disp)
        functions[name]={'address':hex(address),'size':len(code),'sha256':hashlib.sha256(code).hexdigest(),
                         'data_references':[hex(a) for a in sorted(references)]}
    guard=next(address for address,symbol in binary.import_pointers().items() if symbol=='___stack_chk_guard')
    report={'functions':functions,'external_calls':external,'unexecuted_exception_calls':unexecuted,
            'stack_guard_slot':hex(guard),'source':'rbx/LightingParameters.c; rbx/Matrix3.c; v8datamodel/Lighting.c',
            'comparison':'All five original function bodies unchanged. Only cos/sincosf, C++ initialization guards and the stack-guard pointer are adapted to Windows.'}
    FIXTURE.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


def original_rows(binary_path,extract_metadata=False):
    dll=C.CDLL(str(ROOT/'vm0735.dll'));U=C.c_size_t
    dll.host_import_address.argtypes,dll.host_import_address.restype=[C.c_char_p,U],U
    dll.oracle_stack_guard.restype=U
    dll.original_call_sky.argtypes=[U,C.c_void_p,C.c_double,C.c_float,C.c_float]
    dll.original_call_sky.restype=None
    rng=random.Random(73586400)
    cases=[(second,latitude) for second in [0,1,21599,21600,43199,43200,64800,86399] for latitude in [-90,-66.5,0,23.5,41.7333,66.5,90]]
    cases.extend((rng.randrange(86400),rng.uniform(-180,180)) for _ in range(1000))
    rows=[]
    with MachO(binary_path) as binary:
        report=extract(binary) if extract_metadata else json.loads(FIXTURE.read_text())
        hooks={int(a,16):dll.host_import_address(item['import'].encode(),len(item['import'])) for a,item in report['external_calls'].items()}
        overrides={int(report['stack_guard_slot'],16):struct.pack('<Q',dll.oracle_stack_guard())}
        with Original(binary,report,dll,hooks=hooks,enabled=report['functions'],data_overrides=overrides,writable_data=True,data_padding=1) as original:
            for second,latitude in cases:
                result=C.create_string_buffer(92)
                C.memmove(C.addressof(result)+76,b'\xA5'*16,16)
                dll.original_call_sky(original.functions['sky_time']+original.slide,result,second,0,latitude)
                assert result.raw[76:92]==b'\xA5'*16,'Sky output overrun'
                rows.append([second,C.c_float(latitude).value,list(struct.unpack_from('<6f',result.raw,40))])
    return rows


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--binary',type=Path,default=Path('D:/Release-RobloxStudioApp/RobloxStudio.app/Contents/MacOS/RobloxStudio'))
    parser.add_argument('--extract',action='store_true')
    parser.add_argument('--probe',action='store_true')
    args=parser.parse_args()
    rows=original_rows(args.binary,args.extract)
    if args.probe:
        print(json.dumps({'cases':len(rows),'first':rows[:3]}));return
    runtime=Runtime(args.binary)
    try:
        runtime.open_libraries()
        with tempfile.TemporaryDirectory(prefix='sky-directions-') as folder:
            work=Path(folder)
            execute_source(runtime,ROOT,bootstrap(ROOT,{'side':'server','duration':0}),work,'bootstrap')
            source='''local lighting=game:GetService('Lighting')
for index,row in ROWS do
    local seconds=row[1]
    lighting.TimeOfDay=string.format('%02d:%02d:%02d',math.floor(seconds/3600),math.floor(seconds/60)%60,seconds%60)
    lighting.GeographicLatitude=row[2]
    local sun,moon=lighting:GetSunDirection(),lighting:GetMoonDirection()
    for i,value in {sun.X,sun.Y,sun.Z,moon.X,moon.Y,moon.Z} do
        assert(math.abs(value-row[3][i])<3e-6,'Sky mismatch '..index..' component '..i..': '..value..' ~= '..row[3][i])
    end
end
return true
'''.replace('ROWS',lua_literal(rows))
            assert execute_source(runtime,ROOT,source,work,'sky-comparison')==[True]
    finally:runtime.close()
    assert not runtime.owned and not runtime.backing_errors
    print('ORIGINAL SUN / MOON DIRECTION CHECKS PASSED',len(rows))


if __name__=='__main__':main()
