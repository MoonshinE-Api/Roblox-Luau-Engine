"""Real-time and nested-VM fleet movement with a cross-process shutdown save."""
import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--binary',default='D:/Release-RobloxStudioApp/RobloxStudio.app/Contents/MacOS/RobloxStudio')
    args=parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='bulk-movement-') as directory:
        work=Path(directory);project=work/'project';project.mkdir()
        database=work/'fleet.sqlite3';compiled=work/'fleet.luauc'
        source=ROOT/'examples/bulk_fleet.luau'
        subprocess.run([str(ROOT/'recovery-luau-compile.exe'),str(source),str(compiled)],check=True)
        bytecode=compiled.read_bytes();assert bytecode[0]==9
        shutil.copyfile(ROOT/'tests/vendor/Fiu.luau',project/'Fiu.luau')
        literal='"'+''.join(f'\\{b:03d}' for b in bytecode)+'"'
        (project/'Main.server.luau').write_text("local Fiu=require(script.Parent.Fiu)\nlocal settings=Fiu.luau_newsettings();settings.vectorCtor=Vector3.new;settings.vectorSize=3\nlocal execute,close=Fiu.luau_load("+literal+",getfenv(),settings)\nexecute()\n-- Keep Fiu callbacks alive through shutdown.\n",encoding='utf-8')
        for target,flags in ((source,['--realtime']),(project,[])):
            duration='3' if flags else '.3'
            result=subprocess.run([sys.executable,str(ROOT/'run.py'),str(target),'--no-player','--duration',duration,
                '--data-store',str(database),'--wall-timeout','45','--binary',args.binary,*flags],
                capture_output=True,text=True,encoding='utf-8',timeout=55)
            output=result.stdout+result.stderr
            assert result.returncode==0 and 'MOVING FLEET SAVED' in output,output
        reader=work/'reader';reader.mkdir();script=reader/'read.luau'
        script.write_text("""local data=game:GetService('DataStoreService'):GetDataStore('MovingFleet'):GetAsync('last')
assert(data.count==160 and data.frames>=10)
local t=data.frames/60
assert(math.abs(data.position[1]-(6+math.sin(t+1)*3))<1e-6)
assert(math.abs(data.position[2]-(5+math.cos(t*2+1)))<1e-6 and data.position[3]==0)
print('NESTED FLEET SAVE SURVIVED PROCESS EXIT',data.count,data.frames)
""",encoding='utf-8')
        result=subprocess.run([sys.executable,str(ROOT/'run.py'),str(script),'--duration','0',
            '--data-store',str(database),'--binary',args.binary],capture_output=True,text=True,encoding='utf-8',timeout=30)
        assert result.returncode==0,(result.stdout,result.stderr)
    print('REALTIME AND FIU FLEET MOVEMENT, EVENTS, CLONING AND SHUTDOWN PERSISTENCE PASSED')


if __name__=='__main__':main()
