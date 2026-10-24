"""Bound compressed RBXM headers/chunks before the isolated data-only decoder."""
import struct

def check_binary(data):
    if len(data)<32 or data[:14]!=b'<roblox!\x89\xff\r\n\x1a\n':raise ValueError('Unsupported Roblox binary header')
    version,classes,instances=struct.unpack_from('<HII',data,14)
    if version!=0 or classes>10000 or instances>10000:raise ValueError('Binary model exceeds supported version/tree limits')
    position=32;total=0;ended=False
    while position+16<=len(data):
        kind,compressed,raw,reserved=struct.unpack_from('<4sIII',data,position)
        position+=16;length=compressed or raw;total+=raw
        if total>64*1024*1024 or position+length>len(data):raise ValueError('Invalid/oversized Roblox binary chunk')
        position+=length
        if kind==b'END\0':ended=True;break
    if not ended or position!=len(data):raise ValueError('Missing END/trailing Roblox binary data')
