local teams,players=game:GetService('Teams'),game:GetService('Players')
local team=teams:WaitForChild('SharedTeam')
local ready=game:GetService('ReplicatedStorage'):WaitForChild('TeamReady')
local clientEvents=0
team.PlayerAdded:Connect(function(player)
    assert(game:GetService('RunService'):IsClient() and players.LocalPlayer==player)
    task.wait();assert(game:GetService('RunService'):IsClient())
    clientEvents+=1
end)
while not ready.Value do task.wait() end
players.LocalPlayer.Team=team
task.wait(.04)
assert(clientEvents==1 and #team:GetPlayers()==1)
print('CLIENT TEAM CALLBACK CONTEXT PASSED')
