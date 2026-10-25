local function near(a,b,tolerance) assert((a-b).Magnitude<(tolerance or 1e-8),tostring(a)..' ~= '..tostring(b)) end
local function frame(a,b)
    near(a.Position,b.Position);near(a.RightVector,b.RightVector);near(a.UpVector,b.UpVector);near(a.LookVector,b.LookVector)
end
local function rejects(fn) assert(not pcall(fn),'Expected failure') end
for _,kind in {'Part','WedgePart','CornerWedgePart'} do
    local p=Instance.new(kind,workspace)
    assert(p.Orientation==Vector3.zero and p.Rotation==Vector3.zero)
    local counts={};local order={}
    for _,key in {'CFrame','Position','AssemblyCenterOfMass','Orientation','Rotation'} do
        counts[key]=0;p:GetPropertyChangedSignal(key):Connect(function() counts[key]+=1;table.insert(order,key) end)
    end
    p.CFrame=p.CFrame
    assert(#order==0)
    p.Position=Vector3.new(2,3,4)
    assert(table.concat(order,',')=='CFrame,Position,AssemblyCenterOfMass,Orientation,Rotation')
    for key in counts do assert(counts[key]==1) end
    p.Position=p.Position;assert(counts.Position==1)
    p.Orientation=Vector3.new(20,30,40)
    frame(p.CFrame,CFrame.fromOrientation(math.rad(20),math.rad(30),math.rad(40))+Vector3.new(2,3,4))
    near(p.Orientation,Vector3.new(20,30,40))
    p.Rotation=Vector3.new(20,30,40)
    frame(p.CFrame,CFrame.Angles(math.rad(20),math.rad(30),math.rad(40))+Vector3.new(2,3,4))
    near(p.Rotation,Vector3.new(20,30,40))
    for key in counts do assert(counts[key]==3) end
    local copy=p:Clone();frame(copy.CFrame,p.CFrame);near(copy.Orientation,p.Orientation)
    rejects(function() p.Orientation={} end);rejects(function() p.Rotation=3 end);rejects(function() p.CFrame=Vector3.zero end)
    local tween=game:GetService('TweenService'):Create(p,TweenInfo.new(0.05,Enum.EasingStyle.Linear),{Orientation=Vector3.new(0,90,0)})
    tween:Play();tween.Completed:Wait()
    near(p.Orientation,Vector3.new(0,90,0));near(p.Position,Vector3.new(2,3,4))
    p:Destroy();copy:Destroy()
end
local random=Random.new(735)
local p=Instance.new('Part',workspace)
for i=1,300 do
    local angles=Vector3.new(random:NextInteger(-80,80),random:NextInteger(-170,170),random:NextInteger(-170,170))
    p.Orientation=angles;near(p.Orientation,angles)
    p.CFrame=CFrame.new(1,2,3)*CFrame.Angles(math.rad(20),math.rad(30),math.rad(40))
    near(p.Rotation,Vector3.new(20,30,40))
end
p.Orientation=Vector3.new(0,-180,0);assert(p.Orientation.Y==180)
p.Orientation=Vector3.new(12.34567,0,0);assert(p.Orientation.X==12.346)
p:Destroy()
print('BASEPART ORIENTATION, ROTATION, DERIVED SIGNALS, CLONE AND TWEEN CHECKS PASSED',300)
