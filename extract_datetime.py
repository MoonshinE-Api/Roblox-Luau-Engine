"""Collect DateTime source evidence and all locale data from the supplied app."""
import argparse,hashlib,json,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64,CS_OP_MEM
from capstone.x86 import X86_REG_RIP
from macho import MachO
from original import Original

def main():
    p=argparse.ArgumentParser();p.add_argument('--binary',type=Path,required=True);p.add_argument('--dump',type=Path,required=True)
    args=p.parse_args();root=Path(__file__).parent
    resources=args.binary.parent.parent/'Resources/content/configs/DateTimeLocaleConfigs'
    locales={};files={}
    for path in sorted(resources.glob('*.json')):
        raw=path.read_bytes();data=json.loads(raw)
        for name,count in [('months',12),('monthsShort',12),('weekdays',7),('weekdaysShort',7),('weekdaysMin',7)]:
            assert len(data[name])==count and all(isinstance(x,str) for x in data[name])
        locales[path.stem]=data;files[path.name]=hashlib.sha256(raw).hexdigest()
    assert len(locales)==24
    cs=Cs(CS_ARCH_X86,CS_MODE_64);cs.detail=True
    extra={'from_seconds':0x102a7414a,'from_millis':0x102a73e0c,'components':0x102a7492e,
           'iso_parse':0x102a74d4a,'iso_format':0x102a74648,'format':0x1000e1093,
           'bridge_seconds':0x10464c444,'bridge_millis':0x10464c4ac,'tostring':0x102a73db0}
    functions={};review={}
    with MachO(args.binary) as binary:
        for name,address in (Original.ENGINE_DATE | extra).items():
            code=binary.function_bytes(address);refs=set();lines=[]
            for ins in cs.disasm(code,address):
                if name in Original.ENGINE_DATE:lines.append(f'{ins.address:#x}: {ins.mnemonic} {ins.op_str}')
                for op in ins.operands:
                    if op.type==CS_OP_MEM and op.mem.base==X86_REG_RIP:refs.add(ins.address+ins.size+op.mem.disp)
            record={'address':hex(address),'size':len(code),'sha256':hashlib.sha256(code).hexdigest(),
                    'data_references':[hex(a) for a in sorted(refs)]}
            if name in Original.ENGINE_DATE:record['instructions']=lines;functions[name]=record
            else:review[name]=record
        fallbacks={}
        for i in range(14):
            a,n,b,m=struct.unpack('<QQQQ',binary.read(0x10c70a4e0+32*i,32))
            fallbacks[binary.read(a,n).decode()]=binary.read(b,m).decode()
        epoch=struct.unpack('<q',binary.read(0x109451008,8))[0]
        assert epoch==2440588*86400000000
    sources={}
    for relative in ['util/DateTime.c','script/DateTimeBridge.c','free/_free_f.part001.c','free/_free_u.part002.c','free/_free_r.part003.c']:
        sources[relative]=hashlib.sha256((args.dump/relative).read_bytes()).hexdigest()
    tokens=['YYYY','YY','MMMM','MMM','MM','M','DDDD','DDD','DD','D','dddd','ddd','dd','d',
            'HH','H','hh','h','mm','m','SSS','SS','S','ss','s','A','a','LTS','LT','LLLL','LLL','LL','L','llll','lll','ll','l']
    result={'version':'0.735.19.7351131','functions':functions,'reviewed':review,'locales':locales,'locale_file_sha256':files,
            'language_fallbacks':fallbacks,'tokens':tokens,'source_sha256':sources,'epoch_ticks':epoch,
            'min_seconds':-17987443200,'max_seconds':253402300799,
            'limits':['Formatting/ISO parser behavior is reconstructed; full original C++ locale/stream pipeline is not executed.',
                      'Timezone rules come from host UCRT; historical macOS zone databases can differ.']}
    (root/'data/datetime_recovery.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'locale_count':len(locales),'token_count':len(tokens),'epoch_ticks':epoch}))
if __name__=='__main__':main()
