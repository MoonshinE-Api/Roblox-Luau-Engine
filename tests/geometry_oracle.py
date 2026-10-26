"""Native build 735 primitive radii and scaled convex vertices, not cast solver parity."""
import argparse
import ctypes as C
import hashlib
import json
from pathlib import Path
import random
import struct
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from macho import MachO
from original import Original

FIXTURE=ROOT/'tests/fixtures/geometry_functions.json'


def extract(binary):
    from capstone import Cs,CS_ARCH_X86,CS_MODE_64,CS_OP_IMM,CS_OP_MEM,CS_GRP_JUMP
    from capstone.x86 import X86_REG_RIP
    cs=Cs(CS_ARCH_X86,CS_MODE_64);cs.detail=True;functions={}
    for name,address in Original.ENGINE_GEOMETRY.items():
        code=binary.function_bytes(address);references=set()
        for ins in cs.disasm(code,address):
            if (ins.mnemonic=='call' or ins.group(CS_GRP_JUMP)) and ins.operands[0].type==CS_OP_IMM:
                target=ins.operands[0].imm;assert address<=target<address+len(code),(name,hex(target))
            for op in ins.operands:
                if op.type==CS_OP_MEM and op.mem.base==X86_REG_RIP:references.add(ins.address+ins.size+op.mem.disp)
        functions[name]={'address':hex(address),'size':len(code),'sha256':hashlib.sha256(code).hexdigest(),
                         'data_references':[hex(a) for a in sorted(references)]}
    report={'functions':functions,'source':'v8world/Ball.c; v8world/Cylinder.c; v8world/Mesh.c',
        'comparison':'Four unchanged native functions. Borrowed dimensions and fixed-size mesh records; no dependency bridges.',
        'limits':'Compares primitive radii, vertex counts and hull vertices only. Parry replaces the collision kernel; Roblox cast, broadphase, margins and physics assembly algorithms are not executed.'}
    FIXTURE.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');return report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--binary',type=Path,default=Path('D:/Release-RobloxStudioApp/RobloxStudio.app/Contents/MacOS/RobloxStudio'))
    parser.add_argument('--extract',action='store_true');args=parser.parse_args()
    dll=C.CDLL(str(ROOT/'vm0735.dll'));U=C.c_size_t;F=C.POINTER(C.c_float)
    dll.original_call_vector_f32.argtypes=[U,U,F];dll.original_call_vector_f32.restype=C.c_float
    dll.original_call_vertex.argtypes=[U,U,C.c_uint32,F]
    dll.geometry_vertex.argtypes=[C.c_uint32,F,U,F];dll.geometry_vertex.restype=C.c_int
    dll.geometry_radii.argtypes=[C.c_uint32,F,F];dll.geometry_radii.restype=C.c_int
    randomizer=random.Random(735314)
    vectors=[(.05,.05,.05),(4,1.2,2),(10,4,6),(512,512,512)]
    vectors.extend(tuple(2**randomizer.uniform(-4,9) for _ in range(3)) for _ in range(1200))
    vertices=0;radii=0
    with MachO(args.binary) as binary:
        report=extract(binary) if args.extract else json.loads(FIXTURE.read_text())
        with Original(binary,report,dll,enabled=report['functions']) as native:
            for row in vectors:
                sizes=(C.c_float*3)(*row);out=(C.c_float*3)();expected=(C.c_float*3)()
                for kind,name in ((2,'ball_radius'),(3,'cylinder_bound')):
                    value=dll.original_call_vector_f32(native.functions[name]+native.slide,0,sizes)
                    assert dll.geometry_radii(kind,sizes,out)==0
                    assert out[0 if kind==2 else 1]==value,(row,kind,list(out),value)
                    radii+=1
                for kind,mesh_kind,count in ((1,0,8),(4,1,6),(5,2,5)):
                    mesh=C.create_string_buffer(16)
                    struct.pack_into('<fffB',mesh,0,*sizes,mesh_kind)
                    assert native.call('poly_vertex_count',C.addressof(mesh))==count
                    for index in range(count):
                        dll.original_call_vertex(native.functions['poly_vertex']+native.slide,C.addressof(mesh),index,expected)
                        assert dll.geometry_vertex(kind,sizes,index,out)==0
                        assert bytes(out)==bytes(expected),(row,kind,index,list(out),list(expected))
                        vertices+=1
    print('ORIGINAL PRIMITIVE RADII, COUNTS AND SCALED CONVEX VERTICES PASSED',radii,vertices)


if __name__=='__main__':main()
