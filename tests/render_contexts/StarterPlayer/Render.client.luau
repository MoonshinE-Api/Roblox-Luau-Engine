local run=game:GetService('RunService')
local storage=game:GetService('ReplicatedStorage')
local ticks=0
run:BindToRenderStep('client',Enum.RenderPriority.Camera.Value,function(dt)
    assert(run:IsClient() and game:GetService('Players').LocalPlayer and dt>0)
    ticks+=1;storage:SetAttribute('ClientRenderTicks',ticks)
end)
for _=1,6 do run.RenderStepped:Wait() end
run:UnbindFromRenderStep('client')
assert(ticks>=6)
print('BOTH-MODE CLIENT RENDER PASSED')
