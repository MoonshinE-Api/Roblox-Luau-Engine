"""CLI propagation of callback errors and intentionally suspended invocations."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--binary',default='D:/Release-RobloxStudioApp/RobloxStudio.app/Contents/MacOS/RobloxStudio')
    args=parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='callback-cli-') as directory:
        folder=Path(directory)
        for name,source,status,marker in [
            ('unassigned',"local f=Instance.new('BindableFunction');f:Invoke();error('MUST NOT REACH')",0,'1 script thread(s) remain suspended.'),
            ('unhandled',"local f=Instance.new('BindableFunction')\nf.OnInvoke=function() task.wait(.02);error('unhandled-callback-marker') end\nf:Invoke()",1,'unhandled.luau:2'),
            ('handled',"local f=Instance.new('BindableFunction');f.OnInvoke=function() error('handled-callback-marker') end;local ok,err=pcall(function() f:Invoke() end);assert(not ok and string.find(err,'handled-callback-marker',1,true));print('HANDLED CALLBACK ERROR')",0,'HANDLED CALLBACK ERROR'),
        ]:
            case=folder/name;case.mkdir();path=case/(name+'.luau');path.write_text(source,encoding='utf-8')
            result=subprocess.run([sys.executable,str(ROOT/'run.py'),str(path),'--duration','.1','--binary',args.binary],
                                  capture_output=True,text=True,encoding='utf-8',timeout=30)
            output=result.stdout+result.stderr
            assert result.returncode==status and marker in output,(name,result.returncode,output)
            assert 'MUST NOT REACH' not in output and 'Traceback (most recent call last)' not in output,output
            assert output.count('ERROR: ')==(1 if name=='unhandled' else 0),output
    (ROOT/'data/callback_comparison.json').write_text(json.dumps({'status':'PASS','checks':[
        'missing callback suspends without an error','unhandled callback source location and exit status',
        'callee error reported once','pcall catches callee errors without failing the script']},indent=2)+'\n',encoding='utf-8')
    print('CALLBACK CLI ERRORS, SOURCE LOCATIONS AND SUSPENDED INVOCATIONS PASSED')


if __name__=='__main__':main()
