"""Recovered builtin font rows plus independently encoded Font attribute fixtures."""
import argparse,base64,hashlib,json,struct,subprocess,sys,tempfile
from pathlib import Path
import xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from model_attributes import decode_attributes
from model_xml import read_model
from run import lua_literal
p=argparse.ArgumentParser();p.add_argument('--binary',type=Path,default=Path('D:/Release-RobloxStudioApp/RobloxStudio.app/Contents/MacOS/RobloxStudio'));args=p.parse_args()
def string(value):
    value=value.encode('utf-8');return struct.pack('<I',len(value))+value
def entry(name,weight,style,family,cached=''):
    return string(name)+b'\x21'+struct.pack('<HB',weight,style)+string(family)+string(cached)
fonts=json.loads((root/'data/font_recovery.json').read_text())['enum_fonts']
assert len(fonts)==52
rows=[('ImportedFont',700,1,'rbxasset://fonts/families/Arial.json','rbxasset://fonts/Arial-Bold.ttf'),
      ('FallbackFont',123,17,'rbxassetid://11702779409',''),('UnicodeFont',100,0,'rbxassetid://шрифт','cached'),
      ('UI/fonts.Main-1',500,0,'rbxassetid://123','')]
payload=struct.pack('<I',len(rows))+b''.join(entry(*row) for row in rows)
decoded=decode_attributes(payload)
assert decoded[1]['values'][1:3]==[400,0]
bad_utf8=struct.pack('<I',1)+string('Bad')+b'\x21'+struct.pack('<HB',400,0)+struct.pack('<I',1)+b'\xff'+string('')
for bad in (payload[:-1],payload+b'x',bad_utf8):
    try:decode_attributes(bad)
    except ValueError:pass
    else:raise AssertionError('Invalid font attribute accepted')
with tempfile.TemporaryDirectory(prefix='font-check-') as directory:
    folder=Path(directory);model=folder/'fonts.rbxmx';binary=folder/'fonts.rbxm';normalized=folder/'normalized.rbxmx';driver=folder/'main.luau'
    # Unknown enum numbers have a reader fallback; use normalized records for
    # independent rbx-dom roundtrips, which validate enum values on write.
    stable=[rows[0],('FallbackFont',400,0,rows[1][3],''),*rows[2:]]
    stable_payload=struct.pack('<I',len(stable))+b''.join(entry(*row) for row in stable)
    tree=ET.Element('roblox',version='4');node=ET.SubElement(tree,'Item',{'class':'Folder'});props=ET.SubElement(node,'Properties')
    ET.SubElement(props,'string',name='Name').text='FontModel'
    ET.SubElement(props,'BinaryString',name='AttributesSerialize').text=base64.b64encode(stable_payload).decode()
    ET.ElementTree(tree).write(model,encoding='utf-8')
    for direction,a,b in [('to-binary',model,binary),('to-xml',binary,normalized)]:
        subprocess.run([str(root/'recovery-asset-codec.exe'),direction,str(a),str(b)],check=True)
    def by_name(path):return {row['name']:(row['kind'],row['values']) for row in read_model(path)['items'][0]['attributes']}
    assert by_name(model)==by_name(normalized)
    program='local catalog='+lua_literal(fonts)+'''\nfor name,row in catalog do
local f=Font.fromEnum(Enum.Font[name]);assert(f.Family==row.family and f.Weight.Value==row.weight and f.Style.Value==row.style)
f.Bold=not f.Bold;assert(Font.fromEnum(Enum.Font[name]).Weight.Value==row.weight)
end
local object=workspace.FontModel;local font=object:GetAttribute('ImportedFont')
assert(typeof(font)=='Font' and font.Weight==Enum.FontWeight.Bold and font.Style==Enum.FontStyle.Italic)
font.Bold=false;assert(object:GetAttribute('ImportedFont').Bold)
local clone=object:Clone();local c=clone:GetAttribute('ImportedFont');c.Family='modified';clone:SetAttribute('ImportedFont',c)
assert(object:GetAttribute('ImportedFont').Family=='rbxasset://fonts/families/Arial.json')
assert(clone:GetAttribute('ImportedFont').Family=='modified')
assert(object:GetAttribute('UnicodeFont').Family=='rbxassetid://шрифт')
assert(object:GetAttribute('FallbackFont')==Font.new('rbxassetid://11702779409'))
assert(object:GetAttribute('UI/fonts.Main-1').Weight==Enum.FontWeight.Medium)
print('FONT CATALOG AND MODEL CHECK PASSED')
'''
    driver.write_text(program,encoding='utf-8')
    for imported in (model,binary,normalized):
        for mode in ('server','client'):
            result=subprocess.run([sys.executable,str(root/'run.py'),str(driver),'--binary',str(args.binary),'--model',str(imported),'--mode',mode],capture_output=True,text=True,encoding='utf-8',timeout=60)
            assert result.returncode==0 and 'FONT CATALOG AND MODEL CHECK PASSED' in result.stdout,(mode,str(imported),result.stdout,result.stderr)
report={'status':'PASS','builtin_rows':52,'formats':['XML','compressed RBXM','normalized XML'], 'contexts':['server','client'],
    'checks':['recovered builtin family/weight/style rows','Font attribute byte layout','cached face bytes survive independent codec roundtrip','reader enum fallback','UTF-8 family','attribute and clone copy isolation','malformed input'],
    'limits':['font metadata only; no glyph rendering or downloading','constructor fromId follows native 0.735 int32 bridge','ContentId normalization beyond slash/NUL not exhaustively compared','not a dynamic native Font oracle']}
(root/'data/font_comparison.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('FONT CATALOG/MODEL CHECKS PASSED')
