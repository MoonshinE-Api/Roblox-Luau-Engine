"""Real infinite-loop termination, output/error status, process-tree cleanup."""
import argparse,ctypes as C,json,multiprocessing as mp,os,subprocess,sys,tempfile,time
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from host_limits import WindowsJob,worker_arguments


def tree_worker(ready,path):
    if not ready.wait(10):return
    child=subprocess.Popen([sys.executable,'-c','import time; time.sleep(300)'],creationflags=subprocess.CREATE_NO_WINDOW)
    Path(path).write_text(str(child.pid))
    child.wait()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--binary',default='D:/Release-RobloxStudioApp/RobloxStudio.app/Contents/MacOS/RobloxStudio');args=parser.parse_args()
    assert os.name=='nt'
    assert worker_arguments(['main.luau','--wall-timeout=1','--mode','both','--wall-timeout','2'])==['main.luau','--mode','both']
    assert worker_arguments(['--wall-timeout','1','--','--wall-timeout=literal.luau'])==['--','--wall-timeout=literal.luau']
    context=mp.get_context('spawn')
    with tempfile.TemporaryDirectory(prefix='host-limit-test-') as directory:
        folder=Path(directory);pidfile=folder/'descendant.pid';ready=context.Event()
        job=WindowsJob();process=context.Process(target=tree_worker,args=(ready,str(pidfile)));child_handle=None
        api=C.WinDLL('kernel32',use_last_error=True)
        api.OpenProcess.argtypes=[C.c_uint32,C.c_int,C.c_uint32];api.OpenProcess.restype=C.c_void_p
        api.WaitForSingleObject.argtypes=[C.c_void_p,C.c_uint32];api.WaitForSingleObject.restype=C.c_uint32
        api.CloseHandle.argtypes=[C.c_void_p];api.CloseHandle.restype=C.c_int
        try:
            process.start();job.assign(process);ready.set()
            deadline=time.monotonic()+15
            while not pidfile.exists() and time.monotonic()<deadline:time.sleep(.02)
            assert pidfile.exists(),'Tree worker failed to start'
            child_handle=api.OpenProcess(0x100000,False,int(pidfile.read_text()))
            assert child_handle,'Unable to observe descendant'
            job.close();process.join(5)
            assert not process.is_alive() and api.WaitForSingleObject(child_handle,0)==0,'Job left a descendant alive'
        finally:
            job.close()
            if process.pid is not None:
                if process.is_alive():process.kill();process.join(5)
                process.close()
            if child_handle:api.CloseHandle(child_handle)
        def run(name,source,flags):
            case=folder/name;case.mkdir(exist_ok=True)
            path=case/(name+'.luau');path.write_text(source,encoding='utf-8')
            start=time.monotonic()
            result=subprocess.run([sys.executable,str(root/'run.py'),str(path),'--binary',args.binary,*flags],capture_output=True,text=True,encoding='utf-8',timeout=80)
            assert 'Traceback (most recent call last)' not in result.stdout+result.stderr,(name,result.stdout,result.stderr)
            return result,time.monotonic()-start
        result,_=run('success',"local p=Instance.new('Part',workspace);p.Name='bounded';print('BOUNDED SUCCESS',p.Name)",['--wall-timeout','60'])
        assert result.returncode==0 and 'BOUNDED SUCCESS' in result.stdout,(result.returncode,result.stdout,result.stderr)
        result,_=run('failure',"error('deadline-error-marker')",['--wall-timeout=60'])
        assert result.returncode==1 and 'deadline-error-marker' in result.stdout+result.stderr and 'failure.luau:1' in result.stdout+result.stderr,(result.returncode,result.stdout,result.stderr)
        result,_=run('syntax','local =',['--wall-timeout','60'])
        assert result.returncode==1 and 'syntax.luau' in result.stderr,(result.returncode,result.stderr)
        result,elapsed=run('infinite',"print('INFINITE LOOP ENTERED');while true do end",['--duration','0.01','--wall-timeout','20'])
        assert result.returncode==124 and 'wall-time limit' in result.stderr and 'INFINITE LOOP ENTERED' in result.stdout,(result.returncode,result.stdout,result.stderr)
        assert 19<=elapsed<35,elapsed
        result,_=run('startup',"error('MUST NOT EXECUTE')",['--wall-timeout','.001'])
        assert result.returncode==124 and 'MUST NOT EXECUTE' not in result.stderr,(result.returncode,result.stderr)
        for value in ('0','-1','nan','inf'):
            result,_=run('invalid','print(1)',['--wall-timeout',value]);assert result.returncode==2 and 'finite and positive' in result.stderr,result.stderr
        result,_=run('abbreviated','print(1)',['--wall','1']);assert result.returncode==2 and 'unrecognized arguments' in result.stderr,result.stderr
    report={'status':'PASS','infinite_loop_timeout_seconds':20,'observed_elapsed_seconds':elapsed,
        'checks':['normal script/output','runtime and compiler error status/location','non-yielding infinite loop','deadline includes startup','invalid bounds','Job owns VM and descendant processes; no survivors'],
        'limits':['Optional CLI process deadline; not an in-VM instruction budget or security sandbox.','Forced timeout stops all script contexts together.']}
    (root/'data/host_limit_comparison.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('HOST DEADLINE/PROCESS TREE CHECKS PASSED')


if __name__=='__main__':main()
