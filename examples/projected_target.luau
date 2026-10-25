-- Run with --mode client --duration 1. Uses public Roblox APIs only.
local camera=workspace.CurrentCamera
assert(camera,'Run this example in client mode')
camera.CameraType=Enum.CameraType.Scriptable
camera.CFrame=CFrame.lookAt(Vector3.new(0,4,20),Vector3.zero)
camera.FieldOfView=70
local target=Instance.new('Part',workspace)
target.Name='TrackedTarget';target.Anchored=true;target.Size=Vector3.new(3,3,3)
target.Color=Color3.fromRGB(100,160,255)
local player=game:GetService('Players').LocalPlayer
local screen=Instance.new('ScreenGui',player.PlayerGui)
screen.IgnoreGuiInset=true
local label=Instance.new('TextLabel',screen)
label.Name='TargetLabel';label.Size=UDim2.fromOffset(200,32)
label.AnchorPoint=Vector2.new(0.5,1)
label.Font=Enum.Font.ArialBold;label.TextSize=20
label.BackgroundTransparency=0.25
local gradient=Instance.new('UIGradient',label)
gradient.Color=ColorSequence.new(Color3.fromRGB(80,130,220),Color3.fromRGB(30,50,100))
local tween=game:GetService('TweenService'):Create(target,TweenInfo.new(0.2,Enum.EasingStyle.Linear),{Position=Vector3.new(5,0,0)})
tween:Play()
local updates=0
repeat
    local point,visible=camera:WorldToViewportPoint(target.Position)
    label.Visible=visible;label.Position=UDim2.fromOffset(point.X,point.Y)
    label.Text=string.format('%s: %.1f studs',target.Name,(camera.CFrame.Position-target.Position).Magnitude)
    local ray=camera:ViewportPointToRay(point.X,point.Y)
    local hit=workspace:Raycast(ray.Origin,ray.Direction*100)
    assert(hit and hit.Instance==target,'Projected ray should select the target')
    updates+=1
    task.wait()
until tween.PlaybackState==Enum.PlaybackState.Completed
assert(updates>=2 and label.Visible)
print('PROJECTED TARGET / UI / TWEEN / RAYCAST PASSED',updates,'updates',label.Text)
screen:Destroy();target:Destroy()
