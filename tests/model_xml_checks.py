"""XML script trees, contexts, disabled scripts, source labels and optional vLua."""
import argparse
import base64
import hashlib
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import xml.etree.ElementTree as ET

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from run import lua_literal
from model_xml import read_model

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--binary',type=Path,default=Path('D:/Release-RobloxStudioApp/RobloxStudio.app/Contents/MacOS/RobloxStudio'))
parser.add_argument('--user-model',type=Path)
args=parser.parse_args()

def prop(item,tag,name,value):
    properties=item.find('Properties')
    if properties is None:properties=ET.SubElement(item,'Properties')
    ET.SubElement(properties,tag,name=name).text=value

def item(parent,kind,name,source=None):
    node=ET.SubElement(parent,'Item',{'class':kind})
    prop(node,'string','Name',name)
    if source is not None:prop(node,'ProtectedString','Source',source)
    return node

with tempfile.TemporaryDirectory(prefix='xml-model-test-') as directory:
    folder=Path(directory);model=folder/'model.rbxmx';main=folder/'main.luau'
    tree=ET.Element('roblox',version='4')
    calculator=item(tree,'ModuleScript','XMLCalc','local n=require(script.Values);return function(x) return x+n end')
    prop(calculator,'BinaryString','Tags',base64.b64encode(b'xml-tag\0').decode())
    item(calculator,'ModuleScript','Values','return 37')
    item(tree,'Script','AutoServer','assert(game:GetService("RunService"):IsServer());workspace:SetAttribute("XMLServer",true)')
    item(tree,'LocalScript','AutoClient','assert(game:GetService("RunService"):IsClient());workspace:SetAttribute("XMLClient",true)')
    client=item(tree,'Script','ClientContext','assert(game:GetService("RunService"):IsClient());workspace:SetAttribute("XMLClientContext",true)')
    prop(client,'token','RunContext','2')
    disabled=item(tree,'Script','Disabled','error("Disabled XML Script ran")')
    prop(disabled,'bool','Disabled','true')
    disabled=item(tree,'Script','NotEnabled','error("NotEnabled XML Script ran")')
    prop(disabled,'bool','Enabled','false')
    ET.ElementTree(tree).write(model,encoding='utf-8')
    def run(mode='both',extra=()):
        return subprocess.run([sys.executable,str(root/'run.py'),str(main),'--model',str(model),
            '--binary',str(args.binary),'--mode',mode,'--duration','.5',*extra],capture_output=True,text=True,encoding='utf-8',timeout=60)
    for mode in ('server','client','both'):
        main.write_text('''assert(require(workspace.XMLCalc)(5)==42)
assert(workspace.XMLCalc:HasTag('xml-tag'))
assert(workspace:GetAttribute('XMLServer')=='''+('nil' if mode=='client' else 'true')+''')
assert(workspace:GetAttribute('XMLClient')=='''+('nil' if mode=='server' else 'true')+''')
assert(workspace:GetAttribute('XMLClientContext')=='''+('nil' if mode=='server' else 'true')+''')
print('XML TREE/CONTEXT CHECK PASSED')''',encoding='utf-8')
        result=run(mode)
        assert result.returncode==0 and 'XML TREE/CONTEXT CHECK PASSED' in result.stdout,(mode,result.stdout,result.stderr)
    # Invalid format/unsupported behavior must fail before opening the native VM.
    for invalid in ('<broken', '<roblox version="4"><Item class="MeshPart"/></roblox>',
            '<!DOCTYPE roblox><roblox version="4"/>',
            '<roblox version="4"><Item class="ModuleScript"><Properties><BinaryString name="AttributesSerialize">AAAA</BinaryString></Properties></Item></roblox>'):
        model.write_text(invalid,encoding='utf-8');result=run()
        assert result.returncode==2 and 'Traceback' not in result.stderr,(result.stdout,result.stderr)
    tree=ET.Element('roblox',version='4')
    item(tree,'Script','Bad','local a=1\nlocal b=2\nerror("XML_LOCATION")')
    ET.ElementTree(tree).write(model,encoding='utf-8')
    main.write_text('print("XML source location test")',encoding='utf-8')
    result=run();output=result.stdout+result.stderr
    assert result.returncode==1 and 'model.rbxmx::/Bad:3' in output and 'Traceback' not in output,output
    print('XML SCRIPT TREE, CONTEXT, ERRORS AND SOURCE LABEL CHECKS PASSED')

    if args.user_model:
        original=args.user_model.read_bytes();digest=hashlib.sha256(original).hexdigest()
        record=read_model(args.user_model)
        # Copy only into a disposable test directory; never modify the source.
        model.write_bytes(original)
        driver=(root/'examples/xml_loadstring.luau').read_text(encoding='utf-8')
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def do_GET(self):
                body=b'hello, chatgpt'
                self.send_response(200);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        threading.Thread(target=server.serve_forever,daemon=True).start()
        try:
            outputs=[]
            for mode in ('server','client'):
                main.write_text(driver,encoding='utf-8')
                result=run(mode);output=result.stdout+result.stderr
                assert result.returncode==0 and 'XML COMPILER AND LUA 5.1 VM ENGINE CHECK PASSED' in output,output
                outputs.append({'mode':mode,'stdout':result.stdout.strip()})
            source="local h=game:GetService('HttpService');h.HttpEnabled=true;local t=h:GetAsync("+lua_literal(f'http://127.0.0.1:{server.server_port}/hello')+");assert(t=='hello, chatgpt');print('XML COMPILED HTTP PASSED',t)"
            main.write_text("local compile=require(workspace.Loadstr1ng);local f,e=compile("+lua_literal(source)+",getfenv());assert(f,e);f()",encoding='utf-8')
            result=run('server');output=result.stdout+result.stderr
            assert result.returncode==0 and 'XML COMPILED HTTP PASSED' in output,output
            outputs.append({'mode':'compiled-http','stdout':result.stdout.strip()})
            assert hashlib.sha256(args.user_model.read_bytes()).hexdigest()==digest
            evidence={'file':str(args.user_model),'sha256':digest,'bytes':len(original),'items':record['count'],
                'identity':'vLua 5.1 with Yueliang and FiOne, not Fiu/LuauCeption',
                'original_unchanged':True,'source_to_bytecode_inside_runtime':True,'checks':outputs,
                'sources':[{'path':x['label'],'sha256':hashlib.sha256(x['source'].encode()).hexdigest()}
                    for x in [record['items'][0],*record['items'][0]['children']]],
                'status':'PASS'}
            (root/'evidence/user_xml_comparison.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
            for output in outputs:print(output['mode'],output['stdout'])
        finally:server.shutdown();server.server_close()
