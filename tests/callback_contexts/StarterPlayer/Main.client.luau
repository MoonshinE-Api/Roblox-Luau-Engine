local run=game:GetService('RunService')
local storage=game:GetService('ReplicatedStorage')
local bind=storage:WaitForChild('PerSide')
local toServer=storage:WaitForChild('DelayedServer')
local toClient=storage:WaitForChild('DelayedClient')
local bound=false
task.spawn(function()
    local label,value=bind:Invoke('before-client-assignment')
    assert(label=='client-bind' and value=='before-client-assignment' and run:IsClient())
    bound=true
end)
task.wait(0.02);assert(not bound,'Server BindableFunction callback leaked into the client')
bind.OnInvoke=function(value)
    assert(run:IsClient() and not run:IsServer())
    task.wait(0.02)
    return 'client-bind',value
end
local ok,message=pcall(function() toServer.OnServerInvoke=function() end end)
assert(not ok and string.find(message,'only be implemented on the server',1,true))
local result=table.pack(toServer:InvokeServer(19))
assert(result.n==4 and result[1]=='server-reply' and result[2]==nil and result[3]==19 and result[4]==nil)
assert(run:IsClient() and bound)
ok,message=pcall(function() toServer:InvokeServer('fail') end)
assert(not ok and string.find(message,'server-queued-error',1,true))
task.wait(0.02)
toClient.OnClientInvoke=function(value,...)
    assert(run:IsClient())
    if value~='fail' then assert(select('#',...)==1) end
    local label,argument=bind:Invoke(value)
    assert(label=='client-bind' and argument==value and run:IsClient())
    if value=='fail' then error('client-queued-error') end
    return 'client-reply',nil,value,nil
end
if not storage:GetAttribute('ServerCallbackFinished') then storage:GetAttributeChangedSignal('ServerCallbackFinished'):Wait() end
assert(run:IsClient())
print('QUEUED REMOTE CLIENT CALLBACK CONTEXT AND BINDABLE ISOLATION PASSED')
