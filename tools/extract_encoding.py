"""Record selected EncodingService contracts from the user's decompilation."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argparse
import hashlib
import json
from pathlib import Path
import re

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=Path('D:/0.735-full/rbx/EncodingService.c'))
    args=parser.parse_args();data=args.source.read_bytes();text=data.decode('utf-8')
    selected=[]
    for match in re.finditer(r'// Address: (0x[0-9a-f]+) \| Name: ([^\r\n]+)\r?\n(.*?)(?=\r?\n// Address:|\r?\n// END|\Z)',text,re.S):
        if any(name in match[2] for name in ('base64Encode','base64Decode','computeStringHash','computeBufferHash','compressBuffer','decompressBuffer','getDecompressedBufferSize')):
            selected.append({'address':match[1],'symbol':match[2],
                'decompiled_body_sha256':hashlib.sha256(match[3].encode()).hexdigest()})
    assert len(selected)==7,len(selected)
    report={'source':str(args.source),'source_sha256':hashlib.sha256(data).hexdigest(),'selected_functions':selected,
        'recovered_contract':{'Blake2b_digest_bytes':32,'Blake3_digest_bytes':32,'hash_result':'binary string / copied bytes for buffer',
            'zstd_compression_level':[-7,22],'max_decompressed_size':1073741824,'unknown_frame_size':'nil getter / error on decompress'},
        'implementation':'semantic Python/Rust host implementation; not original native code execution',
        'unverified':['exact compressed bytes','Base64 tolerance','native errors/argument coercion'],
        'compatibility_aliases':['CompressBufferZstd','DecompressBufferZstd','GetDecompressedBufferSizeZstd'],
        'aliases_native_presence_verified':False,
        'references':['https://create.roblox.com/docs/reference/engine/classes/EncodingService',
            'https://docs.python.org/3.14/library/compression.zstd.html',
            'https://github.com/BLAKE3-team/BLAKE3/blob/1.8.2/test_vectors/test_vectors.json']}
    (Path(__file__).resolve().parents[1]/'data/encoding_recovery.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'functions':len(selected),'source_sha256':report['source_sha256']}))

if __name__=='__main__':main()
