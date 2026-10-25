"""Attachments, animated bones, effect values and references survive XML/RBXM."""
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
    parser.add_argument('--binary',type=Path,default=Path('D:/Release-RobloxStudioApp/RobloxStudio.app/Contents/MacOS/RobloxStudio'))
    args=parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='environment-model-') as folder:
        work=Path(folder);xml=work/'scene.rbxmx';binary=work/'scene.rbxm';script=work/'main.luau'
        root=ET.Element('roblox',version='4')
        def item(parent,kind,name,referent=None):
            node=ET.SubElement(parent,'Item',{'class':kind,**({'referent':referent} if referent else {})})
            ET.SubElement(ET.SubElement(node,'Properties'),'string',name='Name').text=name
            return node
        def prop(node,tag,name,text=None,fields=None):
            value=ET.SubElement(node.find('Properties'),tag,name=name)
            if fields:
                for key,data in fields.items():ET.SubElement(value,key).text=str(data)
            else:value.text=text
            return value
        def frame(node,key,x,y,z):
            prop(node,'CoordinateFrame',key,fields=dict(zip(('X','Y','Z','R00','R01','R02','R10','R11','R12','R20','R21','R22'),(x,y,z,1,0,0,0,1,0,0,0,1))))
        scene=item(root,'Model','Scene');part=item(scene,'Part','Root','part');frame(part,'CFrame',10,0,0)
        beam=item(part,'Beam','Link')
        prop(beam,'Ref','Attachment0','a');prop(beam,'Ref','Attachment1','tip')
        ET.SubElement(prop(beam,'Content','Texture'),'url').text='rbxassetid://1234'
        prop(beam,'NumberSequence','Transparency','0 0.2 1 1 0.8 2 ')
        a=item(part,'Attachment','A','a');frame(a,'CFrame',1,2,3)
        spot=item(a,'SpotLight','Glow');prop(spot,'float','Range','8');prop(spot,'float','Angle','40')
        bone=item(part,'Bone','Bone','bone');frame(bone,'CFrame',0,4,0);frame(bone,'Transform',0,2,0)
        tip=item(bone,'Attachment','Tip','tip');frame(tip,'CFrame',0,1,0)
        particles=item(tip,'ParticleEmitter','FX')
        prop(particles,'NumberRange','Lifetime','1.25 2.5')
        prop(particles,'NumberSequence','Size','0 1 0 1 2 0 ')
        prop(particles,'ColorSequence','Color','0 1 0 0 0 1 0 0 1 0 ')
        prop(particles,'float','Rate','30')
        trail=item(part,'Trail','Path');prop(trail,'Ref','Attachment0','a');prop(trail,'Ref','Attachment1','tip')
        rope=item(part,'RopeConstraint','Rope');prop(rope,'Ref','Attachment0','a');prop(rope,'Ref','Attachment1','tip')
        camera=item(scene,'Camera','Camera');bloom=item(camera,'BloomEffect','Bloom');prop(bloom,'float','Intensity','2')
        atmosphere=item(scene,'Atmosphere','Air');prop(atmosphere,'float','Density','0.5')
        ET.ElementTree(root).write(xml,encoding='utf-8')
        subprocess.run([str(ROOT/'recovery-asset-codec.exe'),'to-binary',str(xml),str(binary)],check=True)
        script.write_text('''local s=workspace.Scene;local p=s.Root
assert((p.A.WorldPosition-Vector3.new(11,2,3)).Magnitude<1e-7)
assert((p.Bone.WorldPosition-Vector3.new(10,4,0)).Magnitude<1e-7)
-- Transform is intentionally not saved by the binary codec.
assert((p.Bone.Tip.WorldPosition-Vector3.new(10,TIPY,0)).Magnitude<1e-7)
assert(p.Link.Attachment0==p.A and p.Link.Attachment1==p.Bone.Tip)
assert(p.Path.Attachment0==p.A and p.Rope.Attachment1==p.Bone.Tip)
assert(table.find(p.A:GetConstraints(),p.Rope))
assert(p.Link.Texture=='rbxassetid://1234' and p.Link.Transparency.Keypoints[1].Envelope==0)
assert(p.A.Glow.Range==8 and p.A.Glow.Angle==40)
assert(p.Bone.Tip.FX.Lifetime==NumberRange.new(1.25,2.5))
assert(p.Bone.Tip.FX.Size.Keypoints[2].Value==2 and p.Bone.Tip.FX.Color.Keypoints[1].Value==Color3.new(1,0,0))
assert(s.Camera.Bloom.Intensity==2 and s.Air.Density==0.5)
local copy=s:Clone()
assert(copy.Root.Link.Attachment0==copy.Root.A and copy.Root.Rope.Attachment1==copy.Root.Bone.Tip)
assert(copy.Root.Link.Attachment0~=p.A)
print('ENVIRONMENT XML/BINARY REFERENCES AND VALUES PASSED')
''',encoding='utf-8')
        source=script.read_text()
        for model in [xml,binary]:
            assert read_model(model)['count']>=12
            script.write_text(source.replace('TIPY','7' if model==xml else '5'),encoding='utf-8')
            result=subprocess.run([sys.executable,str(ROOT/'run.py'),str(script),'--model',str(model),'--binary',str(args.binary),'--duration','0.1','--wall-timeout','30'],
                                  capture_output=True,text=True,encoding='utf-8',timeout=40)
            assert result.returncode==0,(str(model),result.stdout,result.stderr)
        for value in ['2 1','1','NaN 2','0 1 2']:
            particles.find("Properties/NumberRange").text=value
            ET.ElementTree(root).write(xml,encoding='utf-8')
            try:read_model(xml)
            except ValueError:pass
            else:raise AssertionError('Invalid NumberRange accepted')
        particles.find("Properties/NumberRange").text='1 2'
        beam.find("Properties/Ref[@name='Attachment0']").text='part'
        ET.ElementTree(root).write(xml,encoding='utf-8')
        try:read_model(xml)
        except ValueError:pass
        else:raise AssertionError('Invalid Attachment reference accepted')
    print('ENVIRONMENT MODEL XML/RBXM, FORWARD REFERENCES, CLONE AND INVALID INPUT CHECKS PASSED')


if __name__=='__main__':main()
