local TweenService=game:GetService("TweenService")
local part=Instance.new("Part",workspace)
part.Name="TweenedPart"
part.Anchored=true
part.CFrame=CFrame.new(0,5,0)
local tween=TweenService:Create(part,TweenInfo.new(0.5,Enum.EasingStyle.Sine,Enum.EasingDirection.InOut),{
    CFrame=CFrame.new(10,5,0)*CFrame.Angles(0,math.pi/2,0),
    Color=Color3.new(0,1,0),
    Transparency=0.5,
})
tween:Play()
print("Started",tween.PlaybackState)
local result=tween.Completed:Wait()
print("Finished",result,part.Position,part.Transparency)
assert(result==Enum.PlaybackState.Completed and part.Position==Vector3.new(10,5,0))
