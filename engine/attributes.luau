return function(R)
    function R.applyAttributes(object,records)
        for _,record in records do
            local kind,value=record.kind,record.values
            if kind=='string' then
                value=buffer.tostring(R.jsonDecode('{"m":null,"t":"buffer","base64":"'..value..'"}'))
            elseif kind=='Font' then
                value=R.importFont(value)
            elseif kind=='NumberSequence' or kind=='ColorSequence' then
                local points={}
                for _,point in value do
                    if kind=='NumberSequence' then table.insert(points,R.datatypes.NumberSequenceKeypoint.new(table.unpack(point)))
                    else table.insert(points,R.datatypes.ColorSequenceKeypoint.new(point[1],R.datatypes.Color3.new(point[2],point[3],point[4]))) end
                end
                value=R.datatypes[kind].new(points)
            elseif kind~='number' and kind~='boolean' then
                value=R.datatypes[kind].new(table.unpack(value))
            end
            object:SetAttribute(record.name,value)
        end
    end
end
