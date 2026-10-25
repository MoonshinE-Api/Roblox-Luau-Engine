-- A headless animated scene. No particles, light pixels or mesh skinning are rendered.
local lighting=game:GetService('Lighting')
lighting.ClockTime=8
local root=Instance.new('Part',workspace)
root.Name='AnimatedEnvironment';root.Anchored=true;root.Position=Vector3.new(0,5,0)
local a=Instance.new('Attachment',root);a.Name='BeamStart';a.Position=Vector3.new(-4,0,0)
local bone=Instance.new('Bone',root);bone.Name='AnimatedBone';bone.Position=Vector3.new(4,0,0)
local b=Instance.new('Attachment',bone);b.Name='BeamEnd'
local beam=Instance.new('Beam',root);beam.Attachment0=a;beam.Attachment1=b
beam.Color=ColorSequence.new(Color3.fromHex('#f80'),Color3.fromHex('#08f'))
beam.Transparency=NumberSequence.new(0.2);beam.Width0=0.5;beam.Width1=0.1
local light=Instance.new('PointLight',b);light.Color=Color3.fromHex('#08f');light.Range=16
local particles=Instance.new('ParticleEmitter',b)
particles.Lifetime=NumberRange.new(0.5,1.5);particles.Speed=NumberRange.new(2,4);particles.Rate=20
local bloom=Instance.new('BloomEffect',lighting);bloom.Intensity=0.7
local frames=0
local connection=game:GetService('RunService').Heartbeat:Connect(function()
    frames+=1
    bone.Transform=CFrame.new(0,math.sin(time()*8),0)*CFrame.fromAxisAngle(Vector3.zAxis,math.sin(time()*4))
    light.Brightness=1+math.sin(time()*8)^2
    assert((b.WorldCFrame-b.WorldPosition).Position==Vector3.zero)
    assert((b.WorldPosition-bone.TransformedWorldCFrame.Position).Magnitude<1e-7)
end)
local tween=game:GetService('TweenService'):Create(lighting,TweenInfo.new(0.5,Enum.EasingStyle.Linear),{ClockTime=18})
tween:Play();tween.Completed:Wait();connection:Disconnect()
assert(lighting.TimeOfDay=='18:00:00' and frames>=29)
local clone=root:Clone()
assert(clone.Beam.Attachment0==clone.BeamStart and clone.Beam.Attachment1==clone.AnimatedBone.BeamEnd)
print('ANIMATED ATTACHMENTS / BONE / BEAM / LIGHTING CLOCK PASSED',frames,'frames',lighting.TimeOfDay,b.WorldPosition)
root:Destroy();clone:Destroy();bloom:Destroy()
