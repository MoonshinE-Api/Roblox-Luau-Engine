"""Extract BrickColor literals from the supplied dump, verifying x64 arguments."""
import argparse,hashlib,json,re,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64,CS_OP_IMM,CS_OP_REG,CS_OP_MEM
from capstone.x86 import X86_REG_RIP
from macho import MachO

def main():
    p=argparse.ArgumentParser();p.add_argument('--binary',type=Path,required=True);p.add_argument('--dump',type=Path,required=True)
    args=p.parse_args();root=Path(__file__).parent
    source=(args.dump/'rbx/BrickMap.c').read_text(encoding='utf-8')
    records=[]
    pattern=r'basic_string\[abi:ne200100\]<0>\(a1: (\w+), a2: ("[^"\n]*")\); /\*(0x[0-9a-f]+)\*/\s*RBX::BrickColor::BrickMap::insert\(a1: this, a2: (\d+), a3: (\d+), a4: (\d+), a5: (\d+), a6: \1, a7: \w+\); /\*(0x[0-9a-f]+)\*/'
    for m in re.finditer(pattern,source):
        records.append({'name':json.loads(m[2]),'string_site':int(m[3],16),'number':int(m[4]),
                        'rgb':[int(m[i]) for i in (5,6,7)],'insert_site':int(m[8],16)})
    assert len(records)>200
    palette_source=source[source.index('// Address: 0x102a4b312'):]
    palette_matches=list(re.finditer(r'v4\[0\] = (\d+); /\*(0x[0-9a-f]+)\*/',palette_source))
    assert len(palette_matches)==128
    cs=Cs(CS_ARCH_X86,CS_MODE_64);cs.detail=True
    def reg(ins,r):
        n=ins.reg_name(r)
        if n.startswith('e') and len(n)==3:return 'r'+n[1:]
        if n.startswith('r') and n.endswith('d'):return n[:-1]
        return n
    with MachO(args.binary) as binary:
        code=binary.function_bytes(0x102a45cea);values={};calls={}
        for ins in cs.disasm(code,0x102a45cea):
            op=ins.operands
            if ins.mnemonic=='lea' and op[0].type==CS_OP_REG and op[1].type==CS_OP_MEM and op[1].mem.base==X86_REG_RIP:
                values[reg(ins,op[0].reg)]=ins.address+ins.size+op[1].mem.disp
            elif ins.mnemonic in ('mov','movabs') and op[0].type==CS_OP_REG:
                k=reg(ins,op[0].reg)
                if op[1].type==CS_OP_IMM:values[k]=op[1].imm
                elif op[1].type==CS_OP_REG and reg(ins,op[1].reg) in values:values[k]=values[reg(ins,op[1].reg)]
                else:values.pop(k,None)
            elif ins.mnemonic=='xor' and op[0].type==CS_OP_REG and op[1].type==CS_OP_REG and op[0].reg==op[1].reg:values[reg(ins,op[0].reg)]=0
            elif ins.mnemonic=='call':
                calls[ins.address]=(dict(values),op[0].imm if op[0].type==CS_OP_IMM else None)
                for k in ('rax','rdi','rsi','rdx','rcx','r8','r9','r10','r11'):values.pop(k,None)
        for row in records:
            values,target=calls[row['string_site']]
            assert binary.string(values['rsi'])==row['name'],row
            values,target=calls[row['insert_site']]
            assert target==0x102a4b242
            assert [values[k] for k in ('rsi','rdx','rcx','r8')]==[row['number']]+row['rgb'],row
            row['string_site']=hex(row['string_site']);row['insert_site']=hex(row['insert_site'])
        palette_code=binary.function_bytes(0x102a4b312)
        instructions={ins.address:ins for ins in cs.disasm(palette_code,0x102a4b312)}
        for m in palette_matches:
            ins=instructions[int(m[2],16)]
            assert ins.mnemonic=='mov' and ins.operands[0].type==CS_OP_MEM and ins.operands[1].type==CS_OP_IMM
            assert ins.operands[1].imm==int(m[1])
        palette=[int(m[1]) for m in palette_matches]
        assert set(palette)<=set(row['number'] for row in records)
        multiplier=struct.unpack('<4f',binary.read(0x1094d1d20,16))
        assert multiplier==(0.003921568859368563,)*4
        library=next(a for n,a,k,s in binary.symbols() if n==b'__ZN3RBX3Lua16BrickColorBridge12classLibraryE')
        constants={};registration={}
        for i in range(32):
            text,fn=struct.unpack('<QQ',binary.read(library+i*16,16))
            if not text:break
            name=binary.string(text);body=binary.function_bytes(fn)
            registration[name]={'address':hex(fn),'sha256':hashlib.sha256(body).hexdigest()}
            for ins in cs.disasm(body,fn):
                op=ins.operands
                if name in {'White','Gray','DarkGray','Black','Red','Yellow','Green','Blue'} and ins.mnemonic=='mov' and op[0].type==CS_OP_MEM and ins.reg_name(op[0].mem.base)=='rax' and op[1].type==CS_OP_IMM:
                    constants[name]=op[1].imm
        assert constants=={'White':1,'Gray':194,'DarkGray':199,'Black':26,'Red':21,'Yellow':24,'Green':28,'Blue':23}
        new_code=binary.function_bytes(0x104649aa6)
        zero_path=[f'{ins.address:#x}: {ins.mnemonic} {ins.op_str}' for ins in cs.disasm(new_code,0x104649aa6) if ins.address<=0x104649b41]
        result={'version':'0.735.19.7351131','colors':records,'palette':palette,
                'source':'rbx/BrickMap.c','verified_colors':len(records),'verified_palette':len(palette),
                'constructor_sha256':hashlib.sha256(code).hexdigest(),'palette_sha256':hashlib.sha256(palette_code).hexdigest(),
                'color_byte_multiplier':multiplier[0],'constant_constructors':constants,'class_library':registration,
                'new_zero_argument':{'observed_result':1003,'bridge_sha256':hashlib.sha256(new_code).hexdigest(),
                    'instructions':zero_path,'reason':'Initial 194 userdata is followed by closest(0,0,0) and another allocation; one top result is returned.'},
                'limits':['Alias map not reconstructed. Palette preference flags used for duplicate names.']}
    (root/'evidence/brickcolor_catalog.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('version','verified_colors','verified_palette','constructor_sha256','palette_sha256')}))
if __name__=='__main__':main()
