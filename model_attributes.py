"""Bounded AttributesSerialize reader, based on rbx_types 3.1.0's format.

Values are inert typed records. Binary strings stay base64 until materialized
in Luau, so arbitrary bytes are preserved by both XML and asset JSON transport.
"""
import base64
from functools import cache
import json
import math
from pathlib import Path
import re
import struct

LIMIT=16*1024*1024

@cache
def brick_numbers():
    catalog=json.loads((Path(__file__).resolve().parent/'evidence/brickcolor_catalog.json').read_text(encoding='utf-8'))
    return {row['number'] for row in catalog['colors']}


def basic_rotation(identifier):
    x,y=divmod(identifier-1,6)
    axes=((1,0,0),(0,1,0),(0,0,1),(-1,0,0),(0,-1,0),(0,0,-1))
    if not 0<=x<6 or x%3==y%3:raise ValueError('Invalid attribute CFrame rotation ID')
    a,b=axes[x],axes[y]
    c=(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
    return [coordinate for row in zip(a,b,c) for coordinate in row]


def decode_attributes(data):
    if len(data)>LIMIT:raise ValueError('AttributesSerialize exceeds host limit 16 MiB')
    if not data:return []
    position=0
    def read(format):
        nonlocal position
        size=struct.calcsize('<'+format)
        if position+size>len(data):raise ValueError('Truncated AttributesSerialize')
        values=struct.unpack_from('<'+format,data,position);position+=size
        if any(isinstance(x,float) and not math.isfinite(x) for x in values):raise ValueError('Nonfinite attribute values unsupported')
        return list(values)
    def scalar(format):return read(format)[0]
    def string():
        nonlocal position
        size=scalar('I')
        if position+size>len(data):raise ValueError('Truncated attribute string')
        value=data[position:position+size];position+=size;return value
    count=scalar('I')
    if count>1024:raise ValueError('AttributesSerialize exceeds host limit 1024 attributes')
    result=[];names=set()
    formats={4:('number','i'),5:('number','f'),6:('number','d'),9:('UDim','fi'),10:('UDim2','fifi'),
             14:('BrickColor','I'),15:('Color3','fff'),16:('Vector2','ff'),17:('Vector3','fff'),
             27:('NumberRange','ff'),28:('Rect','ffff')}
    for _ in range(count):
        try:name=string().decode('utf-8')
        except UnicodeError:raise ValueError('Invalid UTF-8 attribute name') from None
        if not re.fullmatch('[A-Za-z0-9_./-]{1,100}',name) or name.startswith('RBX') or name in names:
            raise ValueError('Invalid/duplicate attribute name')
        names.add(name);kind_id=scalar('B')
        if kind_id==2:kind='string';values=base64.b64encode(string()).decode('ascii')
        elif kind_id==3:kind='boolean';values=scalar('B')!=0
        elif kind_id in formats:
            kind,format=formats[kind_id];values=read(format)
            if kind=='number':values=values[0]
            if kind=='BrickColor' and values[0] not in brick_numbers():raise ValueError('Invalid serialized BrickColor number')
        elif kind_id==33:
            kind='Font';weight,style=read('HB')
            try:family,cached=string().decode('utf-8'),string().decode('utf-8')
            except UnicodeError:raise ValueError('Invalid UTF-8 Font attribute') from None
            values=[family,weight if weight in range(100,901,100) else 400,style if style in (0,1) else 0,cached]
        elif kind_id==20:
            kind='CFrame';values=read('fff');rotation=scalar('B')
            values+=read('fffffffff') if rotation==0 else basic_rotation(rotation)
        elif kind_id in (23,25):
            kind='NumberSequence' if kind_id==23 else 'ColorSequence';length=scalar('I')
            if not 2<=length<=20:raise ValueError('Attribute sequence requires 2..20 keypoints')
            values=[]
            for _ in range(length):
                envelope,time=read('ff')
                point=[time]+read('f' if kind_id==23 else 'fff')
                if kind_id==23:point.append(envelope)
                values.append(point)
        else:raise ValueError(f'Unsupported attribute type ID {kind_id}')
        result.append({'name':name,'kind':kind,'values':values})
    if position!=len(data):raise ValueError('Trailing AttributesSerialize data')
    return result
