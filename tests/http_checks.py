"""Real loopback transport, concurrent yield, binary bodies, errors and JSON oracle."""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import gzip
import json
import random
import subprocess
import sys
import tempfile
import threading
import time

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from run import lua_literal
from http_runtime import HttpRuntime,Transfer
import ctypes as C

# The scheduler deadline must also cover a worker blocked in name resolution.
# Its late completion must never replace a buffer already pinned for native Lua.
manager=HttpRuntime()
def blocked(options,body):
    time.sleep(.12)
    return {'Success':True},b'late'
manager.request=blocked
identifier=manager.start({'Timeout':.01},b'')
time.sleep(.03)
pointer=manager.dispatch(1,identifier)
transfer=Transfer.from_address(pointer)
assert 'timeout' in json.loads(C.string_at(transfer.metadata,transfer.metadata_len))['Error']
time.sleep(.13)
assert manager.dispatch(1,identifier)==pointer
manager.dispatch(2,identifier)
assert not manager.jobs and not manager.workers
manager.close()

class Handler(BaseHTTPRequestHandler):
    protocol_version='HTTP/1.1'
    slow_pair=threading.Barrier(2)
    def log_message(self,*args):pass
    def do_GET(self):
        code=200;headers={}
        if self.path=='/hello':body=b'hello, chatgpt'
        elif self.path=='/slow':
            try:self.slow_pair.wait(timeout=5);body=b'slow'
            except threading.BrokenBarrierError:body=b'requests did not overlap'
        elif self.path=='/timeout':time.sleep(.2);body=b'late'
        elif self.path=='/status':code=418;body=b'teapot'
        elif self.path=='/binary':body=bytes(range(256))*3
        elif self.path=='/large':body=b'x'*(12*1024*1024)
        elif self.path=='/gzip':body=gzip.compress(b'hello\x00compressed');headers['Content-Encoding']='gzip'
        elif self.path=='/redirect':code=302;body=b'';headers['Location']='/hello'
        else:code=404;body=b'missing'
        self.reply(code,body,headers)
    def do_HEAD(self):
        self.send_response(200);self.send_header('Content-Length','42');self.send_header('Content-Encoding','gzip');self.end_headers()
    def do_POST(self):
        body=self.rfile.read(int(self.headers.get('Content-Length',0)))
        if self.headers.get('Content-Encoding')=='gzip':body=gzip.decompress(body)
        if self.path=='/headers':
            body=json.dumps({'data':body.decode(),'kind':self.headers.get('Content-Type'),'custom':self.headers.get('X-Example')}).encode()
        self.reply(201,body)
    do_PUT=do_POST
    do_PATCH=do_POST
    do_DELETE=do_POST
    do_OPTIONS=do_POST
    def reply(self,code,body,headers=None):
        self.send_response(code)
        for key,value in (headers or {}).items():self.send_header(key,value)
        self.send_header('Content-Length',str(len(body)));self.send_header('X-Reply','yes');self.end_headers()
        try:self.wfile.write(body)
        except (BrokenPipeError,ConnectionResetError,ConnectionAbortedError):pass

server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
server.daemon_threads=True
threading.Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}'
source='local base='+lua_literal(base)+''' 
local http=game:GetService('HttpService');http.HttpEnabled=true
assert(http:GetAsync(base..'/hello')=='hello, chatgpt')
assert(http:GetAsync(base..'/redirect')=='hello, chatgpt')
assert(http:GetAsync(base..'/gzip')=='hello\\0compressed')
local response=http:RequestAsync({Url=base..'/status'})
assert(not response.Success and response.StatusCode==418 and response.Body=='teapot' and response.Headers['x-reply']=='yes')
assert(not pcall(function() http:GetAsync(base..'/status') end))
local binary=http:GetAsync(base..'/binary')
assert(#binary==768)
for i=1,#binary do assert(binary:byte(i)==(i-1)%256) end
local echo=http:PostAsync(base..'/headers','data',Enum.HttpContentType.TextPlain,true,{['X-Example']='present'})
local decoded=http:JSONDecode(echo)
assert(decoded.data=='data' and decoded.kind=='text/plain' and decoded.custom=='present')
for _,method in {'POST','PUT','PATCH','DELETE','OPTIONS'} do
    local r=http:RequestAsync({Url=base..'/echo',Method=method,Body=binary,Compress=Enum.HttpCompression.Gzip})
    assert(r.Success and r.StatusCode==201 and r.Body==binary)
end
assert(http:RequestAsync({Url=base..'/hello',Method='HEAD'}).Body=='')
assert(not pcall(function() http:RequestAsync({Url=base,Method='GET',Body=''}) end))
assert(not pcall(function() http:RequestAsync({Url='file:///example'}) end))
assert(not pcall(function() http:RequestAsync({Url=base,Headers={Bad='a\\r\\nInjected: yes'}}) end))
assert(not pcall(function() http:RequestAsync({Url=base..'/timeout',Timeout=.05}) end))
local count,ticked=0,false
local done=Instance.new('BindableEvent')
for i=1,2 do task.spawn(function()
    assert(http:GetAsync(base..'/slow')=='slow');count+=1
    if count==2 then done:Fire() end
end) end
task.defer(function() ticked=true end)
done.Event:Wait()
assert(ticked,'Another Luau task did not run while awaiting HTTP')
print('ASYNC HTTP TRANSPORT CHECKS PASSED')
'''
# A seeded reference corpus compares encode/decode semantics with stdlib JSON,
# including all control bytes, supplementary Unicode, numeric precision and null.
rng=random.Random(735)
def value(depth=0):
    choices=4 if depth>=4 else 6
    choice=rng.randrange(choices)
    if choice==0:return rng.choice([False,True,None])
    if choice==1:return rng.uniform(-1e100,1e100)
    if choice==2:return rng.randrange(-2**52,2**52)
    if choice==3:return ''.join(chr(rng.choice([rng.randrange(0,128),0x416,0x4e2d,0x1f680])) for _ in range(rng.randrange(16)))
    if choice==4:
        # Null holes have multiple valid Lua sequence boundaries. Their precise
        # native layout is covered separately, not by Python list equality.
        return [False if x is None else x for x in (value(depth+1) for _ in range(rng.randrange(8)))]
    return {f'key{i}':value(depth+1) for i in range(rng.randrange(8))}
corpus=[value() for _ in range(600)]
vectors=[json.dumps(v,ensure_ascii=True,separators=(',',':')) for v in corpus]
oracle='''local http=game:GetService('HttpService')
local vectors='''+lua_literal(vectors)+'''
for i,text in vectors do
    local decoded=http:JSONDecode(text)
    print('JSON_ORACLE:'..http:JSONEncode(decoded))
end
'''
def normalized(v):
    # Empty JSON objects and arrays become the same Lua table; object null
    # values are skipped. Array null holes become null inside the VM raw length.
    if isinstance(v,dict):
        d={k:normalized(x) for k,x in v.items() if x is not None}
        return d if d else []
    if isinstance(v,list):
        # rawlen does not retain trailing JSON null elements.
        while v and v[-1] is None:v=v[:-1]
        return [normalized(x) for x in v]
    return v
try:
    with tempfile.TemporaryDirectory(prefix='luau-http-') as directory:
        folder=Path(directory)
        for mode in ('virtual','realtime'):
            file=folder/'main.luau'
            file.write_text(source,encoding='utf-8')
            command=[sys.executable,str(root/'run.py'),str(file),'--duration','4',*sys.argv[1:]]
            if mode=='realtime':command+=['--realtime']
            result=subprocess.run(command,capture_output=True,text=True,timeout=50)
            assert result.returncode==0 and 'ASYNC HTTP TRANSPORT CHECKS PASSED' in result.stdout,(mode,result.stdout,result.stderr)
            print(mode.upper()+' HTTP TRANSPORT PASSED')
        file.write_text("local h=game:GetService('HttpService');h.HttpEnabled=true;assert(not pcall(function() h:GetAsync("+lua_literal(base+ '/hello')+") end));print('CLIENT HTTP RESTRICTION PASSED')",encoding='utf-8')
        result=subprocess.run([sys.executable,str(root/'run.py'),str(file),'--mode','client',*sys.argv[1:]],capture_output=True,text=True,timeout=50)
        assert result.returncode==0 and 'CLIENT HTTP RESTRICTION PASSED' in result.stdout,(result.stdout,result.stderr)
        file.write_text(oracle,encoding='utf-8')
        result=subprocess.run([sys.executable,str(root/'run.py'),str(file),*sys.argv[1:]],capture_output=True,text=True,encoding='utf-8',timeout=50)
        assert result.returncode==0,(result.stdout,result.stderr)
        decoded=[json.loads(line.removeprefix('JSON_ORACLE:')) for line in result.stdout.splitlines() if line.startswith('JSON_ORACLE:')]
        assert len(decoded)==len(corpus),len(decoded)
        for i,(expected,actual) in enumerate(zip(corpus,decoded)):
            assert normalized(expected)==actual,(i,expected,actual)
        print('600 JSON REFERENCE VECTORS PASSED')
        file.write_text("local h=game:GetService('HttpService');h.HttpEnabled=true;print(h:GetAsync("+lua_literal(base+'/large')+"))",encoding='utf-8')
        result=subprocess.run([sys.executable,str(root/'run.py'),str(file),'--memory-mb','8',*sys.argv[1:]],capture_output=True,text=True,timeout=50)
        output=result.stdout+result.stderr
        assert result.returncode==1 and 'memory' in output.lower() and 'native fault' not in output and 'Traceback' not in output,output[:1000]
        print('HTTP RESPONSE OOM CLEANUP PASSED')
finally:
    server.shutdown();server.server_close()
