"""Real asset transport with XML/binary fixtures, compilation, require and cache."""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import base64
import json
import struct
import subprocess
import sys
import tempfile
import threading
import urllib.parse
import xml.etree.ElementTree as ET

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from assets import check_binary

def xml(source,name='MainModule'):
    tree=ET.Element('roblox',version='4')
    node=ET.SubElement(tree,'Item',{'class':'ModuleScript'})
    props=ET.SubElement(node,'Properties')
    ET.SubElement(props,'string',name='Name').text=name
    raw=struct.pack('<I',1)+struct.pack('<I',9)+b'AssetFlag'+b'\x02'+struct.pack('<I',10)+b'from-asset'
    ET.SubElement(props,'BinaryString',name='AttributesSerialize').text=base64.b64encode(raw).decode()
    source="assert(script:GetAttribute('AssetFlag')=='from-asset');"+source
    ET.SubElement(props,'ProtectedString',name='Source').text=source
    child=ET.SubElement(node,'Item',{'class':'ModuleScript'})
    props=ET.SubElement(child,'Properties')
    ET.SubElement(props,'string',name='Name').text='Child'
    ET.SubElement(props,'ProtectedString',name='Source').text='return 37'
    return ET.tostring(tree,encoding='utf-8')

with tempfile.TemporaryDirectory(prefix='asset-check-') as directory:
    folder=Path(directory);source=folder/'model.rbxmx';binary=folder/'model.rbxm'
    source.write_bytes(xml("local value=require(script.Child);local remote=require(202);task.wait(.02);shared.assetRuns=(shared.assetRuns or 0)+1;return {answer=value+5,other=remote,name=script.Name}"))
    subprocess.run([str(root/'recovery-asset-codec.exe'),'to-binary',str(source),str(binary)],check=True)
    check_binary(binary.read_bytes())
    for bad in (b'bad',binary.read_bytes()[:-1],binary.read_bytes()+b'extra'):
        try:check_binary(bad)
        except ValueError:pass
        else:raise AssertionError('Accepted invalid binary')
    oversized=bytearray(binary.read_bytes());struct.pack_into('<I',oversized,20,10001)
    try:check_binary(oversized)
    except ValueError:pass
    else:raise AssertionError('Accepted oversized binary tree')
    fixtures={101:binary.read_bytes(),202:xml('return "nested-asset"'),303:xml('return nil'),
        404:xml('return 5','WrongName'),505:xml('error("ASSET_SOURCE_ERROR")'),606:xml('local ='),
        707:b'<roblox version="4"><Item class="MeshPart"/></roblox>',808:xml('return require(808)')}
    hits={};lock=threading.Lock()
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_GET(self):
            query=urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query)
            key='assetversionid' if 'assetversionid' in query else 'id'
            identifier=int(query[key][0])
            with lock:hits[(key,identifier)]=hits.get((key,identifier),0)+1
            body=fixtures.get(identifier,b'missing')
            self.send_response(200 if identifier in fixtures else 404)
            self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        main=folder/'main.luau'
        main.write_text('''local done=Instance.new('BindableEvent')
local a,b,count=nil,nil,0
task.spawn(function() a=require(101);count+=1;if count==2 then done:Fire() end end)
task.spawn(function() b=require(101);count+=1;if count==2 then done:Fire() end end)
done.Event:Wait()
assert(a==b and a.answer==42 and a.other=='nested-asset' and a.name=='MainModule' and shared.assetRuns==1)
assert(require(101)==a and shared.assetRuns==1)
assert(require(303)==nil and require(303)==nil)
local insert=game:GetService('InsertService')
local loaded=insert:LoadAsset(101)
assert(loaded:IsA('Model') and loaded.Parent==nil and loaded.MainModule.Child:IsA('ModuleScript'))
assert(require(loaded.MainModule).answer==42 and shared.assetRuns==2)
local other=game:GetService('AssetService'):LoadAssetAsync(202)
assert(require(other.MainModule)=='nested-asset')
assert(require(insert:LoadAssetVersion(202).MainModule)=='nested-asset')
local objects=game:GetObjects('rbxassetid://202')
assert(#objects==1 and require(objects[1])=='nested-asset' and objects[1].Parent==nil)
for _,id in {-1,1.25,9007199254740992,404,505,606,707,808,999} do
    local ok,reason=pcall(require,id);assert(not ok and type(reason)=='string','Accepted invalid asset '..id)
    if id==505 then assert(reason:find('rbxassetid://505::/MainModule:1',1,true),reason) end
end
assert(not pcall(function() game:GetObjects('file:///model.rbxm') end))
print('ASSET XML/BINARY/REQUIRE/CACHE CHECKS PASSED')
''',encoding='utf-8')
        # Keep test endpoint configuration outside the public runtime API.
        launcher='import sys;sys.path.insert(0,'+repr(str(root))+');import asset_delivery;asset_delivery.configured=lambda:(None,"test fixture");import assets;assets.ASSET_BASE_URL='+repr(f'http://127.0.0.1:{server.server_port}/asset/')+';import run;sys.argv=["run.py",*sys.argv[1:]];run.main()'
        result=subprocess.run([sys.executable,'-c',launcher,str(main),'--duration','1',*sys.argv[1:]],capture_output=True,text=True,encoding='utf-8',timeout=90)
        assert result.returncode==0 and 'ASSET XML/BINARY/REQUIRE/CACHE CHECKS PASSED' in result.stdout,(result.stdout,result.stderr)
        assert hits[('id',101)]==2 and hits[('id',303)]==1,hits
        assert hits[('assetversionid',202)]==1,hits
        before=sum(hits.values())
        main.write_text("assert(not pcall(require,101));assert(not pcall(function() game:GetService('AssetService'):LoadAssetAsync(202) end));print('CLIENT ASSET RESTRICTION PASSED')",encoding='utf-8')
        result=subprocess.run([sys.executable,'-c',launcher,str(main),'--mode','client',*sys.argv[1:]],capture_output=True,text=True,encoding='utf-8',timeout=60)
        assert result.returncode==0 and 'CLIENT ASSET RESTRICTION PASSED' in result.stdout,(result.stdout,result.stderr)
        assert sum(hits.values())==before,'Client made asset network requests'
        (root/'data/asset_comparison.json').write_text(json.dumps({'status':'PASS','fixture_transport':'loopback HTTP',
            'binary_codec':'rbx_binary 3.0.1 / rbx_xml 3.0.1','public_live_asset_verified':False,
            'checks':['XML and compressed binary','compile in worker/load bytecode in native VM','nested require(id)',
                'parallel require coalescing','nil cache','fresh LoadAsset instances','asset version query','GetObjects',
                'errors/asset source labels','cyclic numeric require','unsupported models','server-only'],
            'requests':{f'{key}:{identifier}':count for (key,identifier),count in sorted(hits.items())}},indent=2)+'\n',encoding='utf-8')
        print('ASSET XML/BINARY/REQUIRE/CACHE CHECKS PASSED')
    finally:server.shutdown();server.server_close()
