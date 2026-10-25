local run=game:GetService('RunService')
local storage=game:GetService('ReplicatedStorage')
local bind=Instance.new('BindableFunction',storage);bind.Name='PerSide'
local toServer=Instance.new('RemoteFunction',storage);toServer.Name='DelayedServer'
local toClient=Instance.new('RemoteFunction',storage);toClient.Name='DelayedClient'
bind.OnInvoke=function(value)
    assert(run:IsServer() and not run:IsClient())
    task.wait(0.02)
    return 'server-bind',value
end
task.delay(0.06,function()
    toServer.OnServerInvoke=function(player,value)
        assert(run:IsServer() and player==game:GetService('Players'):GetPlayers()[1])
        local label,argument=bind:Invoke(value)
        assert(label=='server-bind' and argument==value and run:IsServer())
        if value=='fail' then error('server-queued-error') end
        return 'server-reply',nil,value,nil
    end
end)
local player=game:GetService('Players'):GetPlayers()[1]
local result=table.pack(toClient:InvokeClient(player,31,nil))
assert(result.n==4 and result[1]=='client-reply' and result[2]==nil and result[3]==31 and result[4]==nil)
assert(run:IsServer())
local ok,message=pcall(function() toClient:InvokeClient(player,'fail') end)
assert(not ok and string.find(message,'client-queued-error',1,true))
assert(run:IsServer())
local event=Instance.new('RemoteEvent')
player.Parent=nil
assert(not pcall(function() event:FireClient(player) end))
assert(not pcall(function() toClient:InvokeClient(player) end))
player.Parent=game:GetService('Players')
storage:SetAttribute('ServerCallbackFinished',true)
print('QUEUED REMOTE SERVER CALLBACK CONTEXT AND RECIPIENT CHECKS PASSED')
