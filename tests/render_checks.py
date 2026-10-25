"""Render callbacks cannot suspend and errors do not skip other bindings."""
import argparse
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--binary',default='D:/Release-RobloxStudioApp/RobloxStudio.app/Contents/MacOS/RobloxStudio')
    args=parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='render-callback-errors-') as directory:
        folder=Path(directory)
        for name,callback,expected in [('failure',"error('intentional render failure')",'intentional render failure'),
                                       ('yield','task.wait()','callback cannot yield')]:
            script=folder/(name+'.client.luau')
            script.write_text('''local run=game:GetService('RunService')
local count=0
run:BindToRenderStep('bad',1,function() CALLBACK end)
run:BindToRenderStep('good',2,function() assert(run:IsClient());count+=1 end)
task.wait(0.05)
assert(count>=2,'Other bindings must keep executing')
run:UnbindFromRenderStep('bad');run:UnbindFromRenderStep('good')
print('OTHER RENDER BINDINGS CONTINUED')
'''.replace('CALLBACK',callback),encoding='utf-8')
            result=subprocess.run([sys.executable,str(ROOT/'run.py'),str(script),'--binary',args.binary,
                '--mode','client','--duration','0.1','--wall-timeout','30'],capture_output=True,text=True,encoding='utf-8',timeout=40)
            output=result.stdout+result.stderr
            assert result.returncode==1 and expected in output and 'OTHER RENDER BINDINGS CONTINUED' in output,output
    print('RENDER CALLBACK ERROR, NON-YIELD AND CONTINUATION CHECKS PASSED')


if __name__=='__main__':main()
