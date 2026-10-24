"""Compare reconstructed Random against unchanged original Mach-O functions.

Requires Capstone only with --extract; ordinary validation uses saved metadata.
"""
import argparse
import ctypes as C
import hashlib
import json
from pathlib import Path
import random
import math
import struct
from macho import MachO
from original import Original

def extract(binary,root):
    from capstone import Cs,CS_ARCH_X86,CS_MODE_64,CS_OP_IMM,CS_OP_MEM,CS_GRP_JUMP
    from capstone.x86 import X86_REG_RIP
    cs=Cs(CS_ARCH_X86,CS_MODE_64);cs.detail=True
    functions={};external={};imports=binary.import_stubs()
    for name,address in Original.ENGINE_RANDOM.items():
        code=binary.function_bytes(address);refs=set();listing=[]
        for ins in cs.disasm(code,address):
            listing.append(f'{ins.address:#x}: {ins.mnemonic} {ins.op_str}')
            if (ins.mnemonic=='call' or ins.group(CS_GRP_JUMP)) and ins.operands[0].type==CS_OP_IMM:
                target=ins.operands[0].imm
                if not address<=target<address+len(code) and target not in Original.ENGINE_RANDOM.values():
                    assert imports.get(target)=='_ldexp',f'Unreviewed dependency {target:#x}'
                    external[hex(target)]={'import':imports[target]}
            for op in ins.operands:
                if op.type==CS_OP_MEM and op.mem.base==X86_REG_RIP:refs.add(ins.address+ins.size+op.mem.disp)
        functions[name]={'address':hex(address),'size':len(code),'sha256':hashlib.sha256(code).hexdigest(),
                         'data_references':[hex(a) for a in sorted(refs)],'instructions':listing}
    report={'functions':functions,'external_calls':external,'source':'v8datamodel/Random.c; script/RandomBridge.c'}
    (root/'data/random_recovery.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report

def main():
    p=argparse.ArgumentParser();p.add_argument('--binary',type=Path,required=True);p.add_argument('--extract',action='store_true')
    args=p.parse_args();root=Path(__file__).parent
    dll=C.CDLL(str((root/'vm0735.dll').resolve()));U=C.c_size_t
    dll.host_import_address.argtypes,dll.host_import_address.restype=[C.c_char_p,U],U
    dll.original_call_f64.argtypes,dll.original_call_f64.restype=[U,U],C.c_double
    dll.original_call_f64_range.argtypes,dll.original_call_f64_range.restype=[U,U,C.c_double,C.c_double],C.c_double
    dll.recovered_random_seed.argtypes=[U,C.c_uint64]
    dll.recovered_random_number.argtypes,dll.recovered_random_number.restype=[U],C.c_double
    dll.recovered_random_range.argtypes,dll.recovered_random_range.restype=[U,C.c_double,C.c_double],C.c_double
    dll.recovered_random_integer.argtypes,dll.recovered_random_integer.restype=[U,C.c_int64,C.c_int64],C.c_int64
    counts={'seed':0,'number':0,'range':0,'integer':0};vectors=[]
    rng=random.Random(7351131)
    with MachO(args.binary) as binary:
        report=extract(binary,root) if args.extract else json.loads((root/'data/random_recovery.json').read_text())
        hooks={int(a,16):dll.host_import_address(b'_ldexp',6) for a in report['external_calls']}
        with Original(binary,report,dll,hooks=hooks,enabled=report['functions']) as original:
            def address(name):return original.functions[name]+original.slide
            first,second=C.c_uint64(),C.c_uint64();pa,pb=C.addressof(first),C.addressof(second)
            for seed in [0,1,42,12345,2**32+7,2**53-1,2**64-1]+[rng.getrandbits(64) for _ in range(193)]:
                original.call_u('random_seed',pa,seed);dll.recovered_random_seed(pb,seed)
                assert first.value==second.value;counts['seed']+=1
                row=[]
                for i in range(50):
                    a=dll.original_call_f64(address('random_number'),pa);b=dll.recovered_random_number(pb)
                    assert struct.pack('<d',a)==struct.pack('<d',b),(seed,i,a,b)
                    assert first.value==second.value;counts['number']+=1
                    if seed in (0,1,42) and i<5:row.append(a)
                if row:vectors.append({'seed':seed,'numbers':row})
            edges=[0.0,-0.0,1.0,-1.0,float('inf'),-float('inf'),float('nan'),1e308,-1e308,5e-324]
            bounds=[(a,b) for a in edges for b in edges]
            bounds +=[tuple(rng.uniform(-1e12,1e12) for _ in range(2)) for _ in range(3000)]
            for a,b in bounds:
                first.value=second.value=rng.getrandbits(64)
                x=dll.original_call_f64_range(address('random_range'),pa,a,b);y=dll.recovered_random_range(pb,a,b)
                assert (math.isnan(x) and math.isnan(y)) or struct.pack('<d',x)==struct.pack('<d',y),(a,b,x,y)
                assert first.value==second.value;counts['range']+=1
            pairs=[(0,0),(1,6),(-10,10),(10,-10),(0,4294967293),(0,4294967294),(-2**63,2**63-1),(-2**53,2**53)]
            pairs +=[(rng.randint(-2**63,2**63-1),rng.randint(-2**63,2**63-1)) for _ in range(3000)]
            for a,b in pairs:
                first.value=second.value=rng.getrandbits(64)
                x=C.c_int64(original.call3('random_integer',pa,a & (2**64-1),b & (2**64-1))).value
                y=dll.recovered_random_integer(pb,a,b)
                assert x==y,(a,b,x,y)
                assert first.value==second.value;counts['integer']+=1
    result={'counts':counts,'number_vectors':vectors,'status':'PASS',
            'comparison':'Original function bytes unchanged; only ldexp import adapted to Windows UCRT.',
            'limits':'Seedless entropy and unit-vector trigonometry are not compared; NaN payloads are not compared.'}
    (root/'data/random_comparison.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))
if __name__=='__main__':main()
