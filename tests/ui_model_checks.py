"""UI values, references, and script behavior survive XML and RBXM conversion."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from model_xml import read_model
from model_properties import ENUMS,parse_property


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--binary',default='D:/Release-RobloxStudioApp/RobloxStudio.app/Contents/MacOS/RobloxStudio')
    args=parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='ui-model-') as directory:
        folder=Path(directory)
        tree=ET.Element('roblox',version='4')
        def item(parent,kind,name,ref=None):
            node=ET.SubElement(parent,'Item',{'class':kind,**({'referent':ref} if ref else {})})
            ET.SubElement(ET.SubElement(node,'Properties'),'string',name='Name').text=name
            return node
        def prop(node,tag,name,text=None,parts=None):
            value=ET.SubElement(node.find('Properties'),tag,name=name)
            if parts:
                for key,data in parts:ET.SubElement(value,key).text=str(data)
            else:value.text=text
            return value
        gui=item(tree,'ScreenGui','UI')
        prop(gui,'bool','Enabled','true');prop(gui,'bool','IgnoreGuiInset','true')
        # ScreenInsets is the canonical field serialized by the current codec.
        prop(gui,'token','ScreenInsets',str(ENUMS['ScreenInsets']['None']))
        frame=item(gui,'Frame','Panel','panel')
        prop(frame,'UDim2','Size',parts=[('XS',0),('XO',400),('YS',0),('YO',200)])
        prop(frame,'Vector2','AnchorPoint',parts=[('X',0.5),('Y',0.5)])
        button=item(frame,'TextButton','Button','button')
        prop(button,'UDim2','Size',parts=[('XS',0.5),('XO',10),('YS',0),('YO',40)])
        prop(button,'string','Text','Hello from XML')
        prop(button,'Ref','NextSelectionDown','button')
        font=prop(button,'Font','FontFace')
        ET.SubElement(ET.SubElement(font,'Family'),'url').text='rbxasset://fonts/families/Arial.json'
        ET.SubElement(font,'Weight').text='700';ET.SubElement(font,'Style').text='Italic'
        image=item(frame,'ImageLabel','Icon')
        ET.SubElement(prop(image,'Content','Image'),'url').text='rbxassetid://1234'
        rect=prop(image,'Rect2D','SliceCenter')
        for key,coords in [('min',(2,3)),('max',(20,30))]:
            node=ET.SubElement(rect,key)
            for axis,value in zip(('X','Y'),coords):ET.SubElement(node,axis).text=str(value)
        gradient=item(button,'UIGradient','Gradient')
        prop(gradient,'ColorSequence','Color','0 1 0 0 0 1 0 0 1 0')
        prop(gradient,'NumberSequence','Transparency','0 0.1 0 1 0.9 0')
        corner=item(button,'UICorner','Corner');prop(corner,'UDim','CornerRadius',parts=[('S',0),('O',12)])
        for key in ('TopLeftRadius','TopRightRadius','BottomLeftRadius','BottomRightRadius'):
            prop(corner,'UDim',key,parts=[('S',0),('O',12)])
        xml=folder/'ui.rbxmx';rbxm=folder/'ui.rbxm';driver=folder/'main.luau'
        ET.ElementTree(tree).write(xml,encoding='utf-8')
        subprocess.run([str(ROOT/'recovery-asset-codec.exe'),'to-binary',str(xml),str(rbxm)],check=True)
        driver.write_text('''local gui=workspace.UI
assert(gui:IsA('LayerCollector') and gui.Enabled and gui.IgnoreGuiInset)
local p=gui.Panel;local b=p.Button
assert(p.Size==UDim2.fromOffset(400,200) and p.AnchorPoint==Vector2.new(0.5,0.5))
assert(b.Text=='Hello from XML' and b.Size==UDim2.new(0.5,10,0,40))
assert(b.NextSelectionDown==b and b.FontFace.Bold and b.FontFace.Style==Enum.FontStyle.Italic)
assert(p.Icon.Image=='rbxassetid://1234' and p.Icon.SliceCenter==Rect.new(2,3,20,30))
assert(b.Gradient.Color.Keypoints[2].Value==Color3.new(0,0,1))
assert(math.abs(b.Gradient.Transparency.Keypoints[2].Value-0.9)<1e-6)
assert(b.Corner.CornerRadius==UDim.new(0,12))
local clone=gui:Clone();assert(clone.Panel.Button.NextSelectionDown==clone.Panel.Button)
print('UI MODEL IMPORT PASSED')
''',encoding='utf-8')
        for model in (xml,rbxm):
            assert read_model(model)['count']==6
            subprocess.run([sys.executable,str(ROOT/'run.py'),str(driver),'--binary',args.binary,'--model',str(model),'--wall-timeout','30'],check=True)
        # Host-side import errors must be diagnosed before entering the VM.
        for tag,name,text,parts in [('NumberSequence','Transparency','0 0 -1 1 1 0',None),
                                    ('ColorSequence','Color','0.2 1 0 0 0 1 0 1 0 0',None),
                                    ('UDim2','Size',None,[('XS',0),('XO',2)])]:
            field=ET.Element(tag,name=name)
            field.text=text
            for key,value in parts or []:ET.SubElement(field,key).text=str(value)
            try:parse_property('UIGradient' if 'Sequence' in tag else 'Frame',name,field)
            except ValueError:pass
            else:raise AssertionError('Malformed UI property accepted')
    print('UI XML/BINARY/TYPED VALUE/REFERENCE CHECKS PASSED')


if __name__=='__main__':main()
