-- A local two-team round using players, characters, damage and persistent scores.
local players,teams=game:GetService('Players'),game:GetService('Teams')
local store=game:GetService('DataStoreService'):GetDataStore('TeamRounds')
local scores={Red=0,Blue=0}
for _,definition in {{'Red','Bright red'},{'Blue','Bright blue'}} do
    local team=Instance.new('Team');team.Name=definition[1]
    team.TeamColor=BrickColor.new(definition[2]);team.Parent=teams
end
local roster={}
for i=1,4 do
    local player=Instance.new('Player');player.Name='Local'..i;player.UserId=73000+i;player.Parent=players
    assert(player.Team and not player.Neutral)
    local model=Instance.new('Model',workspace);model.Name=player.Name
    local root=Instance.new('Part',model);root.Name='HumanoidRootPart';root.Anchored=true
    root.Position=Vector3.new(i*8,5,0)
    local head=Instance.new('Part',model);head.Name='Head';head.Anchored=true
    head.Position=root.Position+Vector3.new(0,3,0)
    player.Character=model
    local humanoid=Instance.new('Humanoid',model)
    humanoid.Died:Connect(function()
        local winner=if player.Team==teams.Red then 'Blue' else 'Red'
        scores[winner]+=1
        print(player.Name,'defeated; point awarded to',winner)
    end)
    table.insert(roster,{player=player,humanoid=humanoid})
end
assert(#teams.Red:GetPlayers()==2 and #teams.Blue:GetPlayers()==2)
local protection=Instance.new('ForceField',roster[1].player.Character)
roster[1].humanoid:TakeDamage(100);assert(roster[1].humanoid.Health==100)
protection:Destroy()
roster[1].humanoid:TakeDamage(100);roster[3].humanoid:TakeDamage(100)
task.wait(.04)
assert(scores.Blue==2 and scores.Red==0)
game:BindToClose(function(reason)
    store:SetAsync('latest',{scores=scores,reason=reason.Name,players=#roster})
    print('TEAM ROUND SAVED',scores.Red,scores.Blue,reason.Name)
end)
print('LOCAL TEAM ROUND COMPLETE')
