"""Nested convex arena, model imports and persistent close callbacks."""
import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from model_xml import read_model


def run(target,binary,*flags,timeout=90):
    result=subprocess.run([sys.executable,str(ROOT/'run.py'),str(target),'--binary',binary,*flags],
        capture_output=True,text=True,encoding='utf-8',timeout=timeout)
    assert result.returncode==0,(result.stdout,result.stderr)
    return result.stdout


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--binary',default='D:/Release-RobloxStudioApp/RobloxStudio.app/Contents/MacOS/RobloxStudio')
    args=parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='convex-engine-') as directory:
        work=Path(directory);project=work/'project';project.mkdir();database=work/'arena.sqlite3'
        bytecode=work/'arena.luauc'
        subprocess.run([str(ROOT/'recovery-luau-compile.exe'),str(ROOT/'examples/projectile_arena.luau'),str(bytecode)],check=True)
        data=bytecode.read_bytes();assert data[0]==9
        shutil.copyfile(ROOT/'tests/vendor/Fiu.luau',project/'Fiu.luau')
        literal='"'+''.join(f'\\{b:03d}' for b in data)+'"'
        (project/'Main.server.luau').write_text("local Fiu=require(script.Parent.Fiu)\nlocal settings=Fiu.luau_newsettings();settings.vectorCtor=Vector3.new;settings.vectorSize=3\nlocal execute,close=Fiu.luau_load("+literal+",getfenv(),settings)\nexecute()\n-- The Fiu interpreter remains live for yielding close callbacks.\n",encoding='utf-8')
        output=run(project,args.binary,'--no-player','--duration','1.2','--data-store',str(database),'--wall-timeout','75')
        assert 'PROJECTILE ARENA SAVED' in output
        reader=work/'reader';reader.mkdir();script=reader/'main.luau'
        script.write_text("""local saved=game:GetService('DataStoreService'):GetDataStore('ProjectileArena'):GetAsync('latest')
assert(saved.actors==32 and saved.ticks==60 and saved.casts>=1920 and saved.collisions>100 and saved.surfaces>=5)
assert(saved.reason=='DeveloperShutdown')
print('NESTED CONVEX ARENA SAVE SURVIVED PROCESS EXIT',saved.collisions)
""",encoding='utf-8')
        assert 'SURVIVED PROCESS EXIT' in run(script,args.binary,'--duration','0','--data-store',str(database))
        model=ET.Element('roblox',version='4')
        scene=ET.SubElement(model,'Item',{'class':'Model'})
        ET.SubElement(ET.SubElement(scene,'Properties'),'string',name='Name').text='ConvexModel'
        for index,(class_name,shape) in enumerate((('Part',0),('Part',2),('WedgePart',None),('CornerWedgePart',None))):
            item=ET.SubElement(scene,'Item',{'class':class_name});properties=ET.SubElement(item,'Properties')
            ET.SubElement(properties,'string',name='Name').text='Shape'+str(index)
            ET.SubElement(properties,'bool',name='Anchored').text='true'
            size=ET.SubElement(properties,'Vector3',name='Size')
            for axis in ('X','Y','Z'):ET.SubElement(size,axis).text='4'
            position=ET.SubElement(properties,'CoordinateFrame',name='CFrame')
            names=('X','Y','Z','R00','R01','R02','R10','R11','R12','R20','R21','R22')
            for axis,value in zip(names,(index*10,0,-10,1,0,0,0,1,0,0,0,1)):ET.SubElement(position,axis).text=str(value)
            if shape is not None:ET.SubElement(properties,'token',name='shape').text=str(shape)
        xml=work/'convex.rbxmx';binary=work/'convex.rbxm';ET.ElementTree(model).write(xml,encoding='utf-8')
        subprocess.run([str(ROOT/'recovery-asset-codec.exe'),'to-binary',str(xml),str(binary)],check=True)
        script.write_text("""local model=workspace.ConvexModel
local params=RaycastParams.new();params.FilterType=Enum.RaycastFilterType.Include;params.FilterDescendantsInstances={model}
for i=0,3 do
    local part=model['Shape'..i]
    assert(workspace:Raycast(part.Position+Vector3.new(0,10,0),Vector3.new(0,-20,0),params).Instance==part)
    assert(workspace:Spherecast(part.Position+Vector3.new(0,10,0),1,Vector3.new(0,-20,0),params).Instance==part)
end
print('IMPORTED CONVEX GEOMETRY PASSED')
""",encoding='utf-8')
        for path in (xml,binary):
            assert read_model(path)['count']==5
            assert 'IMPORTED CONVEX GEOMETRY PASSED' in run(script,args.binary,'--model',str(path),'--duration','.1','--wall-timeout','45')
    print('FIU CONVEX ARENA, MODEL FORMATS AND CROSS-PROCESS SHUTDOWN SAVE PASSED')


if __name__=='__main__':main()
