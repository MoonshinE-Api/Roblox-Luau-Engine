"""Execute bytecode with a real Luau interpreter written in Luau, inside our VM.

Fiu is an unchanged MIT-licensed test dependency, pinned in vendor/Fiu.luau.
The production engine does not import it or depend on it.
"""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import threading

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from run import lua_literal

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_GET(self):
        body=b'hello, chatgpt'
        self.send_response(200);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)

server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
payload=r'''
local a,b,c=...
assert(a==11 and b==nil and c=='varargs')
local module=require(script.Parent.Helper)
assert(module(9)==81)
local function factorial(n) return if n<2 then 1 else n*factorial(n-1) end
assert(factorial(8)==40320)
local failures=0
for _,value in {1,2,3} do
    local ok,message=pcall(function() if value==2 then error('nested error') end end)
    if not ok then assert(message:find('nested error'));failures+=1 end
end
assert(failures==1)
local closure
do local value=10;closure=function(inc) value+=inc;return value end end
assert(closure(2)==12 and closure(3)==15)
local odd=setmetatable({value=7},{__add=function(x,y) return x.value+y end})
assert(odd+5==12)
local random=Random.new(735)
local folder=Instance.new('Folder',workspace);folder.Name='NestedInterpreter'
local signals=0;local event=Instance.new('BindableEvent',folder)
event.Event:Connect(function(amount) signals+=amount end)
for i=1,20 do
    local part=Instance.new('Part',folder)
    part.Name='Part'..i;part.Anchored=true;part.Position=Vector3.new(i*8,2,0)
    part.BrickColor=BrickColor.palette(random:NextInteger(0,127))
    part:SetAttribute('Index',i)
    local clone=part:Clone();assert(clone.Name==part.Name and clone:GetAttribute('Index')==i);clone:Destroy()
    event:Fire(i)
end
assert(signals==210)
local part=folder.Part1
local tween=game:GetService('TweenService'):Create(part,TweenInfo.new(.05,Enum.EasingStyle.Linear),{Transparency=.75})
tween:Play()
assert(tween.Completed:Wait()==Enum.PlaybackState.Completed and part.Transparency==.75)
local h=game:GetService('HttpService');h.HttpEnabled=true
local encoded=h:JSONEncode({nested=true,sum=signals})
assert(h:JSONDecode(encoded).sum==210)
local text=h:GetAsync(URL)
assert(text=='hello, chatgpt')
folder:Destroy()
print('NESTED LUAU VM ENGINE AND HTTP PASSED',text)
return signals,nil,'nested-result'
'''.replace('URL',lua_literal(f'http://127.0.0.1:{server.server_port}/hello'))
try:
    with tempfile.TemporaryDirectory(prefix='nested-luau-') as directory:
        folder=Path(directory);project=folder/'project';project.mkdir()
        source=folder/'payload.luau';bytecode=folder/'payload.luauc'
        source.write_text(payload,encoding='utf-8')
        subprocess.run([str(root/'recovery-luau-compile.exe'),str(source),str(bytecode)],check=True)
        compiled=bytecode.read_bytes()
        assert compiled[0]==9,compiled[:4]
        literal='"'+''.join(f'\\{b:03d}' for b in compiled)+'"'
        shutil.copyfile(root/'tests/vendor/Fiu.luau',project/'Fiu.luau')
        (project/'Helper.luau').write_text('return function(n) return n*n end',encoding='utf-8')
        (project/'Main.server.luau').write_text('''local Fiu=require(script.Parent.Fiu)
local settings=Fiu.luau_newsettings()
settings.vectorCtor=vector.create
settings.vectorSize=3
local main,close=Fiu.luau_load('''+literal+''',getfenv(),settings)
local a,b,c=main(11,nil,'varargs')
assert(a==210 and b==nil and c=='nested-result')
close()
''',encoding='utf-8')
        result=subprocess.run([sys.executable,str(root/'run.py'),str(project),'--duration','1',*sys.argv[1:]],capture_output=True,text=True,encoding='utf-8',timeout=60)
        assert result.returncode==0 and 'NESTED LUAU VM ENGINE AND HTTP PASSED' in result.stdout,(result.stdout,result.stderr)
        report={'interpreter':'Fiu','revision':'fa1983d39f11f2b650b871d7a2d4e3b4c3e4ef2b',
                'source_sha256':hashlib.sha256((root/'tests/vendor/Fiu.luau').read_bytes()).hexdigest(),
                'bytecode_version':compiled[0],'payload_sha256':hashlib.sha256(compiled).hexdigest(),
                'result':result.stdout.strip(),'full_compatibility_proven':False}
        (root/'evidence/nested_vm_comparison.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        print(result.stdout.strip())
finally:
    server.shutdown();server.server_close()
