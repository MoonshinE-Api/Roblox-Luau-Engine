local run=game:GetService('RunService')
local function rejects(fn) assert(not pcall(fn),'Expected failure') end
if run:IsServer() then
    rejects(function() run:BindToRenderStep('server',1,function()end) end)
    rejects(function() return run.PreRender end)
    rejects(function() return run.RenderStepped end)
    print('SERVER RENDER CONTEXT RESTRICTIONS PASSED');return
end
assert(run:IsClient())
local frame,early,late=0,0,0
local order={}
local pre=run.PreRender:Connect(function(dt)
    assert(run:IsClient() and dt>0);frame+=1;order={}
end)
run:BindToRenderStep('late',300,function(dt)
    assert(run:IsClient() and game:GetService('Players').LocalPlayer and dt>0)
    assert(order[1]=='early' and table.find(order,'dup1') and table.find(order,'dup2'))
    table.insert(order,'late');late+=1
end)
run:BindToRenderStep('early',100,function()
    assert(#order==0);table.insert(order,'early');early+=1
end)
run:BindToRenderStep('duplicates',200,function() table.insert(order,'dup1') end)
run:BindToRenderStep('duplicates',250,function() table.insert(order,'dup2') end)
local observer=run.RenderStepped:Connect(function()
    assert(run:IsClient() and order[#order]=='late')
end)
for _=1,4 do run.RenderStepped:Wait() end
assert(frame>=4 and early==late and early>=4)
run:UnbindFromRenderStep('early');run:UnbindFromRenderStep('late');run:UnbindFromRenderStep('duplicates')
run:UnbindFromRenderStep('missing');observer:Disconnect()
local stopped=early
run.RenderStepped:Wait();assert(early==stopped)
local mutations=0
run:BindToRenderStep('mutating',1,function()
    mutations+=1
    run:UnbindFromRenderStep('mutating')
    run:BindToRenderStep('new-next-frame',2,function()
        mutations+=10;run:UnbindFromRenderStep('new-next-frame')
    end)
end)
run.RenderStepped:Wait();assert(mutations==1)
run.RenderStepped:Wait();assert(mutations==11)
local owner=Instance.new('LocalScript')
__engine.withContext({side='client',script=owner},function()
    run:BindToRenderStep('destroyed-owner',1,function() error('Destroyed owner callback ran') end)
end)
owner:Destroy();run.RenderStepped:Wait()
rejects(function() run:BindToRenderStep('bad',Enum.RenderPriority.Camera,function()end) end)
rejects(function() run:BindToRenderStep('bad',0/0,function()end) end)
rejects(function() run:BindToRenderStep('bad',1,false) end)
pre:Disconnect()
print('RENDER PRIORITY, DUPLICATE NAME, MUTATION, OWNER AND CLIENT CONTEXT PASSED')
