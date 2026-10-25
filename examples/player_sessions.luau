-- Local Player records exercise server scripts; they do not connect real clients.
local players=game:GetService('Players')
local store=game:GetService('DataStoreService'):GetDataStore('PlayerSessionExample')
local sessions={}
local function joined(player)
    local record={score=0,characters=0}
    sessions[player]=record
    record.added=player.CharacterAdded:Connect(function(character)
        record.characters+=1
        print('CHARACTER READY',player.Name,character.Name)
    end)
    record.removing=player.CharacterRemoving:Connect(function(character)
        print('CHARACTER REMOVING',player.Name,character.Name)
    end)
end
players.PlayerAdded:Connect(joined)
for _,player in players:GetPlayers() do joined(player) end
players.PlayerRemoving:Connect(function(player,reason)
    local record=sessions[player]
    if not record then return end
    store:SetAsync(tostring(player.UserId),{score=record.score,characters=record.characters,reason=reason.Name})
    record.added:Disconnect();record.removing:Disconnect();sessions[player]=nil
    print('SESSION SAVED',player.Name,record.score,record.characters)
end)
local player=Instance.new('Player');player.Name='ScriptedRecord';player.UserId=735100;player.Parent=players
local character=Instance.new('Model',workspace);character.Name='LocalCharacter'
local head=Instance.new('Part',character);head.Name='Head';head.Position=Vector3.new(10,5,0)
player.Character=character
assert(players:GetPlayerFromCharacter(character)==player)
assert(player:DistanceFromCharacter(Vector3.new(13,9,0))==5)
sessions[player].score=42
player.Character=nil;player.Parent=nil
local saved=store:GetAsync('735100');assert(saved.score==42 and saved.characters==1)
player:Destroy();character:Destroy()
print('PLAYER SESSION, CHARACTER AND SAVE EXAMPLE PASSED')
