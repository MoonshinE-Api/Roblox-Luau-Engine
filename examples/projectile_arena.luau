-- A scripted continuous-collision arena using the convex query kernel.
-- These are anchored objects moved explicitly by Luau, not a rigid-body solver.
local run=game:GetService('RunService')
local arena=Instance.new('Model',workspace);arena.Name='ProjectileArena'
local geometry=Instance.new('Folder',arena);geometry.Name='Geometry'
local actors=Instance.new('Folder',arena);actors.Name='Projectiles'
local function obstacle(class,name,position,size,shape)
    local p=Instance.new(class,geometry);p.Name=name;p.Anchored=true;p.Position=position;p.Size=size
    p.Material=Enum.Material.Metal
    if shape then p.Shape=shape end
    return p
end
obstacle('Part','Floor',Vector3.new(0,-1,0),Vector3.new(62,2,62))
obstacle('Part','Ceiling',Vector3.new(0,15,0),Vector3.new(62,2,62))
for _,side in {-1,1} do
    obstacle('Part','WallX'..side,Vector3.new(side*30,7,0),Vector3.new(2,14,62))
    obstacle('Part','WallZ'..side,Vector3.new(0,7,side*30),Vector3.new(62,14,2))
end
obstacle('Part','Core',Vector3.new(0,5,0),Vector3.new(6,6,6),Enum.PartType.Ball)
obstacle('Part','Cylinder',Vector3.new(-12,4,8),Vector3.new(8,4,4),Enum.PartType.Cylinder)
obstacle('WedgePart','Ramp',Vector3.new(12,3,7),Vector3.new(8,6,10))
obstacle('CornerWedgePart','Corner',Vector3.new(-8,2,-12),Vector3.new(8,4,8))
local parts,positions,velocities,frames={},{},{},{}
local radius,skin=.4,.001
for i=1,32 do
    local angle=i*math.pi*2/32;local x,z=math.cos(angle),math.sin(angle)
    local p=Instance.new('Part',actors);p.Name='Projectile'..i;p.Anchored=true;p.CanCollide=false
    p.Shape=Enum.PartType.Ball;p.Size=Vector3.one*(radius*2);p.Color=Color3.fromHSV(i/32,1,1)
    parts[i]=p;positions[i]=Vector3.new(x*23,5,z*23)
    velocities[i]=Vector3.new(-x*180+z*20,math.sin(i*.7)*30,-z*180-x*20)
    p.Position=positions[i]
end
local params=RaycastParams.new();params.FilterType=Enum.RaycastFilterType.Include;params.FilterDescendantsInstances={geometry}
local ticks,casts,collisions=0,0,0
local hitKinds={}
local connection=run.Heartbeat:Connect(function()
    for i,position in positions do
        local velocity=velocities[i];local remaining=1/60;local speed=velocity.Magnitude
        for bounce=1,4 do
            local motion=velocity*remaining;casts+=1
            local hit=workspace:Spherecast(position,radius,motion,params)
            if not hit then position+=motion;break end
            collisions+=1;hitKinds[hit.Instance.Name]=true
            position+=motion.Unit*math.max(0,hit.Distance-skin)
            position+=hit.Normal*skin
            remaining*=math.max(0,1-hit.Distance/motion.Magnitude)
            velocity-=2*velocity:Dot(hit.Normal)*hit.Normal
            if remaining<1e-8 then break end
        end
        assert(math.abs(velocity.Magnitude-speed)<1e-5,'A reflection changed speed')
        assert(math.abs(position.X)<29 and math.abs(position.Z)<29 and position.Y>radius-.01 and position.Y<14-radius+.01,'A projectile tunneled through the room')
        positions[i],velocities[i]=position,velocity;frames[i]=CFrame.new(position)
    end
    workspace:BulkMoveTo(parts,frames,Enum.BulkMoveMode.FireCFrameChanged)
    ticks+=1
    game:GetService('Lighting').ClockTime=6+ticks/30
end)
while ticks<60 do task.wait() end
connection:Disconnect()
assert(collisions>100 and casts>=32*60 and hitKinds.Core)
local kinds=0;for _ in hitKinds do kinds+=1 end
assert(kinds>=5,'Expected multiple convex surface contacts')
game:BindToClose(function(reason)
    task.wait(.01)
    local store=game:GetService('DataStoreService'):GetDataStore('ProjectileArena')
    store:SetAsync('latest',{actors=#parts,ticks=ticks,casts=casts,collisions=collisions,surfaces=kinds,reason=reason.Name})
    print('PROJECTILE ARENA SAVED',#parts,ticks,collisions,kinds)
end)
print('CONTINUOUS PROJECTILE ARENA PASSED',#parts,ticks,casts,collisions,kinds)
