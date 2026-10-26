-- 160 anchored objects animated by a headless frame loop.
local run=game:GetService('RunService')
local parts,positions,frames={},{},{}
local model=Instance.new('Model',workspace);model.Name='MovingFleet'
for i=1,160 do
    local part=Instance.new('Part',model);part.Name='Ship'..i
    part.Anchored=true;part.Size=Vector3.new(2,1,4)
    parts[i]=part;positions[i]=Vector3.new((i%20)*6,5,math.floor(i/20)*8)
end
local transformEvents,positionEvents,updates=0,0,0
parts[1]:GetPropertyChangedSignal('CFrame'):Connect(function() transformEvents+=1 end)
parts[1]:GetPropertyChangedSignal('Position'):Connect(function() positionEvents+=1 end)
local connection=run.Heartbeat:Connect(function()
    local now=time()
    for i,position in positions do
        frames[i]=CFrame.new(position+Vector3.new(math.sin(now+i)*3,math.cos(now*2+i),0))*CFrame.Angles(0,now,0)
    end
    workspace:BulkMoveTo(parts,frames,Enum.BulkMoveMode.FireCFrameChanged)
    updates+=1
end)
while updates<12 do task.wait() end
connection:Disconnect()
assert(transformEvents==updates and positionEvents==0,'Unexpected movement notifications')
local copy=model:Clone()
assert(#copy:GetChildren()==160 and copy.Ship1.CFrame==parts[1].CFrame)
game:BindToClose(function()
    local store=game:GetService('DataStoreService'):GetDataStore('MovingFleet')
    local position=parts[1].Position
    store:SetAsync('last',{count=#parts,frames=updates,position={position.X,position.Y,position.Z}})
    print('MOVING FLEET SAVED',#parts,updates)
end)
print('BULK FLEET FRAMES PASSED',#parts,updates,transformEvents,positionEvents)
