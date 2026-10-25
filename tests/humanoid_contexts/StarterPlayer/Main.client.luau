local run=game:GetService('RunService')
local probe=game:GetService('ReplicatedStorage'):WaitForChild('HumanoidContextProbe')
local h=probe.Target.Value
assert(h:GetStateEnabled(Enum.HumanoidStateType.Dead),'Server flag must not replicate into client metadata')
local changed,deaths=0,0
h.StateEnabledChanged:Connect(function() assert(run:IsClient());changed+=1 end)
h.Died:Connect(function() assert(run:IsClient());deaths+=1;probe:SetAttribute('ClientDeaths',deaths) end)
local waited=false
local waiter=task.spawn(function() h.Died:Wait();assert(run:IsClient());waited=true end)
h:SetStateEnabled(Enum.HumanoidStateType.Dead,false)
probe:SetAttribute('ClientReady',true)
if not probe:GetAttribute('AllowClientDeath') then probe:GetAttributeChangedSignal('AllowClientDeath'):Wait() end
assert(deaths==0 and changed==1 and not waited)
assert(coroutine.status(waiter)=='suspended','Server event consumed a client-side waiter')
h:SetStateEnabled(Enum.HumanoidStateType.Dead,true)
task.wait(.02)
assert(deaths==1 and changed==2 and waited and coroutine.status(waiter)=='dead')
probe:SetAttribute('ClientDone',true)
print('HUMANOID CLIENT FLAGS, DEATH WAITER AND FILTERED EVENT CONTEXT PASSED')
