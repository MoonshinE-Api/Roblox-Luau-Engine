return function(R)
    function R.applyModelProperties(object,records,references)
        for _,record in records do
            local kind,value=record.kind,record.values
            if kind=='Instance?' then
                if value~=nil then value=assert(references[value],'Unresolved imported Instance reference') end
            elseif string.sub(kind,1,5)=='Enum.' then
                local found=nil
                for _,item in R.Enum[string.sub(kind,6)]:GetEnumItems() do
                    if item.Value==value then found=item;break end
                end
                value=assert(found,'Invalid imported enum value')
            elseif kind=='PhysicalProperties?' then
                if value~=nil then value=R.datatypes.PhysicalProperties.new(table.unpack(value)) end
            elseif kind~='number' and kind~='boolean' and kind~='string' then
                value=R.datatypes[kind].new(table.unpack(value))
            end
            object[record.name]=value
        end
    end
end
