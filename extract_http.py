"""Record selected local 0.735 HTTP/JSON source evidence, without copying the dump."""
import argparse
import hashlib
import json
from pathlib import Path
import re

FUNCTIONS={
    'v8datamodel/HttpService.c':{
        '0x10567159e':'JSONDecode Lua bridge, parse failure versus null result',
        '0x10567185a':'JSONEncode Lua bridge',
        '0x10567194c':'UrlEncode wrapper',
        '0x105671984':'GUID wrapper and lowercase feature flag',
    },
    'v8xml/WebParser.c':{'0x1049680a8':'JSON parse entry','0x104968d6e':'JSON Lua writer entry'},
    'free/_free_w.part001.c':{
        '0x104968a82':'buffer base64 versus Zstandard compression',
        '0x104968e6d':'raw array length, string UTF-8, cycles, feature-flag numeric variants',
    },
    'free/_free_p.c':{'0x104967219':'null skipping and tagged engine values','0x104968033':'strict versus relaxed parser'},
    'free/_free_h.c':{'0x104969f28':'non-JSON values serialize as null'},
    'script/LuaArguments.c':{'0x10462f00a':'non-string table keys'},
    'rbx/Url.c':{'0x102bd0a20':'URL encoding entry','0x102bd0a5e':'ASCII alphanumeric byte predicate'},
}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dump',type=Path,default=Path('D:/0.735-full'))
    args=parser.parse_args()
    records={}
    for relative,requested in FUNCTIONS.items():
        data=(args.dump/relative).read_bytes();source=data.decode('utf-8')
        starts=list(re.finditer(r'^// Address: (0x[0-9a-f]+) \| Name: (.+)$',source,re.M))
        selected={}
        for i,match in enumerate(starts):
            address=match[1]
            if address not in requested:continue
            end=starts[i+1].start() if i+1<len(starts) else len(source)
            selected[address]={'name':match[2],'reason':requested[address],
                'function_text_sha256':hashlib.sha256(source[match.start():end].encode()).hexdigest()}
        assert selected.keys()==requested.keys(),(relative,requested.keys()-selected.keys())
        records[relative]={'sha256':hashlib.sha256(data).hexdigest(),'functions':selected}
    report={'source_build':'0.735.19.7351131','sources':records,
        'restored_semantics':['rawlen/rawget arrays; dictionary keys ignored when array length > 0',
            'empty table becomes []','cycles rejected; shared noncyclic tables permitted',
            'UTF-8 string validation','JSON null skips object members and leaves array holes',
            'non-JSON userdata/functions/threads become null','all non-ASCII-alphanumeric URL bytes percent encoded',
            'uncompressed base64 buffer envelope m:null,t:buffer,base64:string'],
        'host_implementation':'JSON recreated in Luau; OS GUID entropy; Python stdlib HTTP workers; native ABI copies responses',
        'not_proven':['original native JSON parser/writer differential parity','live fast-flag configuration',
            'exact float decimal spelling','Zstandard buffer encoding/decoding','Studio HTTP caches, rate limits, cloud policies and TLS backend'],
        'choices':{'nonfinite_encode':'null branch; tagged numeric decode supported',
            'guid_case':'lowercase','json_max_depth':128,'buffer_max_bytes':50*1024*1024,
            'http_max_active_workers':64,'http_default_and_max_timeout_seconds':30,
            'response_max_bytes':50*1024*1024,'http_enabled_default':False},
    }
    target=Path(__file__).resolve().parent/'evidence/http_recovery.json'
    target.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'Recorded {sum(len(x["functions"]) for x in records.values())} reviewed HTTP/JSON/URL functions')

if __name__=='__main__':main()
