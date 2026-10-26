local function near(a,b,tolerance)
    local difference=if type(a)=='number' then math.abs(a-b) else (a-b).Magnitude
    assert(difference<(tolerance or 1e-6),tostring(a)..' ~= '..tostring(b))
end
local function rejects(fn) assert(not pcall(fn),'Expected invalid geometry to fail') end
local model=Instance.new('Model',workspace);model.Name='ConvexTests'
local function part(class,name,position,size,shape)
    local value=Instance.new(class,model);value.Name=name;value.Anchored=true
    value.Position=position;value.Size=size
    if shape then value.Shape=shape end
    return value
end
local box=part('Part','Target',Vector3.new(0,0,-10),Vector3.new(2,2,2))
local filter=RaycastParams.new();filter.FilterType=Enum.RaycastFilterType.Include;filter.FilterDescendantsInstances={box}
local hit=workspace:Blockcast(CFrame.identity,Vector3.new(2,2,2),Vector3.new(0,0,-20),filter)
assert(hit.Instance==box and typeof(hit)=='RaycastResult');near(hit.Distance,8);near(hit.Normal,Vector3.zAxis)
near(hit.Position.Z,-9)
hit=workspace:Spherecast(Vector3.zero,2,Vector3.new(0,0,-20),filter)
assert(hit.Instance==box);near(hit.Distance,7);near(hit.Position,Vector3.new(0,0,-9));near(hit.Normal,Vector3.zAxis)
hit=workspace:Spherecast(Vector3.new(2.8,0,0),2,Vector3.new(0,0,-20),filter)
near(hit.Distance,9-math.sqrt(4-1.8^2),2e-5)
near(hit.Normal,Vector3.new(.9,0,math.sqrt(.19)),2e-5)
-- Expanding the target AABB would incorrectly hit this rounded corner.
assert(workspace:Spherecast(Vector3.new(2.5,2.5,0),2,Vector3.new(0,0,-20),filter)==nil)
assert(workspace:Blockcast(CFrame.new(box.Position),Vector3.new(4,4,4),Vector3.new(0,0,-20),filter)==nil)
assert(workspace:Spherecast(box.Position,1,Vector3.new(0,0,-20),filter)==nil)
assert(workspace:Spherecast(Vector3.zero,0,Vector3.new(0,0,-20),filter).Distance==9)
assert(workspace:Blockcast(CFrame.identity,Vector3.zero,Vector3.new(0,0,-20),filter).Distance==9)
assert(workspace:Blockcast(CFrame.identity,Vector3.one,Vector3.zero,filter)==nil)
assert(workspace:Spherecast(Vector3.zero,1,Vector3.zero,filter)==nil)

local ball=part('Part','Ball',Vector3.new(10,0,-10),Vector3.new(10,4,6),Enum.PartType.Ball)
local cylinder=part('Part','Cylinder',Vector3.new(20,0,-10),Vector3.new(6,4,8),Enum.PartType.Cylinder)
local wedge=part('WedgePart','Wedge',Vector3.new(30,0,-10),Vector3.new(2,2,2))
local corner=part('CornerWedgePart','Corner',Vector3.new(40,0,-10),Vector3.new(2,2,2))
filter.FilterDescendantsInstances={model}
hit=workspace:Raycast(Vector3.new(10,0,0),Vector3.new(0,0,-20),filter)
assert(hit.Instance==ball);near(hit.Distance,8);near(hit.Normal,Vector3.zAxis)
hit=workspace:Raycast(Vector3.new(20,0,0),Vector3.new(0,0,-20),filter)
assert(hit.Instance==cylinder);near(hit.Distance,8);near(hit.Normal,Vector3.zAxis)
hit=workspace:Raycast(Vector3.new(30,0,-10),Vector3.new(-20,0,0),filter)
assert(hit.Instance==cylinder);near(hit.Distance,7);near(hit.Normal,Vector3.xAxis)
hit=workspace:Raycast(Vector3.new(30,10,-10),Vector3.new(0,-20,0),filter)
assert(hit.Instance==wedge);near(hit.Distance,10);near(hit.Normal,Vector3.new(0,1,-1).Unit)
hit=workspace:Raycast(Vector3.new(40.5,10,-10),Vector3.new(0,-20,0),filter)
assert(hit.Instance==corner);near(hit.Distance,10);near(hit.Normal,Vector3.new(0,1,1).Unit)
assert(workspace:Raycast(ball.Position,Vector3.new(0,0,-20),filter)==nil)

local probe=part('Part','Probe',Vector3.zero,Vector3.new(2,2,2),Enum.PartType.Ball)
filter.FilterDescendantsInstances={box}
hit=workspace:Shapecast(probe,Vector3.new(0,0,-20),filter)
near(hit.Distance,8);near(probe.Position,Vector3.zero)
local overlap=OverlapParams.new();overlap.FilterType=Enum.RaycastFilterType.Include;overlap.FilterDescendantsInstances={cylinder}
probe.Shape=Enum.PartType.Block;probe.Size=Vector3.new(.1,.1,.1);probe.Position=Vector3.new(20,1.8,-8.2)
assert(#workspace:GetPartBoundsInBox(probe.CFrame,probe.Size,overlap)==1)
assert(#workspace:GetPartsInPart(probe,overlap)==0)
probe.Position=cylinder.Position;assert(workspace:GetPartsInPart(probe,overlap)[1]==cylinder)
probe.Position=Vector3.new(30,.9,-10.9);overlap.FilterDescendantsInstances={wedge}
assert(#workspace:GetPartBoundsInBox(probe.CFrame,probe.Size,overlap)==1 and #workspace:GetPartsInPart(probe,overlap)==0)
probe.Position=wedge.Position;assert(workspace:GetPartsInPart(probe,overlap)[1]==wedge)

-- The cast actor is ignored automatically, and nested WorldModels stay isolated.
probe.Position=Vector3.zero;probe.Size=Vector3.one;filter.FilterDescendantsInstances={box,probe}
hit=workspace:Shapecast(probe,Vector3.new(0,0,-20),filter);assert(hit.Instance==box)
local wm=Instance.new('WorldModel',workspace)
local isolated=Instance.new('Part',wm);isolated.Anchored=true;isolated.Position=Vector3.new(0,0,-5);isolated.Size=Vector3.one
assert(wm:Spherecast(Vector3.zero,.5,Vector3.new(0,0,-20)).Instance==isolated)
assert(workspace:Spherecast(Vector3.zero,.5,Vector3.new(0,0,-20),filter).Instance==box)

-- Eligibility rules are shared with the existing ray and overlap APIs.
filter.FilterDescendantsInstances={box};box.CanQuery=false
assert(workspace:Spherecast(Vector3.zero,1,Vector3.new(0,0,-20),filter)==nil)
filter.RespectCanCollide=true;assert(workspace:Spherecast(Vector3.zero,1,Vector3.new(0,0,-20),filter).Instance==box)
box.CanCollide=false;assert(workspace:Blockcast(CFrame.identity,Vector3.one,Vector3.new(0,0,-20),filter)==nil)
filter.BruteForceAllSlow=true;assert(workspace:Blockcast(CFrame.identity,Vector3.one,Vector3.new(0,0,-20),filter).Instance==box)
filter.BruteForceAllSlow=false;filter.RespectCanCollide=false;box.CanQuery=true;box.CanCollide=true
local physics=game:GetService('PhysicsService')
physics:RegisterCollisionGroup('ConvexActor');physics:RegisterCollisionGroup('ConvexTarget')
box.CollisionGroup='ConvexTarget';filter.CollisionGroup='ConvexActor'
physics:CollisionGroupSetCollidable('ConvexActor','ConvexTarget',false)
assert(workspace:Spherecast(Vector3.zero,1,Vector3.new(0,0,-20),filter)==nil)
physics:CollisionGroupSetCollidable('ConvexActor','ConvexTarget',true)
assert(workspace:Spherecast(Vector3.zero,1,Vector3.new(0,0,-20),filter).Instance==box)
physics:UnregisterCollisionGroup('ConvexActor');physics:UnregisterCollisionGroup('ConvexTarget')
filter.CollisionGroup='Default'

rejects(function() workspace:Blockcast(CFrame.identity,Vector3.new(-1,2,3),Vector3.one) end)
rejects(function() workspace:Blockcast(CFrame.identity,Vector3.new(513,2,3),Vector3.one) end)
rejects(function() workspace:Spherecast(Vector3.zero,-1,Vector3.one) end)
rejects(function() workspace:Spherecast(Vector3.zero,257,Vector3.one) end)
rejects(function() workspace:Spherecast(Vector3.zero,0/0,Vector3.one) end)
rejects(function() workspace:Spherecast(Vector3.zero,1,Vector3.new(0,0,1025)) end)
rejects(function() workspace:Blockcast(CFrame.new(math.huge,0,0),Vector3.one,Vector3.one) end)
rejects(function() workspace:Shapecast(model,Vector3.one) end)
rejects(function() workspace:Shapecast(probe,Vector3.new(0/0,0,0)) end)
rejects(function() workspace:GetPartsInPart(probe,RaycastParams.new()) end)
rejects(function() workspace:Raycast(Vector3.zero,Vector3.one,OverlapParams.new()) end)
rejects(function() workspace:Spherecast(Vector3.zero,1,Vector3.zero,OverlapParams.new()) end)
-- Packed target caches must follow edits and batched transforms immediately.
filter.FilterDescendantsInstances={box}
box.Shape=Enum.PartType.Ball;box.Size=Vector3.new(10,4,6)
hit=workspace:Raycast(Vector3.zero,Vector3.new(0,0,-30),filter);near(hit.Distance,8)
workspace:BulkMoveTo({box},{CFrame.new(0,0,-20)},Enum.BulkMoveMode.FireCFrameChanged)
hit=workspace:Spherecast(Vector3.zero,1,Vector3.new(0,0,-40),filter);near(hit.Distance,17)
box.Size=Vector3.new(2,2,2)
hit=workspace:Spherecast(Vector3.zero,1,Vector3.new(0,0,-40),filter);near(hit.Distance,18)
box.Shape=Enum.PartType.Block
hit=workspace:Blockcast(CFrame.identity,Vector3.one,Vector3.new(0,0,-40),filter);near(hit.Distance,18.5)
wm:Destroy();model:Destroy()
print('CONVEX RAYS, SHAPE CASTS, EXACT OVERLAPS, PRIMITIVES AND FILTERS PASSED')
