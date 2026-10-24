"""Recover material literals and reviewed constructor functions from build 0.735."""
import argparse
import ctypes as C
import hashlib
import json
from pathlib import Path
import re
import struct
from capstone import Cs,CS_ARCH_X86,CS_MODE_64,CS_OP_MEM,CS_OP_IMM,CS_OP_REG
from capstone.x86 import X86_REG_RIP
from macho import MachO
from original import Original

def f32(value):return struct.unpack('<f',struct.pack('<f',float(value)))[0]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--binary',type=Path,default=Path('D:/Release-RobloxStudioApp/RobloxStudio.app/Contents/MacOS/RobloxStudio'))
    p.add_argument('--dump',type=Path,default=Path('D:/0.735-full'))
    args=p.parse_args();root=Path(__file__).resolve().parent
    relative='v8world/MaterialProperties.c';source=(args.dump/relative).read_text(encoding='utf-8')
    calls=re.findall(r'RBX::PhysicalProperties::PhysicalProperties\(\s*/\*(0x[0-9a-f]+)\*/(.*?)\);',source,re.S)
    rows=[]
    for site,body in calls:
        matches=re.findall(r'a[2-7]: (-?[0-9.]+)',body)
        assert len(matches)==6,(site,matches)
        rows.append({'site':site,'properties':[f32(x) for x in matches]})
    assert len(rows)==46,len(rows)
    cs=Cs(CS_ARCH_X86,CS_MODE_64);cs.detail=True;functions={}
    with MachO(args.binary) as binary:
        for name,address in Original.ENGINE_PHYSICAL.items():
            code=binary.function_bytes(address);refs=set()
            for instruction in cs.disasm(code,address):
                for op in instruction.operands:
                    if op.type==CS_OP_MEM and op.mem.base==X86_REG_RIP:refs.add(instruction.address+instruction.size+op.mem.disp)
            functions[name]={'address':hex(address),'size':len(code),'sha256':hashlib.sha256(code).hexdigest(),
                'data_references':[hex(x) for x in sorted(refs)]}
        # Check each source-derived constructor argument against binary register
        # loads. XMM registers carry the six scalar float arguments in SysV ABI.
        values={};seen={}
        for ins in cs.disasm(binary.function_bytes(0x1002926da),0x1002926da):
            ops=ins.operands
            if ins.mnemonic in ('movss','movaps','movups','movsd','movdqa') and ops[0].type==CS_OP_REG:
                target=ins.reg_name(ops[0].reg)
                if target.startswith('xmm'):
                    if ops[1].type==CS_OP_MEM and ops[1].mem.base==X86_REG_RIP:
                        at=ins.address+ins.size+ops[1].mem.disp;values[target]=struct.unpack('<f',binary.read(at,4))[0]
                    elif ops[1].type==CS_OP_REG and ins.reg_name(ops[1].reg) in values:values[target]=values[ins.reg_name(ops[1].reg)]
                    else:values.pop(target,None)
            elif ins.mnemonic in ('xorps','pxor') and ops[0].type==CS_OP_REG and ops[1].type==CS_OP_REG and ops[0].reg==ops[1].reg:
                values[ins.reg_name(ops[0].reg)]=0.0
            elif ins.mnemonic=='call':
                if ops[0].type==CS_OP_IMM and ops[0].imm==0x104936ea8:
                    seen[hex(ins.address)]=[values.get('xmm'+str(i)) for i in range(6)]
                for i in range(16):values.pop('xmm'+str(i),None)
        for row in rows:assert seen.get(row['site'])==row['properties'],(row,seen.get(row['site']))
        dll=C.CDLL(str(root/'vm0735.dll'))
        with Original(binary,{'functions':functions},dll,enabled=Original.ENGINE_PHYSICAL) as image:
            enums=json.loads((root/'data/enum_catalog.json').read_text(encoding='utf-8'))['enums']['Material']
            materials={}
            for name,value in enums.items():
                index=image.call_u('material_index',value,0)
                assert index==255 or index<len(rows)-1,(name,index)
                materials[name]={'enum_value':value,'native_index':index,
                    'properties':rows[0 if index==255 else index+1]['properties']}
        three_defaults=list(struct.unpack('<2f',binary.read(0x108F2F400,8)))
        assert three_defaults==[1,1]
        minimum_density=struct.unpack('<f',binary.read(0x108f46788,4))[0]
        unit_volume={'Ball':struct.unpack('<f',struct.pack('<I',1057360530))[0],
            'Cylinder':struct.unpack('<f',struct.pack('<I',1061752795))[0],
            'Wedge':struct.unpack('<f',binary.read(0x109060A30,4))[0],
            'CornerWedge':struct.unpack('<f',binary.read(0x109060A64,4))[0]}
        centers={'Wedge':list(struct.unpack('<3f',binary.read(0x109060A34,12))),
                 'CornerWedge':list(struct.unpack('<3f',binary.read(0x109060A68,12)))}
    source_paths=['util/PhysicalProperties.c','script/PhysicalPropertiesBridge.c',relative,'free/_free_g.part001.c',
                  'rbx/Part.c','rbx/MassProperties.c','v8world/Primitive.c']
    report={'version':'0.735.19.7351131','functions':functions,'materials':materials,
        'minimum_density':minimum_density,'unit_volume':unit_volume,'unit_center':centers,
        'table_constructors':rows,'verified_binary_argument_vectors':len(rows),
        'numeric_defaults':{'FrictionWeight':1.0,'ElasticityWeight':three_defaults[0],'AcousticAbsorption':three_defaults[1]},
        'source_sha256':{name:hashlib.sha256((args.dump/name).read_bytes()).hexdigest() for name in source_paths},
        'limits':['World MaterialService/MaterialVariant overrides are a separate subsystem.','Lua bridge coercion and warning frequency not executed natively.']}
    (root/'data/physical_recovery.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'materials':len(materials),'binary_argument_vectors':len(rows)}))

if __name__=='__main__':main()
