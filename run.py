"""Compile source files and run them on the supplied original VM plus recovered API."""
import argparse
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile

from vm_runtime import Runtime


class ScriptFailure(RuntimeError):
    """A script/compile error already reported with its Luau location."""


def lua_literal(value):
    if value is None:return 'nil'
    if value is True:return 'true'
    if value is False:return 'false'
    if isinstance(value,(int,float)):return repr(value)
    if isinstance(value,str):
        # JSON's \u0001 escapes are not valid Luau (which uses \u{...}).
        # Fixed-width decimal escapes also preserve NUL before decimal digits.
        escapes={'\\':'\\\\','"':'\\"','\n':'\\n','\r':'\\r','\t':'\\t','\b':'\\b','\f':'\\f'}
        return '"'+''.join(escapes.get(c) or (f'\\{ord(c):03d}' if ord(c)<32 or ord(c)==127 else c) for c in value)+'"'
    if isinstance(value,list):return '{'+','.join(lua_literal(x) for x in value)+'}'
    return '{'+','.join('['+lua_literal(k)+']='+lua_literal(v) for k,v in value.items())+'}'


def bootstrap(root,config):
    catalog=json.loads((root/'data/class_catalog.json').read_text(encoding='utf-8'))['classes']
    parents={name:record['parent'] for name,record in catalog.items() if record.get('parent')}
    fallback=json.loads((root/'data/hierarchy_fallback.json').read_text(encoding='utf-8'))['parents']
    for name,parent in fallback.items():parents.setdefault(name,parent)
    known={name:True for name in catalog}
    enums=json.loads((root/'data/enum_catalog.json').read_text(encoding='utf-8'))['enums']
    brickcolors=json.loads((root/'data/brickcolor_catalog.json').read_text(encoding='utf-8'))
    dates=json.loads((root/'data/datetime_recovery.json').read_text(encoding='utf-8'))
    physical=json.loads((root/'data/physical_recovery.json').read_text(encoding='utf-8'))
    fonts=json.loads((root/'data/font_recovery.json').read_text(encoding='utf-8'))
    ui=json.loads((root/'data/ui_property_catalog.json').read_text(encoding='utf-8'))
    colors=[[row['number'],row['name'],*row['rgb']] for row in brickcolors['colors']]
    source='local R={proxy=__host_proxy,config='+lua_literal(config)+',classes='+lua_literal(parents)+',knownClasses='+lua_literal(known)+',enumCatalog='+lua_literal(enums)+',brickColors='+lua_literal(colors)+',brickPalette='+lua_literal(brickcolors['palette'])+',brickConstants='+lua_literal(brickcolors['constant_constructors'])+'}\n'
    source+='R.dateTimeLocales='+lua_literal(dates['locales'])+';R.dateTimeTokens='+lua_literal(dates['tokens'])+';R.dateTimeFallbacks='+lua_literal(dates['language_fallbacks'])+'\n'
    source+='R.physicalCatalog='+lua_literal({key:physical[key] for key in ('materials','minimum_density','unit_volume','unit_center')})+'\n'
    source+='R.fontCatalog='+lua_literal(fonts['enum_fonts'])+';R.uiCatalog='+lua_literal(ui)+'\n'
    for name in ['datatypes','enums','value_types','physical_properties','font','sequences','random','brickcolor','datetime','query_params','scheduler','instances','services','ui','camera','json','http','encoding','attributes','model_properties','assets','spatial','tweens','bootstrap']:
        source+='do local initialize=(function()\n'+(root/f'engine/{name}.luau').read_text(encoding='utf-8')+'\nend)();initialize(R) end\n'
    return source


def compile_source(root,source,working,name):
    input_path=working/(name+'.luau')
    output_path=working/(name+'.luauc')
    input_path.write_text(source,encoding='utf-8')
    subprocess.run([str(root/'recovery-luau-compile.exe'),str(input_path),str(output_path)],check=True)
    return output_path.read_bytes()


def execute_source(runtime,root,source,working,name):
    runtime.load(compile_source(root,source,working,name),('@'+name).encode())
    status=runtime.execute()
    values=runtime.stack()
    runtime.image.call('__Z10lua_settopP9lua_Statei',runtime.state,argument=0)
    if status:raise ScriptFailure(values[-1] if values else f'Lua status {status}')
    return values


def project_entry(path,mode,load_source=None,models=()):
    """Filesystem project loader: server/client suffixes and sibling ModuleScripts."""
    lines=['local R=__engine','local objects={}','local sourceFunctions={}']
    scripts=[]
    identifier=0
    services={'Workspace','ReplicatedStorage','ReplicatedFirst','ServerScriptService','ServerStorage','StarterPlayer','StarterGui','StarterPack'}
    def node(classname,name,parent):
        nonlocal identifier
        identifier+=1
        ref=f'objects[{identifier}]'
        lines.append(f'{ref}=R.new({lua_literal(classname)},{parent},true);{ref}.Name={lua_literal(name)}')
        return ref
    def register_source(file,kind,name,object_ref,text=None,label=None,disabled=False,side=None):
        if load_source is None:
            source=text if text is not None else file.read_text(encoding='utf-8-sig')
            factory='function() return function()\n'+source+'\nend end'
        else:
            slots=load_source(file,text=text,label=label)
            functions=f'sourceFunctions[{identifier}]'
            lines.append(f'{functions}={{server={slots["server"]},client={slots["client"]}}}')
            for slot in slots.values():lines.append(f'{slot}=nil')
            selected='R.current().side' if kind=='ModuleScript' else lua_literal(side or ('client' if kind=='LocalScript' else 'server'))
            factory=f'function() return {functions}[{selected}] end'
        if kind=='ModuleScript':lines.append(f'R.registerModule({object_ref},{factory})')
        elif not disabled:scripts.append((object_ref,name,side or ('client' if kind=='LocalScript' else 'server'),factory))
    def source_file(file,parent,force=None):
        stem=file.stem
        if stem.endswith('.server'):kind,name='Script',stem[:-7]
        elif stem.endswith('.client'):kind,name='LocalScript',stem[:-7]
        else:kind,name='ModuleScript',stem
        if force:kind=force
        object_ref=node(kind,name,parent)
        register_source(file,kind,name,object_ref)
    def model_item(record,parent,model_path,references,deferred):
        kind,name=record['class'],record['name']
        ref=node(kind,name,parent)
        references[record['id']]=ref
        deferred.append((ref,record['typed_properties']))
        properties=record['properties']
        for key,value in properties.items():
            expression=f'Enum.RunContext:GetEnumItems()[{value+1}]' if key=='RunContext' else lua_literal(value)
            lines.append(f'{ref}[{lua_literal(key)}]={expression}')
        for tag in record['tags']:lines.append(f'{ref}:AddTag({lua_literal(tag)})')
        lines.append(f'R.applyAttributes({ref},{lua_literal(record["attributes"])})')
        if kind in {'ModuleScript','Script','LocalScript'}:
            side='client' if kind=='LocalScript' or properties.get('RunContext')==2 else 'server'
            disabled=properties.get('Disabled',False) or not properties.get('Enabled',True)
            register_source(model_path,kind,name,ref,text=record['source'],label=record['label'],disabled=disabled,side=side)
        for child in record['children']:model_item(child,ref,model_path,references,deferred)
    def folder(directory,parent):
        if directory.name in services:
            ref=f'game:GetService({lua_literal(directory.name)})'
        else:ref=node('Folder',directory.name,parent)
        for child in sorted(directory.iterdir(),key=lambda f:f.name.lower()):
            if child.is_symlink():continue
            if child.is_dir() and child.name not in {'.git','target','node_modules','__pycache__'}:folder(child,ref)
            elif child.is_file() and child.suffix in {'.lua','.luau'}:source_file(child,ref)
    for model in models:
        references={};deferred=[]
        for record in model['items']:model_item(record,'workspace',model['path'],references,deferred)
        reference_table='{'+','.join(f'[{key}]={value}' for key,value in references.items())+'}'
        lines.append('do local modelReferences='+reference_table)
        for ref,properties in deferred:lines.append(f'R.applyModelProperties({ref},{lua_literal(properties)},modelReferences)')
        lines.append('end')
    if path.is_dir():
        for child in sorted(path.iterdir(),key=lambda f:f.name.lower()):
            if child.is_symlink():continue
            if child.is_dir() and child.name not in {'.git','target','node_modules','__pycache__'}:folder(child,'game')
            elif child.is_file() and child.suffix in {'.lua','.luau'}:source_file(child,'game')
    else:
        side='client' if mode=='client' or path.stem.endswith('.client') else 'server'
        parent='R.player.PlayerScripts' if side=='client' else 'game:GetService("ServerScriptService")'
        parent=node('Folder',path.parent.name,parent)
        for sibling in sorted(path.parent.iterdir(),key=lambda f:f.name.lower()):
            if sibling.is_file() and sibling.suffix in {'.lua','.luau'}:
                if sibling.resolve()==path.resolve():source_file(sibling,parent,'LocalScript' if side=='client' else 'Script')
                elif not sibling.stem.endswith(('.server','.client')):source_file(sibling,parent)
    for ref,name,side,factory in scripts:
        if mode=='both' or mode==side:
            lines.append(f'R.run(({factory})(),{lua_literal(name)},{lua_literal(side)},{ref})')
    lines.append('local result=R.drain();assert(result.errors==0,"Script task errors: "..result.errors);return result.pending')
    return '\n'.join(lines)


def main(argv=None):
    # Pipe output must preserve fetched Unicode and JSON independently of the
    # Windows legacy code page used by a parent process.
    for stream in (sys.stdout,sys.stderr):
        if hasattr(stream,'reconfigure'):stream.reconfigure(encoding='utf-8',errors='backslashreplace')
    arguments=list(sys.argv[1:] if argv is None else argv)
    if arguments and arguments[0] in {'.login','.logout','.auth'}:
        from asset_auth import command
        status=command(arguments)
        if status:raise SystemExit(status)
        return
    p=argparse.ArgumentParser(description='Standalone Luau + developing Roblox Engine API, using the supplied original VM',
        allow_abbrev=False,
        epilog='Asset login: run.py .login [--api-key], .auth or .logout (no script/binary needed).')
    p.add_argument('script',type=Path)
    p.add_argument('--binary',type=Path,default=Path(r'D:/Release-RobloxStudioApp/RobloxStudio.app/Contents/MacOS/RobloxStudio'))
    p.add_argument('--mode',choices=['server','client','both'],default='server')
    p.add_argument('--duration',type=float,default=1)
    p.add_argument('--realtime',action='store_true',help='Pace scheduler events with the monotonic wall clock')
    p.add_argument('--memory-mb',type=int,default=256)
    p.add_argument('--viewport-width',type=int,default=1280,help='Headless UI viewport width in pixels')
    p.add_argument('--viewport-height',type=int,default=720,help='Headless UI viewport height in pixels')
    p.add_argument('--wall-timeout',type=float,help='Optional real-time deadline in seconds; stops the entire VM process tree (Windows)')
    p.add_argument('--model',type=Path,action='append',default=[],help='Import supported .rbxmx XML or .rbxm binary model data under Workspace; repeatable')
    args=p.parse_args(arguments)
    if not math.isfinite(args.duration) or args.duration<0:p.error('--duration must be finite and nonnegative')
    if args.memory_mb<=0:p.error('--memory-mb must be positive')
    if args.viewport_width<=0 or args.viewport_height<=0:p.error('Viewport dimensions must be positive')
    if args.wall_timeout is not None and (not math.isfinite(args.wall_timeout) or args.wall_timeout<=0):p.error('--wall-timeout must be finite and positive')
    if not args.script.exists():p.error(f'Script/project not found: {args.script}')
    if args.script.is_file() and args.script.suffix not in {'.lua','.luau'}:p.error('Expected a .lua or .luau file')
    if args.wall_timeout is not None:
        from host_limits import supervise
        try:raise SystemExit(supervise(arguments,args.wall_timeout))
        except KeyboardInterrupt:raise SystemExit(130) from None
        except OSError as error:raise ScriptFailure(f'VM process supervisor: {error}') from None
    from model_xml import read_model
    try:models=[read_model(path) for path in args.model]
    except (OSError,ValueError,subprocess.TimeoutExpired) as error:p.error(f'Model import: {error}')
    root=Path(__file__).parent
    runtime=Runtime(args.binary,memory_mb=args.memory_mb)
    try:
        runtime.open_libraries()
        with tempfile.TemporaryDirectory(prefix='recovery-luau-') as folder:
            working=Path(folder)
            execute_source(runtime,root,bootstrap(root,{'side':args.mode,'duration':args.duration,'realtime':args.realtime,'viewportSize':[args.viewport_width,args.viewport_height]}),working,'engine-bootstrap')
            source_count=0
            compilations=[]
            def load_source(file,text=None,label=None):
                nonlocal source_count
                source_count+=1
                diagnostic=label or file.resolve().as_posix()
                input_path=working/f'chunk-{source_count}.luau'
                output_path=working/f'chunk-{source_count}.luauc'
                input_path.write_text(text if text is not None else file.read_text(encoding='utf-8-sig'),encoding='utf-8')
                slots={}
                for side in ('server','client'):
                    name=f'__compiled_{source_count}_{side}'
                    slots[side]=name
                compilations.append((input_path,output_path,diagnostic,slots))
                return slots
            entry=project_entry(args.script,args.mode,load_source,models)
            if compilations:
                manifest=working/'compile-batch.txt'
                manifest.write_text(''.join(str(field)+'\0' for job in compilations for field in job[:3]),encoding='utf-8')
                try:subprocess.run([str(root/'recovery-luau-compile.exe'),'--batch',str(manifest)],check=True)
                except subprocess.CalledProcessError:raise ScriptFailure('Compilation failed; see source diagnostics above') from None
                for _,output_path,label,slots in compilations:
                    bytecode=output_path.read_bytes()
                    for name in slots.values():
                        runtime.load(bytecode,('@'+label).encode());runtime.publish_top(name)
            result=execute_source(runtime,root,entry,working,args.script.name)
            if result and result[0]:print(f'{int(result[0])} script thread(s) remain suspended.')
    finally:runtime.close()
    if runtime.output_errors:raise ScriptFailure('Host output failed: '+runtime.output_errors[0])
    if runtime.http.callback_errors:raise ScriptFailure('HTTP host callback failed: '+runtime.http.callback_errors[0])
    if runtime.backing_errors:raise RuntimeError(runtime.backing_errors)
    if runtime.owned:raise RuntimeError(f'Backing allocations remain: {len(runtime.owned)}')


if __name__=='__main__':
    try:main()
    except ScriptFailure as error:
        print(f'Execution failed: {error}',file=sys.stderr)
        sys.exit(1)
