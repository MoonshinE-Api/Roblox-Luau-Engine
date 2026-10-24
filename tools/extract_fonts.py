"""Recover Enum.Font mapping from native initialization stores and local resources."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argparse,hashlib,json,re,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64,CS_OP_MEM,CS_OP_IMM,CS_OP_REG
from capstone.x86 import X86_REG_RIP
from macho import MachO

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--binary',type=Path,default=Path('D:/Release-RobloxStudioApp/RobloxStudio.app/Contents/MacOS/RobloxStudio'))
    p.add_argument('--dump',type=Path,default=Path('D:/0.735-full'))
    args=p.parse_args();root=Path(__file__).resolve().parents[1]
    relative='_free/_free_g.part001.c';text=(args.dump/relative).read_text(encoding='utf-8')
    text=text[text.index('// Address: 0x100398556'):];text=text[:text.index('// Address: 0x10039a0b0')]
    rows=[]
    for match in re.finditer(r'RBX::Text::createUrl\(this: \(RBX::Text \*\)&unk_([0-9A-F]+), a2: "([^"]+)"\); /\*(0x[0-9a-f]+)\*/',text):
        rows.append({'destination':int(match[1],16),'family_name':match[2],'call_site':int(match[3],16)})
    assert len(rows)==52,len(rows)
    cs=Cs(CS_ARCH_X86,CS_MODE_64);cs.detail=True
    with MachO(args.binary) as binary:
        code=binary.function_bytes(0x100398556);regs={};vectors={};calls={};stores={}
        def register(ins,value):
            name=ins.reg_name(value)
            return 'r'+name[1:] if name.startswith('e') and len(name)==3 else name
        for ins in cs.disasm(code,0x100398556):
            ops=ins.operands
            if ins.mnemonic=='lea' and ops[0].type==CS_OP_REG and ops[1].type==CS_OP_MEM and ops[1].mem.base==X86_REG_RIP:
                regs[register(ins,ops[0].reg)]=ins.address+ins.size+ops[1].mem.disp
            elif ins.mnemonic in ('movaps','movups','movdqa') and ops[0].type==CS_OP_REG and ops[1].type==CS_OP_MEM and ops[1].mem.base==X86_REG_RIP:
                vectors[ins.reg_name(ops[0].reg)]=binary.read(ins.address+ins.size+ops[1].mem.disp,16)
            elif ins.mnemonic in ('movaps','movups','movdqu','movdqa') and ops[0].type==CS_OP_MEM and ops[0].mem.base==X86_REG_RIP and ops[1].type==CS_OP_REG:
                stores[ins.address+ins.size+ops[0].mem.disp]=vectors.get(ins.reg_name(ops[1].reg))
            elif ins.mnemonic in ('mov','movabs'):
                if ops[0].type==CS_OP_REG:
                    target=register(ins,ops[0].reg)
                    if ops[1].type==CS_OP_IMM:regs[target]=ops[1].imm
                    elif ops[1].type==CS_OP_REG and register(ins,ops[1].reg) in regs:regs[target]=regs[register(ins,ops[1].reg)]
                    else:regs.pop(target,None)
                elif ops[0].type==CS_OP_MEM and ops[0].mem.base==X86_REG_RIP:
                    value=ops[1].imm if ops[1].type==CS_OP_IMM else regs.get(register(ins,ops[1].reg)) if ops[1].type==CS_OP_REG else None
                    if value is not None:stores[ins.address+ins.size+ops[0].mem.disp]=int(value).to_bytes(ops[0].size,'little',signed=value<0)
            elif ins.mnemonic=='call':
                calls[ins.address]=(dict(regs),ops[0].imm if ops[0].type==CS_OP_IMM else None)
                regs={};vectors={}
        enums=json.loads((root/'data/enum_catalog.json').read_text(encoding='utf-8'))['enums']['Font']
        by_number={value:name for name,value in enums.items()};result={};resources={}
        first=rows[0]['destination'];target=None
        for index,row in enumerate(rows):
            assert row['destination']==first+48*index
            arguments,called=calls[row['call_site']]
            assert arguments['rdi']==row['destination']
            name=row['family_name'].encode();assert binary.read(arguments['rsi'],len(name)+1)==name+b'\0'
            if target is None:target=called
            assert called==target
            raw=stores.get(row['destination']+32)
            assert raw and len(raw)>=8,row
            weight,style=struct.unpack('<ii',raw[:8])
            assert weight in range(100,1000,100) and style in (0,1)
            family='rbxasset://fonts/families/'+row['family_name']+'.json'
            path=args.binary.parent.parent/'Resources/content/fonts/families'/(row['family_name']+'.json')
            if path.is_file():
                data=path.read_bytes();resources[path.name]={'sha256':hashlib.sha256(data).hexdigest(),'faces':len(json.loads(data)['faces'])}
            result[by_number[index]]={'enum_value':index,'family':family,'weight':weight,'style':style}
        bridge=binary.function_bytes(0x104657bce)
        instructions=[f'{i.address:#x}: {i.mnemonic} {i.op_str}' for i in cs.disasm(bridge,0x104657bce) if i.mnemonic in ('cvttsd2si','mov') and 'r14' in i.op_str]
    report={'version':'0.735.19.7351131','enum_fonts':result,'native_rows_verified':len(rows),
        'initializer_sha256':hashlib.sha256(code).hexdigest(),'resource_files':resources,
        'from_id_bridge_sha256':hashlib.sha256(bridge).hexdigest(),'from_id_review':instructions,
        'source_sha256':{name:hashlib.sha256((args.dump/name).read_bytes()).hexdigest() for name in (relative,'rbx/FontInfo.c','script/FontBridge.c')},
        'limits':['Family/weight/style only; no renderer/font asset loading.','Native 0.735 fromId converts via signed int32 then unsigned int32.','Mutable value copying is implemented semantically.']}
    (root/'data/font_recovery.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'native_enum_fonts':len(result),'resources':len(resources)}))

if __name__=='__main__':main()
