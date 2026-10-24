return function(R)
    local V3,CF,C3=R.datatypes.Vector3,R.datatypes.CFrame,R.datatypes.Color3
    local services={}
    for _,name in {"Workspace","Players","RunService","ReplicatedStorage","ReplicatedFirst","ServerStorage","ServerScriptService",
        "StarterPlayer","StarterGui","StarterPack","Lighting","SoundService","Teams","HttpService","CollectionService",
        "TweenService","DataStoreService","Debris","UserInputService","ContextActionService","GuiService","TextService",
        "MarketplaceService","TeleportService","PhysicsService","PathfindingService","ContentProvider","TestService",
        "LocalizationService","Chat","TextChatService","InsertService","BadgeService","GroupService","MessagingService",
        "MemoryStoreService","VRService","Stats","LogService","AssetService","PolicyService","MaterialService","EncodingService"} do services[name]=true end
    R.serviceClasses=services
    R.models=setmetatable({}, {__mode='k'})
    R.noncreatable={Instance=true,PVInstance=true,BasePart=true,FormFactorPart=true,LuaSourceContainer=true,BaseScript=true,
        ServiceProvider=true,ServiceInstance=true,WorldRoot=true,DataModel=true,ValueBase=true}
    for name in services do R.noncreatable[name]=true;R.knownClasses[name]=true end
    R.classes.ServiceProvider=R.classes.ServiceProvider or "Instance"
    R.classes.ServiceInstance=R.classes.ServiceInstance or "Instance"
    for _,name in {"BoolValue","NumberValue","IntValue","StringValue","ObjectValue","Vector3Value","CFrameValue","Color3Value","BrickColorValue","RayValue","IntConstrainedValue","DoubleConstrainedValue"} do
        R.classes[name]=R.classes[name] or "ValueBase"
    end
    local function property(d,key,kind,value) d.propertyTypes[key]=kind;d.props[key]=value end
    function R.initializeProperties(object,d)
        if d.class=="HttpService" then property(d,"HttpEnabled","boolean",false) end
        if R.isClass(d.class,"BasePart") then
            for _,key in {"Anchored","Massless","Locked"} do property(d,key,"boolean",false) end
            for _,key in {"CanCollide","CanTouch","CanQuery","CastShadow"} do property(d,key,"boolean",true) end
            property(d,"CFrame","CFrame",CF.new());property(d,"PivotOffset","CFrame",CF.new())
            property(d,"Size","Vector3",V3.new(4,1.2,2));property(d,"Color","Color3",C3.fromRGB(163,162,165))
            property(d,"Transparency","number",0);property(d,"Reflectance","number",0)
            property(d,"Velocity","Vector3",V3.zero);property(d,"RotVelocity","Vector3",V3.zero)
            property(d,"AssemblyLinearVelocity","Vector3",V3.zero);property(d,"AssemblyAngularVelocity","Vector3",V3.zero)
            property(d,"RootPriority","number",0);property(d,"CollisionGroup","string","Default")
            property(d,"Material","Enum.Material",R.Enum.Material.Plastic)
            property(d,'MaterialVariant','string','');property(d,'CustomPhysicalProperties','PhysicalProperties?',nil)
            for _,face in {"Top","Bottom","Left","Right","Front","Back"} do property(d,face.."Surface","Enum.SurfaceType",R.Enum.SurfaceType.Smooth) end
        end
        if d.class=="Part" then property(d,"Shape","Enum.PartType",R.Enum.PartType.Block) end
        if d.class=='MaterialVariant' then
            property(d,'BaseMaterial','Enum.Material',R.Enum.Material.Plastic)
            property(d,'CustomPhysicalProperties','PhysicalProperties?',nil)
        end
        if R.isClass(d.class,"Model") then
            property(d,"PrimaryPart","Instance?",nil);property(d,"WorldPivot","CFrame",CF.new())
            R.models[object]=true
        end
        if d.class=="Workspace" then
            property(d,"Gravity","number",196.2);property(d,"CurrentCamera","Instance?",nil)
            property(d,"FallenPartsDestroyHeight","number",-500);property(d,"StreamingEnabled","boolean",false)
        end
        if d.class=="Camera" then
            property(d,"CFrame","CFrame",CF.new());property(d,"Focus","CFrame",CF.new());property(d,"FieldOfView","number",70)
            property(d,"CameraSubject","Instance?",nil)
        end
        if R.isClass(d.class,"BaseScript") then property(d,"Disabled","boolean",false);property(d,"Enabled","boolean",true);property(d,"RunContext","Enum.RunContext",R.Enum.RunContext.Legacy) end
        local kinds={BoolValue="boolean",NumberValue="number",IntValue="number",StringValue="string",ObjectValue="Instance?",
            Vector3Value="Vector3",CFrameValue="CFrame",Color3Value="Color3",BrickColorValue="BrickColor"}
        if kinds[d.class] then
            local defaults={boolean=false,number=0,string="",Vector3=V3.zero,CFrame=CF.new(),Color3=C3.new(),BrickColor=R.datatypes.BrickColor.Gray()}
            property(d,"Value",kinds[d.class],defaults[kinds[d.class]])
        end
        if d.class=="Player" then property(d,"UserId","number",1);property(d,"DisplayName","string","LocalPlayer");property(d,"Character","Instance?",nil) end
        if d.class=="Humanoid" then
            property(d,"Health","number",100);property(d,"MaxHealth","number",100);property(d,"WalkSpeed","number",16)
            property(d,"JumpPower","number",50);property(d,"JumpHeight","number",7.2);property(d,"UseJumpPower","boolean",true)
        end
    end
    local M,G,S,E=R.classMethods,R.classGetters,R.classSetters,R.classEvents
    M.ServiceProvider={}
    function M.ServiceProvider:GetService(name)
        assert(services[name],"'"..tostring(name).."' is not a valid Service name")
        if not R.services[name] then R.services[name]=R.new(name,self,true) end
        return R.services[name]
    end
    M.ServiceProvider.service=M.ServiceProvider.GetService
    function M.ServiceProvider:FindService(name) return R.services[name] end
    R.services={}
    R.game=R.new("DataModel",nil,true);R.game.Name="Game"
    R.workspace=R.game:GetService("Workspace")
    for _,name in {"Players","RunService","ReplicatedStorage","ServerStorage","ServerScriptService","StarterPlayer","StarterGui","Lighting","CollectionService"} do R.game:GetService(name) end
    M.DataModel={IsLoaded=function() return true end,BindToClose=function(_,fn) table.insert(R.closeCallbacks,fn) end}
    R.closeCallbacks={}
    G.DataModel={PlaceId=function() return R.config.placeId or 0 end,GameId=function() return R.config.gameId or 0 end,
        JobId=function() return "standalone-local" end,CreatorId=function() return R.config.creatorId or 0 end}
    local run=R.game:GetService("RunService")
    M.RunService={IsServer=function() return R.current().side=="server" end,IsClient=function() return R.current().side=="client" end,
        IsStudio=function() return false end,IsRunning=function() return true end,IsEdit=function() return false end}
    E.RunService={Heartbeat=true,Stepped=true,PreSimulation=true,PostSimulation=true,PreRender=true,RenderStepped=true}
    function R.step(dt)
        for model in R.models do
            local primary=R.instances[model].props.PrimaryPart
            if primary and not primary:IsDescendantOf(model) then model.PrimaryPart=nil end
        end
        R.fire(run,"PreSimulation",dt);R.fire(run,"Stepped",R.now,dt)
        R.fire(run,"PostSimulation",dt);R.fire(run,"Heartbeat",dt)
        if R.config.side=="client" then R.fire(run,"PreRender",dt);R.fire(run,"RenderStepped",dt) end
    end
    G.BasePart={Position=function(self) return self.CFrame.Position end,
        Mass=function(self) return self:GetMass() end,
        AssemblyMass=function(self) return if self.Anchored then math.huge else self:GetMass() end,
        CenterOfMass=function(self)
            local center=R.physicalCatalog.unit_center[self.ClassName=='WedgePart' and 'Wedge' or self.ClassName=='CornerWedgePart' and 'CornerWedge' or '']
            if center then
                local size=self.Size
                return V3.new(R.float32(center[1]*R.float32(math.max(.05,size.X))),R.float32(center[2]*R.float32(math.max(.05,size.Y))),R.float32(center[3]*R.float32(math.max(.05,size.Z))))
            end
            assert(self.ClassName=='Part','CenterOfMass geometry is not implemented for '..self.ClassName)
            return V3.zero
        end,
        AssemblyCenterOfMass=function(self) return self.CFrame:PointToWorldSpace(self.CenterOfMass) end,
        AssemblyRootPart=function(self) return self end,BrickColor=function(self) return R.datatypes.BrickColor.new(self.Color) end}
    S.BasePart={Position=function(self,v) assert(typeof(v)=="Vector3","Position requires Vector3");self.CFrame=self.CFrame.Rotation+v;R.changed(self,"Position") end,
        Color=function(self,v)
            assert(typeof(v)=="Color3","Color requires Color3")
            local d=R.instances[self]
            if d.props.Color~=v then
                local observe=d.signals.Changed or d.signals["property:BrickColor"]
                local before=if observe then self.BrickColor else nil
                d.props.Color=v;R.changed(self,"Color")
                if observe and self.BrickColor~=before then R.changed(self,"BrickColor") end
            end
        end,
        BrickColor=function(self,v) assert(typeof(v)=="BrickColor","BrickColor requires BrickColor");self.Color=v.Color end}
    M.BasePart={
        GetPivot=function(self) return self.CFrame*self.PivotOffset end,
        PivotTo=function(self,cf) self.CFrame=cf*self.PivotOffset:Inverse() end,
        GetMass=function(self) return R.float32(R.partVolume(self)*self.CurrentPhysicalProperties.Density) end,
    }
    M.BasePart.getMass=M.BasePart.GetMass
    local materialService=R.game:GetService('MaterialService')
    local overrides={}
    local function material(value)
        assert(typeof(value)=='EnumItem' and value.EnumType==R.Enum.Material,'Expected Enum.Material')
        return value
    end
    M.MaterialService={}
    function M.MaterialService:GetBaseMaterialOverride(value) return overrides[material(value)] or '' end
    function M.MaterialService:SetBaseMaterialOverride(value,name)
        material(value);assert(type(name)=='string','Material variant name must be a string');overrides[value]=name
    end
    function M.MaterialService:GetMaterialVariant(value,name)
        material(value);assert(type(name)=='string','Material variant name must be a string')
        if name=='' then return nil end
        for _,variant in self:GetDescendants() do
            if variant:IsA('MaterialVariant') and variant.Name==name and variant.BaseMaterial==value then return variant end
        end
        return nil
    end
    G.BasePart.CurrentPhysicalProperties=function(self)
        if self.CustomPhysicalProperties then return self.CustomPhysicalProperties end
        local variant=materialService:GetMaterialVariant(self.Material,self.MaterialVariant)
        if variant and variant.CustomPhysicalProperties then return variant.CustomPhysicalProperties end
        local base=materialService:GetMaterialVariant(self.Material,materialService:GetBaseMaterialOverride(self.Material))
        if base and base.CustomPhysicalProperties then return base.CustomPhysicalProperties end
        return R.datatypes.PhysicalProperties.new(self.Material)
    end
    E.BasePart={Touched=true,TouchEnded=true}
    M.Model={}
    local function modelBounds(self,rotation)
        local inverse=rotation:Inverse()
        local minimum,maximum=nil,nil
        for _,part in self:GetDescendants() do
            if not part:IsA('BasePart') then continue end
            local half=part.Size*.5
            for _,x in {-1,1} do for _,y in {-1,1} do for _,z in {-1,1} do
                local corner=inverse:PointToWorldSpace(part.CFrame:PointToWorldSpace(V3.new(x*half.X,y*half.Y,z*half.Z)))
                if minimum then
                    minimum=V3.new(math.min(minimum.X,corner.X),math.min(minimum.Y,corner.Y),math.min(minimum.Z,corner.Z))
                    maximum=V3.new(math.max(maximum.X,corner.X),math.max(maximum.Y,corner.Y),math.max(maximum.Z,corner.Z))
                else minimum,maximum=corner,corner end
            end end end
        end
        if not minimum then return nil,V3.zero end
        return rotation+rotation:PointToWorldSpace((minimum+maximum)*.5),maximum-minimum
    end
    G.Model={WorldPivot=function(self)
        local props=R.instances[self].props
        if props._modelPivotInitialized then return props.WorldPivot end
        local center=modelBounds(self,CF.new());return center or CF.new()
    end}
    S.Model={WorldPivot=function(self,value)
        assert(typeof(value)=='CFrame','WorldPivot requires CFrame')
        local props=R.instances[self].props;props._modelPivotInitialized=true
        if props.WorldPivot~=value then props.WorldPivot=value;R.changed(self,'WorldPivot') end
    end,PrimaryPart=function(self,value)
        assert(value==nil or R.instances[value] and value:IsA('BasePart'),'PrimaryPart requires a BasePart')
        local props=R.instances[self].props
        if props.PrimaryPart~=value then props.PrimaryPart=value;R.changed(self,'PrimaryPart') end
    end}
    function M.Model:GetPivot() return if self.PrimaryPart then self.PrimaryPart:GetPivot() else self.WorldPivot end
    function M.Model:GetBoundingBox()
        local rotation=if self.PrimaryPart then self.PrimaryPart.CFrame.Rotation else CF.new()
        local center,size=modelBounds(self,rotation)
        return center or self:GetPivot(),size
    end
    function M.Model:GetExtentsSize() local _,size=self:GetBoundingBox();return size end
    function M.Model:PivotTo(cf)
        local delta=cf*self:GetPivot():Inverse()
        for _,item in self:GetDescendants() do if item:IsA("BasePart") then item.CFrame=delta*item.CFrame end end
        self.WorldPivot=cf
    end
    function M.Model:MoveTo(position) self:PivotTo(self:GetPivot().Rotation+position) end
    local players=R.game:GetService("Players")
    R.player=R.new("Player",players,true);R.player.Name=R.config.playerName or "LocalPlayer"
    R.new("PlayerGui",R.player,true);R.new("PlayerScripts",R.player,true)
    G.Players={LocalPlayer=function() return if R.current().side=="client" then R.player else nil end}
    M.Players={GetPlayers=function() return {R.player} end,
        GetPlayerByUserId=function(_,id) return if id==R.player.UserId then R.player else nil end,
        GetPlayerFromCharacter=function(_,model) return if R.player.Character==model then R.player else nil end}
    E.Players={PlayerAdded=true,PlayerRemoving=true};E.Player={CharacterAdded=true,CharacterRemoving=true}
    M.BindableEvent={Fire=function(self,...) R.fire(self,"Event",...) end};E.BindableEvent={Event=true}
    M.RemoteEvent={
        FireServer=function(self,...) assert(R.current().side=="client","FireServer requires client context");R.fire(self,"OnServerEvent",R.player,...) end,
        FireClient=function(self,player,...) assert(R.current().side=="server","FireClient requires server context");assert(player==R.player,"Unknown player");R.fire(self,"OnClientEvent",...) end,
        FireAllClients=function(self,...) assert(R.current().side=="server","FireAllClients requires server context");R.fire(self,"OnClientEvent",...) end,
    }
    E.RemoteEvent={OnServerEvent=true,OnClientEvent=true}
    local callbacks=setmetatable({}, {__mode="k"})
    local function slot(class,key)
        G[class]=G[class] or {};S[class]=S[class] or {}
        G[class][key]=function(self) local c=callbacks[self] and callbacks[self][key];return if c then c.fn else nil end
        S[class][key]=function(self,fn)
            assert(fn==nil or type(fn)=="function","Expected callback function")
            callbacks[self]=callbacks[self] or {}
            callbacks[self][key]=if fn then {fn=fn,context=R.current()} else nil
        end
    end
    slot("BindableFunction","OnInvoke");slot("RemoteFunction","OnServerInvoke");slot("RemoteFunction","OnClientInvoke")
    local function invoke(self,key,...)
        local c=callbacks[self] and callbacks[self][key];assert(c,key.." callback is not assigned")
        return R.withContext(c.context,c.fn,...)
    end
    M.BindableFunction={Invoke=function(self,...) return invoke(self,"OnInvoke",...) end}
    M.RemoteFunction={
        InvokeServer=function(self,...) assert(R.current().side=="client","InvokeServer requires client context");return invoke(self,"OnServerInvoke",R.player,...) end,
        InvokeClient=function(self,player,...) assert(R.current().side=="server","InvokeClient requires server context");assert(player==R.player,"Unknown player");return invoke(self,"OnClientInvoke",...) end,
    }
    M.Debris={AddItem=function(_,object,lifetime) R.task.delay(lifetime or 10,function() object:Destroy() end) end}
    local tagSignals={added={},removed={}}
    function R.tagChanged(object,tag,added)
        if object:IsDescendantOf(R.game) then
            local signal=(if added then tagSignals.added else tagSignals.removed)[tag]
            if signal then R.fireSignal(signal,object) end
        end
    end
    function R.tagAncestryChanged(nodes,wasInside,isInside)
        if wasInside==isInside then return end
        local registry=if isInside then tagSignals.added else tagSignals.removed
        for _,object in nodes do
            for tag in R.instances[object].tags do
                local signal=registry[tag]
                if signal then R.fireSignal(signal,object) end
            end
        end
    end
    M.CollectionService={
        AddTag=function(_,object,tag) R.instanceMethods.AddTag(object,tag) end,RemoveTag=function(_,object,tag) R.instanceMethods.RemoveTag(object,tag) end,
        HasTag=function(_,object,tag) return R.instanceMethods.HasTag(object,tag) end,GetTags=function(_,object) return R.instanceMethods.GetTags(object) end,
        GetTagged=function(_,tag) local result={};for _,object in R.game:GetDescendants() do if R.instanceMethods.HasTag(object,tag) then table.insert(result,object) end end;return result end,
        GetAllTags=function() local tags={};for _,object in R.game:GetDescendants() do for tag in R.instances[object].tags do tags[tag]=true end end;local result={};for tag in tags do table.insert(result,tag) end;return result end,
        GetInstanceAddedSignal=function(_,tag) if not tagSignals.added[tag] then tagSignals.added[tag]=R.newSignal() end;return tagSignals.added[tag] end,
        GetInstanceRemovedSignal=function(_,tag) if not tagSignals.removed[tag] then tagSignals.removed[tag]=R.newSignal() end;return tagSignals.removed[tag] end,
    }
end
