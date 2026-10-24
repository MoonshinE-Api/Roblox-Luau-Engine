"""Encoding format vectors, original contract, VM integration and OOM ownership."""
import base64
from compression import zstd
import ctypes as C
import hashlib
import json
from pathlib import Path
import random
import struct
import subprocess
import sys
import tempfile
from unittest.mock import patch

root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from encoding_runtime import transform,LIMIT,frame_size
from http_runtime import HttpRuntime,Transfer
from run import lua_literal,bootstrap,execute_source
from vm_runtime import Runtime

cases=[]
def row(action,data,algorithm=None,level=None):
    options={'Action':action}
    if algorithm:options['Algorithm']=algorithm
    if level is not None:options['Level']=level
    metadata,body=transform(options,data)
    cases.append((options,data,body,metadata))
    return metadata,body

# RFC 4648 vectors plus every binary byte / padding boundary.
for raw,encoded in ((b'',b''),(b'f',b'Zg=='),(b'fo',b'Zm8='),(b'foo',b'Zm9v'),
                    (b'foob',b'Zm9vYg=='),(b'fooba',b'Zm9vYmE='),(b'foobar',b'Zm9vYmFy')):
    assert row('base64-encode',raw)[1]==encoded
    assert row('base64-decode',encoded)[1]==raw
generator=random.Random(735)
for length in (1,2,3,4,31,32,255,256,257,1024):
    raw=generator.randbytes(length)
    assert row('base64-decode',row('base64-encode',raw)[1])[1]==raw
for bad in (b'!',b'Zg',b'Zg===',b'Zg==\n',b'Z===',b'=AAA',b'Zg==Zg==',b'Zm-v',b'Zm_v'):
    try:transform({'Action':'base64-decode'},bad)
    except ValueError:pass
    else:raise AssertionError('Invalid Base64 accepted')

# Published BLAKE3 tests cross 64-byte blocks, 1024-byte chunks and tree boundaries.
vectors=json.loads((root/'tests/vendor/blake3_vectors.json').read_text())['cases']
for vector in vectors:
    raw=bytes(i%251 for i in range(vector['length']))
    assert row('hash',raw,'Blake3')[1].hex()==vector['hash']
for name,expected in {
    'Md5':'900150983cd24fb0d6963f7d28e17f72',
    'Sha1':'a9993e364706816aba3e25717850c26c9cd0d89d',
    'Sha256':'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad',
    'Blake2b':'bddd813c634239723171ef3fee98579b94964e3bb1cb3e427262c8c068d52319',
}.items():assert row('hash',b'abc',name)[1].hex()==expected
for name in ('Md5','Sha1','Sha256','Blake2b'):
    row('hash',bytes(range(256))*3+b'\0',name)

# Construct raw-block Zstd frames directly from the format (no compressor).
for raw in (b'',b'abc',bytes(range(255))):
    frame=b'\x28\xb5\x2f\xfd\x20'+bytes([len(raw)])+((len(raw)<<3)|1).to_bytes(3,'little')+raw
    assert row('size',frame,'Zstd')[0]['Size']==len(raw)
    assert row('decompress',frame,'Zstd')[1]==raw
for level in (-7,0,1,3,22):
    raw=b'hello\0encoding service!'*120
    compressed=row('compress',raw,'Zstd',level)[1]
    assert zstd.decompress(compressed)==raw
    assert row('decompress',compressed,'Zstd')[1]==raw
    assert row('size',compressed,'Zstd')[0]['Size']==len(raw)
unknown=zstd.ZstdCompressor(options={zstd.CompressionParameter.content_size_flag:0}).compress(b'abc',zstd.ZstdCompressor.FLUSH_FRAME)
oversized=b'\x28\xb5\x2f\xfd\xe0'+struct.pack('<Q',1024*1024*1024+1)+b'\x01\0\0'
host_oversized=b'\x28\xb5\x2f\xfd\xe0'+struct.pack('<Q',LIMIT+1)+b'\x01\0\0'
assert row('size',unknown,'Zstd')[0]['Size'] is None
assert row('size',oversized,'Zstd')[0]['Size'] is None
assert row('size',host_oversized,'Zstd')[0]['Size']==LIMIT+1
compressed=zstd.compress(b'abc',options={zstd.CompressionParameter.checksum_flag:1})
corrupt=compressed[:-1]+bytes([compressed[-1]^1])
invalid=[b'',b'invalid',unknown,oversized,host_oversized,compressed[:-1],corrupt,compressed+b'extra',compressed+compressed]
for data in invalid:
    try:transform({'Action':'decompress','Algorithm':'Zstd'},data)
    except ValueError:pass
    else:raise AssertionError('Invalid/unsupported Zstd accepted')
for level in (-8,23,1.5,True):
    try:transform({'Action':'compress','Algorithm':'Zstd','Level':level},b'abc')
    except ValueError:pass
    else:raise AssertionError('Invalid compression level accepted')

# Run the vectors through actual Luau, buffer and synchronous native bridge.
with tempfile.TemporaryDirectory(prefix='encoding-check-') as directory:
    folder=Path(directory);script=folder/'main.luau'
    lines=["local e=game:GetService('EncodingService');local z=Enum.CompressionAlgorithm.Zstd",
           "assert(game:FindService('EncodingService')==e);assert(not pcall(Instance.new,'EncodingService'))",
           "local function unhex(s)return buffer.fromstring((s:gsub('..',function(c)return string.char(tonumber(c,16))end)))end",
           "local function hex(s)return (s:gsub('.',function(c)return string.format('%02x',string.byte(c))end))end"]
    for options,data,expected,metadata in cases:
        argument='unhex('+lua_literal(data.hex())+')';action=options['Action']
        if action=='hash':
            expression='e:ComputeBufferHash('+argument+',Enum.HashAlgorithm.'+options['Algorithm']+')'
            lines.append('assert(hex(e:ComputeStringHash(buffer.tostring('+argument+'),Enum.HashAlgorithm.'+options['Algorithm']+'))=='+lua_literal(expected.hex())+')')
        elif action=='compress':expression='e:CompressBuffer('+argument+',z,'+str(options.get('Level',1))+')'
        elif action=='decompress':expression='e:DecompressBuffer('+argument+',z)'
        elif action=='size':
            lines.append('assert(e:GetDecompressedBufferSize('+argument+',z)=='+lua_literal(metadata['Size'])+')');continue
        else:expression='e:'+('Base64Encode' if action=='base64-encode' else 'Base64Decode')+'('+argument+')'
        lines.append('assert(hex(buffer.tostring('+expression+'))=='+lua_literal(expected.hex())+')')
    lines.extend([
        "local raw=buffer.fromstring('legacy aliases');local compressed=e:CompressBufferZstd(raw)",
        "assert(e:GetDecompressedBufferSizeZstd(compressed)==14);assert(buffer.tostring(e:DecompressBufferZstd(compressed))=='legacy aliases')",
        "assert(buffer.tostring(e:DecompressBuffer(e:CompressBuffer(raw,z),z))=='legacy aliases')",
        "for _,f in {function()e:Base64Encode('x')end,function()e:Base64Decode('x')end,function()e:CompressBuffer(raw,'Zstd')end,function()e:CompressBuffer(raw,z,1.5)end,function()e:CompressBuffer(raw,z,0/0)end,function()e:DecompressBuffer(raw,z)end,function()e:ComputeStringHash(raw,Enum.HashAlgorithm.Sha1)end,function()e:ComputeBufferHash(raw,'Sha1')end,function()e:ComputeBufferHash(raw,Enum.Material.Plastic)end} do assert(not pcall(f))end",
        "local co=coroutine.create(function()return e:ComputeStringHash('abc',Enum.HashAlgorithm.Sha256),e:Base64Encode(raw),e:CompressBuffer(raw,z)end)",
        "assert(coroutine.resume(co));assert(coroutine.status(co)=='dead','EncodingService yielded')",
        "local http=game:GetService('HttpService');local packed=buffer.tostring(e:Base64Encode(compressed))",
        "local decoded=http:JSONDecode('{\"m\":null,\"t\":\"buffer\",\"zbase64\":\"'..packed..'\"}')",
        "assert(typeof(decoded)=='buffer' and buffer.tostring(decoded)=='legacy aliases')",
        "assert(not pcall(function()http:JSONDecode('{\"m\":null,\"t\":\"buffer\",\"zbase64\":\"!!!!\"}')end))",
        "print('ENCODING SERVICE VECTOR AND VM CHECKS PASSED')"])
    script.write_text('\n'.join(lines),encoding='utf-8')
    result=subprocess.run([sys.executable,str(root/'run.py'),str(script),*sys.argv[1:]],capture_output=True,text=True,encoding='utf-8',timeout=90)
    assert result.returncode==0 and 'ENCODING SERVICE VECTOR AND VM CHECKS PASSED' in result.stdout,(result.stdout,result.stderr)
    # Native response allocation may throw; the synchronous wrapper must release
    # the pinned host result even when Lua catches an out-of-memory exception.
    binary=Path(r'D:/Release-RobloxStudioApp/RobloxStudio.app/Contents/MacOS/RobloxStudio')
    if '--binary' in sys.argv:binary=Path(sys.argv[sys.argv.index('--binary')+1])
    runtime=Runtime(binary,memory_mb=8)
    try:
        runtime.open_libraries()
        execute_source(runtime,root,bootstrap(root,{'mode':'server','duration':.1,'realtime':False}),folder,'bootstrap')
        with patch('encoding_runtime.transform',return_value=({},b'x'*(12*1024*1024))):
            # Execute synchronously without scheduler scaffolding to inspect
            # host result ownership immediately following protected Lua OOM.
            execute_source(runtime,root,"local ok=pcall(function()game:GetService('EncodingService'):Base64Encode(buffer.create(1))end);assert(not ok);return true",folder,'oom')
        assert not runtime.http.jobs,'Synchronous encoding result leaked after OOM'
    finally:runtime.close()

report={'status':'PASS','format_vectors':len(cases),'blake3_published_vectors':len(vectors),
        'checks':['RFC4648/all bytes/padding','five raw digest algorithms','hand-built Zstd frames/levels -7..22',
            'invalid/unknown/oversized/truncated/checksum/trailing frames','original VM binary string/buffer integration',
            'non-yielding coroutine call','legacy Zstd aliases','HttpService zbase64','native OOM pinned-response cleanup'],
        'native_engine_byte_parity_verified':False,'host_limit_bytes':LIMIT}
(root/'evidence/encoding_comparison.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('ENCODING SERVICE VECTOR/VM/OOM CHECKS PASSED')
