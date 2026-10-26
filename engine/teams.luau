-- Color-based team membership and local player assignment from build 735.
-- This module does not create connections, spawn avatars or simulate spawn pads.
return function(R)
    local M,G,S,E=R.classMethods,R.classGetters,R.classSetters,R.classEvents
    local players,teams=R.game:GetService('Players'),R.game:GetService('Teams')
    local previousTeams=setmetatable({}, {__mode='k'})
    local function initialize(object,data)
        local function property(name,kind,value) data.propertyTypes[name]=kind;data.props[name]=value end
        if data.class=='Player' then
            property('Neutral','boolean',true);property('TeamColor','BrickColor',R.datatypes.BrickColor.new(1))
        elseif data.class=='Team' then
            property('TeamColor','BrickColor',R.datatypes.BrickColor.new(1))
            property('AutoAssignable','boolean',true);property('AutoColorCharacters','boolean',true);property('Score','number',0)
        end
    end
    local init=R.initializeProperties
    function R.initializeProperties(object,data) init(object,data);initialize(object,data) end
    for _,object in players:GetChildren() do if object:IsA('Player') then initialize(object,R.instances[object]) end end
    M.Teams={}
    function M.Teams:GetTeams()
        local result={}
        for _,child in self:GetChildren() do if child:IsA('Team') then table.insert(result,child) end end
        return result
    end
    -- The deprecated native implementation is empty, including in build 735.
    function M.Teams:RebalanceTeams() end
    local function fromColor(color)
        for _,team in teams:GetChildren() do if team:IsA('Team') and team.TeamColor==color then return team end end
        return nil
    end
    local function currentTeam(player)
        if player.Neutral or not player:IsDescendantOf(R.game) then return nil end
        return fromColor(player.TeamColor)
    end
    local function setInternal(player,team)
        local old=previousTeams[player]
        if old==team then return end
        previousTeams[player]=team
        if old then R.fire(old,'PlayerRemoved',player) end
        if team then R.fire(team,'PlayerAdded',player) end
        R.changed(player,'Team')
    end
    local function refresh(player)
        if player:IsDescendantOf(R.game) then setInternal(player,currentTeam(player)) end
    end
    local function recalculate()
        for _,player in players:GetPlayers() do refresh(player) end
    end
    G.Player=G.Player or {};G.Player.Team=currentTeam
    function S.Player.Team(player,team)
        assert(team==nil or R.instances[team] and team:IsA('Team'),'Team requires Team or nil')
        assert(player.Parent==players,"Failed to set player's team because the player left the game")
        assert(team==nil or team.Parent==teams,'Setting Player.Team failed because team must be a child of the Teams service')
        if team then player.TeamColor=team.TeamColor;player.Neutral=false else player.Neutral=true end
    end
    function S.Player.Neutral(player,value)
        assert(type(value)=='boolean','Neutral requires boolean')
        local properties=R.instances[player].props
        if properties.Neutral==value then return end
        properties.Neutral=value;R.changed(player,'Neutral');refresh(player)
    end
    function S.Player.TeamColor(player,value)
        assert(typeof(value)=='BrickColor','TeamColor requires BrickColor')
        local properties=R.instances[player].props
        if properties.TeamColor==value then return end
        properties.TeamColor=value;R.changed(player,'TeamColor')
        if not player.Neutral then refresh(player) end
    end
    S.Team={}
    function S.Team.TeamColor(team,value)
        assert(typeof(value)=='BrickColor','TeamColor requires BrickColor')
        local properties=R.instances[team].props
        if properties.TeamColor==value then return end
        properties.TeamColor=value
        if team.Parent==teams then recalculate() end
        R.changed(team,'TeamColor')
    end
    function S.Team.Score(team,value)
        assert(type(value)=='number','Score requires number');value=R.toInt32(value)
        local properties=R.instances[team].props
        if properties.Score~=value then properties.Score=value;R.changed(team,'Score') end
    end
    M.Team={}
    function M.Team:GetPlayers()
        assert(self.Parent==teams,'Team:GetPlayers() failed because team must be a child of the Teams service')
        local result={}
        for _,player in players:GetPlayers() do
            if not player.Neutral and player.TeamColor==self.TeamColor then table.insert(result,player) end
        end
        return result
    end
    E.Team={PlayerAdded=true,PlayerRemoved=true}
    function R.playerJoining(player)
        setInternal(player,fromColor(player.TeamColor))
        if R.current().side=='client' then return end
        local chosen,minimum=nil,10000
        for _,team in teams:GetChildren() do
            if team:IsA('Team') and team.AutoAssignable then
                local count=#team:GetPlayers()
                if count<minimum then chosen,minimum=team,count end
            end
        end
        if chosen then player.TeamColor=chosen.TeamColor;player.Neutral=false end
    end
    function R.playerLeaving(player)
        local team=currentTeam(player)
        if team then R.fire(team,'PlayerRemoved',player) end
    end
    local after=R.parentChanged
    function R.parentChanged(object,old,parent)
        if after then after(object,old,parent) end
        if object:IsA('Team') and (old==teams or parent==teams) then recalculate() end
    end
end
