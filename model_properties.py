"""Typed XML properties limited to the implemented runtime property schema."""
import json
import math
from pathlib import Path
import struct
from model_attributes import brick_numbers

ROOT=Path(__file__).resolve().parent
SCHEMA=json.loads((ROOT/'evidence/model_property_schema.json').read_text(encoding='utf-8'))['classes']
ENUMS=json.loads((ROOT/'evidence/enum_catalog.json').read_text(encoding='utf-8'))['enums']
ALIASES={'size':'Size','shape':'Shape','Color3uint8':'Color','WorldPivotData':'WorldPivot'}


def number(text,single=False):
    try:
        value=float(text)
        if single:value=struct.unpack('<f',struct.pack('<f',value))[0]
    except (ValueError,OverflowError):raise ValueError('Invalid XML numeric value') from None
    if not math.isfinite(value):raise ValueError('Nonfinite XML property unsupported')
    return value


def parse_property(class_name,key,prop):
    key=ALIASES.get(key,key);kind=SCHEMA[class_name].get(key)
    if kind is None:raise ValueError(f'Unsupported XML property {class_name}.{key}')
    text=prop.text or '';tag=prop.tag
    if key=='WorldPivot' and tag=='OptionalCoordinateFrame':
        children=list(prop)
        if not children:return None
        if len(children)!=1 or children[0].tag!='CFrame':raise ValueError('Invalid optional CFrame')
        prop=children[0];tag='CoordinateFrame'
    def components(names):
        if [child.tag for child in prop]!=list(names):raise ValueError(f'Invalid XML {kind} components')
        return [number(child.text or '',True) for child in prop]
    if (kind in ('boolean','string','number','BrickColor','Instance?') or kind.startswith('Enum.')) and list(prop):
        raise ValueError('Unexpected nested scalar XML property')
    if kind=='boolean' and tag=='bool':
        if text not in ('true','false'):raise ValueError('Invalid XML boolean')
        value=text=='true'
    elif kind=='string' and tag in ('string','ProtectedString'):
        if list(prop):raise ValueError('Invalid XML string')
        value=text
    elif kind=='number' and tag in ('float','double','int','int64'):
        if tag in ('int','int64'):
            try:value=int(text)
            except ValueError:raise ValueError('Invalid XML integer') from None
            if abs(value)>9007199254740991:raise ValueError('XML integer exceeds exact host numeric range')
        else:value=number(text,tag=='float')
    elif kind.startswith('Enum.') and tag=='token':
        try:value=int(text)
        except ValueError:raise ValueError('Invalid XML enum token') from None
        if value not in ENUMS[kind[5:]].values():raise ValueError('Unknown XML enum token')
    elif kind=='Instance?' and tag=='Ref':
        if list(prop):raise ValueError('Invalid XML reference')
        value=None if text.strip() in ('','null','nil') else text.strip()
    elif kind=='Vector3' and tag=='Vector3':value=components(('X','Y','Z'))
    elif kind=='CFrame' and tag=='CoordinateFrame':value=components(('X','Y','Z','R00','R01','R02','R10','R11','R12','R20','R21','R22'))
    elif kind=='Color3' and tag in ('Color3','Color3uint8'):
        if list(prop):value=components(('R','G','B'))
        else:
            try:packed=int(text)
            except ValueError:raise ValueError('Invalid XML packed color') from None
            if not 0<=packed<=0xffffffff:raise ValueError('Invalid XML packed color')
            value=[((packed>>shift)&255)/255 for shift in (16,8,0)]
    elif kind=='BrickColor' and tag in ('int','BrickColor'):
        try:color=int(text)
        except ValueError:raise ValueError('Invalid XML BrickColor') from None
        if color not in brick_numbers():raise ValueError('Unknown XML BrickColor')
        value=[color]
    elif kind=='PhysicalProperties?' and tag=='PhysicalProperties':
        children=list(prop)
        if not children or children[0].tag!='CustomPhysics':raise ValueError('Missing XML CustomPhysics flag')
        flag=children[0].text
        if flag=='false':
            if len(children)!=1:raise ValueError('Unexpected default PhysicalProperties fields')
            value=None
        elif flag=='true':
            names=['CustomPhysics','Density','Friction','Elasticity','FrictionWeight','ElasticityWeight']
            if len(children)==7:names.append('AcousticAbsorption')
            if [child.tag for child in children]!=names:raise ValueError('Invalid XML PhysicalProperties components')
            value=[number(child.text or '',True) for child in children[1:]]
            if len(value)==5:value.append(1)
        else:raise ValueError('Invalid XML CustomPhysics boolean')
    else:raise ValueError(f'Unsupported XML {tag} for {class_name}.{key} ({kind})')
    return {'name':key,'kind':kind,'values':value}
