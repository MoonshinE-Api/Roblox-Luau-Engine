local teams=game:GetService('Teams')
local team=Instance.new('Team');team.Name='SharedTeam';team.AutoAssignable=false
team.TeamColor=BrickColor.new('Bright red');team.Parent=teams
local done=Instance.new('BoolValue',game:GetService('ReplicatedStorage'));done.Name='TeamReady'
local serverEvents=0
team.PlayerAdded:Connect(function(player)
    assert(game:GetService('RunService'):IsServer())
    task.wait();assert(game:GetService('RunService'):IsServer())
    assert(player.Team==team);serverEvents+=1
end)
task.wait(.03)
done.Value=true
task.wait(.05)
assert(serverEvents==1)
assert(game:GetService('Players').LocalPlayer==nil)
print('SERVER TEAM CALLBACK CONTEXT PASSED')
