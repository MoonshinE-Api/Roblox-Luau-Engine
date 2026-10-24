"""Recover enum names/values from local constructors and verify literal call arguments."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from capstone import Cs,CS_ARCH_X86,CS_MODE_64,CS_OP_IMM,CS_OP_REG,CS_OP_MEM
from capstone.x86 import X86_REG_RIP
from macho import MachO


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--dump',type=Path,required=True)
    p.add_argument('--binary',type=Path,required=True)
    p.add_argument('--out',type=Path,default=Path(__file__).parent/'data/enum_catalog.json')
    args=p.parse_args()
    records=[]
    header=re.compile(r'^// Address: (0x[0-9a-fA-F]+) \| Name: (.+)$',re.M)
    literal=r'"((?:[^"\\]|\\.)*)"'
    for path in sorted((args.dump/'reflection').glob('EnumDesc.part*.c')):
        source=path.read_text(encoding='utf-8')
        matches=list(header.finditer(source))
        for i,match in enumerate(matches):
            block=source[match.end():matches[i+1].start() if i+1<len(matches) else len(source)]
            enum=re.search(r'EnumDescriptor::EnumDescriptor\([^;]*?a2:\s*'+literal,block,re.S)
            if not enum:continue
            items=[]
            for call in re.finditer(r'EnumDescriptor::Item::Item\((.*?)\);',block,re.S):
                name=re.search(r'\ba2:\s*'+literal,call[1])
                value=re.search(r'\ba5:\s*(-?(?:0x[0-9a-fA-F]+|\d+))(?:u|LL|uLL)?\s*,',call[1])
                if name and value:
                    n=int(value[1],0)
                    if n>=0x80000000:n-=0x100000000
                    items.append((json.loads('"'+name[1]+'"'),n))
            if items:records.append({'name':enum[1],'address':int(match[1],16),'symbol':match[2],
                'source':str(path.relative_to(args.dump)).replace('\\','/'),'line':source.count('\n',0,match.start())+1,'items':items})
    cs=Cs(CS_ARCH_X86,CS_MODE_64);cs.detail=True
    enums={};verification=[]
    with MachO(args.binary) as binary:
        item_functions=set();symbols={}
        required={r['address'] for r in records}
        for name,address,kind,section in binary.symbols():
            if b'EnumDescriptor4ItemC' in name:item_functions.add(address)
            if address in required:symbols.setdefault(address,set()).add(name.decode())
        def reg(instruction,register):
            name=instruction.reg_name(register)
            if name.startswith('e') and len(name)==3:return 'r'+name[1:]
            if name.startswith('r') and name.endswith('d'):return name[:-1]
            return name
        for record in records:
            assert record['symbol'] in symbols[record['address']]
            values={};calls=[]
            code=binary.function_bytes(record['address'])
            for ins in cs.disasm(code,record['address']):
                op=ins.operands
                if ins.mnemonic=='lea' and op[0].type==CS_OP_REG and op[1].type==CS_OP_MEM and op[1].mem.base==X86_REG_RIP:
                    values[reg(ins,op[0].reg)]=ins.address+ins.size+op[1].mem.disp
                elif ins.mnemonic in {'mov','movabs'} and op[0].type==CS_OP_REG:
                    key=reg(ins,op[0].reg)
                    if op[1].type==CS_OP_IMM:values[key]=op[1].imm
                    elif op[1].type==CS_OP_REG and reg(ins,op[1].reg) in values:values[key]=values[reg(ins,op[1].reg)]
                    else:values.pop(key,None)
                elif ins.mnemonic=='xor' and op[0].type==CS_OP_REG and op[1].type==CS_OP_REG and op[0].reg==op[1].reg:
                    values[reg(ins,op[0].reg)]=0
                elif ins.mnemonic=='call':
                    if op[0].type==CS_OP_IMM and op[0].imm in item_functions:
                        if 'rsi' in values and 'r8' in values:
                            name=binary.string(values['rsi'])
                            value=values['r8'] & 0xffffffff
                            if value>=0x80000000:value-=0x100000000
                            calls.append((name,value))
                    for key in ['rax','rdi','rsi','rdx','rcx','r8','r9','r10','r11']:values.pop(key,None)
            known=set(calls)
            verified=[item for item in record['items'] if item in known]
            # Expose only values confirmed in both the dump and original instructions.
            if verified:
                enums.setdefault(record['name'],{})
                enums[record['name']].update(verified)
            verification.append({'name':record['name'],'address':hex(record['address']),'source':record['source'],
                'line':record['line'],'sha256':hashlib.sha256(code).hexdigest(),'source_items':len(record['items']),
                'verified_items':len(verified),'unresolved_items':[item for item in record['items'] if item not in known]})
    result={'version':'0.735.19.7351131','enums':enums,'constructors':verification,
        'verified_enum_count':len(enums),'verified_item_count':sum(map(len,enums.values())),
        'limits':['Literal registration arguments only','Conditional feature-flag availability and aliases are not reconstructed']}
    args.out.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in {'enums','constructors'}},indent=2))


if __name__=='__main__':main()
