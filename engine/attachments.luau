-- Headless attachment/bone transforms and constraint references. No skinning or solver.
-- References: physics/Attachment.c, rbx/BoneInstance.c, creator-docs.
return function(R)
    local CF,V3=R.datatypes.CFrame,R.datatypes.Vector3
    local G,S,M=R.classGetters,R.classSetters,R.classMethods
    local function property(d,key,kind,value) d.propertyTypes[key]=kind;d.props[key]=value end
    local function finite(v)
        assert(typeof(v)=='Vector3' and v.X==v.X and v.Y==v.Y and v.Z==v.Z
            and math.max(math.abs(v.X),math.abs(v.Y),math.abs(v.Z))<math.huge,'Expected finite Vector3')
        return v
    end
    local function degrees(...) local a={...};for i,v in a do a[i]=math.deg(v) end;return V3.new(table.unpack(a)) end
    local function rotatedAxis(old,axis)
        if axis.Magnitude<1e-4 then return old end
        axis=axis.Unit
        local up=old.UpVector-axis*axis:Dot(old.UpVector)
        if up.Magnitude<1e-4 then
            local cross=old.RightVector:Cross(axis)
            local rotation=CF.fromAxisAngle(cross,math.atan2(cross.Magnitude,old.RightVector:Dot(axis)))
            up=rotation:VectorToWorldSpace(old.UpVector)
            up-=axis*axis:Dot(up)
        end
        return CF.fromMatrix(old.Position,axis,up.Unit)
    end
    local function rotatedSecondary(old,up)
        local axis=old.RightVector
        up-=axis*axis:Dot(up)
        if up.Magnitude<1e-4 then return old end
        return CF.fromMatrix(old.Position,axis,up.Unit)
    end
    local parentFrame,worldFrame
    parentFrame=function(object)
        local parent=object.Parent
        while parent do
            if parent:IsA('Attachment') then return worldFrame(parent,true) end
            if parent:IsA('BasePart') then return parent.CFrame end
            if parent:IsA('PVInstance') then return parent:GetPivot() end
            parent=parent.Parent
        end
        return CF.identity
    end
    worldFrame=function(object,transformed)
        local frame=parentFrame(object)*R.instances[object].props.CFrame
        if transformed and object:IsA('Bone') then frame*=object.Transform end
        return frame
    end
    G.Attachment={
        Position=function(self) return self.CFrame.Position end,
        Axis=function(self) return self.CFrame.RightVector end,
        SecondaryAxis=function(self) return self.CFrame.UpVector end,
        Orientation=function(self) return degrees(self.CFrame:ToOrientation()) end,
        Rotation=function(self) return degrees(self.CFrame:ToEulerAnglesXYZ()) end,
        WorldCFrame=function(self) return worldFrame(self,false) end,
        WorldPosition=function(self) return self.WorldCFrame.Position end,
        WorldAxis=function(self) return self.WorldCFrame.RightVector end,
        WorldSecondaryAxis=function(self) return self.WorldCFrame.UpVector end,
        WorldOrientation=function(self) return degrees(self.WorldCFrame:ToOrientation()) end,
        WorldRotation=function(self) return degrees(self.WorldCFrame:ToEulerAnglesXYZ()) end,
    }
    G.Bone={
        TransformedCFrame=function(self) return self.CFrame*self.Transform end,
        TransformedWorldCFrame=function(self) return worldFrame(self,true) end,
    }
    local observed={'Position','Axis','SecondaryAxis','Orientation','Rotation','WorldPosition','WorldAxis','WorldSecondaryAxis','WorldOrientation','WorldRotation','WorldCFrame'}
    local function writeFrame(self,value)
        assert(typeof(value)=='CFrame','Expected CFrame')
        finite(value.Position);finite(value.RightVector);finite(value.UpVector)
        local old=R.instances[self].props.CFrame
        local normalized=rotatedSecondary(rotatedAxis(old,value.RightVector),value.UpVector).Rotation+value.Position
        if normalized==old then return end
        local before={}
        for _,key in observed do before[key]=self[key] end
        R.instances[self].props.CFrame=normalized
        R.changed(self,'CFrame')
        for _,key in observed do if self[key]~=before[key] then R.changed(self,key) end end
        if self:IsA('Bone') then R.changed(self,'TransformedCFrame');R.changed(self,'TransformedWorldCFrame') end
    end
    S.Attachment={
        CFrame=writeFrame,
        Position=function(self,value) self.CFrame=self.CFrame.Rotation+finite(value) end,
        Axis=function(self,value) writeFrame(self,rotatedAxis(self.CFrame,finite(value))) end,
        SecondaryAxis=function(self,value) writeFrame(self,rotatedSecondary(self.CFrame,finite(value))) end,
        Orientation=function(self,value)
            finite(value);self.CFrame=CF.fromOrientation(math.rad(value.X),math.rad(value.Y),math.rad(value.Z))+self.Position
        end,
        Rotation=function(self,value)
            finite(value);self.CFrame=CF.Angles(math.rad(value.X),math.rad(value.Y),math.rad(value.Z))+self.Position
        end,
        WorldCFrame=function(self,value) assert(typeof(value)=='CFrame','Expected CFrame');self.CFrame=parentFrame(self):ToObjectSpace(value) end,
        WorldPosition=function(self,value) self.Position=parentFrame(self):PointToObjectSpace(finite(value)) end,
        WorldAxis=function(self,value) self.Axis=parentFrame(self):VectorToObjectSpace(finite(value)) end,
        WorldSecondaryAxis=function(self,value) self.SecondaryAxis=parentFrame(self):VectorToObjectSpace(finite(value)) end,
        WorldOrientation=function(self,value)
            finite(value);self.WorldCFrame=CF.fromOrientation(math.rad(value.X),math.rad(value.Y),math.rad(value.Z))+self.WorldPosition
        end,
    }
    S.Bone={Transform=function(self,value)
        assert(typeof(value)=='CFrame','Expected CFrame')
        finite(value.Position);finite(value.RightVector);finite(value.UpVector)
        value=rotatedSecondary(rotatedAxis(CF.identity,value.RightVector),value.UpVector).Rotation+value.Position
        local d=R.instances[self]
        if d.props.Transform~=value then
            d.props.Transform=value
            R.changed(self,'Transform');R.changed(self,'TransformedCFrame');R.changed(self,'TransformedWorldCFrame')
        end
    end}
    M.Attachment={
        GetAxis=function(self) return self.Axis end,GetSecondaryAxis=function(self) return self.SecondaryAxis end,
        SetAxis=function(self,value) self.Axis=value end,SetSecondaryAxis=function(self,value) self.SecondaryAxis=value end,
        GetConstraints=function(self)
            local result={}
            for object,d in R.instances do
                if not d.locked and object:IsA('Constraint') and (d.props.Attachment0==self or d.props.Attachment1==self) then table.insert(result,object) end
            end
            return result
        end,
    }
    S.Constraint=S.Constraint or {}
    for _,key in {'Attachment0','Attachment1'} do
        S.Constraint[key]=function(object,value)
            assert(value==nil or R.instances[value] and value:IsA('Attachment'),'Expected Attachment or nil')
            local d=R.instances[object]
            if d.props[key]~=value then d.props[key]=value;R.changed(object,key) end
        end
    end
    R.noncreatable.Constraint=true
    local initialize=R.initializeProperties
    function R.initializeProperties(object,d)
        initialize(object,d)
        if R.isClass(d.class,'Attachment') then
            property(d,'CFrame','CFrame',CF.identity);property(d,'Visible','boolean',false)
            for _,key in {'Position','Orientation','Rotation','Axis','SecondaryAxis','WorldPosition','WorldOrientation','WorldAxis','WorldSecondaryAxis'} do
                property(d,key,'Vector3',V3.zero)
            end
            property(d,'WorldCFrame','CFrame',CF.identity)
        end
        if R.isClass(d.class,'Bone') then property(d,'Transform','CFrame',CF.identity) end
        if R.isClass(d.class,'Constraint') then
            property(d,'Attachment0','Instance?',nil);property(d,'Attachment1','Instance?',nil)
            property(d,'Enabled','boolean',true);property(d,'Visible','boolean',false)
        end
    end
end
