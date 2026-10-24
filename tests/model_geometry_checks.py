"""Real XML/binary imports, forward references, source labels and asset delivery."""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import xml.etree.ElementTree as ET

root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from model_xml import read_model
from model_properties import ENUMS,SCHEMA

def item(parent,kind,name,referent=None):
    options={'class':kind}
    if referent:options['referent']=referent
    node=ET.SubElement(parent,'Item',options);prop(node,'string','Name',name);return node
def prop(node,tag,name,value=None,components=None):
    properties=node.find('Properties')
    if properties is None:properties=ET.SubElement(node,'Properties')
    field=ET.SubElement(properties,tag,name=name)
    if components:
        for key,value in components.items():ET.SubElement(field,key).text=str(value)
    elif value is not None:field.text=str(value)
    return field
def cf(x,y,z,rotate=False):
    return dict(zip(('X','Y','Z','R00','R01','R02','R10','R11','R12','R20','R21','R22'),
                    (x,y,z,0,-1,0,1,0,0,0,0,1) if rotate else (x,y,z,1,0,0,0,1,0,0,0,1)))

with tempfile.TemporaryDirectory(prefix='model-geometry-') as directory:
    folder=Path(directory);model=folder/'geometry.rbxmx';binary=folder/'geometry.rbxm';main=folder/'main.luau'
    tree=ET.Element('roblox',version='4');arena=item(tree,'Model','Arena','arena')
    prop(arena,'Ref','PrimaryPart','primary')
    target=item(arena,'ObjectValue','Target','target');prop(target,'Ref','Value','other')
    cyclic=item(arena,'ObjectValue','Self','cyclic');prop(cyclic,'Ref','Value','cyclic')
    camera=item(arena,'Camera','Camera');prop(camera,'Ref','CameraSubject','primary')
    prop(camera,'float','FieldOfView',80);prop(camera,'CoordinateFrame','Focus',components=cf(0,3,0))
    primary=item(arena,'Part','Root','primary');prop(primary,'bool','Anchored','true')
    prop(primary,'CoordinateFrame','CFrame',components=cf(10,2,0,True))
    prop(primary,'CoordinateFrame','PivotOffset',components=cf(0,.5,0))
    prop(primary,'Vector3','size',components={'X':2,'Y':4,'Z':6})
    prop(primary,'Color3uint8','Color3uint8',0x123456)
    prop(primary,'token','Material',ENUMS['Material']['Metal'])
    prop(primary,'token','shape',ENUMS['PartType']['Block'])
    other=item(arena,'Part','Other','other');prop(other,'bool','Anchored','true')
    prop(other,'CoordinateFrame','CFrame',components=cf(14,4,0))
    prop(other,'Vector3','Size',components={'X':2,'Y':2,'Z':2})
    configuration=item(arena,'Configuration','Settings')
    for kind,name,tag,value in [('BoolValue','Flag','bool','true'),('NumberValue','Number','double','1.25'),
        ('IntValue','Integer','int64','735'),('StringValue','Text','string','hello, model')]:
        prop(item(configuration,kind,name),tag,'Value',value)
    prop(item(configuration,'Vector3Value','Vector'),'Vector3','Value',components={'X':1,'Y':2,'Z':3})
    prop(item(configuration,'CFrameValue','Frame'),'CoordinateFrame','Value',components=cf(3,4,5))
    prop(item(configuration,'Color3Value','Color'),'Color3','Value',components={'R':.25,'G':.5,'B':.75})
    prop(item(configuration,'BrickColorValue','Brick'),'int','Value',21)
    item(configuration,'BindableEvent','Event')
    source=item(arena,'Script','AutoServer');prop(source,'ProtectedString','Source',"assert(script.Parent.PrimaryPart==script.Parent.Root);script.Parent:SetAttribute('AutoServer',true)")
    humanoid=item(arena,'Humanoid','Bot');prop(humanoid,'float','Health',75);prop(humanoid,'float','WalkSpeed',12)
    source=item(tree,'ModuleScript','MainModule');prop(source,'ProtectedString','Source',"local a=script.Parent.Arena;assert(a.Target.Value==a.Other and a.PrimaryPart==a.Root);return a")
    ET.ElementTree(tree).write(model,encoding='utf-8')
    subprocess.run([str(root/'recovery-asset-codec.exe'),'to-binary',str(model),str(binary)],check=True)
    for imported in (model,binary):
        parsed=read_model(imported)
        assert parsed['path']==imported and parsed['count']>=18
        assert parsed['items'][0]['typed_properties'][0]['values']==parsed['items'][0]['children'][3]['id']
    script='''local a=workspace.Arena
assert(a.PrimaryPart==a.Root and a.Target.Value==a.Other and a.Self.Value==a.Self)
assert(a.Camera.CameraSubject==a.Root and a.Camera.FieldOfView==80)
assert(a.Bot.Health==BOT_HEALTH and a.Bot.WalkSpeed==12,'Humanoid values: '..a.Bot.Health..'/'..a.Bot.WalkSpeed)
assert(a.Root.Anchored and a.Root.Size==Vector3.new(2,4,6) and a.Root.Material==Enum.Material.Metal)
assert(a.Root.Shape==Enum.PartType.Block and a.Root.Color==Color3.fromRGB(0x12,0x34,0x56))
local settings=a.Settings
assert(settings.Flag.Value and settings.Number.Value==1.25 and settings.Integer.Value==735 and settings.Text.Value=='hello, model')
assert(settings.Vector.Value==Vector3.new(1,2,3) and settings.Frame.Value.Position==Vector3.new(3,4,5))
assert(settings.Color.Value==Color3.new(.25,.5,.75) and settings.Brick.Value==BrickColor.new(21))
assert(require(workspace.MainModule)==a)
assert(a:GetAttribute('AutoServer')==AUTO)
local center,size=a:GetBoundingBox()
assert((center.Position-Vector3.new(11.5,3,0)).Magnitude<1e-5)
assert((size-Vector3.new(4,7,6)).Magnitude<1e-5 and a:GetExtentsSize()==size)
assert(a:GetPivot()==a.Root:GetPivot() and a:GetPivot().Position==Vector3.new(9.5,2,0))
local cloned=a:Clone();cloned.Parent=workspace
assert(cloned.PrimaryPart==cloned.Root and cloned.Target.Value==cloned.Other and cloned.Self.Value==cloned.Self)
cloned:PivotTo(CFrame.new(100,20,0));assert((cloned:GetPivot().Position-Vector3.new(100,20,0)).Magnitude<1e-5)
assert(a.Root.Position==Vector3.new(10,2,0))
local ray=workspace:Raycast(Vector3.new(10,2,20),Vector3.new(0,0,-40))
assert(ray and ray.Instance==a.Root and math.abs(ray.Position.Z-3)<1e-5)
print('MODEL GEOMETRY AND REFERENCE IMPORT PASSED')
'''
    for imported in (model,binary):
        for mode in ('server','client'):
            # Health can_load=true/can_save=false in the Roblox contract: the
            # XML field loads, but saving binary deliberately drops it.
            main.write_text(script.replace('AUTO','true' if mode=='server' else 'nil').replace('BOT_HEALTH','75' if imported==model else '100'),encoding='utf-8')
            result=subprocess.run([sys.executable,str(root/'run.py'),str(main),'--model',str(imported),'--mode',mode,*sys.argv[1:]],
                capture_output=True,text=True,encoding='utf-8',timeout=60)
            assert result.returncode==0 and 'MODEL GEOMETRY AND REFERENCE IMPORT PASSED' in result.stdout,(str(imported),mode,result.stdout,result.stderr)
    # XML reference strings are scoped to each --model file, even if repeated.
    second=folder/'second.rbxmx'
    second.write_text('<roblox version="4"><Item class="Model"><Properties><string name="Name">Arena2</string><Ref name="PrimaryPart">primary</Ref></Properties><Item class="Part" referent="primary"><Properties><string name="Name">Root</string></Properties></Item></Item></roblox>',encoding='utf-8')
    main.write_text("assert(workspace.Arena.PrimaryPart==workspace.Arena.Root);assert(workspace.Arena2.PrimaryPart==workspace.Arena2.Root);assert(workspace.Arena.Root~=workspace.Arena2.Root);print('MODEL REFERENCE NAMESPACES PASSED')",encoding='utf-8')
    result=subprocess.run([sys.executable,str(root/'run.py'),str(main),'--model',str(binary),'--model',str(second),*sys.argv[1:]],capture_output=True,text=True,encoding='utf-8',timeout=60)
    assert result.returncode==0 and 'MODEL REFERENCE NAMESPACES PASSED' in result.stdout,(result.stdout,result.stderr)
    # Asset download passes exactly the same data through JSON and compilation.
    content=binary.read_bytes()
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_GET(self):
            self.send_response(200);self.send_header('Content-Length',str(len(content)));self.end_headers();self.wfile.write(content)
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        main.write_text('''local a=require(909)
assert(a.PrimaryPart==a.Root and a.Target.Value==a.Other and a.Self.Value==a.Self)
assert(a:GetAttribute('AutoServer')==nil,'Loaded Script should stay dormant')
local model=game:GetService('InsertService'):LoadAsset(909)
assert(model.Arena.PrimaryPart==model.Arena.Root and model.Arena.Root~=a.Root)
assert(require(model.MainModule)==model.Arena)
model.Parent=workspace
assert(model.Arena.Root.Material==Enum.Material.Metal)
local objects=game:GetObjects('rbxassetid://909');assert(#objects==2)
assert(objects[1].PrimaryPart==objects[1].Root and objects[1].Target.Value==objects[1].Other)
print('BINARY ASSET GEOMETRY AND REFERENCES PASSED')
''',encoding='utf-8')
        launcher='import sys;sys.path.insert(0,'+repr(str(root))+');import asset_delivery;asset_delivery.configured=lambda:(None,"fixture");import assets;assets.ASSET_BASE_URL='+repr(f'http://127.0.0.1:{server.server_port}/asset/')+';import run;sys.argv=["run.py",*sys.argv[1:]];run.main()'
        result=subprocess.run([sys.executable,'-c',launcher,str(main),*sys.argv[1:]],capture_output=True,text=True,encoding='utf-8',timeout=60)
        assert result.returncode==0 and 'BINARY ASSET GEOMETRY AND REFERENCES PASSED' in result.stdout,(result.stdout,result.stderr)
    finally:server.shutdown();server.server_close()
    for invalid in [
        '<Item class="Model"><Properties><Ref name="PrimaryPart">missing</Ref></Properties></Item>',
        '<Item class="Part" referent="same"/><Item class="Folder" referent="same"/>',
        '<Item class="Model"><Properties><Ref name="PrimaryPart">folder</Ref></Properties><Item class="Folder" referent="folder"/></Item>',
        '<Item class="Part"><Properties><token name="Material">999999</token></Properties></Item>',
        '<Item class="Part"><Properties><double name="Transparency">NaN</double></Properties></Item>',
        '<Item class="Part"><Properties><Vector3 name="Size"><X>1</X></Vector3></Properties></Item>',
        '<Item class="Part"><Properties><bool name="Anchored">no</bool></Properties></Item>',
        '<Item class="Part"><Properties><string name="MeshId">external</string></Properties></Item>'
    ]:
        model.write_text('<roblox version="4">'+invalid+'</roblox>',encoding='utf-8')
        try:read_model(model)
        except ValueError:pass
        else:raise AssertionError('Invalid model accepted')
    # Binary model source labels must point to the original file, not temp XML.
    tree=ET.Element('roblox',version='4');bad=item(tree,'ModuleScript','Bad');prop(bad,'ProtectedString','Source','local a=1\nerror("BINARY_MODEL_LOCATION")')
    ET.ElementTree(tree).write(model,encoding='utf-8')
    subprocess.run([str(root/'recovery-asset-codec.exe'),'to-binary',str(model),str(binary)],check=True)
    main.write_text('require(workspace.Bad)',encoding='utf-8')
    result=subprocess.run([sys.executable,str(root/'run.py'),str(main),'--model',str(binary),*sys.argv[1:]],capture_output=True,text=True,encoding='utf-8',timeout=60)
    assert result.returncode==1 and 'geometry.rbxm::/Bad:2' in result.stdout+result.stderr,(result.stdout,result.stderr)

report={'status':'PASS','classes':len(SCHEMA),'observed_property_declarations':sum(len(x) for x in SCHEMA.values()),
    'checks':['XML and compressed RBXM CLI import','forward/self/cross-root refs','PrimaryPart/ObjectValue/CameraSubject',
        'Part transforms/size/color/enums','ValueBase typed values','server/client startup after reference binding',
        'Model bounds/Clone/PivotTo/raycast','binary require/LoadAsset/GetObjects references','invalid inputs and original binary source labels'],
    'limits':'Explicit runtime schema; unsupported classes/properties still fail, no full place/mesh/physics simulation'}
(root/'evidence/model_geometry_comparison.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('MODEL GEOMETRY/REFERENCES/BINARY/ASSET CHECKS PASSED')
