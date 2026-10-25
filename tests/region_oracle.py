"""Compare region construction and grid expansion with unchanged build 735 code.

The original C++ exception path is never executed; invalid resolutions are tested
through the Luau API instead. Capstone is needed only to regenerate the fixture.
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

FIXTURE=ROOT/'tests/fixtures/region_functions.json'


def extract(binary):
    from capstone import Cs,CS_ARCH_X86,CS_MODE_64,CS_OP_IMM,CS_OP_MEM,CS_GRP_JUMP
    from capstone.x86 import X86_REG_RIP
    cs=Cs(CS_ARCH_X86,CS_MODE_64);cs.detail=True
    functions={};unexecuted=[]
    for name,address in Original.ENGINE_REGION.items():
        code=binary.function_bytes(address);references=set()
        for ins in cs.disasm(code,address):
            if (ins.mnemonic=='call' or ins.group(CS_GRP_JUMP)) and ins.operands[0].type==CS_OP_IMM:
                target=ins.operands[0].imm
                if not address<=target<address+len(code) and target not in Original.ENGINE_REGION.values():
                    assert name=='region_expand' and target==0x1041ac28e,hex(target)
                    unexecuted.append(hex(target))
            for op in ins.operands:
                if op.type==CS_OP_MEM and op.mem.base==X86_REG_RIP:references.add(ins.address+ins.size+op.mem.disp)
        functions[name]={'address':hex(address),'size':len(code),'sha256':hashlib.sha256(code).hexdigest(),
                         'data_references':[hex(a) for a in sorted(references)]}
    report={'functions':functions,'unexecuted_exception_targets':unexecuted,
            'source':'util/Region3.c; script/Region3Bridge.c',
            'restriction':'Only positive finite float32 resolutions enter the native expansion function.'}
    FIXTURE.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--binary',type=Path,default=Path('D:/Release-RobloxStudioApp/RobloxStudio.app/Contents/MacOS/RobloxStudio'))
    parser.add_argument('--extract',action='store_true')
    args=parser.parse_args()
    dll=C.CDLL(str(ROOT/'vm0735.dll'))
    dll.original_call_region.argtypes=[C.c_size_t,C.c_void_p,C.c_void_p,C.c_float]
    dll.original_call_region.restype=None
    rng=random.Random(735735)
    cases=[([-5,-1.25,0],[3,4,9],4),([5,4,3],[-5,-4,-3],2),([0,0,0],[0,0,0],1)]
    for i in range(600):
        a=[rng.uniform(-10000,10000) for _ in range(3)]
        b=[a[j]+rng.uniform(-500,500) for j in range(3)]
        cases.append((a,b,rng.choice([0.125,0.5,1,2,3,4,16,0.001,1000])))
    # One representable float on either side of exact grid boundaries.
    for bits in [0x3f7fffff,0x3f800000,0x3f800001,0xbf800001,0xbf800000,0xbf7fffff]:
        x=struct.unpack('<f',struct.pack('<I',bits))[0]
        cases.append(([x,x,x],[x,x,x],1))
    rows=[];guard=b'\xA5'*16
    with MachO(args.binary) as binary:
        report=extract(binary) if args.extract else json.loads(FIXTURE.read_text())
        with Original(binary,report,dll,enabled=report['functions']) as original:
            for minimum,maximum,resolution in cases:
                resolution=C.c_float(resolution).value
                assert 0<resolution<math.inf
                extents=(C.c_float*6)(*minimum,*maximum)
                region=C.create_string_buffer(76);expanded=C.create_string_buffer(76)
                C.memmove(C.addressof(region)+60,guard,16);C.memmove(C.addressof(expanded)+60,guard,16)
                original.call_u('region_init',C.addressof(region),C.addressof(extents))
                dll.original_call_region(original.functions['region_expand']+original.slide,expanded,region,resolution)
                assert region.raw[60:76]==guard and expanded.raw[60:76]==guard
                center_size=list(struct.unpack_from('<6f',region.raw,36))
                expanded_values=list(struct.unpack_from('<6f',expanded.raw,36))
                rows.append([minimum,maximum,resolution,center_size,expanded_values])
    runtime=Runtime(args.binary)
    try:
        runtime.open_libraries()
        with tempfile.TemporaryDirectory(prefix='region-comparison-') as folder:
            work=Path(folder)
            execute_source(runtime,ROOT,bootstrap(ROOT,{'side':'server','duration':0}),work,'bootstrap')
            source='''local rows=ROWS
local function check(region,expected,index)
    local p,s=region.CFrame.Position,region.Size
    for i,value in {p.X,p.Y,p.Z,s.X,s.Y,s.Z} do
        assert(value==expected[i],'Region mismatch '..index..' component '..i..': '..value..' ~= '..expected[i])
    end
    assert(region.CFrame.Rotation==CFrame.identity)
end
for index,row in rows do
    local region=Region3.new(Vector3.new(table.unpack(row[1])),Vector3.new(table.unpack(row[2])))
    check(region,row[4],index)
    check(region:ExpandToGrid(row[3]),row[5],index)
end
return #rows
'''.replace('ROWS',lua_literal(rows))
            assert execute_source(runtime,ROOT,source,work,'regions')==[len(rows)]
    finally:runtime.close()
    assert not runtime.owned and not runtime.backing_errors
    print('ORIGINAL REGION CONSTRUCTION / GRID EXPANSION CHECKS PASSED',len(rows))


if __name__=='__main__':main()
