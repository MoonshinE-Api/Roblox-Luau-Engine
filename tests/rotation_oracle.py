"""Compare Euler decomposition and lookAlong against original build 735 functions.

Only asinf/atan2f imports are adapted to the host float math library. Results
are compared within 3e-6, including the original gimbal-lock and parallel-up thresholds.
"""
import argparse
import ctypes as C
import hashlib
import json
import math
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

FIXTURE=ROOT/'tests/fixtures/rotation_functions.json'


def extract(binary):
    from capstone import Cs,CS_ARCH_X86,CS_MODE_64,CS_OP_IMM,CS_OP_MEM,CS_GRP_JUMP
    from capstone.x86 import X86_REG_RIP
    cs=Cs(CS_ARCH_X86,CS_MODE_64);cs.detail=True
    functions={};external={};imports=binary.import_stubs()
    for name,address in Original.ENGINE_ROTATION.items():
        code=binary.function_bytes(address);references=set()
        for ins in cs.disasm(code,address):
            if (ins.mnemonic=='call' or ins.group(CS_GRP_JUMP)) and ins.operands[0].type==CS_OP_IMM:
                target=ins.operands[0].imm
                if not address<=target<address+len(code):
                    assert imports.get(target) in {'_asinf','_atan2f'},hex(target)
                    external[hex(target)]={'import':imports[target]}
            for op in ins.operands:
                if op.type==CS_OP_MEM and op.mem.base==X86_REG_RIP:references.add(ins.address+ins.size+op.mem.disp)
        functions[name]={'address':hex(address),'size':len(code),'sha256':hashlib.sha256(code).hexdigest(),
                         'data_references':[hex(a) for a in sorted(references)]}
    report={'functions':functions,'external_calls':external,'source':'rbx/Matrix3.c; script/CoordinateFrameBridge.c',
            'comparison':'Unchanged Euler decomposition and lookAlong bytes; asinf/atan2f imports use host float math; tolerance 3e-6.'}
    FIXTURE.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


def matrix(angles,order):
    result=[[1,0,0],[0,1,0],[0,0,1]]
    for axis in order:
        sine,cosine=math.sin(angles[axis]),math.cos(angles[axis])
        r=([[1,0,0],[0,cosine,-sine],[0,sine,cosine]] if axis=='X' else
           [[cosine,0,sine],[0,1,0],[-sine,0,cosine]] if axis=='Y' else
           [[cosine,-sine,0],[sine,cosine,0],[0,0,1]])
        result=[[sum(result[i][k]*r[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    return [struct.unpack('<f',struct.pack('<f',v))[0] for row in result for v in row]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--binary',type=Path,default=Path('D:/Release-RobloxStudioApp/RobloxStudio.app/Contents/MacOS/RobloxStudio'))
    parser.add_argument('--extract',action='store_true')
    args=parser.parse_args()
    dll=C.CDLL(str(ROOT/'vm0735.dll'));U=C.c_size_t
    dll.host_import_address.argtypes,dll.host_import_address.restype=[C.c_char_p,U],U
    dll.original_call4.argtypes,dll.original_call4.restype=[U]*5,U
    rows=[];look_rows=[];rng=random.Random(735741)
    with MachO(args.binary) as binary:
        report=extract(binary) if args.extract else json.loads(FIXTURE.read_text())
        hooks={int(address,16):dll.host_import_address(item['import'].encode(),len(item['import'])) for address,item in report['external_calls'].items()}
        with Original(binary,report,dll,hooks=hooks,enabled=report['functions']) as original:
            for name in report['functions']:
                if name=='rotation_look_along':continue
                order=name.rsplit('_',1)[-1].upper()
                angles=[{axis:rng.uniform(-math.pi,math.pi) for axis in 'XYZ'} for _ in range(500)]
                for sign in [-1,1]:
                    for offset in [0,-1e-5,1e-5,-0.0005,0.0005,-0.001,0.001,-0.01,0.01]:
                        item={'X':0.7,'Y':-0.3,'Z':1.1};item[order[1]]=sign*math.pi/2+offset;angles.append(item)
                for item in angles:
                    components=matrix(item,order);m=(C.c_float*9)(*components)
                    a,b,c=C.c_float(),C.c_float(),C.c_float()
                    dll.original_call4(original.functions[name]+original.slide,C.addressof(m),C.addressof(a),C.addressof(b),C.addressof(c))
                    by_axis=dict(zip(order,[a.value,b.value,c.value]))
                    rows.append([order,components,[by_axis[axis] for axis in 'XYZ']])
            look_cases=[([0,1,0],[0,1,0]),([1,0,0],[1,0,0]),([0,0,-1],[0,0,2]),
                        ([1e-8,1,0],[0,2,0]),([0,0,0],[0,1,0]),([1,2,3],[0,0,0])]
            look_cases.extend(([rng.uniform(-2,2) for _ in range(3)],[rng.uniform(-2,2) for _ in range(3)]) for _ in range(200))
            for direction,up in look_cases:
                d=(C.c_float*3)(*direction);u=(C.c_float*3)(*up);out=(C.c_float*12)()
                original.call3('rotation_look_along',C.addressof(out),C.addressof(d),C.addressof(u))
                look_rows.append([direction,up,list(out)[:9]])
    runtime=Runtime(args.binary)
    try:
        runtime.open_libraries()
        with tempfile.TemporaryDirectory(prefix='rotation-comparison-') as folder:
            work=Path(folder)
            execute_source(runtime,ROOT,bootstrap(ROOT,{'side':'server','duration':0}),work,'bootstrap')
            source='''local rows=ROWS
for index,row in rows do
    local cf=CFrame.new(0,0,0,table.unpack(row[2]))
    local angles={cf:ToEulerAngles(Enum.RotationOrder[row[1]])}
    for component,value in angles do
        local difference=value-row[3][component]
        local delta=math.abs(math.atan2(math.sin(difference),math.cos(difference)))
        assert(delta<3e-6,'Euler mismatch '..row[1]..' row '..index..' component '..component..': '..value..' ~= '..row[3][component])
    end
end
return #rows
'''.replace('ROWS',lua_literal(rows))
            assert execute_source(runtime,ROOT,source,work,'rotations')==[len(rows)]
            source='''local rows=ROWS
for index,row in rows do
    local cf=CFrame.lookAlong(Vector3.zero,Vector3.new(table.unpack(row[1])),Vector3.new(table.unpack(row[2])))
    local components={cf:GetComponents()}
    for i,expected in row[3] do
        local value=components[i+3]
        assert((value~=value and expected~=expected) or math.abs(value-expected)<3e-6,'lookAlong mismatch '..index..' component '..i)
    end
end
return #rows
'''.replace('ROWS',lua_literal(look_rows))
            assert execute_source(runtime,ROOT,source,work,'look-along')==[len(look_rows)]
    finally:runtime.close()
    assert not runtime.owned and not runtime.backing_errors
    print('ORIGINAL SIX-ORDER EULER AND LOOK-ALONG CHECKS PASSED',len(rows),len(look_rows))


if __name__=='__main__':main()
