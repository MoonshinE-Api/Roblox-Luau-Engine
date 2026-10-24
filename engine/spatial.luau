-- Headless geometry queries. Bounding queries use oriented boxes; ray/narrow-phase
-- queries currently require block Parts. There is no dynamics solver or terrain.
return function(R)
    local V3=R.datatypes.Vector3
    local function vector(value)
        assert(typeof(value)=="Vector3" and value.X==value.X and value.Y==value.Y and value.Z==value.Z
            and math.abs(value.X)<math.huge and math.abs(value.Y)<math.huge and math.abs(value.Z)<math.huge,"Expected finite Vector3")
        return value
    end
    local function size(value)
        vector(value);assert(value.X>=0 and value.Y>=0 and value.Z>=0,"Size must be nonnegative")
        return value
    end
    local function block(part)
        assert(part.ClassName=="Part" and part.Shape==R.Enum.PartType.Block,
            "Exact spatial queries currently support block Parts; unsupported geometry: "..part.ClassName)
    end
    local function params(value,name)
        if value==nil then return R.queryParams[R.datatypes[name].new()] end
        assert(typeof(value)==name and R.queryParams[value],"Expected "..name)
        return R.queryParams[value]
    end
    local groups={Default=0}
    local matrix={}
    local function group(name) assert(type(name)=="string" and groups[name]~=nil,"Unknown collision group: "..tostring(name));return groups[name] end
    local function pair(a,b) local x,y=group(a),group(b);return math.min(x,y)*32+math.max(x,y) end
    local physics={}
    function physics:IsCollisionGroupRegistered(name) return groups[name]~=nil end
    function physics:GetMaxCollisionGroups() return 32 end
    function physics:RegisterCollisionGroup(name)
        assert(type(name)=="string" and #name>0,"Invalid collision group name")
        if groups[name]~=nil then return end
        local used={};for _,id in groups do used[id]=true end
        for id=1,31 do if not used[id] then groups[name]=id;return end end
        error("Maximum collision groups reached",2)
    end
    function physics:CreateCollisionGroup(name) self:RegisterCollisionGroup(name);return groups[name] end
    function physics:GetCollisionGroupId(name) return group(name) end
    function physics:GetCollisionGroupName(id) for name,value in groups do if value==id then return name end end;error("Unknown collision group id",2) end
    function physics:GetRegisteredCollisionGroups()
        local result={}
        for name,id in groups do
            local mask=0xffffffff
            for other=0,31 do
                if matrix[math.min(id,other)*32+math.max(id,other)]==false then mask=bit32.band(mask,bit32.bnot(bit32.lshift(1,other))) end
            end
            if mask>=0x80000000 then mask-=0x100000000 end
            table.insert(result,{name=name,mask=mask})
        end
        table.sort(result,function(a,b) return groups[a.name]<groups[b.name] end);return result
    end
    function physics:GetCollisionGroups()
        local result=self:GetRegisteredCollisionGroups();for _,record in result do record.id=groups[record.name] end;return result
    end
    function physics:CollisionGroupSetCollidable(a,b,value) assert(type(value)=="boolean","Expected boolean");matrix[pair(a,b)]=value end
    function physics:CollisionGroupsAreCollidable(a,b) return matrix[pair(a,b)]~=false end
    function physics:SetPartCollisionGroup(part,name) group(name);assert(typeof(part)=="Instance" and part:IsA("BasePart"),"Expected BasePart");part.CollisionGroup=name end
    function physics:CollisionGroupContainsPart(name,part) group(name);return part.CollisionGroup==name end
    function physics:UnregisterCollisionGroup(name)
        local id=group(name);assert(id~=0,"Cannot unregister Default")
        groups[name]=nil
        for other=0,31 do matrix[math.min(id,other)*32+math.max(id,other)]=nil end
        for object,d in R.instances do if d.props.CollisionGroup==name then object.CollisionGroup="Default" end end
    end
    physics.RemoveCollisionGroup=physics.UnregisterCollisionGroup
    function physics:RenameCollisionGroup(old,new)
        local id=group(old);assert(id~=0 and type(new)=="string" and #new>0 and groups[new]==nil,"Invalid collision group rename")
        groups[new],groups[old]=id,nil
        for object,d in R.instances do if d.props.CollisionGroup==old then object.CollisionGroup=new end end
    end
    R.classMethods.PhysicsService=physics
    R.classSetters.BasePart.CollisionGroup=function(part,name)
        group(name)
        local data=R.instances[part]
        if data.props.CollisionGroup~=name then data.props.CollisionGroup=name;R.changed(part,"CollisionGroup") end
    end
    -- Collision filtering is local to this runtime; there is no physics replication.
    local function accepts(part,p)
        if not p.BruteForceAllSlow and not (if p.RespectCanCollide then part.CanCollide else part.CanQuery) then return false end
        if not physics:CollisionGroupsAreCollidable(p.CollisionGroup,part.CollisionGroup) then return false end
        local listed=false
        for _,ancestor in p.FilterDescendantsInstances do
            if part==ancestor or part:IsDescendantOf(ancestor) then listed=true;break end
        end
        return if p.FilterType==R.Enum.RaycastFilterType.Include then listed else not listed
    end
    local function parts(root,p)
        assert(root:IsA("WorldRoot"),"Expected WorldRoot")
        group(p.CollisionGroup)
        local result={}
        for _,part in root:GetDescendants() do
            if part:IsA("BasePart") then
                local parent=part.Parent
                while parent and parent~=root and not parent:IsA("WorldRoot") do parent=parent.Parent end
                if parent==root and accepts(part,p) then table.insert(result,part) end
            end
        end
        return result
    end
    local function rayBox(origin,direction,part)
        local o=part.CFrame:PointToObjectSpace(origin)
        local d=part.CFrame:VectorToObjectSpace(direction)
        local half=part.Size*0.5
        local low,high=0,1
        local normal=nil
        for _,axis in {"X","Y","Z"} do
            local a,b,c=o[axis],d[axis],half[axis]
            if math.abs(b)<1e-12 then if a< -c or a>c then return end
            else
                local near,far=(-c-a)/b,(c-a)/b
                local sign=-1
                if near>far then near,far=far,near;sign=1 end
                if near>=low then
                    low=near
                    normal=if axis=="X" then V3.new(sign,0,0) elseif axis=="Y" then V3.new(0,sign,0) else V3.new(0,0,sign)
                end
                high=math.min(high,far)
                if low>high then return end
            end
        end
        -- Rays starting strictly inside a solid do not hit that solid.
        if not normal then return end
        return low,part.CFrame:VectorToWorldSpace(normal)
    end
    local function axes(cf) return {cf.RightVector,cf.UpVector,cf.ZVector} end
    local function intersects(cf,extent,otherCF,otherExtent,tolerance)
        local a,b=axes(cf),axes(otherCF)
        local h,k={extent.X/2,extent.Y/2,extent.Z/2},{otherExtent.X/2,otherExtent.Y/2,otherExtent.Z/2}
        local delta=otherCF.Position-cf.Position
        local function separated(axis)
            local length=axis.Magnitude
            if length<1e-10 then return false end
            local radius=0
            for i=1,3 do radius+=h[i]*math.abs(a[i]:Dot(axis))+k[i]*math.abs(b[i]:Dot(axis)) end
            return math.abs(delta:Dot(axis))>radius+(tolerance or 0)*length+1e-9
        end
        for i=1,3 do
            if separated(a[i]) or separated(b[i]) then return false end
            for j=1,3 do if separated(a[i]:Cross(b[j])) then return false end end
        end
        return true
    end
    local world={}
    R.classMethods.WorldRoot=world
    function world:Raycast(origin,direction,parameter)
        vector(origin);vector(direction)
        local p=params(parameter,"RaycastParams")
        if direction.Magnitude==0 then return nil end
        local best,bestNormal,bestPart=nil,nil,nil
        for _,part in parts(self,p) do
            block(part)
            local hit,normal=rayBox(origin,direction,part)
            if hit and (best==nil or hit<best) then best,bestNormal,bestPart=hit,normal,part end
        end
        if bestPart then
            return R.makeRecord("RaycastResult",{Distance=direction.Magnitude*best,Instance=bestPart,
                Material=bestPart.Material,Position=origin+direction*best,Normal=bestNormal})
        end
    end
    local function query(root,p,test,omit)
        local result={}
        for _,part in parts(root,p) do
            if part~=omit and test(part) then
                table.insert(result,part)
                if p.MaxParts>0 and #result>=p.MaxParts then break end
            end
        end
        return result
    end
    function world:GetPartBoundsInBox(cf,extent,parameter)
        assert(typeof(cf)=="CFrame","Expected CFrame");size(extent)
        local p=params(parameter,"OverlapParams")
        return query(self,p,function(part) return intersects(cf,extent,part.CFrame,part.Size,p.Tolerance) end)
    end
    function world:GetPartBoundsInRadius(position,radius,parameter)
        vector(position);assert(type(radius)=="number" and radius>=0 and radius<math.huge,"Expected nonnegative radius")
        local p=params(parameter,"OverlapParams")
        return query(self,p,function(part)
            local localPoint=part.CFrame:PointToObjectSpace(position)
            local half=part.Size*0.5
            local nearest=V3.new(math.clamp(localPoint.X,-half.X,half.X),math.clamp(localPoint.Y,-half.Y,half.Y),math.clamp(localPoint.Z,-half.Z,half.Z))
            return (localPoint-nearest).Magnitude<=radius+p.Tolerance
        end)
    end
    function world:GetPartsInPart(part,parameter)
        assert(typeof(part)=="Instance" and part:IsA("BasePart"),"Expected BasePart");block(part)
        local p=params(parameter,"OverlapParams")
        return query(self,p,function(other) block(other);return intersects(part.CFrame,part.Size,other.CFrame,other.Size,0) end,part)
    end
end
