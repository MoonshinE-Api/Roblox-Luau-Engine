local players=game:GetService('Players')
local storage=game:GetService('ReplicatedStorage')
local run=game:GetService('RunService')
local player=players:GetPlayers()[1]
local probe=Instance.new('Folder',storage);probe.Name='RosterContextProbe'
local remote=Instance.new('RemoteEvent',probe);remote.Name='Broadcast'
local first=Instance.new('Model',workspace);first.Name='OldCharacter';player.Character=first
local seenAdded,seenRemoving=0,0
players.PlayerAdded:Connect(function(value) assert(run:IsServer() and value==player);seenAdded+=1 end)
players.PlayerRemoving:Connect(function(value)
    assert(run:IsServer() and value==player and value.Parent==players and players.NumPlayers==0)
    seenRemoving+=1
end)
if not probe:GetAttribute('ClientReady') then probe:GetAttributeChangedSignal('ClientReady'):Wait() end
remote:FireAllClients('before')
local second=Instance.new('Model',workspace);second.Name='NewCharacter';player.Character=second
assert(first.Parent==nil)
player.Parent=nil
remote:FireAllClients('must-not-deliver')
assert(players.NumPlayers==0 and seenRemoving==1)
player.Parent=players
assert(players.NumPlayers==1 and seenAdded==1)
remote:FireAllClients('after')
task.wait(.05)
assert(probe:GetAttribute('ClientComplete'))
player.Character=nil;first:Destroy();second:Destroy()
print('PLAYER SERVER ROSTER AND BROADCAST MEMBERSHIP CONTEXT PASSED')
