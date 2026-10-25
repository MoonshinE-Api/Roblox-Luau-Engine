"""Typed XML properties limited to the implemented runtime property schema."""
import json
import math
from pathlib import Path
import struct
from model_attributes import brick_numbers

ROOT=Path(__file__).resolve().parent
SCHEMA=json.loads((ROOT/'data/model_property_schema.json').read_text(encoding='utf-8'))['classes']
ENUMS=json.loads((ROOT/'data/enum_catalog.json').read_text(encoding='utf-8'))['enums']
ALIASES={'size':'Size','shape':'Shape','Color3uint8':'Color','WorldPivotData':'WorldPivot',
    'ImageContent':'Image','HoverImageContent':'HoverImage','PressedImageContent':'PressedImage',
    'BottomImageContent':'BottomImage','MidImageContent':'MidImage','TopImageContent':'TopImage',
    'TextureContent':'Texture','MoonTextureContent':'MoonTextureId','SunTextureContent':'SunTextureId',
    'SkyboxBackContent':'SkyboxBk','SkyboxDownContent':'SkyboxDn','SkyboxFrontContent':'SkyboxFt',
    'SkyboxLeftContent':'SkyboxLf','SkyboxRightContent':'SkyboxRt','SkyboxUpContent':'SkyboxUp'}


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
    if (kind in ('boolean','string','number','BrickColor','Instance?') or kind.startswith('Enum.')) and list(prop) and not (kind=='string' and tag in ('Content','ContentId')):
        raise ValueError('Unexpected nested scalar XML property')
    if kind=='boolean' and tag=='bool':
        if text not in ('true','false'):raise ValueError('Invalid XML boolean')
        value=text=='true'
    elif kind=='string' and tag in ('string','ProtectedString'):
        if list(prop):raise ValueError('Invalid XML string')
        value=text
    elif kind=='string' and tag in ('Content','ContentId'):
        children=list(prop)
        if len(children)!=1 or children[0].tag not in ('null','url','uri') or list(children[0]):raise ValueError('Invalid XML URI content')
        if children[0].tag=='null' and (children[0].text or '').strip():raise ValueError('Invalid XML null content')
        value='' if children[0].tag=='null' else children[0].text or ''
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
    elif kind=='Vector2' and tag=='Vector2':value=components(('X','Y'))
    elif kind=='Vector3' and tag=='Vector3':value=components(('X','Y','Z'))
    elif kind=='NumberRange' and tag=='NumberRange':
        if list(prop):raise ValueError('Unexpected XML NumberRange children')
        value=[number(part,True) for part in text.split()]
        if len(value)!=2 or value[0]>value[1]:raise ValueError('Invalid XML NumberRange')
    elif kind=='UDim' and tag=='UDim':value=components(('S','O'))
    elif kind=='UDim2' and tag=='UDim2':value=components(('XS','XO','YS','YO'))
    elif kind=='Rect' and tag=='Rect2D':
        if [child.tag for child in prop]!=['min','max']:raise ValueError('Invalid XML Rect2D')
        value=[]
        for child in prop:
            if [part.tag for part in child]!=['X','Y']:raise ValueError('Invalid XML Rect2D coordinates')
            value.extend(number(part.text or '',True) for part in child)
    elif kind in ('NumberSequence','ColorSequence') and tag==kind:
        if list(prop):raise ValueError('Unexpected XML sequence children')
        fields=[number(field,True) for field in text.split()]
        width=3 if kind=='NumberSequence' else 5
        if len(fields)%width or not 2<=len(fields)//width<=20:raise ValueError('Invalid XML sequence length')
        value=[fields[i:i+width] for i in range(0,len(fields),width)]
        if value[0][0]!=0 or value[-1][0]!=1 or any(not 0<=row[0]<=1 for row in value) or any(a[0]>b[0] for a,b in zip(value,value[1:])):
            raise ValueError('Invalid XML sequence times')
        if kind=='NumberSequence' and any(row[2]<0 for row in value):raise ValueError('Negative XML sequence envelope')
        if kind=='ColorSequence':value=[row[:4] for row in value]
    elif kind=='Font' and tag=='Font':
        names=[child.tag for child in prop]
        if names not in (['Family','Weight','Style'],['Family','Weight','Style','CachedFaceId']):raise ValueError('Invalid XML Font')
        def content(node):
            parts=list(node)
            if len(parts)!=1 or parts[0].tag not in ('url','null') or list(parts[0]):raise ValueError('Invalid XML Font content')
            return parts[0].text or '' if parts[0].tag=='url' else ''
        try:weight=int(prop[1].text or '')
        except ValueError:raise ValueError('Invalid XML Font weight') from None
        style=prop[2].text
        if list(prop[1]) or list(prop[2]) or weight not in ENUMS['FontWeight'].values() or style not in ENUMS['FontStyle']:raise ValueError('Invalid XML Font weight/style')
        value=[content(prop[0]),weight,ENUMS['FontStyle'][style],content(prop[3]) if len(prop)==4 else '']
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
