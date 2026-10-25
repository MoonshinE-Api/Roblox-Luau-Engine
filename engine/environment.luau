-- Typed environment state and lighting clock. No renderer or particle simulator.
return function(R)
    local catalog=R.environmentCatalog
    local types=R.datatypes
    local G,S,M,E=R.classGetters,R.classSetters,R.classMethods,R.classEvents
    local enumCache={}
    local function decode(record)
        local kind,value=record.kind,record.values
        if kind=='Instance?' then return nil end
        if string.sub(kind,1,5)=='Enum.' then
            local name=string.sub(kind,6)
            if not enumCache[name] then
                local map={};for _,item in R.Enum[name]:GetEnumItems() do map[item.Value]=item end;enumCache[name]=map
            end
            return assert(enumCache[name][value],'Unknown environment enum value')
        end
        if kind=='boolean' or kind=='number' or kind=='string' then return value end
        if kind=='BrickColor' then return types.BrickColor.new(value) end
        if kind=='NumberSequence' or kind=='ColorSequence' then
            local points={}
            for _,point in value[1] do
                table.insert(points,if kind=='NumberSequence' then types.NumberSequenceKeypoint.new(table.unpack(point))
                    else types.ColorSequenceKeypoint.new(point[1],types.Color3.new(table.unpack(point[2]))))
            end
            return types[kind].new(points)
        end
        return types[kind].new(table.unpack(value))
    end
    local function valid(record,value)
        if record.kind=='Instance?' then
            assert(value==nil or R.instances[value] and value:IsA(record.target),'Expected '..record.target..' or nil')
        elseif string.sub(record.kind,1,5)=='Enum.' then
            assert(typeof(value)=='EnumItem' and value.EnumType==R.Enum[string.sub(record.kind,6)],'Expected '..record.kind)
        else assert(typeof(value)==record.kind,'Expected '..record.kind) end
        return value
    end
    local function write(object,key,value)
        local d=R.instances[object];local record=assert(d.environmentRules[key])
        value=valid(record,value)
        if record.storage=='Float32' then value=R.float32(value)
        elseif record.storage=='Int32' then value=R.toInt32(value) end
        local bounds=d.environmentClamps[key]
        if bounds and value==value then
            if bounds[1] then value=math.max(bounds[1],value) end
            if bounds[2] then value=math.min(bounds[2],value) end
            if record.storage=='Float32' then value=R.float32(value) end
        end
        if typeof(value)=='Color3' then value=types.Color3.new(R.float32(value.R),R.float32(value.G),R.float32(value.B)) end
        if record.kind=='NumberSequence' and ((object:IsA('Beam') and key=='Transparency') or
            (object:IsA('Trail') and (key=='Transparency' or key=='WidthScale'))) then
            local points={}
            for _,point in value.Keypoints do
                table.insert(points,types.NumberSequenceKeypoint.new(point.Time,math.clamp(point.Value,-1e22,1e22),0))
            end
            value=types.NumberSequence.new(points)
        end
        if d.props[key]~=value then
            d.props[key]=value;R.changed(object,key)
            if object:IsA('Lighting') then R.fire(object,'LightingChanged',false)
            elseif object:IsA('Sky') and object.Parent and object.Parent:IsA('Lighting') then R.fire(object.Parent,'LightingChanged',true) end
        end
    end
    for class,fields in catalog.classes do
        S[class]=S[class] or {}
        for key in fields do S[class][key]=function(object,value) write(object,key,value) end end
    end
    local function initializeEnvironment(object,d)
        d.environmentRules={};d.environmentClamps={}
        local chain={};local class=d.class
        while class do table.insert(chain,1,class);class=R.classes[class] end
        for _,ancestor in chain do
            for key,record in catalog.classes[ancestor] or {} do
                d.environmentRules[key]=record;d.propertyTypes[key]=record.kind;d.props[key]=decode(record)
            end
            for key,bounds in (catalog.clamps or {})[ancestor] or {} do d.environmentClamps[key]=bounds end
        end
        if d.class=='Lighting' then d.props._lightingSeconds=math.modf(d.props.ClockTime*3600) end
    end
    local initialize=R.initializeProperties
    function R.initializeProperties(object,d) initialize(object,d);initializeEnvironment(object,d) end
    for object,d in R.instances do if d.class=='Lighting' then initializeEnvironment(object,d) end end
    R.noncreatable.Light=true;R.noncreatable.PostEffect=true
    -- ClockTime's native setter clamps hours before converting to whole seconds.
    local function normalizeSeconds(seconds)
        seconds=math.modf(seconds)
        seconds=(seconds+2147483648)%4294967296-2147483648
        return seconds%86400
    end
    local function clockWrite(self,seconds)
        assert(type(seconds)=='number' and seconds==seconds and math.abs(seconds)<9007199254,'Time outside supported range')
        seconds=normalizeSeconds(seconds)
        local d=R.instances[self]
        if d.props._lightingSeconds==seconds then return end
        d.props._lightingSeconds=seconds
        R.changed(self,'TimeOfDay');R.changed(self,'ClockTime');R.fire(self,'LightingChanged',false)
    end
    G.Lighting=G.Lighting or {}
    G.Lighting.ClockTime=function(self) return R.float32(R.instances[self].props._lightingSeconds/3600) end
    G.Lighting.TimeOfDay=function(self)
        local seconds=R.instances[self].props._lightingSeconds
        return string.format('%02d:%02d:%02d',math.floor(seconds/3600),math.floor(seconds/60)%60,seconds%60)
    end
    S.Lighting.ClockTime=function(self,value)
        assert(type(value)=='number','ClockTime requires number');value=R.float32(value)
        if value~=value then clockWrite(self,-2147483648);return end
        clockWrite(self,R.float32(math.clamp(value,0,24)*3600))
    end
    S.Lighting.TimeOfDay=function(self,value)
        assert(type(value)=='string','TimeOfDay requires string')
        local sign,hours,minutes,seconds=string.match(value,'^([+-]?)(%d+):(%d+):([%d%.]+)$')
        assert(hours and (string.match(seconds,'^%d+$') or string.match(seconds,'^%d+%.%d+$')),'Expected HH:MM:SS time')
        local total=tonumber(hours)*3600+tonumber(minutes)*60+tonumber(seconds)
        clockWrite(self,if sign=='-' then -total else total)
    end
    M.Lighting=M.Lighting or {}
    function M.Lighting:GetMinutesAfterMidnight() return R.instances[self].props._lightingSeconds/60 end
    function M.Lighting:SetMinutesAfterMidnight(value)
        assert(type(value)=='number','Expected minutes number');clockWrite(self,value*60)
    end
    function M.Lighting:GetMoonPhase() return 0.75 end
    M.Lighting.getMinutesAfterMidnight=M.Lighting.GetMinutesAfterMidnight
    M.Lighting.setMinutesAfterMidnight=M.Lighting.SetMinutesAfterMidnight
    E.Lighting={LightingChanged=true}
    local parentChanged=R.parentChanged
    function R.parentChanged(object,old,parent)
        if parentChanged then parentChanged(object,old,parent) end
        if object:IsA('Sky') then
            if old and old:IsA('Lighting') then R.fire(old,'LightingChanged',true) end
            if parent and parent:IsA('Lighting') then R.fire(parent,'LightingChanged',true) end
        end
    end
end
