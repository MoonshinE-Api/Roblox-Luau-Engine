-- Perspective projection for a fixed headless viewport. No VR pose, camera
-- controller, occlusion, renderer, device safe-area discovery, or native f32 ABI.
return function(R)
    local V2,V3=R.datatypes.Vector2,R.datatypes.Vector3
    local G,S,M=R.classGetters,R.classSetters,R.classMethods
    local dimensions=V2.new(table.unpack(R.config.viewportSize or {1280,720}))
    local near=R.config.cameraNearPlaneZ or -0.5
    local function number(value)
        assert(type(value)=='number' and value==value and math.abs(value)<math.huge,'Expected finite number')
        return value
    end
    local initialize=R.initializeProperties
    function R.initializeProperties(object,d)
        initialize(object,d)
        if d.class=='Camera' then
            local function property(key,kind,value) d.propertyTypes[key]=kind;d.props[key]=value end
            property('CameraType','Enum.CameraType',R.Enum.CameraType.Fixed)
            property('FieldOfViewMode','Enum.FieldOfViewMode',R.Enum.FieldOfViewMode.Vertical)
            property('DiagonalFieldOfView','number',0);property('MaxAxisFieldOfView','number',0)
            property('HeadLocked','boolean',true);property('HeadScale','number',1)
            property('VRTiltAndRollEnabled','boolean',false)
            -- Internal scalar state is copied with the ordinary property map.
            d.props.__cameraFovReference=d.props.FieldOfView
        end
    end
    local function viewport(self) return if R.workspace.CurrentCamera==self then dimensions else V2.one end
    local function factor(self,mode)
        local size=viewport(self);local aspect=size.X/size.Y
        if mode==R.Enum.FieldOfViewMode.Diagonal then return math.sqrt(1+aspect*aspect)
        elseif mode==R.Enum.FieldOfViewMode.MaxAxis then return math.max(1,aspect) end
        return 1
    end
    local function angle(self,mode)
        local d=R.instances[self]
        if self.FieldOfViewMode==mode then return d.props.__cameraFovReference end
        return math.deg(2*math.atan(math.tan(math.rad(d.props.__cameraFovReference)/2)*factor(self,mode)/factor(self,self.FieldOfViewMode)))
    end
    G.Camera=G.Camera or {}
    G.Camera.ViewportSize=viewport
    G.Camera.NearPlaneZ=function() return near end
    G.Camera.FieldOfView=function(self) return angle(self,R.Enum.FieldOfViewMode.Vertical) end
    G.Camera.DiagonalFieldOfView=function(self) return angle(self,R.Enum.FieldOfViewMode.Diagonal) end
    G.Camera.MaxAxisFieldOfView=function(self) return angle(self,R.Enum.FieldOfViewMode.MaxAxis) end
    S.Camera=S.Camera or {}
    local function setAngle(self,value,mode)
        value=math.clamp(number(value),1,if mode==R.Enum.FieldOfViewMode.Vertical then 120 else 179)
        local d=R.instances[self]
        local old={self.FieldOfView,self.DiagonalFieldOfView,self.MaxAxisFieldOfView}
        d.props.__cameraFovReference=if self.FieldOfViewMode==mode then value else
            math.deg(2*math.atan(math.tan(math.rad(value)/2)*factor(self,self.FieldOfViewMode)/factor(self,mode)))
        for i,key in {'FieldOfView','DiagonalFieldOfView','MaxAxisFieldOfView'} do
            if self[key]~=old[i] then R.changed(self,key) end
        end
    end
    S.Camera.FieldOfView=function(self,v) setAngle(self,v,R.Enum.FieldOfViewMode.Vertical) end
    S.Camera.DiagonalFieldOfView=function(self,v) setAngle(self,v,R.Enum.FieldOfViewMode.Diagonal) end
    S.Camera.MaxAxisFieldOfView=function(self,v) setAngle(self,v,R.Enum.FieldOfViewMode.MaxAxis) end
    S.Camera.FieldOfViewMode=function(self,value)
        assert(typeof(value)=='EnumItem' and value.EnumType==R.Enum.FieldOfViewMode,'Expected Enum.FieldOfViewMode')
        local d=R.instances[self]
        if d.props.FieldOfViewMode==value then return end
        local vertical=self.FieldOfView;d.props.FieldOfViewMode=value
        d.props.__cameraFovReference=math.deg(2*math.atan(math.tan(math.rad(vertical)/2)*factor(self,value)))
        R.changed(self,'FieldOfViewMode')
    end
    S.Workspace=S.Workspace or {}
    S.Workspace.CurrentCamera=function(self,value)
        assert(value==nil or R.instances[value] and value:IsA('Camera'),'CurrentCamera requires Camera or nil')
        local d=R.instances[self];local old=d.props.CurrentCamera
        if old==value then return end
        d.props.CurrentCamera=value;R.changed(self,'CurrentCamera')
        for _,camera in {old,value} do
            if camera then
                R.changed(camera,'ViewportSize')
                if camera.FieldOfViewMode~=R.Enum.FieldOfViewMode.Vertical then R.changed(camera,'FieldOfView') end
            end
        end
    end
    M.Camera=M.Camera or {}
    local function vector(value)
        assert(typeof(value)=='Vector3','Expected Vector3')
        number(value.X);number(value.Y);number(value.Z);return value
    end
    function M.Camera:GetRenderCFrame() return self.CFrame end
    function M.Camera:WorldToViewportPoint(point)
        local localPoint=self.CFrame:PointToObjectSpace(vector(point));local depth=-localPoint.Z
        local size=viewport(self);local focal=size.Y/(2*math.tan(math.rad(self.FieldOfView)/2))
        local x=size.X/2+localPoint.X*focal/depth
        local y=size.Y/2-localPoint.Y*focal/depth
        return V3.new(x,y,depth),depth>0 and x>=0 and x<=size.X and y>=0 and y<=size.Y
    end
    function M.Camera:WorldToScreenPoint(point)
        local p,onScreen=self:WorldToViewportPoint(point)
        local inset=R.game:GetService('GuiService'):GetGuiInset()
        return p-V3.new(inset.X,inset.Y,0),onScreen
    end
    function M.Camera:ViewportPointToRay(x,y,depth)
        number(x);number(y);depth=number(depth or 0)
        local size=viewport(self);local focal=size.Y/(2*math.tan(math.rad(self.FieldOfView)/2))
        local localDirection=V3.new((x-size.X/2)/focal,-(y-size.Y/2)/focal,-1).Unit
        local direction=self.CFrame:VectorToWorldSpace(localDirection)
        -- The supplied worldRay routine offsets its origin to the near plane,
        -- then adds the requested distance along its normalized direction.
        local origin=self.CFrame.Position+direction*(depth-near/(-localDirection.Z))
        return R.datatypes.Ray.new(origin,direction)
    end
    function M.Camera:ScreenPointToRay(x,y,depth)
        local inset=R.game:GetService('GuiService'):GetGuiInset()
        return self:ViewportPointToRay(number(x)+inset.X,number(y)+inset.Y,depth)
    end
    if R.config.side=='client' or R.config.side=='both' then
        R.workspace.CurrentCamera=R.new('Camera',R.workspace,true)
    end
end
