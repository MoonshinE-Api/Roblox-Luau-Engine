"""Typed Team/Player imports, binary round trips and local membership behavior."""
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
    with tempfile.TemporaryDirectory(prefix='team-model-') as directory:
        work=Path(directory);xml=work/'teams.rbxmx';binary=work/'teams.rbxm';script=work/'main.luau'
        root=ET.Element('roblox',version='4')
        def item(parent,kind,name):
            node=ET.SubElement(parent,'Item',{'class':kind})
            properties=ET.SubElement(node,'Properties')
            ET.SubElement(properties,'string',name='Name').text=name
            return node,properties
        scene,_=item(root,'Model','TeamFixture')
        red,properties=item(scene,'Team','Red')
        ET.SubElement(properties,'int',name='TeamColor').text='21'
        assign=ET.SubElement(properties,'bool',name='AutoAssignable');assign.text='false'
        ET.SubElement(properties,'int',name='Score').text='27'
        ET.SubElement(properties,'bool',name='AutoColorCharacters').text='false'
        _,properties=item(scene,'Team','Blue')
        ET.SubElement(properties,'int',name='TeamColor').text='23'
        ET.SubElement(properties,'bool',name='AutoAssignable').text='false'
        _,properties=item(scene,'Player','LocalRecord')
        ET.SubElement(properties,'int',name='TeamColor').text='21'
        ET.SubElement(properties,'bool',name='Neutral').text='false'
        ET.SubElement(properties,'int64',name='UserId').text='735123'
        ET.SubElement(properties,'string',name='DisplayName').text='Imported record'
        ET.ElementTree(root).write(xml,encoding='utf-8')
        subprocess.run([str(ROOT/'recovery-asset-codec.exe'),'to-binary',str(xml),str(binary)],check=True)
        source='''local fixture=workspace.TeamFixture
local red,blue,player=fixture.Red,fixture.Blue,fixture.LocalRecord
assert(red.TeamColor==BrickColor.new(21) and red.Score==SCORE and red.AutoColorCharacters==AUTO_COLOR)
assert(not red.AutoAssignable and not blue.AutoAssignable)
assert(player.UserId==USER_ID and player.DisplayName==DISPLAY_NAME and not player.Neutral)
local teams,players=game:GetService('Teams'),game:GetService('Players')
assert(not pcall(function() red:GetPlayers() end))
red.Parent=teams;blue.Parent=teams;player.Parent=players
assert(player.Team==red and #red:GetPlayers()==1)
player.Team=blue;assert(player.TeamColor==BrickColor.new(23) and #blue:GetPlayers()==1)
local copied=red:Clone();assert(copied.Score==SCORE and not copied.AutoAssignable);copied:Destroy()
player:Destroy();red:Destroy();blue:Destroy();fixture:Destroy()
print('IMPORTED TEAM AND PLAYER MEMBERSHIP CHECKS PASSED')
'''
        for model in (xml,binary):
            # These fields are DoesNotSerialize in Roblox reflection metadata.
            # XML can supply them explicitly; RBXM serialization omits them.
            values=('27','false','735123',"'Imported record'") if model==xml else ('0','true','0',"''")
            text=source
            for key,value in zip(('SCORE','AUTO_COLOR','USER_ID','DISPLAY_NAME'),values):text=text.replace(key,value)
            script.write_text(text,encoding='utf-8')
            assert read_model(model)['count']==4
            result=subprocess.run([sys.executable,str(ROOT/'run.py'),str(script),'--model',str(model),
                '--binary',args.binary,'--duration','.1','--wall-timeout','30'],
                capture_output=True,text=True,encoding='utf-8',timeout=40)
            assert result.returncode==0,(str(model),result.stdout,result.stderr)
        assign.tag='string';assign.text='bad'
        ET.ElementTree(root).write(xml,encoding='utf-8')
        try:read_model(xml)
        except ValueError:pass
        else:raise AssertionError('Invalid team boolean accepted')
    print('TEAM/PLAYER XML, BINARY, CLONE AND VALIDATION CHECKS PASSED')


if __name__=='__main__':main()
