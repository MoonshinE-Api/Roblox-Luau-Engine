return function(R)
    local native=__host_random
    local methods={}
    local function state(self)
        assert(typeof(self)=="Random","Expected Random")
        return R.values[self].state
    end
    local function numeric(value)
        local result=if type(value)=="number" then value elseif type(value)=="string" then tonumber(value) else nil
        assert(result~=nil,"Expected number")
        return result
    end
    local function wrap(data)
        return R.makeValue("Random",{state=data},function(_,key)
            if methods[key] then return methods[key] end
            error(tostring(key).." is not a valid member of Random",2)
        end,{
            __eq=function(a,b)
                return typeof(a)=="Random" and typeof(b)=="Random" and buffer.tostring(state(a))==buffer.tostring(state(b))
            end,
            __tostring=function() return "Random" end,
        })
    end
    local function new(seed)
        local data=buffer.create(8)
        if seed==nil then native(data,5) else
            seed=numeric(seed)
            if not (math.abs(seed)<=9007199254740991) then
                __host_print("Random.new seed outside [-9007199254740991, 9007199254740991]; clamped to 0")
                seed=0
            end
            native(data,0,seed)
        end
        return wrap(data)
    end
    function methods:NextNumber(...)
        local data=state(self)
        local n=select("#",...)
        if n==0 then return native(data,1) end
        assert(n>=2,"Random:NextNumber requires 0 or 2 arguments")
        local a,b=...
        return native(data,2,numeric(a),numeric(b))
    end
    function methods:NextInteger(minimum,maximum)
        return native(state(self),3,numeric(minimum),numeric(maximum))
    end
    function methods:NextUnitVector()
        return R.datatypes.Vector3.new(native(state(self),4))
    end
    function methods:Clone()
        local data=buffer.create(8);buffer.copy(data,0,state(self),0,8)
        return wrap(data)
    end
    function methods:Shuffle(array)
        local data=state(self)
        assert(type(array)=="table","Expected table")
        local n=#array
        for i=1,n do assert(rawget(array,i)~=nil,"Attempted to shuffle table containing nil values") end
        for i=n,2,-1 do
            local j=native(data,3,1,i)
            local a,b=rawget(array,i),rawget(array,j)
            rawset(array,j,a);rawset(array,i,b)
        end
    end
    R.datatypes.Random=table.freeze({new=new})
end
