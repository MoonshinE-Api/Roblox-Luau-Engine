-- Procedural parts, palette colors, raycasts, tweens and cloning; --duration 1.
local rng=Random.new(123456)
local snapshot=rng:Clone()
local arena=Instance.new("Model",workspace)
arena.Name="SeededArena"
local collection=game:GetService("CollectionService")
local tweens=game:GetService("TweenService")
local parts,animations,goals={},{},{}
local completed=0
for i=1,20 do
    local part=Instance.new("Part",arena)
    part.Name="Target"..i
    part.Anchored=true
    local height=rng:NextNumber(2,5)
    if i==1 then assert(height==snapshot:NextNumber(2,5)) end
    part.Size=Vector3.new(4,height,4)
    part.Position=Vector3.new(((i-1)%5)*8,height/2,math.floor((i-1)/5)*8)
    part.BrickColor=BrickColor.palette(rng:NextInteger(0,127))
    part:SetAttribute("OriginalPaint",part.BrickColor)
    collection:AddTag(part,"GeneratedTarget")
    local goal=BrickColor.palette(rng:NextInteger(0,127))
    goals[part]=goal
    local animation=tweens:Create(part,TweenInfo.new(0.25,Enum.EasingStyle.Quad,Enum.EasingDirection.InOut),{Color=goal.Color,Transparency=0.25})
    animation.Completed:Connect(function(status)
        assert(status==Enum.PlaybackState.Completed)
        completed+=1
    end)
    table.insert(parts,part);table.insert(animations,animation)
end
rng:Shuffle(parts)
local params=RaycastParams.new()
params.FilterType=Enum.RaycastFilterType.Include
params.FilterDescendantsInstances={arena}
local hits=0
for _,part in parts do
    local result=workspace:Raycast(part.Position+Vector3.new(0,10,0),Vector3.new(0,-20,0),params)
    assert(result and result.Instance==part and result.Normal.Y==1)
    hits+=1
end
for _,animation in animations do animation:Play() end
animations[#animations].Completed:Wait()
task.wait()
assert(completed==20 and hits==20)
for _,part in parts do
    assert(part.Color==goals[part].Color and part.Transparency==0.25)
    assert(typeof(part:GetAttribute("OriginalPaint"))=="BrickColor")
end
local clone=arena:Clone()
clone.Name="ArchivedSeededArena"
clone.Parent=game:GetService("ServerStorage")
assert(#clone:GetChildren()==20 and #collection:GetTagged("GeneratedTarget")==40)
arena:Destroy()
assert(#collection:GetTagged("GeneratedTarget")==20)
print("SEEDED COLORS PASSED",completed,"tweens",hits,"ray hits",#clone:GetChildren(),"archived parts")
