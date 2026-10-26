-- Batched headless transforms. Physical assemblies, contact removal and network
-- ownership changes from the native implementation are not simulated.
return function(R)
    local methods=R.classMethods.WorldRoot
    function methods:BulkMoveTo(partList,cframeList,eventMode)
        assert(type(partList)=='table' and type(cframeList)=='table','BulkMoveTo expects two arrays')
        if eventMode==nil then eventMode=R.Enum.BulkMoveMode.FireAllEvents end
        assert(typeof(eventMode)=='EnumItem' and eventMode.EnumType==R.Enum.BulkMoveMode,'Expected Enum.BulkMoveMode')
        local count=#partList
        assert(count==#cframeList,'Length of part list and length of CFrame list do not match')
        -- Reflection converts the input arrays before native movement begins.
        -- Validate the complete plan and retain it across immediate callbacks.
        local plan={}
        for index=1,count do
            local part,frame=rawget(partList,index),rawget(cframeList,index)
            if part~=nil then
                assert(R.instances[part] and part:IsA('BasePart'),'Can only call BulkMoveTo on BaseParts, partList['..index..'] is invalid')
                assert(typeof(frame)=='CFrame','CFrame list must only contain CFrames, cframeList['..index..'] is invalid')
                table.insert(plan,{part,frame})
            end
        end
        for _,entry in plan do
            if eventMode==R.Enum.BulkMoveMode.FireAllEvents then entry[1].CFrame=entry[2]
            else
                local data=R.instances[entry[1]]
                if data.props.CFrame~=entry[2] then
                    data.props.CFrame=entry[2];R.changed(entry[1],'CFrame')
                end
            end
        end
    end
end
