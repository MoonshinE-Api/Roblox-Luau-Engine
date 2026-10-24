"""Exercise real CLI errors, source locations and a project above 200 modules."""
from pathlib import Path
import subprocess
import sys
import tempfile

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from run import lua_literal
binary=sys.argv[1:]  # Optional --binary supplied by validate.ps1.


def run(path,extra=()):
    return subprocess.run([sys.executable,str(root/'run.py'),str(path),'--duration','0.2',*binary,*extra],
                          capture_output=True,text=True,timeout=60)


with tempfile.TemporaryDirectory(prefix='recovery-cli-') as folder:
    directory=Path(folder)
    valid=directory/'valid';valid.mkdir()
    (valid/'main.luau').write_text('local a=Instance.new("Part",workspace)\na.Name="suck"\nlocal b=a:Clone()\nprint(b.Name)\n',encoding='utf-8')
    result=run(valid/'main.luau')
    assert result.returncode==0 and 'suck' in result.stdout,(result.stdout,result.stderr)
    controls=''.join(chr(i) for i in range(32))+'09\\u0001"\u2064🚀'
    control_script=valid/'controls.luau'
    control_script.write_text('local text='+lua_literal(controls)+'\nlocal bytes='+lua_literal(list(controls.encode('utf-8')))+
        '\nassert(#text==#bytes);for i,v in bytes do assert(text:byte(i)==v) end;print("CONTROL STRING LITERALS PASSED")',encoding='utf-8')
    result=run(control_script)
    assert result.returncode==0 and 'CONTROL STRING LITERALS PASSED' in result.stdout,(result.stdout,result.stderr)
    batch_source=directory/'batch with spaces.luau'
    batch_source.write_text('local function f(x: number): number return x*2 end\nreturn f(...)',encoding='utf-8')
    single=directory/'single.luauc';batched=directory/'batched.luauc';manifest=directory/'jobs.txt'
    compiler=str(root/'recovery-luau-compile.exe')
    subprocess.run([compiler,str(batch_source),str(single)],check=True)
    manifest.write_text(str(batch_source)+'\0'+str(batched)+'\0'+'model.rbxmx::/TypedModule'+'\0',encoding='utf-8')
    subprocess.run([compiler,'--batch',str(manifest)],check=True)
    assert single.read_bytes()==batched.read_bytes(),'Batch compiler changed bytecode'
    batch_source.write_text('local =',encoding='utf-8')
    failed=subprocess.run([compiler,'--batch',str(manifest)],capture_output=True,text=True,encoding='utf-8')
    assert failed.returncode==1 and 'model.rbxmx::/TypedModule' in failed.stderr,failed.stderr
    manifest.write_text('malformed manifest',encoding='utf-8')
    failed=subprocess.run([compiler,'--batch',str(manifest)],capture_output=True,text=True)
    assert failed.returncode==1 and 'manifest' in failed.stderr,failed.stderr
    for flag,value in [('--duration','nan'),('--duration','inf'),('--duration','-1'),('--memory-mb','0')]:
        result=run(valid/'main.luau',(flag,value))
        assert result.returncode==2 and 'Traceback (most recent call last)' not in result.stderr,result.stderr
    for case,source,line in [('lowercase','local a=instance.new("part",workspace)\n',1),
                             ('location','local x=1\nlocal y=2\nerror("source-location-marker")\n',3),
                             ('syntax','local =\n',None)]:
        case_dir=directory/case;case_dir.mkdir()
        file=case_dir/(case+'.luau');file.write_text(source,encoding='utf-8')
        result=run(file)
        output=result.stdout+result.stderr
        assert result.returncode!=0 and 'Traceback (most recent call last)' not in output,output
        if line is not None:assert f'{case}.luau:{line}' in output,output
    project=directory/'large_project'
    modules=project/'ReplicatedStorage';modules.mkdir(parents=True)
    scripts=project/'ServerScriptService';scripts.mkdir()
    for i in range(205):(modules/f'Module{i}.luau').write_text(f'return {i}',encoding='utf-8')
    (scripts/'Main.server.luau').write_text('''local modules=game:GetService("ReplicatedStorage")
local sum=0
for _,module in modules:GetChildren() do sum+=require(module) end
assert(sum==205*204/2)
print("205 MODULE PROJECT PASSED")
''',encoding='utf-8')
    result=run(project)
    assert result.returncode==0 and '205 MODULE PROJECT PASSED' in result.stdout,(result.stdout,result.stderr)
print('CLI ERRORS, SOURCE LOCATIONS AND 205 MODULE CHECKS PASSED')
