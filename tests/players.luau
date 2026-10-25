local players=game:GetService('Players')
local run=game:GetService('RunService')
local baseline=players:GetPlayers()
local baselineCount=#baseline
assert(players.NumPlayers==baselineCount and players.numPlayers==baselineCount)
assert(#players:getPlayers()==baselineCount)
assert(not pcall(function() players.NumPlayers=9 end))
assert(not pcall(function() players.LocalPlayer=nil end))
assert(players:GetPlayerFromCharacter(nil)==nil)
assert(not pcall(function() players:GetPlayerByUserId({}) end))
assert(not pcall(function() players:GetPlayerFromCharacter(Instance.new('Part')) end))
local events={}
local added=players.PlayerAdded:Connect(function(player)
    assert(player.Parent==players and table.find(players:GetPlayers(),player))
    assert(players:GetPlayerByUserId(player.UserId)==player)
    table.insert(events,'+'..player.Name)
end)
local removing=players.PlayerRemoving:Connect(function(player,reason)
    assert(player.Parent==players and not table.find(players:GetPlayers(),player))
    assert(players:GetPlayerByUserId(player.UserId)==nil)
    assert(reason==Enum.PlayerExitReason.Unknown)
    table.insert(events,'-'..player.Name)
end)
local folder=Instance.new('Folder',players)
local first=Instance.new('Player',folder);first.Name='First';first.UserId=721735
assert(first.DisplayName=='' and players.NumPlayers==baselineCount and #events==0)
first.Parent=players
assert(players.NumPlayers==baselineCount+1 and events[1]=='+First')
local second=Instance.new('Player');second.Name='Second';second.UserId=-2147483648;second.Parent=players
assert(players:GetPlayerByUserId(-2147483648)==second and players:GetPlayerByUserId(999999)==nil)
local snapshot=players:GetPlayers();table.clear(snapshot)
assert(players.NumPlayers==baselineCount+2 and #players:GetPlayers()==baselineCount+2)
first.Parent=workspace
assert(events[3]=='-First' and players.NumPlayers==baselineCount+1)
first.Parent=players
local roster=players:GetPlayers()
assert(roster[#roster-1]==second and roster[#roster]==first)
second.UserId=4503599627370495
assert(players:GetPlayerByUserId(-2147483648)==nil and players:GetPlayerByUserId(4503599627370495)==second)

local a=Instance.new('Model',workspace);a.Name='FirstCharacter'
local head=Instance.new('Part',a);head.Name='Head';head.Position=Vector3.new(10,20,30)
local root=Instance.new('Part',a);root.Name='HumanoidRootPart';root.Position=Vector3.new(1000,0,0);a.PrimaryPart=root
local b=Instance.new('Model',workspace);b.Name='SecondCharacter'
local phases={}
first.CharacterRemoving:Connect(function(character)
    assert(first.Character==character)
    assert(players:GetPlayerFromCharacter(character)==first)
    table.insert(phases,'remove:'..character.Name)
end)
first.CharacterAdded:Connect(function(character)
    assert(first.Character==character and players:GetPlayerFromCharacter(character)==first)
    table.insert(phases,'add:'..character.Name)
end)
first:GetPropertyChangedSignal('Character'):Connect(function() table.insert(phases,'changed') end)
assert(first:DistanceFromCharacter(Vector3.zero)==0)
first.Character=a
assert(phases[1]=='add:FirstCharacter' and phases[2]=='changed')
assert(first:DistanceFromCharacter(Vector3.new(13,24,30))==5)
assert(not pcall(function() first:DistanceFromCharacter({}) end))
first.Character=a;assert(#phases==2)
assert(not pcall(function() first.Character=head end));assert(#phases==2 and first.Character==a)
first.Character=b
assert(phases[3]=='remove:FirstCharacter' and phases[4]=='add:SecondCharacter' and phases[5]=='changed')
assert(a.Parent==(if run:IsServer() then nil else workspace))
assert(first:DistanceFromCharacter(Vector3.zero)==0)
first.Character=nil
assert(phases[6]=='remove:SecondCharacter' and phases[7]=='changed')
assert(players:GetPlayerFromCharacter(a)==nil and players:GetPlayerFromCharacter(nil)==nil)
-- The character lookup searches roster references, not the model's parent.
local unparented=Instance.new('Model');second.Character=unparented
assert(players:GetPlayerFromCharacter(unparented)==second)
second.Parent=nil;assert(players:GetPlayerFromCharacter(unparented)==nil)
second.Parent=players;assert(players:GetPlayerFromCharacter(unparented)==second)
second.Character=nil
local fakeHead=Instance.new('Folder',unparented);fakeHead.Name='Head'
second.Character=unparented
assert(second:DistanceFromCharacter(Vector3.zero)==0)
second.Character=nil

-- A waiting coroutine resumes with the same Player reference after a join.
local awaited
local waiter=task.spawn(function() awaited=players.PlayerAdded:Wait() end)
local third=Instance.new('Player');third.Name='Third';third.UserId=991735;third.Parent=players
task.wait(0.02)
assert(coroutine.status(waiter)=='dead' and awaited==third)
third:Destroy();assert(players:GetPlayerByUserId(991735)==nil)
local transient=Instance.new('Player');transient.Name='Transient';transient.UserId=991736
local destroyOnJoin=players.PlayerAdded:Connect(function(player) if player==transient then player:Destroy() end end)
transient.Parent=players
assert(transient.Parent==nil and not table.find(players:GetPlayers(),transient))
destroyOnJoin:Disconnect()
local morph=Instance.new('Player');morph.Name='Morph';morph.UserId=991737;morph.Parent=players
local original=Instance.new('Model',workspace)
local replacement=Instance.new('Model',workspace)
local morphOnce=false
morph.CharacterAdded:Connect(function(character)
    if character==original and not morphOnce then morphOnce=true;morph.Character=replacement end
end)
morph.Character=original
assert(morphOnce and morph.Character==replacement)
morph.Character=nil;morph:Destroy();original:Destroy();replacement:Destroy()
first:Destroy();second:Destroy();folder:Destroy();a:Destroy();b:Destroy();unparented:Destroy()
added:Disconnect();removing:Disconnect()
assert(players.NumPlayers==baselineCount and #players:GetPlayers()==baselineCount)
for index,player in baseline do assert(players:GetPlayers()[index]==player) end
print('LIVE PLAYER ROSTER, REMOVAL TIMING, CHARACTER EVENTS AND HEAD DISTANCE CHECKS PASSED',#events)
