-- Headless UI configuration and explicit UDim geometry. No text shaping,
-- rendering, automatic/list/grid layout, device input, or safe-area discovery.
return function(R)
    local V2,U2=R.datatypes.Vector2,R.datatypes.UDim2
    local M,G,S,E=R.classMethods,R.classGetters,R.classSetters,R.classEvents
    local catalog=R.uiCatalog.classes
    -- The supplied C++ metadata names the public LayerCollector base this way.
    -- Insert its public alias while retaining the native ancestor relationship.
    R.classes.GuiLayerCollector='LayerCollector'
    local enumValues={}
    local function enum(name,value)
        if not enumValues[name] then
            local items={};for _,item in R.Enum[name]:GetEnumItems() do items[item.Value]=item end
            enumValues[name]=items
        end
        return assert(enumValues[name][value],"Unknown UI enum value")
    end
    local function decode(record)
        local kind,v=record.kind,record.values
        if kind=='Instance?' then return nil
        elseif string.sub(kind,1,5)=='Enum.' then return enum(string.sub(kind,6),v)
        elseif kind=='boolean' or kind=='number' or kind=='string' then return v
        elseif kind=='UDim2' then return U2.new(v[1][1],v[1][2],v[2][1],v[2][2])
        elseif kind=='Rect' then return R.datatypes.Rect.new(V2.new(table.unpack(v[1])),V2.new(table.unpack(v[2])))
        elseif kind=='Font' then return R.datatypes.Font.new(v[1],R.Enum.FontWeight[v[2]],R.Enum.FontStyle[v[3]])
        elseif kind=='NumberSequence' or kind=='ColorSequence' then
            local points={}
            for _,point in v[1] do
                table.insert(points,if kind=='NumberSequence' then R.datatypes.NumberSequenceKeypoint.new(table.unpack(point))
                    else R.datatypes.ColorSequenceKeypoint.new(point[1],R.datatypes.Color3.new(table.unpack(point[2]))))
            end
            return R.datatypes[kind].new(points)
        end
        return R.datatypes[kind].new(table.unpack(v))
    end
    local function valid(value,record)
        local kind=record.kind
        if kind=='Instance?' then
            assert(value==nil or (R.instances[value] and value:IsA(record.target)),"Expected "..record.target.." or nil")
        elseif string.sub(kind,1,5)=='Enum.' then
            assert(typeof(value)=='EnumItem' and value.EnumType==R.Enum[string.sub(kind,6)],"Expected "..kind)
        else assert(typeof(value)==kind,"Expected "..kind) end
        if kind=='number' then assert(value==value and math.abs(value)<math.huge,"Expected finite number") end
        return value
    end
    local integers={LayoutOrder=true,ZIndex=true,DisplayOrder=true,SelectionOrder=true,BorderSizePixel=true,
        CursorPosition=true,SelectionStart=true,MaxVisibleGraphemes=true,MaxTextSize=true,MinTextSize=true}
    local function write(object,key,value)
        local d=R.instances[object];value=valid(value,assert(d.uiRules[key]))
        if type(value)=='number' then
            if string.find(key,'Transparency',1,true) then value=math.clamp(value,0,1) end
            if integers[key] then value=math.modf(value) end
            if key=='TextSize' then value=math.clamp(value,1,100) end
            if d.class=='UIScale' and key=='Scale' then value=math.max(0,value) end
        end
        if d.props[key]~=value then d.props[key]=R.copyValue(value);R.changed(object,key) end
    end
    for class,fields in catalog do
        S[class]=S[class] or {}
        for key in fields do S[class][key]=function(object,value) write(object,key,value) end end
    end
    local initialize=R.initializeProperties
    function R.initializeProperties(object,d)
        initialize(object,d)
        local chain={};local class=d.class
        while class do table.insert(chain,1,class);class=R.classes[class] end
        for _,ancestor in chain do
            for key,record in catalog[ancestor] or {} do
                d.uiRules=d.uiRules or {};d.uiRules[key]=record
                d.propertyTypes[key]=record.kind;d.props[key]=decode(record)
            end
        end
        -- Concrete classes can override the representative base-class defaults.
        for key,record in (R.uiCatalog.default_overrides or {})[d.class] or {} do d.props[key]=decode(record) end
    end
    for object,d in R.instances do
        if R.isClass(d.class,'GuiBase2d') then R.initializeProperties(object,d) end
    end
    for _,name in {'GuiBase2d','GuiObject','GuiButton','GuiLabel','LayerCollector'} do R.noncreatable[name]=true end
    local viewport=V2.new(table.unpack(R.config.viewportSize or {1280,720}))
    local inset=V2.new(table.unpack(R.config.guiInset or {0,0}))
    assert(viewport.X>0 and viewport.Y>0,'Viewport must have positive dimensions')
    local function modifier(object,class)
        for _,child in object:GetChildren() do if child:IsA(class) then return child end end
    end
    local rect
    rect=function(object)
        if object:IsA('ScreenGui') then
            local offset=if object.IgnoreGuiInset or object.ScreenInsets==R.Enum.ScreenInsets.None then V2.zero else inset
            return offset,viewport-offset,1,0
        end
        if not object:IsA('GuiObject') then return V2.zero,V2.zero,1,0 end
        local parent=object.Parent
        if not parent or (not parent:IsA('GuiObject') and not parent:IsA('ScreenGui')) then return V2.zero,V2.zero,1,object.Rotation end
        assert(object.AutomaticSize==R.Enum.AutomaticSize.None,'AutomaticSize layout is not implemented')
        for _,child in parent:GetChildren() do
            assert(not child:IsA('UIGridStyleLayout'),'List/grid layout is not implemented')
        end
        local position,parentSize,parentScale,parentRotation=rect(parent)
        local padding=modifier(parent,'UIPadding')
        if padding then
            local function pixels(value,axis) return value.Scale*axis+value.Offset*parentScale end
            local left,right=pixels(padding.PaddingLeft,parentSize.X),pixels(padding.PaddingRight,parentSize.X)
            local top,bottom=pixels(padding.PaddingTop,parentSize.Y),pixels(padding.PaddingBottom,parentSize.Y)
            position+=V2.new(left,top)
            parentSize=V2.new(math.max(0,parentSize.X-left-right),math.max(0,parentSize.Y-top-bottom))
        end
        local scale=parentScale
        for _,child in object:GetChildren() do if child:IsA('UIScale') then scale*=child.Scale end end
        local basis=parentSize
        if object.SizeConstraint==R.Enum.SizeConstraint.RelativeXX then basis=V2.new(parentSize.X,parentSize.X)
        elseif object.SizeConstraint==R.Enum.SizeConstraint.RelativeYY then basis=V2.new(parentSize.Y,parentSize.Y) end
        local size=V2.new(math.max(0,object.Size.X.Scale*basis.X+object.Size.X.Offset*parentScale),
            math.max(0,object.Size.Y.Scale*basis.Y+object.Size.Y.Offset*parentScale))
        size*=if parentScale==0 then 0 else scale/parentScale
        local constraint=modifier(object,'UISizeConstraint')
        if constraint then size=size:Max(constraint.MinSize*scale):Min(constraint.MaxSize*scale) end
        local aspect=modifier(object,'UIAspectRatioConstraint')
        if aspect then
            local maximum=size
            assert(aspect.AspectRatio>0,'AspectRatio must be positive')
            if aspect.DominantAxis==R.Enum.DominantAxis.Width then size=V2.new(size.X,size.X/aspect.AspectRatio)
            else size=V2.new(size.Y*aspect.AspectRatio,size.Y) end
            if aspect.AspectType==R.Enum.AspectType.FitWithinMaxSize then
                local factor=math.min(1,if size.X==0 then 1 else maximum.X/size.X,if size.Y==0 then 1 else maximum.Y/size.Y)
                size*=factor
            end
        end
        if parent:IsA('ScrollingFrame') then position-=parent.CanvasPosition*parentScale end
        local offset=V2.new(object.Position.X.Scale*parentSize.X+object.Position.X.Offset*parentScale,
            object.Position.Y.Scale*parentSize.Y+object.Position.Y.Offset*parentScale)
        return position+offset-object.AnchorPoint*size,size,scale,parentRotation+object.Rotation
    end
    G.GuiBase2d=G.GuiBase2d or {}
    G.GuiBase2d.AbsolutePosition=function(self) local p=rect(self);return p end
    G.GuiBase2d.AbsoluteSize=function(self) local _,s=rect(self);return s end
    G.GuiBase2d.AbsoluteRotation=function(self) local _,_,_,a=rect(self);return a end
    G.ScrollingFrame={AbsoluteCanvasSize=function(self)
        assert(self.AutomaticCanvasSize==R.Enum.AutomaticSize.None,'AutomaticCanvasSize layout is not implemented')
        local _,size,scale=rect(self)
        return V2.new(self.CanvasSize.X.Scale*size.X+self.CanvasSize.X.Offset*scale,
            self.CanvasSize.Y.Scale*size.Y+self.CanvasSize.Y.Offset*scale):Max(size)
    end,AbsoluteWindowSize=function(self) return self.AbsoluteSize end}
    local function visible(object)
        local node=object
        while node do
            if node:IsA('GuiObject') and not node.Visible then return false end
            if node:IsA('LayerCollector') then return node.Enabled end
            node=node.Parent
        end
        return false
    end
    local function inside(object,x,y)
        assert(object.AbsoluteRotation==0,'Rotated UI hit testing is not implemented')
        local p,s=rect(object);return x>=p.X and y>=p.Y and x<p.X+s.X and y<p.Y+s.Y
    end
    M.BasePlayerGui=M.BasePlayerGui or {}
    function M.BasePlayerGui:GetGuiObjectsAtPosition(x,y)
        assert(type(x)=='number' and type(y)=='number','Expected pixel coordinates')
        local result={}
        local descendants=self:GetDescendants()
        local orderByObject={};for i,object in descendants do orderByObject[object]=i end
        for _,object in descendants do
            if object:IsA('GuiObject') and visible(object) and inside(object,x,y) then
                local clipped=false;local parent=object.Parent
                while parent and parent~=self do
                    if parent:IsA('GuiObject') and parent.ClipsDescendants and not inside(parent,x,y) then clipped=true;break end
                    parent=parent.Parent
                end
                if not clipped then table.insert(result,object) end
            end
        end
        local paint={};local sequence=0
        local function paintChildren(parent)
            local children={}
            for _,child in parent:GetChildren() do if child:IsA('GuiObject') then table.insert(children,child) end end
            table.sort(children,function(a,b) return if a.ZIndex~=b.ZIndex then a.ZIndex<b.ZIndex else orderByObject[a]<orderByObject[b] end)
            for _,child in children do sequence+=1;paint[child]=sequence;paintChildren(child) end
        end
        for _,object in descendants do if object:IsA('ScreenGui') then paintChildren(object) end end
        local function order(object)
            local root=object:FindFirstAncestorWhichIsA('ScreenGui')
            return root,root and root.DisplayOrder or 0
        end
        table.sort(result,function(a,b)
            local ra,x=order(a);local rb,y=order(b)
            if x~=y then return x>y end
            if ra~=rb then return (orderByObject[ra] or 0)>(orderByObject[rb] or 0) end
            if ra and ra.ZIndexBehavior==R.Enum.ZIndexBehavior.Global and a.ZIndex~=b.ZIndex then return a.ZIndex>b.ZIndex end
            return (paint[a] or orderByObject[a])>(paint[b] or orderByObject[b])
        end)
        return result
    end
    M.GuiService=M.GuiService or {}
    function M.GuiService:GetGuiInset() return inset,V2.zero end
    M.UserInputService=M.UserInputService or {}
    local focused=nil
    local function focus()
        if focused and R.instances[focused].locked then focused=nil end
        return focused
    end
    function M.UserInputService:GetFocusedTextBox() return focus() end
    M.TextBox={}
    function M.TextBox:IsFocused() return focus()==self end
    function M.TextBox:ReleaseFocus(enterPressed)
        assert(enterPressed==nil or type(enterPressed)=='boolean','Expected boolean')
        if focus()~=self then return end
        focused=nil;self.CursorPosition=-1;self.SelectionStart=-1
        R.fire(self,'FocusLost',enterPressed or false,nil)
    end
    function M.TextBox:CaptureFocus()
        assert(not R.instances[self].locked,'Cannot focus a destroyed TextBox')
        if focus()==self then return end
        if focused then focused:ReleaseFocus(false) end
        focused=self
        if self.ClearTextOnFocus then self.Text='' end
        self.CursorPosition=(utf8.len(self.Text) or #self.Text)+1
        R.fire(self,'Focused')
    end
    E.GuiObject={InputBegan=true,InputChanged=true,InputEnded=true,MouseEnter=true,MouseLeave=true,MouseMoved=true,
        MouseWheelForward=true,MouseWheelBackward=true,SelectionGained=true,SelectionLost=true}
    E.GuiButton={Activated=true,MouseButton1Click=true,MouseButton1Down=true,MouseButton1Up=true,
        MouseButton2Click=true,MouseButton2Down=true,MouseButton2Up=true}
    E.TextBox={Focused=true,FocusLost=true,ReturnPressedFromOnScreenKeyboard=true}
    G.ScreenGui={IgnoreGuiInset=function(self) return self.ScreenInsets==R.Enum.ScreenInsets.None end}
    S.ScreenGui.IgnoreGuiInset=function(self,value)
        assert(type(value)=='boolean','Expected boolean')
        self.ScreenInsets=if value then R.Enum.ScreenInsets.None else R.Enum.ScreenInsets.CoreUISafeInsets
    end
    S.ScreenGui.ScreenInsets=function(self,value)
        local old=self.IgnoreGuiInset;write(self,'ScreenInsets',value)
        if old~=self.IgnoreGuiInset then R.changed(self,'IgnoreGuiInset') end
    end
    G.UICorner={CornerRadius=function(self) return self.TopLeftRadius end}
    S.UICorner.CornerRadius=function(self,value)
        write(self,'CornerRadius',value)
        for _,key in {'TopLeftRadius','TopRightRadius','BottomLeftRadius','BottomRightRadius'} do write(self,key,value) end
    end
    -- Compatibility aliases share storage; FontFace remains a copied value.
    for _,class in {'TextLabel','TextButton','TextBox'} do
        G[class]=G[class] or {};S[class]=S[class] or {}
        G[class].Font=function(self)
            for _,item in R.Enum.Font:GetEnumItems() do
                if R.fontCatalog[item.Name] and R.datatypes.Font.fromEnum(item)==self.FontFace then return item end
            end
            return R.Enum.Font.Unknown
        end
        S[class].Font=function(self,value)
            assert(typeof(value)=='EnumItem' and value.EnumType==R.Enum.Font,'Expected Enum.Font')
            self.FontFace=R.datatypes.Font.fromEnum(value);R.changed(self,'Font')
        end
    end
    -- Computed geometry notifications follow scheduler steps; direct reads are
    -- current immediately. Only objects with subscribed signals are revisited.
    local watched=setmetatable({}, {__mode='k'})
    local signal=R.signal
    function R.signal(object,name)
        local key=string.match(name,'^property:(Absolute%w+)$')
        if key and object:IsA('GuiBase2d') then
            watched[object]=watched[object] or {}
            local ok,value=pcall(function() return object[key] end)
            if ok and watched[object][key]==nil then watched[object][key]=value end
        end
        return signal(object,name)
    end
    local step=R.step
    function R.step(dt)
        step(dt)
        for object,values in watched do
            if R.instances[object].locked then watched[object]=nil
            else
                for key,previous in values do
                    local ok,value=pcall(function() return object[key] end)
                    if ok and value~=previous then values[key]=value;R.changed(object,key) end
                end
            end
        end
    end
    R.uiRect=rect
end
