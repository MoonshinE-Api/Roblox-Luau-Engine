-- The tree operations are reconstructed semantically; this is not an RBX C++ ABI
-- object layout. Class relationships are supplied from the inspected 0.735 dump.
return function(R)
    local data=setmetatable({}, {__mode="k"})
    R.instances=data
    local methods={}
    R.instanceMethods=methods
    local function state(object) local d=data[object];assert(d,"Expected Instance");return d end
    local function isa(class,target)
        if target=="Instance" then return true end
        local visited={}
        while class and not visited[class] do
            if class==target then return true end
            visited[class]=true;class=R.classes[class]
        end
        return false
    end
    R.isClass=isa
    function R.signal(object,name)
        local d=state(object)
        if not d.signals[name] then d.signals[name]=R.newSignal() end
        return d.signals[name]
    end
    function R.fire(object,name,...)
        local signal=state(object).signals[name]
        if signal then R.fireSignal(signal,...) end
    end
    function R.changed(object,key)
        local d=state(object)
        if isa(d.class,"ValueBase") then
            if key=="Value" then R.fire(object,"Changed",d.props.Value) end
        else R.fire(object,"Changed",key) end
        R.fire(object,"property:"..key)
    end
    function methods:IsA(class) return isa(state(self).class,class) end
    methods.isA=methods.IsA
    function methods:GetChildren() return table.clone(state(self).children) end
    methods.getChildren=methods.GetChildren;methods.children=methods.GetChildren
    function methods:GetDescendants()
        local result={}
        local function visit(node) for _,child in state(node).children do table.insert(result,child);visit(child) end end
        visit(self);return result
    end
    function methods:IsDescendantOf(ancestor)
        assert(data[ancestor],"Expected Instance")
        local parent=state(self).parent
        while parent do if parent==ancestor then return true end;parent=state(parent).parent end
        return false
    end
    function methods:IsAncestorOf(descendant) return descendant:IsDescendantOf(self) end
    function methods:FindFirstChild(name,recursive)
        for _,child in state(self).children do if state(child).name==name then return child end end
        if recursive then for _,child in state(self).children do local match=child:FindFirstChild(name,true);if match then return match end end end
    end
    methods.findFirstChild=methods.FindFirstChild
    function methods:FindFirstChildOfClass(class)
        for _,child in state(self).children do if state(child).class==class then return child end end
    end
    function methods:FindFirstChildWhichIsA(class,recursive)
        for _,child in state(self).children do if child:IsA(class) then return child end end
        if recursive then for _,child in state(self).children do local value=child:FindFirstChildWhichIsA(class,true);if value then return value end end end
    end
    function methods:FindFirstAncestor(name)
        local p=state(self).parent
        while p do if state(p).name==name then return p end;p=state(p).parent end
    end
    function methods:FindFirstAncestorOfClass(class)
        local p=state(self).parent
        while p do if state(p).class==class then return p end;p=state(p).parent end
    end
    function methods:FindFirstAncestorWhichIsA(class)
        local p=state(self).parent
        while p do if p:IsA(class) then return p end;p=state(p).parent end
    end
    function methods:GetFullName()
        local names={state(self).name};local parent=state(self).parent
        while parent and parent~=R.game do table.insert(names,1,state(parent).name);parent=state(parent).parent end
        return table.concat(names,".")
    end
    function methods:GetPropertyChangedSignal(key) return R.signal(self,"property:"..key) end
    function methods:GetAttributeChangedSignal(key) return R.signal(self,"attribute:"..key) end
    function methods:GetAttribute(key) return R.copyValue(state(self).attributes[key]) end
    function methods:GetAttributes()
        local result={};for key,value in state(self).attributes do result[key]=R.copyValue(value) end;return result
    end
    local attributeTypes={string=true,number=true,boolean=true,UDim=true,UDim2=true,BrickColor=true,Color3=true,
        Vector2=true,Vector3=true,CFrame=true,NumberSequence=true,ColorSequence=true,NumberRange=true,Rect=true,Font=true}
    function methods:SetAttribute(key,value)
        assert(type(key)=="string" and #key>0 and #key<=100 and string.match(key,"^[A-Za-z0-9_./%-]+$") and string.sub(key,1,3)~="RBX","Invalid attribute name")
        local kind=typeof(value)
        assert(value==nil or attributeTypes[kind] or (kind=="TweenInfo" and R.config.serializeTweenInfoAttributes),"Unsupported attribute type "..kind)
        local d=state(self)
        if d.attributes[key]==value then return end
        d.attributes[key]=R.copyValue(value);R.fire(self,"AttributeChanged",key);R.fire(self,"attribute:"..key)
    end
    function methods:AddTag(tag)
        local d=state(self);if d.tags[tag] then return end;d.tags[tag]=true
        if R.tagChanged then R.tagChanged(self,tag,true) end
    end
    function methods:RemoveTag(tag)
        local d=state(self);if not d.tags[tag] then return end;d.tags[tag]=nil
        if R.tagChanged then R.tagChanged(self,tag,false) end
    end
    function methods:HasTag(tag) return state(self).tags[tag]==true end
    function methods:GetTags() local result={};for tag in state(self).tags do table.insert(result,tag) end;return result end
    function R.parent(object,parent)
        local d=state(object)
        assert(parent==nil or data[parent],"Parent must be an Instance or nil")
        if d.parent==parent then return end
        assert(not d.locked,"The Parent property is locked")
        assert(parent~=object and (parent==nil or not parent:IsDescendantOf(object)),"Attempt to set Parent would result in circular reference")
        assert(not d.parenting,"Recursive Parent assignment")
        if R.validateParent then R.validateParent(object,parent) end
        d.parenting=true
        local old=d.parent
        local wasInGame=R.game and object:IsDescendantOf(R.game) or false
        local nodes={object};for _,child in object:GetDescendants() do table.insert(nodes,child) end
        local ancestor=old
        while ancestor do for _,node in nodes do R.fire(ancestor,"DescendantRemoving",node) end;ancestor=state(ancestor).parent end
        if R.beforeParentChanged then R.beforeParentChanged(object,old,parent) end
        if old then local children=state(old).children;table.remove(children,assert(table.find(children,object))) end
        d.parent=parent
        if parent then table.insert(state(parent).children,object) end
        if old then R.fire(old,"ChildRemoved",object) end
        if parent then
            R.fire(parent,"ChildAdded",object)
            ancestor=parent
            while ancestor do for _,node in nodes do R.fire(ancestor,"DescendantAdded",node) end;ancestor=state(ancestor).parent end
        end
        R.changed(object,"Parent")
        for _,node in nodes do R.fire(node,"AncestryChanged",node,state(node).parent) end
        d.parenting=false
        if R.parentChanged then R.parentChanged(object,old,parent) end
        if R.tagAncestryChanged then R.tagAncestryChanged(nodes,wasInGame,object:IsDescendantOf(R.game)) end
    end
    function methods:WaitForChild(name,timeout)
        local found=self:FindFirstChild(name);if found then return found end
        local deadline=if timeout then R.now+timeout else math.huge
        local signal=R.signal(self,"ChildAdded")
        while R.now<deadline do
            coroutine.yield({kind="signal",signal=R.signals[signal],timeout=if timeout then deadline-R.now else nil})
            found=self:FindFirstChild(name);if found then return found end
        end
    end
    function methods:ClearAllChildren() for _,child in self:GetChildren() do child:Destroy() end end
    function methods:Destroy()
        local d=state(self);if d.locked then return end
        R.fire(self,"Destroying")
        R.parent(self,nil);d.locked=true
        self:ClearAllChildren()
        for _,signal in d.signals do R.disconnectSignal(signal) end
    end
    methods.destroy=methods.Destroy;methods.Remove=methods.Destroy;methods.remove=methods.Destroy
    function methods:Clone()
        if not state(self).archivable then return nil end
        local copies={}
        local function copy(node)
            local old=state(node)
            if not old.archivable then return end
            local value=R.new(old.class,nil,true);copies[node]=value
            local new=state(value)
            new.name,new.archivable=old.name,old.archivable
            new.props,new.attributes,new.tags=table.clone(old.props),table.clone(old.attributes),table.clone(old.tags)
            for key,value in new.props do new.props[key]=R.copyValue(value) end
            for key,value in new.attributes do new.attributes[key]=R.copyValue(value) end
            for _,child in old.children do local cloned=copy(child);if cloned then R.parent(cloned,value) end end
            return value
        end
        local root=copy(self)
        for _,cloned in copies do local d=state(cloned);for key,value in d.props do if copies[value] then d.props[key]=copies[value] end end end
        return root
    end
    local eventNames={Changed=true,ChildAdded=true,ChildRemoved=true,DescendantAdded=true,DescendantRemoving=true,AncestryChanged=true,Destroying=true,AttributeChanged=true}
    R.classMethods,R.classGetters,R.classSetters={},{},{}
    R.classEvents={}
    local function lookup(registry,class,key)
        local visited={}
        while class and not visited[class] do
            visited[class]=true
            local members=registry[class]
            if members and members[key]~=nil then return members[key] end
            class=R.classes[class]
        end
    end
    local function index(object,key)
        local d=state(object)
        if key=="Name" or key=="name" then return d.name elseif key=="Parent" or key=="parent" then return d.parent
        elseif key=="ClassName" or key=="className" then return d.class elseif key=="Archivable" then return d.archivable end
        local method=lookup(R.classMethods,d.class,key) or methods[key]
        if method then return method end
        local getter=lookup(R.classGetters,d.class,key)
        if getter then return getter(object) end
        if d.propertyTypes[key] then return R.copyValue(d.props[key]) end
        if eventNames[key] or lookup(R.classEvents,d.class,key) then return R.signal(object,key) end
        local child=object:FindFirstChild(key);if child then return child end
        error(key.." is not a valid member of "..d.class..' "'..d.name..'"',2)
    end
    local function assign(object,key,value)
        local d=state(object)
        if key=="Parent" or key=="parent" then return R.parent(object,value) end
        if key=="Name" or key=="name" then assert(type(value)=="string","Name must be a string");if d.name~=value then d.name=value;R.changed(object,"Name") end;return end
        if key=="Archivable" then assert(type(value)=="boolean","Archivable must be a boolean");if d.archivable~=value then d.archivable=value;R.changed(object,key) end;return end
        local setter=lookup(R.classSetters,d.class,key)
        if setter then return setter(object,value) end
        if d.propertyTypes[key] then
            local kind=d.propertyTypes[key]
            local optional=string.match(kind,'^(.+)%?$')
            local enumType=string.match(kind,"^Enum%.(.+)$")
            assert((kind=="Instance?" and (value==nil or data[value])) or (optional and optional~='Instance' and (value==nil or typeof(value)==optional)) or (enumType and typeof(value)=="EnumItem" and value.EnumType==R.Enum[enumType]) or typeof(value)==kind,"Invalid value for "..key..", expected "..kind)
            if d.props[key]~=value then d.props[key]=value;R.changed(object,key) end
            return
        end
        if key=="ClassName" or lookup(R.classGetters,d.class,key) then error(key.." is read only",2) end
        error(key.." is not a valid member of "..d.class,2)
    end
    function R.new(class,parent,internal)
        assert(type(class)=="string" and R.knownClasses[class],"Unable to create an Instance of type "..tostring(class))
        if not internal then assert(not R.noncreatable[class],"Unable to create an Instance of type "..class) end
        local object=R.proxy()
        local d={class=class,name=class,archivable=true,children={},props={},attributes={},tags={},signals={},propertyTypes={}}
        data[object]=d
        local mt=getmetatable(object)
        mt.__type,mt.__metatable="Instance","Instance"
        mt.__index,mt.__newindex=index,assign
        mt.__tostring=function(self) return state(self).name end
        if R.initializeProperties then R.initializeProperties(object,d) end
        if parent then R.parent(object,parent) end
        return object
    end
    R.Instance=table.freeze({new=function(class,parent) return R.new(class,parent,false) end})
end
