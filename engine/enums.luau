return function(R)
    local enums,items={},{}
    local function enum(name)
        if enums[name] then return enums[name] end
        local source=R.enumCatalog[name]
        assert(source,"Invalid Enum type "..tostring(name))
        local function item(key)
            local identity=name.."."..key
            if items[identity] then return items[identity] end
            local number=source[key]
            assert(number~=nil,key.." is not a valid EnumItem for "..name)
            local value=R.makeValue("EnumItem",{name=key,value=number},function(_,member)
                if member=="Name" then return key elseif member=="Value" then return number elseif member=="EnumType" then return enums[name] end
                error(member.." is not a valid member of EnumItem",2)
            end,{__tostring=function() return "Enum."..identity end})
            items[identity]=value;return value
        end
        local value=R.makeValue("Enum",{name=name},function(_,key)
            if key=="GetEnumItems" then return function()
                local names={};for n in source do table.insert(names,n) end
                table.sort(names,function(a,b) return source[a]<source[b] or source[a]==source[b] and a<b end)
                local result={};for _,n in names do table.insert(result,item(n)) end;return result
            end end
            return item(key)
        end,{__tostring=function() return "Enum."..name end})
        enums[name]=value;return value
    end
    R.Enum=R.makeValue("Enums",{},function(_,key)
        if key=="GetEnums" then return function()
            local names={};for name in R.enumCatalog do table.insert(names,name) end;table.sort(names)
            local result={};for _,name in names do table.insert(result,enum(name)) end;return result
        end end
        return enum(key)
    end,{__tostring=function() return "Enum" end})
end
