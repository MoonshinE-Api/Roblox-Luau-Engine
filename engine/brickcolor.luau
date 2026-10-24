return function(R)
    local colors,ordered,names,palette={},{},{},R.brickPalette
    local preferred={};for _,id in palette do preferred[id]=true end
    local float=buffer.create(4)
    local function f32(value) buffer.writef32(float,0,value);return buffer.readf32(float,0) end
    -- Color4(uint8) uses this float32 reciprocal and a rounded multiplication.
    local reciprocal=0.003921568859368563
    for _,row in R.brickColors do
        local id,name=row[1],row[2]
        local color=R.datatypes.Color3.new(f32(row[3]*reciprocal),f32(row[4]*reciprocal),f32(row[5]*reciprocal))
        colors[id]={number=id,name=name,color=color}
        table.insert(ordered,id)
    end
    table.sort(ordered)
    -- Native parse scans numeric IDs, preferring a matching palette entry.
    for _,id in ordered do
        local name=colors[id].name
        if not names[name] or not preferred[names[name]] then names[name]=id end
    end
    local packed=buffer.create(#ordered*16)
    for i,id in ordered do
        local offset=(i-1)*16;local color=colors[id].color
        buffer.writeu32(packed,offset,id)
        buffer.writef32(packed,offset+4,color.R);buffer.writef32(packed,offset+8,color.G);buffer.writef32(packed,offset+12,color.B)
    end
    local native=__host_brickcolor
    local function closest(r,g,b) return native(packed,r,g,b) end
    local function make(id)
        local info=colors[id] or colors[194]
        return R.makeValue("BrickColor",info,function(_,key,d)
            if key=="Number" then return d.number elseif key=="Name" then return d.name
            elseif key=="Color" then return d.color elseif key=="r" then return d.color.R
            elseif key=="g" then return d.color.G elseif key=="b" then return d.color.B end
            error(tostring(key).." is not a valid member of BrickColor",2)
        end,{
            __tostring=function(self) return R.values[self].name end,
            __eq=function(a,b) return typeof(a)=="BrickColor" and typeof(b)=="BrickColor" and R.values[a].number==R.values[b].number end,
        })
    end
    local function int32(value)
        if value~=value or math.abs(value)==math.huge then return -2147483648 end
        value=if value<0 then math.ceil(value) else math.floor(value)
        -- Native lua_tointegerx uses cvttsd2si eax, not modulo wrapping.
        return if value< -2147483648 or value>=2147483648 then -2147483648 else value
    end
    local function numeric(value) return if type(value)=="number" then value elseif type(value)=="string" then tonumber(value) else nil end
    local library={}
    function library.new(...)
        local n=select("#",...);local a,b,c=...
        if n==1 then
            local number=numeric(a)
            if number then return make(int32(number)) end
            if type(a)=="string" then return make(names[a:match("^[^%z]*")] or 194) end
            assert(typeof(a)=="Color3","Expected number, string or Color3")
            return make(closest(a.R,a.G,a.B))
        end
        -- Supplied 0.735 bridge falls through to closest(0,0,0) with no args.
        return make(closest(numeric(a) or 0,numeric(b) or 0,numeric(c) or 0))
    end
    function library.palette(index)
        index=numeric(index);assert(index,"Expected number")
        index=int32(index);assert(index>=0 and index<#palette,"palette index out of bounds")
        return make(palette[index+1])
    end
    local random=R.datatypes.Random.new()
    function library.random() return make(palette[random:NextInteger(1,#palette)]) end
    for name,id in R.brickConstants do
        library[name]=function() return make(id) end
    end
    library.New,library.Random=library.new,library.random
    R.datatypes.BrickColor=table.freeze(library)
end
