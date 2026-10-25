-- Headless camera orbit, including a vertical view with parallel up/direction.
-- Run with --mode client --duration 1.2. No graphical window is created.
local run=game:GetService('RunService')
assert(run:IsClient(),'Run this example with --mode client')
local target=Instance.new('Part',workspace)
target.Name='OrbitTarget';target.Anchored=true
target.Size=Vector3.new(8,2,4);target.Position=Vector3.new(0,3,0)
local camera=Instance.new('Camera',workspace)
workspace.CurrentCamera=camera
camera.CFrame=CFrame.lookAt(target.Position+Vector3.new(0,12,0),target.Position)
assert((camera.CFrame.LookVector+Vector3.yAxis).Magnitude<1e-8)
local changes,frames=0,0
target:GetPropertyChangedSignal('Orientation'):Connect(function() changes+=1 end)
local tween=game:GetService('TweenService'):Create(target,TweenInfo.new(1,Enum.EasingStyle.Linear),{Orientation=Vector3.new(30,120,20)})
run:BindToRenderStep('OrbitExample',Enum.RenderPriority.Camera.Value,function()
    frames+=1
    local theta=time()*math.pi*2
    local offset=Vector3.new(math.sin(theta)*12,math.cos(theta)*12,0)
    camera.CFrame=CFrame.lookAt(target.Position+offset,target.Position)
    local projected,visible=camera:WorldToViewportPoint(target.Position)
    assert(visible and math.abs(projected.X-camera.ViewportSize.X/2)<1e-6)
    assert(math.abs(projected.Y-camera.ViewportSize.Y/2)<1e-6)
    local ray=camera:ViewportPointToRay(projected.X,projected.Y)
    assert(ray:Distance(target.Position)<1e-6)
end)
tween:Play();tween.Completed:Wait()
run:UnbindFromRenderStep('OrbitExample')
assert(frames>=50 and changes>=50)
local x,y,z=target.CFrame:ToOrientation()
local rebuilt=CFrame.fromOrientation(x,y,z)
assert((rebuilt.LookVector-target.CFrame.LookVector).Magnitude<1e-8)
local axis,angle=target.CFrame:ToAxisAngle()
print('ORBIT CAMERA / ORIENTATION TWEEN PASSED',frames,'frames',changes,'changes',axis,angle)
target:Destroy();camera:Destroy()
