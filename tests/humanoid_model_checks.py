"""Force-field properties and humanoid behavior after XML/RBXM import."""
import argparse
from pathlib import Path
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from model_xml import read_model


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--binary',default='D:/Release-RobloxStudioApp/RobloxStudio.app/Contents/MacOS/RobloxStudio')
    args=parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='humanoid-model-') as directory:
        work=Path(directory);xml=work/'rig.rbxmx';binary=work/'rig.rbxm';script=work/'main.luau'
        root=ET.Element('roblox',version='4')
        def item(parent,kind,name):
            node=ET.SubElement(parent,'Item',{'class':kind})
            ET.SubElement(ET.SubElement(node,'Properties'),'string',name='Name').text=name
            return node
        scene=item(root,'Model','DamageModel')
        part=item(scene,'Part','HumanoidRootPart')
        ET.SubElement(part.find('Properties'),'bool',name='Anchored').text='true'
        humanoid=item(scene,'Humanoid','Health')
        ET.SubElement(humanoid.find('Properties'),'float',name='MaxHealth').text='250'
        field=item(scene,'ForceField','Protection')
        visible=ET.SubElement(field.find('Properties'),'bool',name='Visible');visible.text='false'
        ET.ElementTree(root).write(xml,encoding='utf-8')
        subprocess.run([str(ROOT/'recovery-asset-codec.exe'),'to-binary',str(xml),str(binary)],check=True)
        script.write_text('''local model=workspace.DamageModel
local h,root,field=model.Health,model.HumanoidRootPart,model.Protection
assert(h.MaxHealth==250 and h.RootPart==root and field.Visible==false and root.Anchored)
h.Health=200;h:TakeDamage(50);assert(h.Health==200)
field.Parent=root;h:TakeDamage(50);assert(h.Health==200)
h.Health=300;assert(h.Health==250)
h.MaxHealth=500;assert(h.Health==300)
local copy=model:Clone()
assert(copy.Health.RootPart==copy.HumanoidRootPart and copy.Health.Health==300)
assert(copy.HumanoidRootPart.Protection.Visible==false)
copy:Destroy();model:Destroy()
print('IMPORTED HUMANOID, FORCE FIELD AND CLONE CHECKS PASSED')
''',encoding='utf-8')
        for model in (xml,binary):
            assert read_model(model)['count']==4
            result=subprocess.run([sys.executable,str(ROOT/'run.py'),str(script),'--model',str(model),
                                   '--binary',args.binary,'--duration','.1','--wall-timeout','30'],
                                  capture_output=True,text=True,encoding='utf-8',timeout=40)
            assert result.returncode==0,(str(model),result.stdout,result.stderr)
        visible.tag='string';visible.text='bad'
        ET.ElementTree(root).write(xml,encoding='utf-8')
        try:read_model(xml)
        except ValueError:pass
        else:raise AssertionError('Invalid force-field boolean accepted')
        misplaced=work/'misplaced.rbxmx'
        misplaced.write_text('<roblox version="4"><Item class="ForceField"><Properties /></Item></roblox>',encoding='utf-8')
        result=subprocess.run([sys.executable,str(ROOT/'run.py'),str(script),'--model',str(misplaced),'--binary',args.binary,'--duration','.1'],
                              capture_output=True,text=True,encoding='utf-8',timeout=30)
        assert result.returncode==1 and 'ForceField cannot be parented to Workspace' in result.stdout+result.stderr,(result.stdout,result.stderr)
        assert 'Traceback (most recent call last)' not in result.stderr
    print('HUMANOID/FORCE FIELD XML, BINARY, CLONE AND VALIDATION CHECKS PASSED')


if __name__=='__main__':main()
