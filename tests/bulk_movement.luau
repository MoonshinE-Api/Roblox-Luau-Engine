local function rejects(fn) assert(not pcall(fn),'Expected failure') end
local function near(a,b) assert((a-b).Magnitude<1e-7,tostring(a)..' ~= '..tostring(b)) end
local a=Instance.new('Part',workspace);a.Anchored=true
local b=Instance.new('WedgePart',workspace);b.Anchored=true
local child=Instance.new('Attachment',b);child.Position=Vector3.new(1,2,3)
local notifications={}
local observed={'CFrame','Position','AssemblyCenterOfMass','Orientation','Rotation'}
local connection=a.Changed:Connect(function(key) table.insert(notifications,key) end)
workspace:BulkMoveTo({a,b},{CFrame.new(5,6,7),CFrame.new(10,20,30)})
assert(table.concat(notifications,',')==table.concat(observed,','))
assert(a.Position==Vector3.new(5,6,7) and b.Position==Vector3.new(10,20,30))
table.clear(notifications)
local rotated=CFrame.new(20,30,40)*CFrame.Angles(.1,.2,.3)
workspace:BulkMoveTo({a,b},{rotated,rotated},Enum.BulkMoveMode.FireCFrameChanged)
assert(table.concat(notifications,',')=='CFrame')
near(child.WorldPosition,rotated:PointToWorldSpace(child.Position))
near(a.Orientation,b.Orientation)
table.clear(notifications)
workspace:BulkMoveTo({a},{rotated},Enum.BulkMoveMode.FireCFrameChanged)
assert(#notifications==0)
local before=a.CFrame
rejects(function() workspace:BulkMoveTo({a,b},{CFrame.identity}) end)
rejects(function() workspace:BulkMoveTo({a,b},{CFrame.identity,Vector3.zero}) end)
rejects(function() workspace:BulkMoveTo({a,child},{CFrame.identity,CFrame.identity}) end)
rejects(function() workspace:BulkMoveTo({a,42},{CFrame.identity,CFrame.identity}) end)
rejects(function() workspace:BulkMoveTo(a,{CFrame.identity}) end)
rejects(function() workspace:BulkMoveTo({a},{CFrame.identity},Enum.EasingStyle.Linear) end)
rejects(function() workspace:BulkMoveTo({a},{CFrame.identity},false) end)
assert(a.CFrame==before)
workspace:BulkMoveTo({},{});assert(a.CFrame==before)
connection:Disconnect()

-- Duplicate entries apply in order. Callback edits to the original arrays do
-- not alter the already converted operation, including subsequent entries.
local parts={a,a,b}
local frames={CFrame.new(1,0,0),CFrame.new(2,0,0),CFrame.new(3,0,0)}
local order={}
local change=a:GetPropertyChangedSignal('CFrame'):Connect(function()
    table.insert(order,a.Position.X)
    parts[2]=child;frames[3]=CFrame.new(999,0,0)
end)
workspace:BulkMoveTo(parts,frames)
assert(order[1]==1 and order[2]==2 and a.Position.X==2 and b.Position.X==3)
change:Disconnect()
workspace:BulkMoveTo({nil,b},{false,CFrame.new(4,0,0)})
assert(b.Position.X==4)
local model=Instance.new('WorldModel')
model:BulkMoveTo({a},{CFrame.new(9,8,7)},Enum.BulkMoveMode.FireCFrameChanged)
assert(a.Position==Vector3.new(9,8,7))
local outside=Instance.new('Part')
workspace:BulkMoveTo({outside},{CFrame.new(4,5,6)});assert(outside.Position==Vector3.new(4,5,6))
local resumed=false
local delayed=a:GetPropertyChangedSignal('CFrame'):Connect(function()
    task.wait()
    assert(b.Position==Vector3.new(7,8,9));resumed=true
end)
workspace:BulkMoveTo({a,b},{CFrame.new(10,11,12),CFrame.new(7,8,9)})
assert(not resumed and b.Position==Vector3.new(7,8,9))
task.wait(.02);assert(resumed);delayed:Disconnect()

-- The spatial query sees the new transform immediately, without a frame step.
a.Size=Vector3.new(2,2,2)
workspace:BulkMoveTo({a},{CFrame.new(0,0,-20)},Enum.BulkMoveMode.FireCFrameChanged)
local params=RaycastParams.new();params.FilterType=Enum.RaycastFilterType.Include;params.FilterDescendantsInstances={a}
local hit=workspace:Raycast(Vector3.zero,Vector3.new(0,0,-50),params)
assert(hit and hit.Instance==a and hit.Distance==19)

local random=Random.new(735271)
local cloud={};for i=1,64 do local p=Instance.new('Part',workspace);p.Anchored=true;cloud[i]=p end
for step=1,40 do
    local targets={}
    for i=1,#cloud do targets[i]=CFrame.new(random:NextNumber(-500,500),i,step)*CFrame.Angles(.01*step,.02*i,0) end
    workspace:BulkMoveTo(cloud,targets,Enum.BulkMoveMode.FireCFrameChanged)
    for i,part in cloud do assert(part.CFrame==targets[i]) end
end
for _,part in cloud do part:Destroy() end
a:Destroy();b:Destroy();model:Destroy();outside:Destroy()
print('BULK MOVEMENT, EVENT MODES, VALIDATION, CALLBACK SNAPSHOTS AND QUERY CHECKS PASSED',2560)
