-- Health and force-field behavior; this does not implement humanoid locomotion,
-- rig constraints, network ownership, animation, or the full state machine.
return function(R)
    local M,G,S,E=R.classMethods,R.classGetters,R.classSetters,R.classEvents
    local tracked=setmetatable({}, {__mode='k'})
    local function metadata(object)
        local record=tracked[object]
        if not record then record={flags={server={},client={}},dead={}};tracked[object]=record end
        return record
    end
    local initialize=R.initializeProperties
    function R.initializeProperties(object,data)
        initialize(object,data)
        if data.class=='Humanoid' then metadata(object)
        elseif data.class=='ForceField' then data.propertyTypes.Visible='boolean';data.props.Visible=true end
    end
    local validate=R.validateParent
    function R.validateParent(object,parent)
        if validate then validate(object,parent) end
        assert(not (parent and object.ClassName=='ForceField' and parent:IsA('Workspace')),'ForceField cannot be parented to Workspace')
    end
    local function side() return if R.current().side=='client' then 'client' else 'server' end
    local function fireSide(object,event,currentSide,...)
        R.fireSignalSide(R.signal(object,event),currentSide,...)
    end
    local function health(object)
        local properties=R.instances[object].props
        local raw=properties.Health
        if raw~=raw then return raw end
        return math.min(properties.MaxHealth,math.max(0,raw))
    end
    G.Humanoid={Health=health}
    function G.Humanoid.RootPart(object)
        local model=object.Parent
        local root=model and model:IsA('Model') and model:FindFirstChild('HumanoidRootPart')
        return if root and root:IsA('BasePart') then root else nil
    end
    S.Humanoid={}
    function S.Humanoid.Health(object,value)
        assert(type(value)=='number','Health requires number');value=R.float32(value)
        local properties=R.instances[object].props
        if properties.Health==value then return end
        properties.Health=value
        R.changed(object,'Health');R.fire(object,'HealthChanged',health(object))
    end
    function S.Humanoid.MaxHealth(object,value)
        assert(type(value)=='number','MaxHealth requires number');value=R.float32(value)
        value=if value==value then math.max(value,0) else 0
        local properties=R.instances[object].props
        if properties.MaxHealth==value then return end
        properties.MaxHealth=value
        R.changed(object,'MaxHealth');R.fire(object,'HealthChanged',health(object))
    end
    local function protected(object)
        local root=G.Humanoid.RootPart(object)
        if root and root:FindFirstChildOfClass('ForceField') then return true end
        local parent=object.Parent
        while parent and not parent:IsA('Workspace') do
            if parent:FindFirstChildOfClass('ForceField') then return true end
            parent=parent.Parent
        end
        return false
    end
    M.Humanoid={}
    function M.Humanoid:TakeDamage(amount)
        assert(type(amount)=='number','TakeDamage requires number')
        if not protected(self) then self.Health=R.float32(self.Health-R.float32(amount)) end
    end
    M.Humanoid.takeDamage=M.Humanoid.TakeDamage
    local function stateValue(state)
        assert(typeof(state)=='EnumItem' and state.EnumType==R.Enum.HumanoidStateType,'Expected HumanoidStateType')
        return state.Value
    end
    function M.Humanoid:GetStateEnabled(state)
        local value=stateValue(state)
        if value>=17 then __host_print('WARNING: Invalid state passed to GetStateEnabled.');return true end
        return metadata(self).flags[side()][value]~=false
    end
    function M.Humanoid:SetStateEnabled(state,enabled)
        local value=stateValue(state)
        assert(type(enabled)=='boolean','Expected enabled boolean')
        if value>=17 then __host_print('WARNING: Invalid state passed to SetStateEnabled.');return end
        local currentSide=side()
        metadata(self).flags[currentSide][value]=enabled
        fireSide(self,'StateEnabledChanged',currentSide,state,enabled)
    end
    E.Humanoid={HealthChanged=true,Died=true,StateEnabledChanged=true}
    local simulate=R.simulate
    function R.simulate(dt)
        if simulate then simulate(dt) end
        local sides=if R.config.side=='both' then {'server','client'} else {if R.config.side=='client' then 'client' else 'server'}
        for humanoid,record in table.clone(tracked) do
            local data=R.instances[humanoid]
            if data and not data.locked and humanoid:IsDescendantOf(R.workspace) then
                if (record.dead.server or record.dead.client) and data.props.Health~=0 then humanoid.Health=0 end
                if health(humanoid)<=0 then
                    for _,currentSide in sides do
                        if not data.locked and humanoid:IsDescendantOf(R.workspace) and health(humanoid)<=0
                            and not record.dead[currentSide] and record.flags[currentSide][15]~=false then
                            record.dead[currentSide]=true
                            fireSide(humanoid,'Died',currentSide)
                        end
                    end
                end
            end
        end
    end
end
