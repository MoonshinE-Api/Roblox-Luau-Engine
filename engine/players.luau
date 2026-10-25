-- Player records and manual character assignment in the headless object tree.
-- Creating a Player here does not create a network connection or load an avatar.
return function(R)
    local M,G,S,E=R.classMethods,R.classGetters,R.classSetters,R.classEvents
    local players=R.game:GetService('Players')
    local roster={}
    for _,child in players:GetChildren() do if child:IsA('Player') then table.insert(roster,child) end end
    function R.playerPresent(player) return table.find(roster,player)~=nil end
    G.Players={
        LocalPlayer=function() return if R.current().side=='client' then R.player else nil end,
        NumPlayers=function() return #roster end,
        numPlayers=function() return #roster end,
    }
    M.Players={}
    function M.Players:GetPlayers() return table.clone(roster) end
    M.Players.getPlayers=M.Players.GetPlayers
    function M.Players:GetPlayerByUserId(userId)
        assert(type(userId)=='number','Expected userId number')
        userId=math.modf(userId)
        for _,player in roster do if player.UserId==userId then return player end end
        return nil
    end
    function M.Players:GetPlayerFromCharacter(character)
        assert(character==nil or R.instances[character] and character:IsA('Model'),'Expected character Model or nil')
        if character==nil then return nil end
        for _,player in roster do if player.Character==character then return player end end
        return nil
    end
    E.Players={PlayerAdded=true,PlayerRemoving=true}
    E.Player={CharacterAdded=true,CharacterRemoving=true}
    local before=R.beforeParentChanged
    function R.beforeParentChanged(object,old,parent)
        if before then before(object,old,parent) end
        if old==players and object:IsA('Player') then
            local index=table.find(roster,object)
            if index then
                -- Native onChildRemoving updates the roster before firing
                -- PlayerRemoving, while the old Parent is still observable.
                table.remove(roster,index)
                R.fire(players,'PlayerRemoving',object,R.Enum.PlayerExitReason.Unknown)
            end
        end
    end
    local after=R.parentChanged
    function R.parentChanged(object,old,parent)
        if after then after(object,old,parent) end
        if parent==players and object:IsA('Player') and not R.playerPresent(object) then
            table.insert(roster,object)
            R.fire(players,'PlayerAdded',object)
        end
    end
    S.Player={}
    function S.Player.Character(player,character)
        assert(character==nil or R.instances[character] and character:IsA('Model'),'Character requires Model or nil')
        local properties=R.instances[player].props
        local previous=properties.Character
        if previous==character then return end
        if previous then
            R.fire(player,'CharacterRemoving',previous)
            if R.current().side=='server' and not R.instances[previous].locked then previous.Parent=nil end
        end
        properties.Character=character
        if character then R.fire(player,'CharacterAdded',character) end
        R.changed(player,'Character')
    end
    M.Player={}
    function M.Player:DistanceFromCharacter(point)
        assert(typeof(point)=='Vector3','DistanceFromCharacter requires Vector3')
        local character=self.Character
        local head=character and character:FindFirstChild('Head')
        if not head or not head:IsA('BasePart') then return 0 end
        local f32,position=R.float32,head.Position
        local x=f32(f32(point.X)-f32(position.X))
        local y=f32(f32(point.Y)-f32(position.Y))
        local z=f32(f32(point.Z)-f32(position.Z))
        return f32(math.sqrt(f32(f32(f32(x*x)+f32(y*y))+f32(z*z))))
    end
end
