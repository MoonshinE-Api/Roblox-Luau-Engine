"""Server-only clocks, perpetual host lifetime, deadline and interrupt cleanup."""
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
    with tempfile.TemporaryDirectory(prefix='headless-checks-') as directory:
        folder=Path(directory)
        script=folder/'server.luau'
        script.write_text('''local players=game:GetService('Players')
local run=game:GetService('RunService')
local lighting=game:GetService('Lighting')
assert(run:IsServer() and players.LocalPlayer==nil)
assert(#players:GetPlayers()==0 and #players:GetChildren()==0)
assert(players:GetPlayerByUserId(0)==nil)
assert(players:GetPlayerFromCharacter(Instance.new('Model'))==nil)
local remote=Instance.new('RemoteEvent')
local called=false;remote.OnClientEvent:Connect(function() called=true end)
remote:FireAllClients();assert(not called)
assert(not pcall(function() remote:FireClient(nil) end))
local fn=Instance.new('RemoteFunction')
assert(not pcall(function() fn:InvokeClient(nil) end))
local part=Instance.new('Part',workspace)
game:GetService('Debris'):AddItem(part,0.06)
local frames=0;local elapsed=0
run.Heartbeat:Connect(function(dt) assert(dt>0);frames+=1;elapsed+=dt end)
lighting.TimeOfDay='12:34:56'
local started=time()
task.delay(0.18,function()
    assert(time()-started>=0.18 and frames>=3 and elapsed>=0.05)
    assert(part.Parent==nil and lighting.TimeOfDay=='12:34:56')
    lighting:SetMinutesAfterMidnight(lighting:GetMinutesAfterMidnight()+1)
    assert(lighting.TimeOfDay=='12:35:56')
    print('HEADLESS TIMERS, FRAMES, DEBRIS AND STATIC CLOCK PASSED')
end)
print('SERVER ENTRY RETURNED')
''',encoding='utf-8')
        def execute(flags,path=script,timeout=45):
            return subprocess.run([sys.executable,str(ROOT/'run.py'),str(path),'--binary',args.binary,*flags],
                                  capture_output=True,text=True,encoding='utf-8',timeout=timeout)
        for flags in (['--duration','.4'],['--duration','.4','--realtime']):
            result=execute(['--no-player',*flags])
            assert result.returncode==0 and 'STATIC CLOCK PASSED' in result.stdout,(result.returncode,result.stdout,result.stderr)
        result=execute(['--no-player','--run-forever','--wall-timeout','16'])
        assert result.returncode==124 and 'STATIC CLOCK PASSED' in result.stdout,(result.returncode,result.stdout,result.stderr)
        assert 'wall-time limit' in result.stderr and 'Traceback' not in result.stderr
        for flags in (['--no-player','--mode','both'],['--no-player','--mode','client'],['--run-forever','--duration','1']):
            result=execute(flags);assert result.returncode==2,(flags,result.stdout,result.stderr)
        client=folder/'invalid.client.luau';client.write_text("error('MUST NOT RUN')",encoding='utf-8')
        result=execute(['--no-player'],client);assert result.returncode==2 and 'requires a server' in result.stderr
        # Raise a real KeyboardInterrupt in the supervisor while it owns a live
        # VM. The job must kill its worker before main returns exit code 130.
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
    timer=threading.Timer(12,_thread.interrupt_main);timer.daemon=True;timer.start()
    try:run.main(sys.argv[2:])
    except SystemExit as error:
        timer.cancel()
        assert error.code==130,error.code
        assert observed and observed[0]
        api=C.WinDLL('kernel32',use_last_error=True)
        api.WaitForSingleObject.argtypes=[C.c_void_p,C.c_uint32];api.WaitForSingleObject.restype=C.c_uint32
        api.CloseHandle.argtypes=[C.c_void_p];api.CloseHandle.restype=C.c_int
        try:assert api.WaitForSingleObject(observed[0],0)==0,'Worker survived interrupt'
        finally:api.CloseHandle(observed[0])
        print('INTERRUPT TERMINATED THE VM WORKER')
    else:raise AssertionError('Perpetual host returned before interrupt')
''',encoding='utf-8')
        result=subprocess.run([sys.executable,str(helper),str(ROOT),str(script),'--binary',args.binary,'--no-player','--run-forever'],
                              capture_output=True,text=True,encoding='utf-8',timeout=35)
        assert result.returncode==0 and 'STATIC CLOCK PASSED' in result.stdout and 'INTERRUPT TERMINATED' in result.stdout,(result.returncode,result.stdout,result.stderr)
        assert 'Traceback' not in result.stderr,result.stderr
    (ROOT/'data/headless_comparison.json').write_text(json.dumps({'status':'PASS','checks':[
        'server without synthetic player','player lookups and remote recipient checks','finite virtual and realtime frames',
        'timers and Debris after entry returns','Lighting clock changes only by script','perpetual host deadline',
        'mutually exclusive lifetime options','client mode rejection','KeyboardInterrupt exits 130 and kills worker']},indent=2)+'\n',encoding='utf-8')
    print('HEADLESS CONTINUOUS HOST AND PLAYER-FREE SERVER CHECKS PASSED')


if __name__=='__main__':main()
