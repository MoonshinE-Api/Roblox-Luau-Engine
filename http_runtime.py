"""Asynchronous HTTP transport for the standalone runner (Python stdlib only).

Workers never enter Lua. Native code copies pinned completion buffers into Lua
after the dispatch callback has returned. This is not Roblox's cloud transport.
"""
import ctypes as C
import gzip
import json
from pathlib import Path
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import zlib

LIMIT=50*1024*1024
MAX_REQUESTS=64
TOKEN=re.compile(r"^[!#$%&'*+.^_`|~0-9A-Za-z-]+$")

class HttpRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        if urllib.parse.urlsplit(newurl).scheme not in ('http','https'):
            raise ValueError('HTTP redirect must use http:// or https://')
        redirected=super().redirect_request(req,fp,code,msg,headers,newurl)
        before=urllib.parse.urlsplit(req.full_url);after=urllib.parse.urlsplit(newurl)
        def origin(parts):return parts.scheme,parts.hostname,parts.port or (443 if parts.scheme=='https' else 80)
        if redirected is not None and origin(before)!=origin(after):
            for key in ('Authorization','Cookie','Cookie2','X-api-key','Proxy-authorization','Host'):
                redirected.remove_header(key)
        return redirected

class Transfer(C.Structure):
    _fields_=[('metadata',C.c_size_t),('metadata_len',C.c_size_t),
              ('body',C.c_size_t),('body_len',C.c_size_t)]

class Completion:
    def __init__(self,metadata,body=b''):
        encoded=json.dumps(metadata,ensure_ascii=True,separators=(',',':')).encode()
        self.metadata=C.create_string_buffer(encoded)
        self.body=C.create_string_buffer(body)
        self.transfer=Transfer(C.addressof(self.metadata),len(encoded),C.addressof(self.body),len(body))

class HttpRuntime:
    def __init__(self,data_store_path=None,shutdown_event=None):
        self.condition=threading.Condition()
        self.next_id=0
        self.jobs={}
        self.deadlines={}
        self.workers=0
        self.closed=False
        self.callback_errors=[]
        self.data_store_path=data_store_path
        self.shutdown_event=shutdown_event
        self.data_stores=None
        @C.CFUNCTYPE(C.c_size_t,C.c_size_t,C.c_size_t)
        def dispatch(op,arg):
            try:
                if op==5:return int(self.shutdown_event is not None and self.shutdown_event.is_set())
                if op in (0,4):
                    data=Transfer.from_address(arg)
                    metadata=json.loads(C.string_at(data.metadata,data.metadata_len))
                    body=C.string_at(data.body,data.body_len)
                    return self.synchronous(metadata,body) if op==4 else self.start(metadata,body)
                with self.condition:
                    if op==1:
                        result=self.jobs.get(arg)
                        if arg in self.jobs and result is None and time.monotonic()>=self.deadlines[arg]:
                            result=Completion({'Error':'HTTP transport: request timeout exceeded'})
                            self.jobs[arg]=result
                        return C.addressof(result.transfer) if result else 0
                    if op==2:self.jobs.pop(arg,None);self.deadlines.pop(arg,None)
                    if op==3:self.condition.wait(min(arg,50)/1000)
                return 0
            except BaseException as error:
                self.callback_errors.append(f'{type(error).__name__}: {error}')
                return 0
        self.dispatch=dispatch

    def synchronous(self,options,body):
        # No Lua API calls here. Native copies the completion after returning.
        try:
            from encoding_runtime import transform
            metadata,body=transform(options,body)
            result=Completion(metadata,body)
        except Exception as error:
            result=Completion({'Error':'EncodingService: '+str(error)})
        with self.condition:
            if self.closed:raise RuntimeError('HTTP runtime closed')
            self.next_id+=1;identifier=self.next_id
            self.jobs[identifier]=result
        return identifier

    def start(self,options,body):
        with self.condition:
            self.next_id+=1
            identifier=self.next_id
            if self.closed:raise RuntimeError('HTTP runtime closed')
            if self.workers>=MAX_REQUESTS:
                # This completion is immediately consumed by the single Lua VM.
                self.jobs[identifier]=Completion({'Error':'Too many outstanding HTTP requests (host limit 64)'})
                return identifier
            self.jobs[identifier]=None
            self.deadlines[identifier]=time.monotonic()+options['Timeout']
            self.workers+=1
        try:threading.Thread(target=self.work,args=(identifier,options,body),daemon=True,name=f'luau-http-{identifier}').start()
        except Exception as error:
            with self.condition:
                self.workers-=1;self.jobs[identifier]=Completion({'Error':f'Unable to start HTTP worker: {error}'})
        return identifier

    def work(self,identifier,options,body):
        try:
            if options.get('Kind')=='DataStore':
                with self.condition:
                    if self.closed:raise RuntimeError('Runtime is closed')
                    if self.data_stores is None:
                        from datastore_runtime import DataStores
                        self.data_stores=DataStores(self.data_store_path)
                    stores=self.data_stores
                metadata,body=stores.request(options,body)
            elif options.get('Kind')=='Asset':
                from assets import load_asset
                metadata,body=load_asset(Path(__file__).resolve().parent,options,self.request)
            else:metadata,body=self.request(options,body)
            result=Completion(metadata,body)
        except Exception as error:
            label='Local data store' if options.get('Kind')=='DataStore' else 'HTTP transport'
            result=Completion({'Error':f'{label}: {type(error).__name__}: {error}'})
        with self.condition:
            self.workers-=1
            # Never replace a pinned completion: the native caller may currently
            # be copying it with the GIL released. Late workers are discarded.
            if not self.closed and identifier in self.jobs and self.jobs[identifier] is None:self.jobs[identifier]=result
            self.condition.notify_all()

    @staticmethod
    def request(options,body):
        url=options['Url']
        parts=urllib.parse.urlsplit(url)
        if parts.scheme not in ('http','https') or not parts.hostname:
            raise ValueError('URL must use http:// or https:// with a host')
        if parts.username is not None or parts.password is not None:
            raise ValueError('URL credentials are not supported; use an Authorization header')
        if any(ord(c)<33 or ord(c)==127 for c in url):raise ValueError('URL contains control characters or spaces')
        method=options['Method']
        if method not in {'GET','HEAD','POST','PUT','DELETE','PATCH','OPTIONS'}:raise ValueError('Unsupported HTTP method')
        headers=options['Headers']
        # Empty Luau tables encode as [] rather than {}.
        if headers==[]:headers={}
        if not isinstance(headers,dict):raise ValueError('Headers must be a dictionary')
        for key,value in headers.items():
            if not isinstance(key,str) or not TOKEN.fullmatch(key):raise ValueError('Invalid header name')
            if not isinstance(value,str) or any(ord(c)<32 and c!='\t' or ord(c)==127 for c in value):
                raise ValueError('Invalid header value')
        if len(body)>LIMIT:raise ValueError('Request body exceeds host limit 50 MiB')
        if options.get('Gzip'):
            body=gzip.compress(body,mtime=0)
            headers={k:v for k,v in headers.items() if k.lower()!='content-encoding'}
            headers['Content-Encoding']='gzip'
        timeout=options['Timeout']
        deadline=time.monotonic()+timeout
        request=urllib.request.Request(url,data=body if options['HasBody'] else None,headers=headers,method=method)
        # Created only by the Python asset loader, never from Luau options.
        # urllib deliberately excludes these headers from ALL redirects.
        for key,value in options.get('_HostCredentialHeaders',{}).items():
            request.add_unredirected_header(key,value)
        # No cookie jar/cache. urllib's default opener handles proxy settings and
        # validates HTTPS using the Python/system trust configuration.
        opener=urllib.request.build_opener(HttpRedirectHandler())
        try:response=opener.open(request,timeout=timeout)
        except urllib.error.HTTPError as error:response=error
        with response:
            chunks=[];total=0
            encoding=response.headers.get('Content-Encoding','').lower()
            if method=='HEAD' or response.code in (204,304):encoding=''
            decoder=zlib.decompressobj(16+zlib.MAX_WBITS) if encoding=='gzip' else (
                zlib.decompressobj() if encoding=='deflate' else None)
            while True:
                if time.monotonic()>deadline:raise TimeoutError('Request exceeded its timeout')
                # read1 allows deadline checks even when the server trickles data.
                chunk=response.read1(65536)
                if not chunk:break
                if decoder:
                    chunk=decoder.decompress(chunk,LIMIT+1-total)
                    if decoder.unconsumed_tail:raise ValueError('Decoded response exceeds host limit 50 MiB')
                    if decoder.unused_data:raise ValueError('Multiple/trailing compressed HTTP streams are not supported')
                total+=len(chunk)
                if total>LIMIT:raise ValueError('Response exceeds host limit 50 MiB')
                chunks.append(chunk)
            if decoder:
                tail=decoder.flush(LIMIT+1-total);total+=len(tail)
                if total>LIMIT:raise ValueError('Decoded response exceeds host limit 50 MiB')
                if not decoder.eof:raise ValueError('Truncated compressed HTTP response')
                chunks.append(tail)
            status=response.code
            return {'Success':200<=status<300,'StatusCode':status,'StatusMessage':str(response.reason or ''),
                    'Headers':{k.lower():v for k,v in response.headers.items()}},b''.join(chunks)

    def close(self):
        with self.condition:
            self.closed=True;self.jobs.clear();self.deadlines.clear();self.condition.notify_all()
        if self.data_stores is not None:self.data_stores.close()
