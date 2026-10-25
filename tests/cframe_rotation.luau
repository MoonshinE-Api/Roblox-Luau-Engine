local function nearFrame(a,b,tolerance)
    local x,y={a:GetComponents()},{b:GetComponents()}
    for i=1,12 do assert(math.abs(x[i]-y[i])<(tolerance or 1e-8),'CFrame component '..i..': '..x[i]..' ~= '..y[i]) end
end
local function rejects(fn) assert(not pcall(fn),'Expected failure') end
assert(CFrame.new('1',false,{}).Position==Vector3.new(1,0,0))
assert(CFrame.new(1,2,3,0,0,0,1)==CFrame.new(1,2,3))
assert(CFrame.new(1,2,3,0,0,0,5)==CFrame.new(1,2,3))
rejects(function() CFrame.new(1) end)
rejects(function() CFrame.new(Vector3.zero,1) end)
rejects(function() CFrame.new(1,2,3,4) end)
local rng=Random.new(735740)
local count=0
for _,order in Enum.RotationOrder:GetEnumItems() do
    for i=1,250 do
        local x,y,z=rng:NextNumber(-3,3),rng:NextNumber(-3,3),rng:NextNumber(-3,3)
        local cf=CFrame.fromEulerAngles(x,y,z,order)
        local a,b,c=cf:ToEulerAngles(order)
        nearFrame(CFrame.fromEulerAngles(a,b,c,order),cf,0.002)
        local axis,angle=cf:ToAxisAngle()
        nearFrame(CFrame.fromAxisAngle(axis,angle),cf,0.0003)
        count+=1
    end
    local middle=string.sub(order.Name,2,2)
    for _,sign in {-1,1} do
        local angles={X=0.7,Y=-0.3,Z=1.1};angles[middle]=sign*math.pi/2
        local cf=CFrame.fromEulerAngles(angles.X,angles.Y,angles.Z,order)
        local x,y,z=cf:ToEulerAngles(order)
        nearFrame(CFrame.fromEulerAngles(x,y,z,order),cf)
    end
end
for i=1,300 do
    local axis=Vector3.new(rng:NextNumber(-1,1),rng:NextNumber(-1,1),rng:NextNumber(-1,1)).Unit
    local angle=rng:NextNumber(-math.pi,math.pi)
    local cf=CFrame.fromAxisAngle(axis*3,angle)
    local sine=math.sin(angle/2)
    nearFrame(CFrame.new(0,0,0,axis.X*sine,axis.Y*sine,axis.Z*sine,math.cos(angle/2)),cf)
    local extracted,rotation=cf:ToAxisAngle()
    nearFrame(CFrame.fromAxisAngle(extracted,rotation),cf,0.0003)
end
for _,axis in {Vector3.xAxis,Vector3.yAxis,Vector3.zAxis,Vector3.new(1,2,3).Unit} do
    local cf=CFrame.fromAxisAngle(axis,math.pi)
    nearFrame(CFrame.fromAxisAngle(cf:ToAxisAngle()),cf,1e-7)
end
local axis,angle=CFrame.identity:ToAxisAngle();assert(axis==Vector3.xAxis and angle==0)
local cf=CFrame.fromOrientation(0.2,0.3,0.4)
nearFrame(cf,CFrame.Angles(0,0.3,0)*CFrame.Angles(0.2,0,0)*CFrame.Angles(0,0,0.4))
nearFrame(CFrame.fromOrientation(cf:ToOrientation()),cf)
nearFrame(CFrame.fromEulerAnglesXYZ(cf:ToEulerAnglesXYZ()),cf)
nearFrame(CFrame.fromEulerAnglesYXZ(cf:ToEulerAnglesYXZ()),cf)
local look=CFrame.lookAlong(Vector3.new(2,3,4),Vector3.xAxis)
assert((look.LookVector-Vector3.xAxis).Magnitude<1e-8 and look.Position==Vector3.new(2,3,4))
for _,direction in {Vector3.yAxis,-Vector3.yAxis,Vector3.xAxis,-Vector3.xAxis} do
    local looking=CFrame.lookAlong(Vector3.zero,direction,direction)
    assert((looking.LookVector-direction).Magnitude<1e-8 and math.abs(looking.UpVector:Dot(direction))<1e-8)
    nearFrame(looking,CFrame.lookAt(Vector3.zero,direction,direction))
end
assert(CFrame.lookAlong(Vector3.new(1e20,0,0),Vector3.xAxis).LookVector==Vector3.xAxis)
rejects(function() CFrame.fromEulerAngles(1,2,3,Enum.Material.Plastic) end)
rejects(function() cf:ToEulerAngles('XYZ') end)
rejects(function() CFrame.fromAxisAngle({},1) end)
print('CFRAME ROTATION ORDERS, QUATERNIONS, AXIS ANGLES AND SINGULARITIES PASSED',count+300)
