-- Compatible with the ready archive delivered before spatial-query development.
-- Headless example: 120 moving targets, 12 tasks, damage events, score, cloning.
-- Run with --duration 2. Damage is scripted; it does not use raycasts or physics.
local TARGET_COUNT,WORKER_COUNT,HEALTH=120,12,4
local SHOTS_PER_WORKER=TARGET_COUNT*HEALTH/WORKER_COUNT
assert(SHOTS_PER_WORKER%1==0)
local RunService=game:GetService("RunService")
local CollectionService=game:GetService("CollectionService")
local ServerStorage=game:GetService("ServerStorage")
local Debris=game:GetService("Debris")
local arena=Instance.new("Model",workspace)
arena.Name="ReadyBuildArena"
arena:SetAttribute("State","Starting")
local score=Instance.new("IntValue",arena)
score.Name="Score"
local defeated=Instance.new("BindableEvent",arena)
defeated.Name="TargetDefeated"
local targets,dead={},{}
local killCount,workerCount,frames,scoreEvents=0,0,0,0
local scoreConnection=score.Changed:Connect(function(value)
    assert(type(value)=="number")
    scoreEvents+=1
end)
defeated.Event:Connect(function(target,worker)
    assert(target:GetAttribute("Health")==0 and worker>=1 and worker<=WORKER_COUNT)
    killCount+=1
    score.Value+=10
end)
for i=1,TARGET_COUNT do
    local target=Instance.new("Part",arena)
    target.Name="Target_"..i
    target.Anchored=true
    target.Size=Vector3.new(2,2,2)
    target.Color=Color3.fromHSV(i/TARGET_COUNT,0.8,1)
    target:SetAttribute("Id",i)
    target:SetAttribute("Health",HEALTH)
    target:SetAttribute("SpawnPosition",Vector3.new((i%15)*4,2,math.floor(i/15)*4))
    target.CFrame=CFrame.new(target:GetAttribute("SpawnPosition"))
    CollectionService:AddTag(target,"ReadyDemoTarget")
    target:GetAttributeChangedSignal("Health"):Connect(function()
        local health=target:GetAttribute("Health")
        if health==0 and not dead[target] then
            dead[target]=true
            target.Transparency=1
            defeated:Fire(target,target:GetAttribute("LastWorker"))
        end
    end)
    targets[i]=target
end
arena.PrimaryPart=targets[1]
for _,target in targets do assert(CollectionService:HasTag(target,"ReadyDemoTarget")) end
local movement=RunService.Heartbeat:Connect(function()
    frames+=1
    for i,target in targets do
        if not dead[target] then
            local spawn=target:GetAttribute("SpawnPosition")
            target.CFrame=CFrame.new(spawn+Vector3.new(0,math.sin(time()*3+i)*0.5,0))*CFrame.Angles(0,time(),0)
        end
    end
end)
local temporary=Instance.new("Folder",workspace)
temporary.Name="TemporaryDemoObject"
Debris:AddItem(temporary,0.05)
arena:SetAttribute("State","Running")
print("DEMO START",TARGET_COUNT,"targets",WORKER_COUNT,"workers")
for worker=1,WORKER_COUNT do
    task.spawn(function()
        for shot=1,SHOTS_PER_WORKER do
            local index=((shot-1)*WORKER_COUNT+worker-1)%TARGET_COUNT+1
            local target=targets[index]
            target:SetAttribute("LastWorker",worker)
            target:SetAttribute("Health",target:GetAttribute("Health")-1)
            task.wait(0.02)
        end
        workerCount+=1
    end)
end
while workerCount<WORKER_COUNT do task.wait(0.01) end
movement:Disconnect()
arena:SetAttribute("State","Finished")
assert(killCount==TARGET_COUNT)
assert(score.Value==TARGET_COUNT*10 and scoreEvents==TARGET_COUNT)
scoreConnection:Disconnect()
assert(frames>0 and temporary.Parent==nil)
local archived=arena:Clone()
archived.Name="ArchivedArena"
archived.Parent=ServerStorage
assert(archived.PrimaryPart==archived:FindFirstChild("Target_1"))
assert(archived.PrimaryPart~=arena.PrimaryPart)
assert(archived.Score.Value==score.Value and archived:GetAttribute("State")=="Finished")
arena:Destroy()
assert(targets[1].Parent==nil and archived.Parent==ServerStorage)
print("DEMO RESULT",killCount,"defeated",archived.Score.Value,"points",frames,"frames")
print("CLONE CHECK",archived:GetFullName(),#archived:GetDescendants(),"descendants")
archived:Destroy()
assert(archived.Parent==nil and workspace:FindFirstChild("ReadyBuildArena")==nil)
print("READY BUILD SHOWCASE PASSED")
