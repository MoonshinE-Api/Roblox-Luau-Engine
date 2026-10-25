local run=game:GetService('RunService')
assert(run:IsServer())
local function rejects(fn,fragment)
    local ok,message=pcall(fn)
    assert(not ok and string.find(tostring(message),fragment,1,true),tostring(message))
end
local direct=Instance.new('BindableFunction')
rejects(function() return direct.OnInvoke end,'get is not available')
rejects(function() direct.OnInvoke=12 end,'Expected callback')
local invokingThread=coroutine.running()
direct.OnInvoke=function(...)
    assert(coroutine.running()~=invokingThread and run:IsServer())
    local args=table.pack(...)
    assert(args.n==4 and args[1]==17 and args[2]==nil and args[3]==false and args[4]==nil)
    return 'answer',nil,false,nil
end
local result=table.pack(direct:Invoke(17,nil,false,nil))
assert(result.n==4 and result[1]=='answer' and result[2]==nil and result[3]==false and result[4]==nil)
rejects(function() return direct.OnInvoke end,'get is not available')
direct.OnInvoke=function() end;assert(table.pack(direct:Invoke()).n==0)
direct.OnInvoke=function() return nil,nil,nil end;assert(table.pack(direct:Invoke()).n==3)
direct.OnInvoke=function() task.wait(0.02);error('callback-error-marker') end
rejects(function() direct:Invoke() end,'callback-error-marker')

local queued=Instance.new('BindableFunction')
local started,completed={},0
for index=1,80 do
    task.spawn(function()
        local response=table.pack(queued:Invoke(index,nil))
        assert(response.n==3 and response[1]==index*2 and response[2]==nil and response[3]==nil)
        completed+=1
    end)
end
task.wait(0.02);assert(#started==0 and completed==0)
queued.OnInvoke=function(value,...)
    assert(select('#',...)==1)
    table.insert(started,value)
    task.wait(0.02)
    return value*2,nil,nil
end
task.wait(0.05);assert(completed==80)
for index=1,80 do assert(started[index]==index) end
queued.OnInvoke=nil
task.delay(0.02,function() queued.OnInvoke=function() return 'reassigned' end end)
assert(queued:Invoke()=='reassigned')

local cancelled=Instance.new('BindableFunction')
local calleeFinished,callerFinished=false,false
cancelled.OnInvoke=function()
    task.wait(0.04);calleeFinished=true;return 'still running'
end
local caller=task.spawn(function() cancelled:Invoke();callerFinished=true end)
task.cancel(caller)
task.wait(0.06);assert(calleeFinished and not callerFinished)

local replacing=Instance.new('BindableFunction')
local oldResult
replacing.OnInvoke=function() task.wait(0.04);return 'old' end
task.spawn(function() oldResult=replacing:Invoke() end)
replacing.OnInvoke=function() return 'new' end
assert(replacing:Invoke()=='new')
task.wait(0.06);assert(oldResult=='old')
local recursive=Instance.new('BindableFunction')
recursive.OnInvoke=function(depth) return if depth==0 then 1 else recursive:Invoke(depth-1)+1 end
assert(recursive:Invoke(12)==13)

local cloned=direct:Clone()
local cloneResult
local cloneCaller=task.spawn(function() cloneResult=cloned:Invoke() end)
task.wait(0.02);assert(cloneResult==nil and coroutine.status(cloneCaller)=='suspended')
cloned.OnInvoke=function() return 'clone has its own callback' end
task.wait(0.02);assert(cloneResult=='clone has its own callback')
local reentrant=Instance.new('BindableFunction')
local answers={}
for index=1,3 do task.spawn(function() answers[index]=reentrant:Invoke(index) end) end
reentrant.OnInvoke=function(value)
    assert(value==1)
    reentrant.OnInvoke=nil
    task.wait(0.02)
    return 'first'
end
task.wait(0.03);assert(answers[1]=='first' and answers[2]==nil and answers[3]==nil)
reentrant.OnInvoke=function(value) return value*10 end
task.wait(0.02);assert(answers[2]==20 and answers[3]==30)
local event=Instance.new('BindableEvent')
direct.OnInvoke=function() return event.Event:Wait() end
task.delay(0.02,function() event:Fire('signal',nil,3) end)
result=table.pack(direct:Invoke())
assert(result.n==3 and result[1]=='signal' and result[2]==nil and result[3]==3)
local remote=Instance.new('RemoteFunction')
rejects(function() return remote.OnServerInvoke end,'get is not available')
rejects(function() remote.OnClientInvoke=function() end end,'only be implemented on the client')
rejects(function() remote:InvokeServer() end,'requires client context')
for _,object in {direct,queued,cancelled,replacing,recursive,cloned,reentrant,event,remote} do object:Destroy() end
print('YIELDING FUNCTION CALLBACKS, QUEUES, TUPLES, ERRORS, REASSIGNMENT AND CANCELLATION PASSED',completed)
