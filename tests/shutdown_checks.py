"""Close callback lifecycle, persistence, graceful interrupt and forced stop."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--binary',default='D:/Release-RobloxStudioApp/RobloxStudio.app/Contents/MacOS/RobloxStudio')
    args=parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='shutdown-checks-') as directory:
        folder=Path(directory);database=folder/'saves.sqlite3'
        def case(name,source):
            directory=folder/name;directory.mkdir()
            path=directory/(name+'.luau');path.write_text(source,encoding='utf-8');return path
        def execute(path,flags=(),timeout=45):
            return subprocess.run([sys.executable,str(ROOT/'run.py'),str(path),'--binary',args.binary,*flags],
                                  capture_output=True,text=True,encoding='utf-8',timeout=timeout)
        writer=case('writer',"""local store=game:GetService('DataStoreService'):GetDataStore('ShutdownChecks')
game:BindToClose(function(reason)
    task.wait(.02)
    store:SetAsync('profile',{saved=true,reason=reason.Name})
    print('SHUTDOWN DATA SAVED')
end)
print('SHUTDOWN WRITER READY')
""")
        reader=case('reader',"""local value=game:GetService('DataStoreService'):GetDataStore('ShutdownChecks'):GetAsync('profile')
assert(value.saved and value.reason=='DeveloperShutdown');print('SHUTDOWN SAVE SURVIVED PROCESS EXIT')
""")
        result=execute(writer,['--duration','.1','--data-store',str(database)])
        assert result.returncode==0 and 'SHUTDOWN DATA SAVED' in result.stdout,(result.stdout,result.stderr)
        result=execute(reader,['--duration','0','--data-store',str(database)])
        assert result.returncode==0 and 'SURVIVED PROCESS EXIT' in result.stdout,(result.stdout,result.stderr)
        broken=case('broken',"""game:BindToClose(function() task.wait(.02);error('shutdown-callback-error') end)
game:BindToClose(function() task.wait(.04);print('OTHER CLOSE CALLBACK FINISHED') end)
""")
        result=execute(broken,['--duration','.1'])
        assert result.returncode==1 and result.stdout.count('ERROR: ')==1 and 'broken.luau:1' in result.stdout,(result.stdout,result.stderr)
        assert 'OTHER CLOSE CALLBACK FINISHED' in result.stdout
        destroyed=case('destroyed',"game:BindToClose(function() error('DESTROYED CALLBACK EXECUTED') end);script:Destroy()")
        result=execute(destroyed,['--duration','.1'])
        assert result.returncode==0 and 'callback was destroyed' in result.stdout and 'DESTROYED CALLBACK EXECUTED' not in result.stdout,(result.stdout,result.stderr)
        expired=case('expired',"game:BindToClose(function() task.wait(100);error('EXPIRED CALLBACK RESUMED') end)")
        result=execute(expired,['--duration','.1'])
        assert result.returncode==0 and 'shutdown callback budget exceeded' in result.stdout and 'EXPIRED CALLBACK RESUMED' not in result.stdout,(result.stdout,result.stderr)
        # The helper raises KeyboardInterrupt in the supervisor. It verifies the
        # owned process is already dead before the run returns status 130.
        helper=folder/'interrupt.py'
        helper.write_text('''import _thread,ctypes as C,sys,threading
sys.path.insert(0,sys.argv[1])
import host_limits,run
if __name__=='__main__':
    observed=[]
    original=host_limits.WindowsJob.assign
    def assign(self,process):
        original(self,process)
        api=C.WinDLL('kernel32',use_last_error=True)
        api.OpenProcess.argtypes=[C.c_uint32,C.c_int,C.c_uint32];api.OpenProcess.restype=C.c_void_p
        observed.append(api.OpenProcess(0x100000,False,process.pid))
    host_limits.WindowsJob.assign=assign
    timers=[threading.Timer(float(value),_thread.interrupt_main) for value in sys.argv[2].split(',')]
    for timer in timers:timer.daemon=True;timer.start()
    try:run.main(sys.argv[3:])
    except SystemExit as error:
        for timer in timers:timer.cancel()
        assert error.code==130,error.code
        assert observed and observed[0]
        api=C.WinDLL('kernel32',use_last_error=True)
        api.WaitForSingleObject.argtypes=[C.c_void_p,C.c_uint32];api.WaitForSingleObject.restype=C.c_uint32
        api.CloseHandle.argtypes=[C.c_void_p];api.CloseHandle.restype=C.c_int
        try:assert api.WaitForSingleObject(observed[0],0)==0,'Worker survived interrupt'
        finally:api.CloseHandle(observed[0])
        print('SHUTDOWN WORKER EXIT VERIFIED')
    else:raise AssertionError('Perpetual host returned before interrupt')
''',encoding='utf-8')
        def interrupt(path,timers,flags=()):
            result=subprocess.run([sys.executable,str(helper),str(ROOT),timers,str(path),'--binary',args.binary,
                                   '--no-player','--run-forever',*flags],capture_output=True,text=True,encoding='utf-8',timeout=40)
            assert result.returncode==0 and 'SHUTDOWN WORKER EXIT VERIFIED' in result.stdout,(result.returncode,result.stdout,result.stderr)
            assert 'Traceback' not in result.stdout+result.stderr,(result.stdout,result.stderr)
            return result
        grace_database=folder/'grace.sqlite3'
        result=interrupt(writer,'12',['--data-store',str(grace_database)])
        assert 'SHUTDOWN WRITER READY' in result.stdout and 'SHUTDOWN DATA SAVED' in result.stdout,(result.stdout,result.stderr)
        assert 'Shutdown requested' in result.stderr,result.stderr
        result=execute(reader,['--duration','0','--data-store',str(grace_database)])
        assert result.returncode==0 and 'SURVIVED PROCESS EXIT' in result.stdout,(result.stdout,result.stderr)
        frozen=case('frozen',"game:BindToClose(function() print('FROZEN CLOSE CALLBACK ENTERED');while true do end end);print('FROZEN SERVER READY')")
        started=time.monotonic();result=interrupt(frozen,'12,14')
        assert 'FROZEN CLOSE CALLBACK ENTERED' in result.stdout,(result.stdout,result.stderr)
        assert time.monotonic()-started<22
        hard=case('hard',"game:BindToClose(function() print('DEADLINE MUST NOT WAIT FOR CLOSE') end);print('HARD DEADLINE READY')")
        result=execute(hard,['--run-forever','--wall-timeout','15'])
        assert result.returncode==124 and 'HARD DEADLINE READY' in result.stdout,(result.stdout,result.stderr)
        assert 'DEADLINE MUST NOT WAIT FOR CLOSE' not in result.stdout
    (ROOT/'data/shutdown_comparison.json').write_text(json.dumps({'status':'PASS','checks':[
        'close callback persistence across processes','independent callbacks and source errors',
        'destroyed script callback skipped','30 simulated second close budget','graceful interrupt executes save',
        'second interrupt stops non-yielding callback','hard deadline remains immediate','no worker survives']},indent=2)+'\n',encoding='utf-8')
    print('SERVER SHUTDOWN, SAVES, GRACEFUL INTERRUPT AND FORCED STOP CHECKS PASSED')


if __name__=='__main__':main()
