"""Import supported Roblox XML/binary model data; never resolve external data.

Binary models use the isolated data-only codec. Unsupported properties fail
explicitly rather than quietly producing a different script environment.
"""
import base64
import hashlib
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from model_attributes import decode_attributes
from model_properties import SCHEMA,parse_property
from model_binary import check_binary

CLASSES=set(SCHEMA)
METADATA={'ScriptGuid','SourceAssetId','HistoryId','UniqueId','Capabilities','DefinesCapabilities'}

def read_model(path):
    path=Path(path)
    if path.stat().st_size>64*1024*1024:raise ValueError('Model exceeds host limit 64 MiB')
    data=path.read_bytes()
    if data.startswith(b'<roblox!'):
        check_binary(data)
        with tempfile.TemporaryDirectory(prefix='model-decode-') as directory:
            normalized=Path(directory)/'model.rbxmx'
            result=subprocess.run([str(Path(__file__).resolve().parent/'recovery-asset-codec.exe'),
                'to-xml',str(path.resolve()),str(normalized)],capture_output=True,text=True,encoding='utf-8',timeout=20)
            if result.returncode:raise ValueError('Roblox binary decode failed: '+result.stderr.strip())
            model=read_model(normalized)
            def relabel(record):
                record['label']=path.resolve().as_posix()+'::'+record['label'].split('::',1)[1]
                for child in record['children']:relabel(child)
            for record in model['items']:relabel(record)
            model.update(path=path,sha256=hashlib.sha256(data).hexdigest())
            return model
    if b'<!DOCTYPE' in data.upper() or b'<!ENTITY' in data.upper():raise ValueError('XML DTD/entities are unsupported')
    try:root=ET.fromstring(data)
    except ET.ParseError as error:raise ValueError(str(error)) from None
    if root.tag!='roblox' or root.attrib.get('version')!='4':raise ValueError('Expected Roblox XML version 4')
    shared={x.attrib.get('md5'):base64.b64decode(''.join((x.text or '').split()),validate=True) for x in root.findall('./SharedStrings/SharedString')}
    count=0;referents={};references=[];node_classes={}
    def item(node,parent='',depth=0):
        nonlocal count
        count+=1
        node_id=count
        if count>10000 or depth>128:raise ValueError('XML model exceeds host tree limits')
        kind=node.attrib.get('class')
        if kind not in CLASSES:raise ValueError(f'XML scripting importer does not support class {kind}')
        node_classes[node_id]=kind
        referent=node.attrib.get('referent')
        if referent:
            if referent in referents or referent in ('null','nil'):raise ValueError('Duplicate/reserved XML referent')
            referents[referent]=node_id
        props={}
        for prop in node.findall('./Properties/*'):
            key=prop.attrib.get('name')
            if not key or key in props:raise ValueError('Missing/duplicate XML property name')
            props[key]=prop
        name=props['Name'].text if 'Name' in props else kind
        if 'Name' in props and (props['Name'].tag!='string' or list(props['Name'])):raise ValueError('Expected XML string Name')
        name=name or ''
        identity=parent+'/'+name
        fields={};tags=[];attributes=[];source='';typed=[];typed_names=set()
        for key,prop in props.items():
            text=prop.text or ''
            if key=='Name':continue
            if key=='Source':
                if kind not in {'ModuleScript','Script','LocalScript'}:raise ValueError('Source requires a script class')
                source=text;continue
            if key in METADATA:
                if key=='Capabilities' and text.strip() not in ('','0'):raise ValueError('Nonzero XML capabilities unsupported')
                if key=='DefinesCapabilities' and text.strip()=='true':raise ValueError('XML capability boundaries unsupported')
                continue
            if key=='LinkedSource':
                if text.strip() or any(x.tag not in {'null','nil'} for x in prop):raise ValueError('External LinkedSource unsupported')
                continue
            if key=='AttributesSerialize':
                if prop.tag not in {'BinaryString','SharedString'}:raise ValueError('Expected binary/shared AttributesSerialize')
                raw=shared.get(text.strip()) if prop.tag=='SharedString' else base64.b64decode(''.join(text.split()),validate=True)
                if raw is None:raise ValueError('Missing shared AttributesSerialize payload')
                attributes=decode_attributes(raw);continue
            if key=='SerializedOverrides':
                if text.strip():raise ValueError(f'Nonempty {key} unsupported by XML scripting importer')
                continue
            if key=='Tags':
                raw=shared.get(text.strip()) if prop.tag=='SharedString' else base64.b64decode(''.join(text.split()),validate=True)
                if raw is None:raise ValueError('Missing shared Tags payload')
                tags=[x.decode('utf-8') for x in raw.split(b'\0') if x];continue
            if (key=='Archivable' or key in {'Disabled','Enabled'} and kind in {'Script','LocalScript'}) and prop.tag=='bool':
                if text not in {'true','false'}:raise ValueError(f'Invalid XML boolean {key}')
                if key!='Archivable' and kind not in {'Script','LocalScript'}:raise ValueError(f'{key} requires BaseScript')
                fields[key]=text=='true';continue
            if key=='RunContext' and prop.tag=='token' and kind=='Script':
                run=int(text)
                if run not in {0,1,2}:raise ValueError('Unsupported XML RunContext')
                fields[key]=run;continue
            value=parse_property(kind,key,prop)
            if value is not None:
                if value['name'] in typed_names:raise ValueError('Duplicate aliased XML property')
                typed_names.add(value['name']);typed.append(value)
                if value['kind']=='Instance?':references.append(value)
        return {'id':node_id,'class':kind,'name':name,'source':source,'label':path.resolve().as_posix()+'::'+identity,
                'properties':fields,'typed_properties':typed,'tags':tags,'attributes':attributes,'children':[item(x,identity,depth+1) for x in node.findall('Item')]}
    items=[item(x) for x in root.findall('Item')]
    for reference in references:
        value=reference['values']
        if value is not None:
            if value not in referents:raise ValueError('Unresolved/external XML reference')
            reference['values']=referents[value]
            if reference['name']=='PrimaryPart' and node_classes[reference['values']] not in {'Part','WedgePart','CornerWedgePart'}:
                raise ValueError('Imported PrimaryPart must reference a BasePart')
            if reference['name'] in {'Attachment0','Attachment1'} and node_classes[reference['values']] not in {'Attachment','Bone'}:
                raise ValueError('Imported attachment reference must target Attachment or Bone')
    return {'path':path,'sha256':hashlib.sha256(data).hexdigest(),'items':items,'count':count}
