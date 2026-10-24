"""Roblox asset delivery -> bounded model decode -> source compilation.

Called in HTTP workers only. No downloaded source is evaluated by Python/Rust.
The supported model properties/classes are the same runtime schema as --model.
"""
import base64
import json
from pathlib import Path
import subprocess
import tempfile
from model_xml import read_model
from asset_delivery import download,LEGACY_URL
from model_binary import check_binary

ASSET_BASE_URL=LEGACY_URL
LIMIT=50*1024*1024

def load_asset(root,options,request):
    root=Path(root)
    identifier=options['AssetId']
    if isinstance(identifier,bool) or not isinstance(identifier,(int,float)) or not 0<identifier<=9007199254740991 or int(identifier)!=identifier:
        raise ValueError('Asset ID must be a positive exact integer')
    identifier=int(identifier)
    data=download(identifier,bool(options.get('AssetVersion')),options['Timeout'],request,ASSET_BASE_URL)
    if len(data)>LIMIT:raise ValueError('Asset exceeds 50 MiB')
    with tempfile.TemporaryDirectory(prefix='roblox-asset-') as directory:
        folder=Path(directory);xml=folder/('asset.rbxm' if data.startswith(b'<roblox!') else 'asset.rbxmx')
        xml.write_bytes(data)
        model=read_model(xml)
        jobs=[];counter=0
        def visit(node,parent=''):
            nonlocal counter
            label=f'rbxassetid://{identifier}'+(' (version)' if options.get('AssetVersion') else '')+'::'+parent+'/'+node['name']
            node['label']=label
            if node['class'] in {'Script','LocalScript','ModuleScript'}:
                counter+=1
                source=folder/f'source-{counter}.luau';out=folder/f'compiled-{counter}.luauc'
                source.write_text(node.pop('source'),encoding='utf-8')
                jobs.append((source,out,label,node))
            else:node.pop('source',None)
            for child in node['children']:visit(child,parent+'/'+node['name'])
        for node in model['items']:visit(node)
        if jobs:
            manifest=folder/'jobs.txt'
            manifest.write_text(''.join(str(field)+'\0' for job in jobs for field in job[:3]),encoding='utf-8')
            result=subprocess.run([str(root/'recovery-luau-compile.exe'),'--batch',str(manifest)],
                capture_output=True,text=True,encoding='utf-8',timeout=20)
            if result.returncode:raise ValueError('Asset source compilation failed: '+result.stderr.strip())
            for _,out,_,node in jobs:node['bytecode']=base64.b64encode(out.read_bytes()).decode('ascii')
        body=json.dumps({'items':model['items'],'count':model['count']},ensure_ascii=True,separators=(',',':')).encode()
        if len(body)>LIMIT:raise ValueError('Compiled asset transfer exceeds 50 MiB')
        return {'Success':True,'StatusCode':200,'StatusMessage':'OK','Headers':{}},body
