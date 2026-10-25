local run=game:GetService('RunService')
local storage=game:GetService('ReplicatedStorage')
local probe=Instance.new('Folder',storage);probe.Name='HumanoidContextProbe'
local model=Instance.new('Model',workspace)
local root=Instance.new('Part',model);root.Name='HumanoidRootPart'
local h=Instance.new('Humanoid',model)
local reference=Instance.new('ObjectValue',probe);reference.Name='Target';reference.Value=h
local changed,deaths=0,0
h.StateEnabledChanged:Connect(function() assert(run:IsServer());changed+=1 end)
h.Died:Connect(function() assert(run:IsServer());deaths+=1 end)
h:SetStateEnabled(Enum.HumanoidStateType.Dead,false)
if not probe:GetAttribute('ClientReady') then probe:GetAttributeChangedSignal('ClientReady'):Wait() end
assert(changed==1 and not h:GetStateEnabled(Enum.HumanoidStateType.Dead))
h.Health=0;task.wait(.03);assert(deaths==0)
h:SetStateEnabled(Enum.HumanoidStateType.Dead,true)
task.wait(.03)
assert(deaths==1 and changed==2 and not probe:GetAttribute('ClientDeaths'))
probe:SetAttribute('AllowClientDeath',true)
task.wait(.05)
assert(deaths==1 and changed==2 and probe:GetAttribute('ClientDone'))
model:Destroy()
print('HUMANOID SERVER FLAGS, DEATH AND FILTERED EVENT CONTEXT PASSED')
