"""Run datatype and transform regression suites through Fiu inside the engine."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
CASES=['datatype_math','regions','cframe_rotation','part_transforms','attachments','environment','sky','callbacks','players','humanoids','teams']


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--binary',type=Path,default=Path('D:/Release-RobloxStudioApp/RobloxStudio.app/Contents/MacOS/RobloxStudio'))
    args=parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='fiu-engine-geometry-') as folder:
        work=Path(folder);project=work/'project';project.mkdir()
        shutil.copyfile(ROOT/'tests/vendor/Fiu.luau',project/'Fiu.luau')
        lines=["local Fiu=require(script.Parent.Fiu)","local settings=Fiu.luau_newsettings()",
               "settings.vectorCtor=Vector3.new;settings.vectorSize=3"]
        hashes={}
        for name in CASES:
            source=ROOT/'tests'/(name+'.luau');bytecode=work/(name+'.luauc')
            hashes[name]=hashlib.sha256(source.read_bytes()).hexdigest()
            subprocess.run([str(ROOT/'recovery-luau-compile.exe'),str(source),str(bytecode)],check=True)
            compiled=bytecode.read_bytes();assert compiled[0]==9
            literal='"'+''.join(f'\\{b:03d}' for b in compiled)+'"'
            lines.extend(['do',f'local execute,close=Fiu.luau_load({literal},getfenv(),settings)',
                          'execute();close()',f"print('NESTED GEOMETRY SUITE PASSED','{name}')",'end'])
        (project/'Main.server.luau').write_text('\n'.join(lines),encoding='utf-8')
        result=subprocess.run([sys.executable,str(ROOT/'run.py'),str(project),'--duration','1','--wall-timeout','60','--binary',str(args.binary)],
                              capture_output=True,text=True,encoding='utf-8',timeout=75)
        output=result.stdout+result.stderr
        assert result.returncode==0,output
        for name in CASES:assert 'NESTED GEOMETRY SUITE PASSED\t'+name in output
        report={'status':'PASS','suites':CASES,'interpreter':'Fiu','bytecode_version':9,
                'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'vector_constructor':'Engine Vector3.new','source_sha256':hashes,
                'interpreter_sha256':hashlib.sha256((ROOT/'tests/vendor/Fiu.luau').read_bytes()).hexdigest(),
                'output':output.strip(),'full_compatibility_proven':False}
        (ROOT/'data/nested_geometry_comparison.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        print(output.strip())


if __name__=='__main__':main()
