"""Bounded disassembly inventory of the supplied Luau VM text interval."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argparse
import hashlib
import json
from pathlib import Path

from capstone import Cs,CS_ARCH_X86,CS_MODE_64,CS_OP_IMM,CS_OP_MEM,CS_GRP_JUMP
from capstone.x86 import X86_REG_RIP
from macho import MachO

START,END=0x1031ce278,0x1031fc453
COLD_START,COLD_END=0x108629482,0x108629af0


def in_vm(address):
    return START<=address<END or COLD_START<=address<COLD_END


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--binary',type=Path,required=True)
    p.add_argument('--out',type=Path,default=Path(__file__).resolve().parents[1]/'data/vm_core.json')
    args=p.parse_args()
    cs=Cs(CS_ARCH_X86,CS_MODE_64);cs.detail=True
    with MachO(args.binary) as binary:
        names={}
        for name,address,kind,section in binary.symbols():
            if in_vm(address) and section==1: names.setdefault(address,[]).append(name.decode())
        functions={}
        required=set()
        imports=binary.import_stubs()
        externals={}
        for address in binary.starts:
            if not in_vm(address): continue
            code=binary.function_bytes(address)
            refs=set();calls=[]
            for instruction in cs.disasm(code,address):
                if (instruction.mnemonic=='call' or instruction.group(CS_GRP_JUMP)) and instruction.operands[0].type==CS_OP_IMM:
                    target=instruction.operands[0].imm
                    calls.append(hex(target));required.add(target)
                    if not in_vm(target): externals[target]=imports.get(target)
                for operand in instruction.operands:
                    if operand.type==CS_OP_MEM and operand.mem.base==X86_REG_RIP:
                        refs.add(instruction.address+instruction.size+operand.mem.disp)
            label=names.get(address,[hex(address)])[0]
            functions[label]={'address':hex(address),'name':label,'size':len(code),'sha256':hashlib.sha256(code).hexdigest(),
                              'data_references':[hex(a) for a in sorted(refs)],'call_targets':calls}
            required.update(refs)
        external_symbols={}
        for name,address,kind,section in binary.symbols():
            if address in required: external_symbols.setdefault(hex(address),[]).append(name.decode())
        report={'range':[hex(START),hex(END)],'cold_range':[hex(COLD_START),hex(COLD_END)],'functions':functions,'external_calls':{
            hex(a):{'import':name,'symbols':external_symbols.get(hex(a),[])} for a,name in sorted(externals.items())},
            'reference_symbols':external_symbols,'imports':{hex(a):n for a,n in imports.items()}}
        args.out.write_text(json.dumps(report,indent=2),encoding='utf-8')
        print(json.dumps({'functions':len(functions),'text_bytes':END-START,'external_calls':report['external_calls']},indent=2))


if __name__=='__main__':main()
