local players,teams=game:GetService('Players'),game:GetService('Teams')
local run=game:GetService('RunService')
local baseline=#players:GetPlayers()
assert(#teams:GetTeams()==0)
local red=Instance.new('Team');red.Name='Red'
assert(red.TeamColor==BrickColor.new(1) and red.AutoAssignable and red.AutoColorCharacters and red.Score==0)
assert(not pcall(function() red:GetPlayers() end))
red.TeamColor=BrickColor.new('Bright red');red.AutoAssignable=false;red.Parent=teams
local blue=Instance.new('Team',teams);blue.Name='Blue';blue.TeamColor=BrickColor.new('Bright blue');blue.AutoAssignable=false
local snapshot=teams:GetTeams();assert(snapshot[1]==red and snapshot[2]==blue)
table.clear(snapshot);assert(#teams:GetTeams()==2)
local folder=Instance.new('Folder',teams)
assert(#teams:GetTeams()==2)
local p=Instance.new('Player');p.Name='TestPlayer'
assert(p.Neutral and p.TeamColor==BrickColor.new(1) and p.Team==nil)
assert(not pcall(function() p.Team=red end))
assert(not pcall(function() p.Team=nil end))
p.Parent=players
local changes={}
local removed=red.PlayerRemoved:Connect(function(player)
    assert(player==p);table.insert(changes,'-red')
end)
local added=red.PlayerAdded:Connect(function(player)
    assert(player==p);table.insert(changes,'+red')
end)
local connection=p:GetPropertyChangedSignal('Team'):Connect(function() table.insert(changes,'team') end)
p.Team=red
assert(p.Team==red and not p.Neutral and p.TeamColor==red.TeamColor)
assert(table.concat(changes,',')=='+red,team' and red:GetPlayers()[1]==p)
p.Team=red;assert(#changes==2)
p.Neutral=true
assert(p.Team==nil and p.TeamColor==red.TeamColor and #red:GetPlayers()==0)
assert(table.concat(changes,',')=='+red,team,-red,team')
p.TeamColor=blue.TeamColor;assert(p.Neutral and p.Team==nil and #changes==4)
p.Neutral=false;assert(p.Team==blue and blue:GetPlayers()[1]==p)
local duplicate=Instance.new('Team');duplicate.Name='Duplicate';duplicate.AutoAssignable=false
duplicate.TeamColor=blue.TeamColor;duplicate.Parent=teams
assert(duplicate:GetPlayers()[1]==p and p.Team==blue)
local duplicateAdded=0
duplicate.PlayerAdded:Connect(function(player) assert(player==p);duplicateAdded+=1 end)
p.Team=duplicate
assert(p.Team==blue and duplicateAdded==0)
local oldColor=blue.TeamColor
blue.TeamColor=BrickColor.new('Bright yellow')
assert(p.Team==duplicate and p.TeamColor==oldColor and duplicateAdded==1 and #blue:GetPlayers()==0)
duplicate.Parent=nil
assert(p.Team==nil and not p.Neutral and p.TeamColor==oldColor)
assert(not pcall(function() duplicate:GetPlayers() end))
duplicate.Parent=teams;assert(p.Team==duplicate and duplicateAdded==2)
blue.TeamColor=oldColor;assert(p.Team==blue)
p.Team=nil;assert(p.Neutral and p.TeamColor==oldColor and #duplicate:GetPlayers()==0)
assert(not pcall(function() p.Team=Instance.new('Part') end))
assert(not pcall(function() p.Team=Instance.new('Team') end))
assert(not pcall(function() p.Neutral=1 end))
assert(not pcall(function() p.TeamColor=Color3.new() end))
assert(not pcall(function() blue.TeamColor='Bright red' end))
assert(not pcall(function() blue.AutoAssignable=1 end))
red.Score=17.9;assert(red.Score==17)
red.Score=-9.8;assert(red.Score==-9)
red.Score=math.huge;assert(red.Score==-2147483648)
local copy=red:Clone();assert(copy.TeamColor==red.TeamColor and not copy.AutoAssignable and copy.Score==red.Score)
assert(not pcall(function() copy:GetPlayers() end));copy:Destroy()

-- Removing a player updates the roster before the team's leave event.
connection:Disconnect();removed:Disconnect();added:Disconnect()
p.Team=red
local leaving=0
local leave=red.PlayerRemoved:Connect(function(player)
    assert(player==p and p.Parent==players and p.Team==red and #red:GetPlayers()==0)
    leaving+=1
end)
p.Parent=nil;assert(leaving==1 and p.Team==nil and not p.Neutral)
leave:Disconnect();p:Destroy()
duplicate:Destroy();folder:Destroy()

-- Server-side joins choose the first smallest eligible team, without
-- rebalancing existing members when AutoAssignable changes.
red.AutoAssignable=true;blue.AutoAssignable=true
local records={}
for i=1,6 do
    local player=Instance.new('Player');player.Name='Balanced'..i;player.Parent=players;records[i]=player
    if run:IsServer() then assert(player.Team==(if i%2==1 then red else blue))
    else assert(player.Neutral and player.Team==nil) end
end
if run:IsServer() then
    assert(#red:GetPlayers()==3 and #blue:GetPlayers()==3)
    red.AutoAssignable=false
    local extra=Instance.new('Player',players);assert(extra.Team==blue);table.insert(records,extra)
    teams:RebalanceTeams();assert(records[1].Team==red and #red:GetPlayers()==3)
end
for _,player in records do player:Destroy() end
blue:Destroy();red:Destroy()
assert(#teams:GetTeams()==0 and #players:GetPlayers()==baseline)

-- Team assignment callbacks may yield; the membership update is already visible.
local gold=Instance.new('Team',teams);gold.TeamColor=BrickColor.new('Gold');gold.AutoAssignable=false
local finished=false
gold.PlayerAdded:Connect(function(player)
    assert(player.Team==gold and gold:GetPlayers()[1]==player)
    task.wait();assert(player.Team==gold);finished=true
end)
local last=Instance.new('Player',players);last.Team=gold
task.wait(.03);assert(finished)
last:Destroy();gold:Destroy()
print('TEAM MEMBERSHIP, DUPLICATE COLORS, JOIN BALANCING AND EVENTS PASSED',run:IsClient())
