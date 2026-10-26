-- Convex query policy for the Rust/Parry kernel. This is not a physics solver.
return function(R)
    local V3,CF=R.datatypes.Vector3,R.datatypes.CFrame
    local spatial,world=R.spatial,R.classMethods.WorldRoot
    local HEADER,RECORD=64,128
    local packedShapes=setmetatable({}, {__mode='k'})
    local function frame(value)
        assert(typeof(value)=='CFrame','Expected CFrame')
        local x,y,z=value.RightVector,value.UpVector,value.ZVector
        spatial.vector(value.Position);spatial.vector(x);spatial.vector(y);spatial.vector(z)
        assert(x.Magnitude>1e-12 and y.Magnitude>1e-12 and z.Magnitude>1e-12,'CFrame rotation is singular')
        -- Build 735 orthonormalizes shape-cast frames. Gram-Schmidt also keeps
        -- malformed direct host packets out of the native rotation conversion.
        x=x.Unit;y=y-x*x:Dot(y)
        assert(y.Magnitude>1e-12,'CFrame rotation is singular')
        y=y.Unit;z=x:Cross(y)
        return CF.fromMatrix(value.Position,x,y,z)
    end
    local function dimensions(value,minimum)
        spatial.size(value)
        local f32=R.float32
        local result=V3.new(f32(math.max(minimum,f32(value.X))),f32(math.max(minimum,f32(value.Y))),f32(math.max(minimum,f32(value.Z))))
        spatial.vector(result);return result
    end
    local function descriptor(part)
        assert(R.instances[part] and part:IsA('BasePart'),'Expected BasePart')
        local kind
        if part.ClassName=='Part' then
            kind=if part.Shape==R.Enum.PartType.Block then 1 elseif part.Shape==R.Enum.PartType.Ball then 2 else 3
        elseif part.ClassName=='WedgePart' then kind=4
        elseif part.ClassName=='CornerWedgePart' then kind=5
        else error('Convex query geometry is not implemented for '..part.ClassName,3) end
        return kind,dimensions(part.Size,.05),frame(part.CFrame)
    end
    local function write(packet,offset,kind,size,cf)
        buffer.writeu32(packet,offset,kind)
        for i,value in {size.X,size.Y,size.Z} do buffer.writef64(packet,offset+8+(i-1)*8,value) end
        for i,value in {cf:GetComponents()} do buffer.writef64(packet,offset+32+(i-1)*8,value) end
    end
    local function copyPart(packet,offset,part)
        local properties=R.instances[part].props
        local cached=packedShapes[part]
        if not cached or cached.frame~=properties.CFrame or cached.size~=properties.Size or cached.shape~=properties.Shape then
            local bytes=buffer.create(RECORD);write(bytes,0,descriptor(part))
            cached={frame=properties.CFrame,size=properties.Size,shape=properties.Shape,bytes=bytes};packedShapes[part]=cached
        end
        buffer.copy(packet,offset,cached.bytes)
    end
    local function direction(value,cast)
        spatial.vector(value)
        if cast then assert(value.Magnitude<=1024,'Shapecast distance exceeds 1024 studs') end
        return value
    end
    local function query(root,mode,kind,size,cf,velocity,parameter,omit)
        local p=spatial.params(parameter,if mode==2 then 'OverlapParams' else 'RaycastParams')
        local candidates={}
        for _,part in spatial.parts(root,p) do if part~=omit then table.insert(candidates,part) end end
        assert(#candidates<=100000,'Spatial query exceeds the host candidate limit of 100000 parts')
        local input=buffer.create(HEADER+RECORD*(#candidates+1))
        local output=buffer.create(64+#candidates*4)
        buffer.writeu32(input,0,0x31514752);buffer.writeu32(input,4,mode);buffer.writeu32(input,8,#candidates)
        if mode==2 and p.MaxParts>0 then buffer.writeu32(input,12,math.min(p.MaxParts,#candidates)) end
        for i,value in {velocity.X,velocity.Y,velocity.Z} do buffer.writef64(input,16+(i-1)*8,value) end
        write(input,HEADER,kind,size,cf)
        for index,part in candidates do copyPart(input,HEADER+RECORD*index,part) end
        local status=__host_geometry(input,output)
        local errors={[-1]='Invalid geometry packet',[-2]='Invalid shape dimensions or frame',[-3]='Unsupported convex query',[-4]='Convex query failed to converge'}
        assert(status==0,errors[status] or 'Native geometry query failed')
        local index=buffer.readu32(output,0)
        if mode==2 then
            local result={}
            for i=0,index-1 do result[i+1]=candidates[buffer.readu32(output,64+i*4)] end
            return result
        end
        if index==0 then return nil end
        local function read(offset) return V3.new(buffer.readf64(output,offset),buffer.readf64(output,offset+8),buffer.readf64(output,offset+16)) end
        local part=candidates[index]
        return R.makeRecord('RaycastResult',{Instance=part,Material=part.Material,
            Distance=velocity.Magnitude*buffer.readf64(output,8),Position=read(16),Normal=read(40)})
    end
    function world:Raycast(origin,velocity,parameter)
        spatial.vector(origin);direction(velocity,false)
        spatial.params(parameter,'RaycastParams')
        if velocity.Magnitude==0 then return nil end
        return query(self,0,0,V3.zero,CF.new(origin),velocity,parameter)
    end
    function world:Blockcast(cf,size,velocity,parameter)
        cf=frame(cf);size=dimensions(size,0);direction(velocity,true)
        spatial.params(parameter,'RaycastParams')
        assert(math.max(size.X,size.Y,size.Z)<=512,'Blockcast size exceeds 512 studs')
        if velocity.Magnitude==0 then return nil end
        return query(self,if size==V3.zero then 0 else 1,1,size,cf,velocity,parameter)
    end
    function world:Spherecast(position,radius,velocity,parameter)
        spatial.vector(position);direction(velocity,true)
        spatial.params(parameter,'RaycastParams')
        assert(type(radius)=='number','Spherecast radius requires number')
        radius=R.float32(radius)
        assert(radius==radius and radius>=0 and radius<=256,'Spherecast radius must be between 0 and 256')
        if velocity.Magnitude==0 then return nil end
        return query(self,if radius==0 then 0 else 1,2,V3.one*(radius*2),CF.new(position),velocity,parameter)
    end
    function world:Shapecast(part,velocity,parameter)
        local kind,size,cf=descriptor(part);direction(velocity,true)
        spatial.params(parameter,'RaycastParams')
        assert(math.max(size.X,size.Y,size.Z)<=512,'Shapecast size exceeds 512 studs')
        if velocity.Magnitude==0 then return nil end
        return query(self,1,kind,size,cf,velocity,parameter,part)
    end
    function world:GetPartsInPart(part,parameter)
        local kind,size,cf=descriptor(part)
        return query(self,2,kind,size,cf,V3.zero,parameter,part)
    end
end
