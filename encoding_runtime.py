"""Bounded, synchronous data transforms for EncodingService; never evaluates data."""
import base64
import binascii
import hashlib
from pathlib import Path
import subprocess
import tempfile

LIMIT=50*1024*1024
ROBLOX_SIZE_LIMIT=1024*1024*1024


def zstd_module():
    try:from compression import zstd
    except ImportError:raise ValueError('Zstd requires Python 3.14+ with compression.zstd') from None
    return zstd


def frame_size(data):
    zstd=zstd_module()
    try:size=zstd.get_frame_info(data).decompressed_size
    except zstd.ZstdError:return None
    return size if size is not None and size<=ROBLOX_SIZE_LIMIT else None


def transform(options,data):
    if len(data)>LIMIT:raise ValueError('input exceeds host limit 50 MiB')
    action=options['Action'];metadata={}
    if action=='base64-encode':
        if (len(data)+2)//3*4>LIMIT:raise ValueError('encoded output exceeds host limit 50 MiB')
        output=base64.b64encode(data)
    elif action=='base64-decode':
        try:output=base64.b64decode(data,validate=True)
        except binascii.Error:raise ValueError('Base64Decode: input is not a base64 string') from None
    elif action=='hash':
        algorithm=options['Algorithm']
        if algorithm=='Blake2b':output=hashlib.blake2b(data,digest_size=32).digest()
        elif algorithm in {'Md5','Sha1','Sha256'}:
            output=hashlib.new(algorithm.lower(),data).digest()
        elif algorithm=='Blake3':
            with tempfile.TemporaryDirectory(prefix='encoding-hash-') as directory:
                folder=Path(directory);source=folder/'input';target=folder/'digest'
                source.write_bytes(data)
                result=subprocess.run([str(Path(__file__).resolve().parent/'recovery-asset-codec.exe'),
                    'blake3',str(source),str(target)],capture_output=True,timeout=20)
                if result.returncode:raise ValueError('Blake3 helper failed')
                output=target.read_bytes()
                if len(output)!=32:raise ValueError('Invalid Blake3 digest size')
        else:raise ValueError('unknown Enum.HashAlgorithm')
    elif action in {'compress','decompress','size'}:
        if options.get('Algorithm')!='Zstd':raise ValueError('unknown Enum.CompressionAlgorithm')
        zstd=zstd_module()
        if action=='compress':
            level=options.get('Level',1)
            if isinstance(level,bool) or not isinstance(level,(int,float)) or int(level)!=level or not -7<=level<=22:
                raise ValueError('unsupported compression level for Zstd')
            output=zstd.compress(data,level=int(level))
        else:
            size=frame_size(data)
            if action=='size':return {'Size':size},b''
            if size is None:raise ValueError('DecompressBuffer: unknown/invalid frame size')
            if size>LIMIT:raise ValueError('decompressed output exceeds host limit 50 MiB')
            try:
                decoder=zstd.ZstdDecompressor(options={zstd.DecompressionParameter.window_log_max:26})
                output=decoder.decompress(data,max_length=size+1)
                if not decoder.eof or decoder.unused_data or len(output)!=size:
                    raise ValueError('DecompressBuffer: truncated/trailing data or size mismatch')
            except zstd.ZstdError:raise ValueError('DecompressBuffer: invalid Zstd data or unsupported window') from None
    else:raise ValueError('unknown encoding action')
    if len(output)>LIMIT:raise ValueError('output exceeds host limit 50 MiB')
    return metadata,output
