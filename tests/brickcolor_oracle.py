"""Compare runtime BrickColor lookup against original code with a recovered catalog.

The global ColorInfo vector is reconstructed from verified registration literals.
Only the singleton initializer is replaced; tested function instructions are intact.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argparse,ctypes as C,hashlib,json,random,struct,tempfile
from pathlib import Path
from macho import MachO
from original import Original
from run import bootstrap,execute_source,lua_literal
from vm_runtime import Runtime

def extract(binary,root):
    from capstone import Cs,CS_ARCH_X86,CS_MODE_64,CS_OP_MEM,CS_OP_IMM,CS_GRP_JUMP
    from capstone.x86 import X86_REG_RIP
    cs=Cs(CS_ARCH_X86,CS_MODE_64);cs.detail=True
    functions={}
    for name,address in Original.ENGINE_BRICK.items():
        code=binary.function_bytes(address);refs=set();listing=[]
        for ins in cs.disasm(code,address):
            listing.append(f'{ins.address:#x}: {ins.mnemonic} {ins.op_str}')
            if (ins.mnemonic=='call' or ins.group(CS_GRP_JUMP)) and ins.operands[0].type==CS_OP_IMM:
                target=ins.operands[0].imm
                assert address<=target<address+len(code) or target==0x102a44546,hex(target)
            for op in ins.operands:
                if op.type==CS_OP_MEM and op.mem.base==X86_REG_RIP:refs.add(ins.address+ins.size+op.mem.disp)
        functions[name]={'address':hex(address),'size':len(code),'sha256':hashlib.sha256(code).hexdigest(),
                         'data_references':[hex(a) for a in sorted(refs)],'instructions':listing}
    result={'functions':functions,'source':'util/BrickColor.c; rbx/BrickMap.c',
            'singleton_hook':'0x102a44546','colorinfo_begin':'0x10cfbc510','colorinfo_end':'0x10cfbc518'}
    (root/'data/brickcolor_recovery.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

def f32(value):return struct.unpack('<f',struct.pack('<f',value))[0]
def pair(a,b):return struct.unpack('<d',struct.pack('<ff',a,b))[0]
def main():
    p=argparse.ArgumentParser();p.add_argument('--binary',type=Path,required=True);p.add_argument('--extract',action='store_true')
    args=p.parse_args();root=Path(__file__).resolve().parents[1]
    catalog=json.loads((root/'data/brickcolor_catalog.json').read_text())
    info=C.create_string_buffer(1033*48);base=C.addressof(info)
    for row in catalog['colors']:
        address=base+48*row['number'];C.c_ubyte.from_address(address).value=1
        rgb=row['rgb'];C.memmove(address+2,bytes(rgb)+b'\xff',4)
        floats=struct.pack('<4f',*(f32(n*0.003921568859368563) for n in rgb),1.0)
        C.memmove(address+8,floats,16)
    dll=C.CDLL(str((root/'vm0735.dll').resolve()));U=C.c_size_t
    dll.host_import_address.argtypes,dll.host_import_address.restype=[C.c_char_p,U],U
    dll.original_call_colors.argtypes,dll.original_call_colors.restype=[U,C.c_double,C.c_double],U
    rng=random.Random(7351131)
    inputs=[[f32(n*0.003921568859368563) for n in row['rgb']] for row in catalog['colors']]
    inputs += [[0.,0.,0.],[1.,1.,1.],[1.,0.,0.],[0.5,0.5,0.5]]
    inputs +=[[f32(rng.uniform(-1,2)) for _ in range(3)] for _ in range(2000)]
    ids=list(range(-2,1040))+[2147483647,-2147483648]
    nearest=[];constructed=[]
    with MachO(args.binary) as binary:
        report=extract(binary,root) if args.extract else json.loads((root/'data/brickcolor_recovery.json').read_text())
        overrides={0x10cfbc510:struct.pack('<Q',base),0x10cfbc518:struct.pack('<Q',base+len(info))}
        hooks={0x102a44546:dll.host_import_address(b'oracle_noop',11)}
        with Original(binary,report,dll,hooks=hooks,enabled=report['functions'],data_overrides=overrides) as image:
            for name,row in report['functions'].items():
                code=C.string_at(image.functions[name]+image.slide,row['size'])
                assert hashlib.sha256(code).hexdigest()==row['sha256']
            fn=image.functions['brick_closest']+image.slide
            for r,g,b in inputs:nearest.append(dll.original_call_colors(fn,pair(r,g),pair(b,1.0)))
            value=C.c_uint32()
            for n in ids:
                image.call_u('brick_constructor',C.addressof(value),n & 0xffffffff)
                constructed.append(value.value)
    # Independent VM process state: compare all overloads with the native answers.
    runtime=Runtime(args.binary)
    try:
        runtime.open_libraries()
        extended=[4294967317,-4294967275,2147483669,1e20,-1e20,21.99,-2147483648.8,2147483647.8]
        valid_ids={row['number'] for row in catalog['colors']}
        # Compare overflow/fractional conversion using the actual VM API too.
        for n in extended:
            runtime.image.call('__Z14lua_pushnumberP9lua_Stated',runtime.state,number=n)
            converted=C.c_int32(runtime.image.call3('__Z14lua_tointegerxP9lua_StateiPi',runtime.state,1,0)).value
            runtime.image.call('__Z10lua_settopP9lua_Statei',runtime.state,argument=0)
            constructed.append(converted if converted in valid_ids else 194)
        ids+=extended
        with tempfile.TemporaryDirectory(prefix='brickcolor-oracle-') as folder:
            working=Path(folder);execute_source(runtime,root,bootstrap(root,{'side':'server','duration':0}),working,'engine-bootstrap')
            probe='local inputs='+lua_literal(inputs)+'\nlocal ids='+lua_literal(ids)+'''\nlocal out={}
for _,rgb in inputs do
 local a=BrickColor.new(rgb[1],rgb[2],rgb[3]).Number
 local b=BrickColor.new(Color3.new(rgb[1],rgb[2],rgb[3])).Number
 assert(a==b,"BrickColor overload mismatch")
 table.insert(out,tostring(a))
end
for _,id in ids do table.insert(out,tostring(BrickColor.new(id).Number)) end
return table.concat(out,",")
'''
            result=execute_source(runtime,root,probe,working,'brickcolor-differential')[0]
            actual=[int(n) for n in result.split(',')]
            assert actual==nearest+constructed,next((i,x,y) for i,(x,y) in enumerate(zip(actual,nearest+constructed)) if x!=y)
    finally:runtime.close()
    assert not runtime.owned and not runtime.backing_errors
    result={'status':'PASS','rgb_cases':len(inputs),'rgb_overloads_compared':2,'numeric_cases':len(ids),
            'limits':'Recovered catalog substituted for singleton initialization; alias lookup, events and defaults are separate checks.'}
    (root/'data/brickcolor_comparison.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
if __name__=='__main__':main()
