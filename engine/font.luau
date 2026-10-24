return function(R)
    local Font={}
    local function enumValue(value,kind,default)
        if value==nil then return default end
        assert(typeof(value)=="EnumItem" and value.EnumType==R.Enum[kind],"Expected Enum."..kind)
        return value
    end
    local function family(value)
        assert(type(value)=="string","Font family must be a string")
        -- The 0.735 bridge passes a C string to ContentId, not a StringView.
        return (string.split(value,"\0")[1]:gsub("\\","/"))
    end
    local make
    make=function(path,weight,style,cachedFace)
        local data={Family=path,Weight=weight,Style=style,cachedFace=cachedFace or ""}
        return R.makeValue("Font",data,function(_,key,v)
            if key=="Bold" then return v.Weight.Value>=600 end
            if key=="Family" or key=="Weight" or key=="Style" then return v[key] end
            error(tostring(key).." is not a valid member of Font",2)
        end,{
            __newindex=function(self,key,value)
                local v=R.values[self]
                if key=="Family" then value=family(value)
                elseif key=="Weight" then value=enumValue(value,"FontWeight");assert(value,"Expected Enum.FontWeight")
                elseif key=="Style" then value=enumValue(value,"FontStyle");assert(value,"Expected Enum.FontStyle")
                elseif key=="Bold" then
                    assert(type(value)=="boolean","Font.Bold must be a boolean")
                    if (v.Weight.Value>=600)==value then return end
                    key="Weight";value=if value then R.Enum.FontWeight.Bold else R.Enum.FontWeight.Regular
                else error(tostring(key).." is not a valid member of Font",2) end
                if v[key]~=value then v[key]=value;v.cachedFace="" end
            end,
            __eq=function(a,b)
                if typeof(a)~="Font" or typeof(b)~="Font" then return false end
                local x,y=R.values[a],R.values[b]
                return x.Family==y.Family and x.Weight==y.Weight and x.Style==y.Style
            end,
            __tostring=function(self)
                local v=R.values[self]
                return "Font { Family = "..v.Family..", Weight = "..v.Weight.Name..", Style = "..v.Style.Name.." }"
            end,
        })
    end
    function Font.new(path,weight,style)
        return make(family(path),enumValue(weight,"FontWeight",R.Enum.FontWeight.Regular),enumValue(style,"FontStyle",R.Enum.FontStyle.Normal))
    end
    function Font.fromName(name,weight,style)
        assert(type(name)=="string","Font name must be a string")
        name=string.split(name,"\0")[1]
        assert(#name>0 and string.match(name,"^[A-Za-z0-9_-]+$"),"Name passed to Font.fromName must only contain alphanumeric characters, underscores, and hyphens.")
        return Font.new("rbxasset://fonts/families/"..name..".json",weight,style)
    end
    function Font.fromId(id,weight,style)
        assert(type(id)=="number","Font ID must be a number")
        -- cvttsd2si r14d, xmm0; mov esi, r14d in the supplied Mac bridge.
        -- Preserve its int32 conversion, including the indefinite overflow result.
        local integer=if id>=0 then math.floor(id) else math.ceil(id)
        if id~=id or integer < -2147483648 or integer > 2147483647 then integer=-2147483648 end
        if integer<0 then integer+=4294967296 end
        assert(integer>0,"ID passed to Font.fromId must be greater than zero.")
        return Font.new("rbxassetid://"..string.format("%.0f",integer),weight,style)
    end
    local weights,styles={},{}
    for _,item in R.Enum.FontWeight:GetEnumItems() do weights[item.Value]=item end
    for _,item in R.Enum.FontStyle:GetEnumItems() do styles[item.Value]=item end
    function Font.fromEnum(item)
        enumValue(item,"Font");assert(item,"Expected Enum.Font")
        local row=R.fontCatalog[item.Name]
        assert(row,"Unknown Enum.Font cannot be converted to Font")
        return make(row.family,assert(weights[row.weight]),assert(styles[row.style]))
    end
    function R.importFont(row)
        return make(family(row[1]),weights[row[2]] or R.Enum.FontWeight.Regular,styles[row[3]] or R.Enum.FontStyle.Normal,row[4])
    end
    function R.copyValue(value)
        if typeof(value)~="Font" then return value end
        local v=R.values[value]
        return make(v.Family,v.Weight,v.Style,v.cachedFace)
    end
    R.datatypes.Font=table.freeze(Font)
end
