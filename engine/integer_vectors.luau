-- Build 735 constructor/overflow rules. Vector2 scalar math uses the fixed
-- FixVector2int16WithFloatMult behavior; runtime feature flags are not simulated.
return function(R)
    local f32,int32=R.float32,R.toInt32
    local function wrap(value) return (value+32768)%65536-32768 end
    local function vector(name,dimensions)
        local library={}
        local fields={X=1,Y=2,Z=3,x=1,y=2,z=3}
        local function components(value) assert(typeof(value)==name,'Expected '..name);return R.values[value] end
        local make
        local function binary(a,b,operation)
            local x,y=components(a),components(b);local result={}
            for i=1,dimensions do result[i]=operation(x[i],y[i]) end
            return make(result)
        end
        make=function(data)
            for i=1,dimensions do data[i]=wrap(data[i]) end
            return R.makeValue(name,data,function(_,key,values)
                local index=fields[key]
                if index and index<=dimensions then return values[index] end
                error(tostring(key)..' is not a valid member of '..name,2)
            end,{
                __tostring=function(self) return table.concat(components(self),', ') end,
                __eq=function(a,b)
                    if typeof(a)~=name or typeof(b)~=name then return false end
                    for i=1,dimensions do if R.values[a][i]~=R.values[b][i] then return false end end
                    return true
                end,
                __add=function(a,b) return binary(a,b,function(x,y) return x+y end) end,
                __sub=function(a,b) return binary(a,b,function(x,y) return x-y end) end,
                __unm=function(a)
                    local result={};for i,value in components(a) do result[i]=-value end;return make(result)
                end,
                __mul=function(a,b)
                    if typeof(a)==name and typeof(b)==name then return binary(a,b,function(x,y) return x*y end) end
                    if typeof(a)~=name then a,b=b,a end
                    local scalar=f32(tonumber(b) or 0)
                    if dimensions==3 then scalar=int32(scalar) end
                    local result={}
                    for i,value in components(a) do result[i]=if dimensions==3 then value*scalar else int32(f32(value*scalar)) end
                    return make(result)
                end,
                __div=function(a,b)
                    if typeof(b)==name then
                        local denominator=components(b);local numerator
                        if typeof(a)==name then numerator=components(a) else
                            local scalar=int32(a);if dimensions==2 then scalar=wrap(scalar) end
                            numerator=table.create(dimensions,scalar)
                        end
                        local result={}
                        for i=1,dimensions do
                            assert(denominator[i]~=0,'Divide by zero exception')
                            result[i]=math.modf(numerator[i]/denominator[i])
                        end
                        return make(result)
                    end
                    local scalar=f32(tonumber(b) or 0)
                    if dimensions==2 then assert(scalar~=0,'Divide by zero exception') end
                    local result={};for i,value in components(a) do result[i]=int32(f32(value/scalar)) end
                    return make(result)
                end,
            })
        end
        function library.new(...)
            local input={...};local data={}
            for i=1,dimensions do data[i]=int32(input[i]) end
            return make(data)
        end
        R.datatypes[name]=table.freeze(library)
    end
    vector('Vector2int16',2);vector('Vector3int16',3)
end
