-- 0.735 bridges: script/LuaRaycastParamsBridge.c, LuaOverlapParamsBridge.c.
-- Newer IncludeInstances/ExcludeInstances/Margin/SizeGradient are not in these bridges.
return function(R)
    local state=setmetatable({}, {__mode="k"})
    R.queryParams=state
    local function instances(value,nested)
        assert(type(value)=="table","Expected an Instance array")
        local output,visiting={},{}
        local function visit(list)
            assert(not visiting[list],"Cyclic filter table")
            visiting[list]=true
            for _,item in list do
                if typeof(item)=="Instance" then table.insert(output,item)
                elseif nested and type(item)=="table" then visit(item)
                else error("Filter must contain Instances"..(if nested then " or tables" else ""),3) end
            end
            visiting[list]=nil
        end
        visit(value)
        return output
    end
    local function constructor(name,overlap)
        local library,methods={},{}
        function methods:AddToFilter(input)
            local data=state[self];assert(data and data.name==name,"Invalid query parameter receiver")
            local additions=if typeof(input)=="Instance" then {input} else instances(input,true)
            for _,item in additions do table.insert(data.FilterDescendantsInstances,item) end
        end
        function library.new()
            local data={name=name,FilterDescendantsInstances={},FilterType=R.Enum.RaycastFilterType.Exclude,
                CollisionGroup="Default",RespectCanCollide=false,BruteForceAllSlow=false}
            if overlap then data.MaxParts,data.Tolerance=0,0 else data.IgnoreWater=false end
            local object=R.proxy();state[object]=data
            local mt=getmetatable(object)
            mt.__type,mt.__metatable=name,name
            mt.__tostring=function() return name end
            mt.__index=function(_,key)
                if methods[key] then return methods[key] end
                if key=="FilterDescendantsInstances" then return table.clone(data[key]) end
                if key~="name" and data[key]~=nil then return data[key] end
                error(key.." is not a valid member of "..name,2)
            end
            mt.__newindex=function(_,key,value)
                if key=="FilterDescendantsInstances" then data[key]=instances(value,false)
                elseif key=="FilterType" then
                    assert(typeof(value)=="EnumItem" and value.EnumType==R.Enum.RaycastFilterType,"Expected Enum.RaycastFilterType")
                    data[key]=value
                elseif key=="CollisionGroup" then assert(type(value)=="string","Expected collision group string");data[key]=value
                elseif key=="RespectCanCollide" or key=="BruteForceAllSlow" or (not overlap and key=="IgnoreWater") then
                    -- These 0.735 setters use lua_toboolean, not a strict boolean conversion.
                    data[key]=value~=nil and value~=false
                elseif overlap and key=="MaxParts" then
                    -- Original bridge converts through lua_tonumberx and then int32.
                    local number=tonumber(value) or 0
                    data[key]=if number~=number or number>=2147483648 or number< -2147483648 then -2147483648 else math.modf(number)
                elseif overlap and key=="Tolerance" then
                    assert(type(value)=="number" and value>=0 and value<=0.0501,"Tolerance must be between 0 and 0.05")
                    -- The upper bound is the documented default; original permits a live FFlag override.
                    data[key]=value
                else error(key.." is not a valid member of "..name,2) end
            end
            return object
        end
        R.datatypes[name]=table.freeze(library)
    end
    constructor("RaycastParams",false)
    constructor("OverlapParams",true)
end
