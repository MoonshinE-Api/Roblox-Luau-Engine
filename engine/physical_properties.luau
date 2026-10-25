return function(R)
    local fields={'Density','Friction','Elasticity','FrictionWeight','ElasticityWeight','AcousticAbsorption'}
    local limits={{R.physicalCatalog.minimum_density,100},{0,2},{0,1},{0,100},{0,100},{0,1}}
    local function make(values)
        local data={};for i,name in fields do data[name]=values[i] end
        return R.makeValue('PhysicalProperties',data,function(_,key,row)
            if row[key]~=nil then return row[key] end
            error(key..' is not a valid member of PhysicalProperties',2)
        end,{
            __tostring=function(self)local parts={};for _,key in fields do table.insert(parts,tostring(self[key]))end;return table.concat(parts,', ')end,
            __eq=function(a,b)
                if typeof(a)~='PhysicalProperties' or typeof(b)~='PhysicalProperties' then return false end
                for _,key in fields do if a[key]~=b[key] then return false end end;return true
            end,
        })
    end
    local PhysicalProperties={};local warnings=0
    function PhysicalProperties.new(...)
        local args=table.pack(...)
        if args.n==1 then
            local material=args[1]
            assert(typeof(material)=='EnumItem' and material.EnumType==R.Enum.Material,'PhysicalProperties.new expects Enum.Material')
            return make(assert(R.physicalCatalog.materials[material.Name],'Missing material properties').properties)
        end
        assert(args.n==3 or args.n==5 or args.n==6,'PhysicalProperties.new expects 1, 3, 5 or 6 arguments')
        if args.n==3 then args[4],args[5]=1,1 end
        if args.n<6 then args[6]=1 end
        local changed={}
        for i,key in fields do
            assert(type(args[i])=='number' and args[i]==args[i],'PhysicalProperties.'..key..' requires a number other than NaN')
            local value=R.float32(args[i]);local clamped=math.clamp(value,limits[i][1],limits[i][2])
            if value~=clamped then table.insert(changed,key) end
            args[i]=clamped
        end
        if #changed>0 and warnings<100 then
            warnings+=1;warn('PhysicalProperties clamped: '..table.concat(changed,', '))
        end
        return make(args)
    end
    R.datatypes.PhysicalProperties=table.freeze(PhysicalProperties)
    local f32=R.float32
    function R.partVolume(part)
        local size=part.Size
        assert(size.X==size.X and size.Y==size.Y and size.Z==size.Z,'Cannot calculate mass for NaN size')
        local x,y,z=math.max(f32(size.X),.05),math.max(f32(size.Y),.05),math.max(f32(size.Z),.05)
        x,y,z=f32(x),f32(y),f32(z)
        local coefficient=1
        if part.ClassName=='Part' then
            local shape=part.Shape
            if shape==R.Enum.PartType.Ball then
                x=math.min(x,y,z);y,z=x,x;coefficient=R.physicalCatalog.unit_volume.Ball
            elseif shape==R.Enum.PartType.Cylinder then
                y=math.min(y,z);z=y;coefficient=R.physicalCatalog.unit_volume.Cylinder
            end
        elseif part.ClassName=='WedgePart' then coefficient=R.physicalCatalog.unit_volume.Wedge
        elseif part.ClassName=='CornerWedgePart' then coefficient=R.physicalCatalog.unit_volume.CornerWedge
        else error('Mass geometry is not implemented for '..part.ClassName,2) end
        return f32(f32(f32(x*y)*z)*coefficient)
    end
end
