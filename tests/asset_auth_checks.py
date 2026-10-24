"""Synthetic credentials only: DPAPI/CLI, scoped delivery, redirects, runtime require."""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
from unittest.mock import patch
import urllib.request

root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
import asset_auth as auth
import asset_delivery as delivery
from http_runtime import HttpRuntime,HttpRedirectHandler

COOKIE='SYNTHETIC-cookie-NOT-A-ROBLOX-SESSION-92471'
KEY='SYNTHETIC-key-NOT-A-ROBLOX-API-KEY-63319'
OK={'Success':True,'StatusCode':200,'StatusMessage':'OK','Headers':{}}
model=b'<roblox version="4"><Item class="ModuleScript"><Properties><string name="Name">MainModule</string><ProtectedString name="Source">return {answer=42}</ProtectedString></Properties></Item></roblox>'
checks=[]

with tempfile.TemporaryDirectory(prefix='asset-auth-check-') as directory:
    folder=Path(directory)
    environment=dict(os.environ,LOCALAPPDATA=str(folder))
    for name in (auth.COOKIE_ENV,auth.KEY_ENV):environment.pop(name,None)
    with patch.dict(os.environ,environment,clear=True):
        assert auth.configured()==(None,'anonymous')
        # Real Windows crypto, isolated from the user's actual saved login.
        auth.save('cookie',COOKIE)
        assert auth.saved()==('cookie',COOKIE)
        assert COOKIE.encode() not in auth.store_path().read_bytes()
        assert auth.configured()==(('cookie',COOKIE),'saved Windows login')
        with patch.dict(os.environ,{auth.KEY_ENV:KEY}):
            assert auth.configured()==(('api-key',KEY),'environment')
            with patch.dict(os.environ,{auth.COOKIE_ENV:COOKIE}):
                try:auth.configured()
                except ValueError as error:assert COOKIE not in str(error) and KEY not in str(error)
                else:raise AssertionError('Ambiguous authentication accepted')
        for invalid in ('','a\r\nInjected: yes','a;b','a b','a,b','\u2064'):
            try:auth.credential('cookie',invalid)
            except ValueError:pass
            else:raise AssertionError('Invalid credential accepted')
        auth.store_path().write_bytes(auth.MAGIC+b'broken DPAPI data')
        try:auth.saved()
        except ValueError as error:assert 'unreadable' in str(error)
        else:raise AssertionError('Corrupt credential accepted')
        auth.store_path().unlink()
    checks.append('Windows DPAPI roundtrip/corruption, environment precedence, credential validation')

    def cli(*arguments):
        result=subprocess.run([sys.executable,str(root/'run.py'),*arguments],env=environment,
            capture_output=True,text=True,encoding='utf-8',timeout=30)
        assert COOKIE not in result.stdout+result.stderr and KEY not in result.stdout+result.stderr
        return result
    assert cli('.login',COOKIE).returncode==0
    state=cli('.auth');assert state.returncode==0 and 'cookie (saved Windows login)' in state.stdout
    checks.append('CLI .login/.auth without creating a VM or printing credentials')

    with patch.object(delivery,'configured',return_value=(('cookie',COOKIE),'test')):
        calls=[]
        def cookie_transport(options,body):
            calls.append(options)
            assert options['_HostCredentialHeaders']=={'Cookie':'.ROBLOSECURITY='+COOKIE}
            assert COOKIE not in options['Url'] and not body
            return OK,model
        assert delivery.download(123,False,2,cookie_transport)==model
        assert calls[-1]['Url']==delivery.LEGACY_URL+'?id=123'
        delivery.download(456,True,2,cookie_transport)
        assert calls[-1]['Url']==delivery.LEGACY_URL+'?assetversionid=456'
        try:delivery.download(123,False,2,cookie_transport,'http://127.0.0.1/asset')
        except ValueError:pass
        else:raise AssertionError('Credential allowed on an alternate endpoint')
        def failing(options,body):raise RuntimeError(COOKIE)
        try:delivery.download(123,False,2,failing)
        except ValueError as error:assert COOKIE not in str(error)
        else:raise AssertionError('Transport failure hidden')
    checks.append('Cookie ID/version routing, fixed endpoint restriction, exception redaction')

    with patch.object(delivery,'configured',return_value=(('api-key',KEY),'test')):
        calls=[]
        def cloud_transport(options,body):
            calls.append(options)
            if len(calls)==1:
                assert options['Url']==delivery.CLOUD_URL+'123'
                assert options['_HostCredentialHeaders']=={'x-api-key':KEY}
                return OK,json.dumps({'location':'https://sc2.rbxcdn.com/synthetic?token=signed'}).encode()
            assert '_HostCredentialHeaders' not in options and options['Headers']=={'Accept':'application/octet-stream'}
            assert options['Timeout']<=calls[0]['Timeout']
            return OK,model
        assert delivery.download(123,False,2,cloud_transport)==model and len(calls)==2
        try:delivery.download(456,True,2,cloud_transport)
        except ValueError as error:assert 'versionId' in str(error)
        else:raise AssertionError('Asset-version ID confused with version number')
        for location in ('http://sc2.rbxcdn.com/file','https://evil.example/file','https://rbxcdn.com.evil.example/file',
                         'https://sc2.rbxcdn.com:444/file','https://user@sc2.rbxcdn.com/file','https://sc2.rbxcdn.com/\r\n'):
            count=[0]
            def bad_location(options,body):count[0]+=1;return OK,json.dumps({'location':location}).encode()
            try:delivery.download(123,False,2,bad_location)
            except ValueError:assert count[0]==1
            else:raise AssertionError('Unsafe CDN location accepted')
    for status in (401,403,404,429,500):
        with patch.object(delivery,'configured',return_value=(None,'anonymous')):
            def status_transport(options,body):return {'Success':False,'StatusCode':status,'StatusMessage':COOKIE},COOKIE.encode()
            try:delivery.download(123,False,2,status_transport)
            except ValueError as error:assert str(status) in str(error) and COOKIE not in str(error)
            else:raise AssertionError('HTTP error ignored')
    checks.append('Open Cloud metadata/CDN separation, shared timeout, URL checks, 401/403/404/429 errors')

    # Actual urllib sockets and redirects, including a change of port = origin.
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_GET(self):
            if self.path.startswith('/redirect'):
                self.send_response(302)
                self.send_header('Location','/echo' if self.path=='/redirect' else other_url+'/echo')
                self.send_header('Content-Length','0');self.end_headers();return
            body=json.dumps(dict(self.headers.items())).encode()
            self.send_response(200);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
    servers=[ThreadingHTTPServer(('127.0.0.1',0),Handler) for _ in range(2)]
    for server in servers:threading.Thread(target=server.serve_forever,daemon=True).start()
    base=f'http://127.0.0.1:{servers[0].server_port}';other_url=f'http://127.0.0.1:{servers[1].server_port}'
    try:
        def headers(path,host=True):
            options={'Url':base+path,'Method':'GET','Headers':{'X-Custom':'keep'},'Timeout':2,'HasBody':False}
            credentials={'Cookie':COOKIE,'Authorization':KEY,'x-api-key':KEY}
            if host:options['_HostCredentialHeaders']=credentials
            else:options['Headers'].update(credentials)
            metadata,data=HttpRuntime.request(options,b'');assert metadata['Success']
            return {key.lower():value for key,value in json.loads(data).items()}
        assert headers('/echo')['cookie']==COOKIE
        for path in ('/redirect','/redirect-other'):
            received=headers(path)
            assert received['x-custom']=='keep' and not any(key in received for key in ('cookie','authorization','x-api-key'))
        received=headers('/redirect-other',host=False)
        assert received['x-custom']=='keep' and not any(key in received for key in ('cookie','authorization','x-api-key'))
        assert headers('/redirect',host=False)['cookie']==COOKIE
        request=urllib.request.Request('https://assetdelivery.roblox.com/start',headers={'Cookie':COOKIE,'x-api-key':KEY})
        redirected=HttpRedirectHandler().redirect_request(request,None,302,'',{},'http://assetdelivery.roblox.com/end')
        assert not redirected.has_header('Cookie') and not redirected.has_header('X-api-key')
    finally:
        for server in servers:server.shutdown();server.server_close()
    checks.append('Real HTTP: host credentials excluded from every redirect; ordinary credentials stripped across origins/downgrades')

    # Login persisted by a different Python process -> require(id) -> decoded
    # model -> original VM. Only transport is mocked; credentials never in Lua.
    script=folder/'main.luau'
    script.write_text("assert(os.getenv==nil);assert(require(123).answer==42);local http=game:GetService('HttpService');http.HttpEnabled=true;assert(http:GetAsync('https://example.invalid/no-account')=='no cookie');print('AUTHENTICATED ASSET VM CHECK PASSED')",encoding='utf-8')
    launcher='''import sys
sys.path.insert(0,ROOT)
from http_runtime import HttpRuntime
def transport(options,body):
    if options['Url']=='https://example.invalid/no-account':
        assert '_HostCredentialHeaders' not in options and not options['Headers']
        return {'Success':True,'StatusCode':200},b'no cookie'
    assert options['Url']=='https://assetdelivery.roblox.com/v1/asset/?id=123'
    assert options['_HostCredentialHeaders']=={'Cookie':'.ROBLOSECURITY='+TOKEN}
    return {'Success':True,'StatusCode':200},MODEL
HttpRuntime.request=staticmethod(transport)
import run
sys.argv=['run.py',*sys.argv[1:]]
run.main()
'''.replace('ROOT',repr(str(root))).replace('TOKEN',repr(COOKIE)).replace('MODEL',repr(model))
    result=subprocess.run([sys.executable,'-c',launcher,str(script),*sys.argv[1:]],env=environment,
                         capture_output=True,text=True,encoding='utf-8',timeout=60)
    assert result.returncode==0 and 'AUTHENTICATED ASSET VM CHECK PASSED' in result.stdout,(result.stdout,result.stderr)
    assert COOKIE not in result.stdout+result.stderr
    assert cli('.logout').returncode==0 and not (folder/'EngineRecovery0735/auth.dpapi').exists()
    assert 'none (anonymous)' in cli('.auth').stdout
    assert cli('.login','--api-key',KEY).returncode==0
    assert 'api-key (saved Windows login)' in cli('.auth').stdout
    assert cli('.logout').returncode==0
    checks.append('Cross-process saved login -> require(id) -> model compilation -> original VM; logout and API-key login')

report={'status':'PASS','credentials':'synthetic only; no real account accessed','live_authenticated_roblox_asset_verified':False,'checks':checks}
(root/'data/asset_auth_comparison.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('ASSET AUTH/DPAPI/REDIRECT/VM CHECKS PASSED')
