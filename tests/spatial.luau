local function reject(fn) assert(not pcall(fn)) end
local function close(a,b) assert(math.abs(a-b)<1e-7,tostring(a).." ~= "..tostring(b)) end
local function contains(list,item) return table.find(list,item)~=nil end
local model=Instance.new("Model",workspace)
model.Name="GeometryTests"
local function part(name,position,extent)
    local p=Instance.new("Part",model);p.Name=name;p.Size=extent or Vector3.new(2,2,2);p.CFrame=CFrame.new(position);p.Anchored=true;return p
end
local near=part("Near",Vector3.new(0,0,-5))
local far=part("Far",Vector3.new(0,0,-10))
local ray=RaycastParams.new()
assert(typeof(ray)=="RaycastParams" and ray.FilterType==Enum.RaycastFilterType.Exclude)
assert(ray.CollisionGroup=="Default" and not ray.IgnoreWater and not ray.RespectCanCollide and #ray.FilterDescendantsInstances==0)
local filter={near};ray.FilterDescendantsInstances=filter;filter[1]=far
assert(ray.FilterDescendantsInstances[1]==near)
local returned=ray.FilterDescendantsInstances;returned[1]=far;assert(ray.FilterDescendantsInstances[1]==near)
ray:AddToFilter({{far}});assert(#ray.FilterDescendantsInstances==2)
ray.FilterDescendantsInstances={}
local hit=workspace:Raycast(Vector3.zero,Vector3.new(0,0,-20),ray)
assert(typeof(hit)=="RaycastResult" and hit.Instance==near and hit.Material==Enum.Material.Plastic)
close(hit.Distance,4);assert(hit.Position==Vector3.new(0,0,-4) and hit.Normal==Vector3.zAxis)
reject(function() hit.Distance=0 end)
ray:AddToFilter(near)
assert(workspace:Raycast(Vector3.zero,Vector3.new(0,0,-20),ray).Instance==far)
ray.FilterType=Enum.RaycastFilterType.Include
assert(workspace:Raycast(Vector3.zero,Vector3.new(0,0,-20),ray).Instance==near)
ray.FilterDescendantsInstances={model}
assert(workspace:Raycast(Vector3.zero,Vector3.new(0,0,-20),ray).Instance==near)
ray.FilterDescendantsInstances={}
assert(workspace:Raycast(Vector3.zero,Vector3.new(0,0,-20),ray)==nil)
ray.FilterType=Enum.RaycastFilterType.Exclude
assert(workspace:Raycast(Vector3.zero,Vector3.new(0,0,-3))==nil)
assert(workspace:Raycast(Vector3.zero,Vector3.zero)==nil)
assert(workspace:Raycast(near.Position,Vector3.new(0,0,-1))==nil)
near.CanQuery=false
assert(workspace:Raycast(Vector3.zero,Vector3.new(0,0,-20)).Instance==far)
ray.RespectCanCollide=true
assert(workspace:Raycast(Vector3.zero,Vector3.new(0,0,-20),ray).Instance==near)
near.CanCollide=false
assert(workspace:Raycast(Vector3.zero,Vector3.new(0,0,-20),ray).Instance==far)
near.CanQuery=true;near.CanCollide=true
local rotated=part("Rotated",Vector3.new(10,0,0),Vector3.new(8,2,2))
rotated.CFrame=rotated.CFrame*CFrame.Angles(0,math.pi/4,0)
hit=workspace:Raycast(Vector3.new(10,0,10),Vector3.new(0,0,-20))
assert(hit.Instance==rotated);close(hit.Normal.Magnitude,1)
local overlap=OverlapParams.new()
assert(typeof(overlap)=="OverlapParams" and overlap.MaxParts==0 and overlap.Tolerance==0)
overlap.FilterType=Enum.RaycastFilterType.Include;overlap:AddToFilter(model)
local found=workspace:GetPartBoundsInBox(CFrame.new(0,0,-7.5),Vector3.new(4,4,10),overlap)
assert(#found==2 and contains(found,near) and contains(found,far))
overlap.MaxParts=1;assert(#workspace:GetPartBoundsInRadius(Vector3.new(0,0,-7.5),5,overlap)==1)
overlap.MaxParts=0
assert(#workspace:GetPartBoundsInRadius(Vector3.new(0,0,-5),0.1,overlap)==1)
assert(#workspace:GetPartBoundsInRadius(Vector3.new(0,0,100),1,overlap)==0)
-- Long thin parallel boxes have overlapping world AABBs but do not overlap.
local thin=part("Thin",Vector3.new(20,0,0),Vector3.new(10,1,0.2))
thin.CFrame=thin.CFrame*CFrame.Angles(0,math.pi/4,0)
local offset=thin.CFrame:VectorToWorldSpace(Vector3.new(0,0,1))
found=workspace:GetPartBoundsInBox(thin.CFrame+offset,thin.Size,overlap)
assert(not contains(found,thin))
found=workspace:GetPartBoundsInBox(thin.CFrame,thin.Size,overlap)
assert(contains(found,thin))
local probe=part("Probe",near.Position)
found=workspace:GetPartsInPart(probe,overlap)
assert(contains(found,near) and not contains(found,probe))
local physics=game:GetService("PhysicsService")
physics:RegisterCollisionGroup("TestA");physics:RegisterCollisionGroup("TestB")
near.CollisionGroup="TestB"
ray.CollisionGroup="TestA"
physics:CollisionGroupSetCollidable("TestA","TestB",false)
assert(workspace:Raycast(Vector3.zero,Vector3.new(0,0,-20),ray).Instance~=near)
physics:CollisionGroupSetCollidable("TestA","TestB",true)
probe:Destroy()
assert(workspace:Raycast(Vector3.zero,Vector3.new(0,0,-20),ray).Instance==near)
physics:RenameCollisionGroup("TestB","Renamed")
assert(near.CollisionGroup=="Renamed")
physics:UnregisterCollisionGroup("Renamed");assert(near.CollisionGroup=="Default")
reject(function() ray.FilterType=Enum.Material.Plastic end)
reject(function() ray.FilterDescendantsInstances={near,1} end)
reject(function() overlap.Tolerance=-1 end)
reject(function() overlap.Tolerance=1 end)
reject(function() near:SetAttribute("Params",ray) end)
reject(function() near.CollisionGroup="Unregistered" end)
reject(function() workspace:GetPartBoundsInRadius(Vector3.zero,-1) end)
local wm=Instance.new("WorldModel",workspace)
local other=Instance.new("Part",wm);other.CFrame=CFrame.new(0,0,-3)
assert(wm:Raycast(Vector3.zero,Vector3.new(0,0,-10)).Instance==other)
assert(workspace:Raycast(Vector3.zero,Vector3.new(0,0,-20)).Instance==near)
wm:Destroy();model:Destroy()
print("SPATIAL QUERY CHECKS PASSED")
