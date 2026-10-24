"""PhysicalProperties and MaterialVariant survive XML / binary model import."""
import argparse,json,subprocess,sys,tempfile
from pathlib import Path
import xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from model_xml import read_model
from model_properties import ENUMS,SCHEMA
p=argparse.ArgumentParser();p.add_argument('--binary',type=Path,default=Path('D:/Release-RobloxStudioApp/RobloxStudio.app/Contents/MacOS/RobloxStudio'));args=p.parse_args()

def item(parent,kind,name):
    node=ET.SubElement(parent,'Item',{'class':kind});ET.SubElement(ET.SubElement(node,'Properties'),'string',name='Name').text=name;return node
def prop(node,tag,name,text=None):
    field=ET.SubElement(node.find('Properties'),tag,name=name)
    if text is not None:field.text=str(text)
    return field
def physical(node,density,legacy=False):
    field=prop(node,'PhysicalProperties','CustomPhysicalProperties')
    values=[('CustomPhysics','true'),('Density',density),('Friction',.5),('Elasticity',.25),('FrictionWeight',2),('ElasticityWeight',3)]
    if not legacy:values.append(('AcousticAbsorption',.125))
    for key,value in values:ET.SubElement(field,key).text=str(value)
    return field

with tempfile.TemporaryDirectory(prefix='physical-model-') as directory:
    folder=Path(directory);model=folder/'physical.rbxmx';binary=folder/'physical.rbxm';driver=folder/'main.luau'
    tree=ET.Element('roblox',version='4');group=item(tree,'Folder','PhysicalModel')
    body=item(group,'Part','Body');prop(body,'bool','Anchored','true')
    size=prop(body,'Vector3','size')
    for key,value in zip(('X','Y','Z'),(2,4,6)):ET.SubElement(size,key).text=str(value)
    physical(body,5)
    legacy=item(group,'Part','Legacy');physical(legacy,2,True)
    default=item(group,'Part','Default')
    ET.SubElement(prop(default,'PhysicalProperties','CustomPhysicalProperties'),'CustomPhysics').text='false'
    variant=item(group,'MaterialVariant','ImportedMetal');prop(variant,'token','BaseMaterial',ENUMS['Material']['Metal']);physical(variant,4)
    for kind in ('WedgePart','CornerWedgePart'):
        wedge=item(group,kind,kind);physical(wedge,3)
        size=prop(wedge,'Vector3','Size')
        for key,value in zip(('X','Y','Z'),(2,4,6)):ET.SubElement(size,key).text=str(value)
    ET.ElementTree(tree).write(model,encoding='utf-8')
    subprocess.run([str(root/'recovery-asset-codec.exe'),'to-binary',str(model),str(binary)],check=True)
    driver.write_text('''local model=workspace.PhysicalModel;local p=model.Body
assert(p.CustomPhysicalProperties.Density==5 and p.CustomPhysicalProperties.AcousticAbsorption==.125 and p:GetMass()==240)
assert(model.Legacy.CustomPhysicalProperties.AcousticAbsorption==1)
assert(model.Default.CustomPhysicalProperties==nil)
assert(model.WedgePart:IsA('BasePart') and math.abs(model.WedgePart:GetMass()-72)<1e-5)
assert(model.CornerWedgePart:IsA('BasePart') and math.abs(model.CornerWedgePart:GetMass()-48)<1e-5)
local variant=model.ImportedMetal;assert(variant.BaseMaterial==Enum.Material.Metal and variant.CustomPhysicalProperties.Density==4)
variant.Parent=game:GetService('MaterialService')
p.CustomPhysicalProperties=nil;p.Material=Enum.Material.Metal;p.MaterialVariant=variant.Name
assert(p:GetMass()==192 and p.CurrentPhysicalProperties==variant.CustomPhysicalProperties)
local clone=p:Clone();assert(clone.MaterialVariant==variant.Name and clone.CustomPhysicalProperties==nil and clone.Mass==192)
clone:Destroy();variant:Destroy();model:Destroy()
print('PHYSICAL MODEL IMPORT CHECK PASSED')
''',encoding='utf-8')
    for imported in (model,binary):
        assert read_model(imported)['count']==7
        for mode in ('server','client'):
            result=subprocess.run([sys.executable,str(root/'run.py'),str(driver),'--binary',str(args.binary),'--model',str(imported),'--mode',mode],
                capture_output=True,text=True,encoding='utf-8',timeout=60)
            assert result.returncode==0 and 'PHYSICAL MODEL IMPORT CHECK PASSED' in result.stdout,(str(imported),mode,result.stdout,result.stderr)
    bad='<roblox version="4"><Item class="Part"><Properties><PhysicalProperties name="CustomPhysicalProperties"><CustomPhysics>wrong</CustomPhysics></PhysicalProperties></Properties></Item></roblox>'
    model.write_text(bad,encoding='utf-8')
    try:read_model(model)
    except ValueError:pass
    else:raise AssertionError('Invalid physical XML accepted')
result={'status':'PASS','formats':['XML','compressed RBXM'],'contexts':['server','client'],
        'classes':len(SCHEMA),'property_declarations':sum(len(row) for row in SCHEMA.values()),
        'checks':['six-field properties','legacy five-field properties/default absorption','null/default properties',
            'MaterialVariant enum and physical data','Wedge and CornerWedge','Clone and dynamic mass/variant lookup','invalid XML']}
(root/'evidence/physical_model_comparison.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('PHYSICAL MODEL XML/BINARY CHECKS PASSED')
