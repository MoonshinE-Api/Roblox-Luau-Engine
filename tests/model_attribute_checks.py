"""AttributesSerialize -> XML / compressed RBXM -> VM values, Clone and signals."""
import base64
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from model_attributes import decode_attributes,basic_rotation
from model_xml import read_model

def string(data):return struct.pack('<I',len(data))+data
def entry(name,type_id,data):return string(name.encode())+bytes([type_id])+data
records=[entry('LightData',2,string(b'harmless-data-only')),
    entry('Binary',2,string(bytes(range(256))+b'\0\xff\xfe')),
    entry('Flag',3,b'\1'),entry('Integer',4,struct.pack('<i',-735)),
    entry('Float',5,struct.pack('<f',1.25)),entry('Double',6,struct.pack('<d',.125)),
    entry('Dimension',9,struct.pack('<fi',.5,-20)),entry('Dimensions',10,struct.pack('<fifi',.5,-20,.25,10)),
    entry('Brick',14,struct.pack('<I',21)),entry('Color',15,struct.pack('<fff',.25,.5,.75)),
    entry('V2',16,struct.pack('<ff',2,3)),entry('V3',17,struct.pack('<fff',2,3,4)),
    entry('Matrix',20,struct.pack('<fffBfffffffff',1,2,3,0,0,-1,0,1,0,0,0,0,1)),
    entry('Range',27,struct.pack('<ff',2,7)),entry('Rectangle',28,struct.pack('<ffff',1,2,3,4)),
    entry('Numbers',23,struct.pack('<Iffffff',2,0,0,1,.25,1,2)),
    entry('Colors',25,struct.pack('<Iffffffffff',2,0,0,1,0,0,0,1,0,0,1))]
rotations=[]
for identifier in range(1,37):
    try:basic_rotation(identifier)
    except ValueError:continue
    rotations.append(identifier)
    records.append(entry('Rotation'+str(identifier),20,struct.pack('<fffB',1,2,3,identifier)))
assert len(rotations)==24
payload=struct.pack('<I',len(records))+b''.join(records)
decoded=decode_attributes(payload);assert len(decoded)==len(records)
for invalid in (b'\0',payload[:-1],payload+b'trailing',struct.pack('<I',1025),
    struct.pack('<I',2)+records[0]*2,
    struct.pack('<I',1)+entry('Bad',255,b''),
    struct.pack('<I',1)+entry('BadBrickColor',14,struct.pack('<I',99999)),
    struct.pack('<I',1)+entry('BadName!',3,b'\0'),
    struct.pack('<I',1)+entry('RBXInternal',3,b'\0'),
    struct.pack('<I',1)+entry('Bad',2,struct.pack('<I',0xffffffff)),
    struct.pack('<I',1)+entry('NaN',6,struct.pack('<d',float('nan'))),
    struct.pack('<I',1)+entry('BadMatrix',20,struct.pack('<fffB',0,0,0,1)),
    struct.pack('<I',1)+entry('HugeSequence',23,struct.pack('<I',0xffffffff))):
    try:decode_attributes(invalid)
    except ValueError:pass
    else:raise AssertionError('Invalid serialized attributes accepted')

with tempfile.TemporaryDirectory(prefix='attribute-check-') as directory:
    folder=Path(directory);model=folder/'model.rbxmx';binary=folder/'model.rbxm';normalized=folder/'normalized.rbxmx'
    tree=ET.Element('roblox',version='4');node=ET.SubElement(tree,'Item',{'class':'ModuleScript'});props=ET.SubElement(node,'Properties')
    ET.SubElement(props,'string',name='Name').text='AttributeModule'
    ET.SubElement(props,'ProtectedString',name='Source').text="return script:GetAttribute('LightData')"
    attribute=ET.SubElement(props,'BinaryString',name='AttributesSerialize')
    # Whitespace wrapping is common in actual Studio XML serialization.
    attribute.text='\n'+base64.encodebytes(payload).decode()+'\n'
    ET.ElementTree(tree).write(model,encoding='utf-8')
    assert read_model(model)['items'][0]['attributes']==decoded
    # Independent rbx-dom decode/encode exercises compact rotations, sequences,
    # field ordering, float layout and arbitrary binary strings.
    for direction,input_path,output_path in [('to-binary',model,binary),('to-xml',binary,normalized)]:
        subprocess.run([str(root/'recovery-asset-codec.exe'),direction,str(input_path),str(output_path)],check=True)
    normalized_records=read_model(normalized)['items'][0]['attributes']
    assert {r['name']:(r['kind'],r['values']) for r in normalized_records}=={r['name']:(r['kind'],r['values']) for r in decoded}
    driver=folder/'main.luau'
    driver.write_text('''local object=workspace.AttributeModule
assert(require(object)=='harmless-data-only')
local a=object:GetAttributes()
assert(a.Flag and a.Integer==-735 and a.Float==1.25 and a.Double==.125)
assert(a.Dimension==UDim.new(.5,-20) and a.Dimensions==UDim2.new(.5,-20,.25,10))
assert(a.Brick==BrickColor.new(21) and a.Color==Color3.new(.25,.5,.75))
assert(a.V2==Vector2.new(2,3) and a.V3==Vector3.new(2,3,4))
assert(a.Range==NumberRange.new(2,7) and a.Rectangle==Rect.new(1,2,3,4))
assert(a.Matrix:PointToWorldSpace(Vector3.new(1,0,0))==Vector3.new(1,3,3))
assert(a.Rotation3.UpVector==Vector3.new(0,0,1))
assert(a.Numbers.Keypoints[2].Value==2 and a.Numbers.Keypoints[2].Envelope==.25)
assert(a.Colors.Keypoints[1].Value==Color3.new(1,0,0) and a.Colors.Keypoints[2].Value==Color3.new(0,0,1))
assert(#a.Binary==259 and a.Binary:byte(1)==0 and a.Binary:byte(256)==255 and a.Binary:byte(259)==254)
a.LightData='changed copy';assert(object:GetAttribute('LightData')=='harmless-data-only')
local clone=object:Clone();assert(clone:GetAttribute('Binary')==object:GetAttribute('Binary'))
local changed=false;clone:GetAttributeChangedSignal('Integer'):Connect(function()changed=true end)
clone:SetAttribute('Integer',42);task.wait();assert(changed and object:GetAttribute('Integer')==-735)
print('MODEL ATTRIBUTES VM CHECK PASSED')
''',encoding='utf-8')
    for imported in (model,normalized):
        for mode in ('server','client'):
            result=subprocess.run([sys.executable,str(root/'run.py'),str(driver),'--model',str(imported),
                '--mode',mode,*sys.argv[1:]],capture_output=True,text=True,encoding='utf-8',timeout=60)
            assert result.returncode==0 and 'MODEL ATTRIBUTES VM CHECK PASSED' in result.stdout,(result.stdout,result.stderr)
    # SharedString-backed attribute payloads use the same reader.
    attribute.tag='SharedString';attribute.text='test-key'
    shared=ET.SubElement(tree,'SharedStrings');ET.SubElement(shared,'SharedString',md5='test-key').text=base64.encodebytes(payload).decode()
    ET.ElementTree(tree).write(model,encoding='utf-8')
    assert read_model(model)['items'][0]['attributes']==decoded

report={'status':'PASS','attribute_values':len(records),'compact_rotations':24,
    'independent_format_roundtrip':'rbx_binary/rbx_xml 3.0.1','contexts':['server','client'],
    'checks':['primitive/types/sequences/CFrame','binary strings preserve all bytes','wrapped/shared XML payload',
        'XML -> compressed RBXM -> XML','import before ModuleScript execution','Clone/signals','malformed/bounded input'],
    'limits':{'payload_bytes':16*1024*1024,'attribute_count':1024,'sequence_keypoints':20},
    'unsupported':['EnumItem','nonfinite numeric values']}
(root/'evidence/model_attribute_comparison.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('MODEL ATTRIBUTES FORMAT/BINARY/VM CHECKS PASSED')
