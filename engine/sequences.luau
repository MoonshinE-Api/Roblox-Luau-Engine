-- Interface contracts: Roblox/creator-docs, see evidence/api_reference.json.
-- Semantic implementation; float32 rounding and native error text remain unverified.
return function(R)
    local record=R.makeRecord
    local function finite(value,label)
        assert(type(value)=="number" and value==value and math.abs(value)<math.huge,label.." must be finite")
        return value
    end
    local function keyTime(time)
        finite(time,"Time");assert(time>=0 and time<=1,"Time must be between 0 and 1")
    end
    local NumberSequenceKeypoint={}
    function NumberSequenceKeypoint.new(time,value,envelope)
        keyTime(time);finite(value,"Value")
        envelope=if envelope==nil then 0 else envelope
        finite(envelope,"Envelope");assert(envelope>=0,"Envelope must be nonnegative")
        return record("NumberSequenceKeypoint",{Time=time,Value=value,Envelope=envelope})
    end
    local ColorSequenceKeypoint={}
    function ColorSequenceKeypoint.new(time,value)
        keyTime(time);assert(typeof(value)=="Color3","Expected Color3")
        assert(value.R>=0 and value.R<=1 and value.G>=0 and value.G<=1 and value.B>=0 and value.B<=1,"Color components must be between 0 and 1")
        return record("ColorSequenceKeypoint",{Time=time,Value=value})
    end
    local function sequenceType(name,keypointType,componentType,point)
        local library={}
        function library.new(first,last)
            local points
            if type(first)=="table" then
                points=table.clone(first)
            else
                assert(typeof(first)==componentType,"Expected "..componentType.." or keypoint array")
                last=if last==nil then first else last
                assert(typeof(last)==componentType,"Expected "..componentType)
                points={point.new(0,first),point.new(1,last)}
            end
            assert(#points>=2 and #points<=20,"Sequence requires between 2 and 20 keypoints")
            local previous=-math.huge
            for _,keypoint in ipairs(points) do
                assert(typeof(keypoint)==keypointType,"Expected "..keypointType)
                assert(keypoint.Time>=previous,"Keypoints must be ordered by time")
                previous=keypoint.Time
            end
            assert(points[1].Time==0 and points[#points].Time==1,"Sequence must begin at 0 and end at 1")
            return R.makeValue(name,points,function(_,key,data)
                if key=="Keypoints" then return table.clone(data) end
                error(key.." is not a valid member of "..name,2)
            end,{
                __tostring=function() return name end,
                __eq=function(a,b)
                    if typeof(a)~=name or typeof(b)~=name then return false end
                    local x,y=R.values[a],R.values[b]
                    if #x~=#y then return false end
                    for i=1,#x do if x[i]~=y[i] then return false end end
                    return true
                end,
            })
        end
        return table.freeze(library)
    end
    R.datatypes.NumberSequenceKeypoint=table.freeze(NumberSequenceKeypoint)
    R.datatypes.ColorSequenceKeypoint=table.freeze(ColorSequenceKeypoint)
    R.datatypes.NumberSequence=sequenceType("NumberSequence","NumberSequenceKeypoint","number",NumberSequenceKeypoint)
    R.datatypes.ColorSequence=sequenceType("ColorSequence","ColorSequenceKeypoint","Color3",ColorSequenceKeypoint)

    local faceAxis={Right="X",Left="X",Top="Y",Bottom="Y",Back="Z",Front="Z"}
    local Faces,Axes={},{}
    function Faces.new(...)
        local fields={Top=false,Bottom=false,Left=false,Right=false,Front=false,Back=false}
        local input=table.pack(...)
        for i=1,input.n do
            local normal=input[i]
            assert(typeof(normal)=="EnumItem" and normal.EnumType==R.Enum.NormalId,"Expected Enum.NormalId")
            fields[normal.Name]=true
        end
        return record("Faces",fields)
    end
    function Axes.new(...)
        local fields={X=false,Y=false,Z=false}
        local input=table.pack(...)
        for i=1,input.n do
            local axis=input[i]
            assert(typeof(axis)=="EnumItem","Expected Enum.Axis or Enum.NormalId")
            if axis.EnumType==R.Enum.Axis then fields[axis.Name]=true
            elseif axis.EnumType==R.Enum.NormalId then fields[faceAxis[axis.Name]]=true
            else error("Expected Enum.Axis or Enum.NormalId",2) end
        end
        for face,axis in faceAxis do fields[face]=fields[axis] end
        return record("Axes",fields)
    end
    R.datatypes.Faces,R.datatypes.Axes=table.freeze(Faces),table.freeze(Axes)
    local PathWaypoint={}
    function PathWaypoint.new(position,action,label)
        assert(typeof(position)=="Vector3","Expected Vector3")
        assert(typeof(action)=="EnumItem" and action.EnumType==R.Enum.PathWaypointAction,"Expected Enum.PathWaypointAction")
        label=if label==nil then "" else label
        assert(type(label)=="string","Expected string label")
        return record("PathWaypoint",{Position=position,Action=action,Label=label})
    end
    R.datatypes.PathWaypoint=table.freeze(PathWaypoint)
end
