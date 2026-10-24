local run=game:GetService("RunService")
local storage=game:GetService("ReplicatedStorage")
local side=require(storage.Side)
assert(side.side=="server")
local remote=Instance.new("RemoteFunction",storage)
remote.Name="BothDirections"
remote.OnServerInvoke=function(player,value)
    assert(run:IsServer() and not run:IsClient())
    assert(require(storage.Side)==side and player.UserId==1)
    task.wait(0.02)
    assert(run:IsServer() and require(storage.Side)==side)
    if value=="fail" then error("intentional server error") end
    return "server",value,nil,4
end
task.wait(0.1)
assert(remote:GetAttribute("ClientReady"))
local result=table.pack(remote:InvokeClient(game:GetService("Players"):GetPlayers()[1],7))
assert(result.n==4 and result[1]=="client" and result[2]==7 and result[3]==nil and result[4]==5)
assert(run:IsServer() and require(storage.Side)==side)
print("SERVER CALLBACK CONTEXT PASSED")
