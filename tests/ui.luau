local function rejects(fn) assert(not pcall(fn),"Expected failure") end
local function equal(a,b) assert((a-b).Magnitude<1e-5,tostring(a).." ~= "..tostring(b)) end
local R=__engine
local representatives={GuiBase2d='Frame',LayerCollector='ScreenGui',GuiObject='Frame',GuiButton='TextButton',UIGridStyleLayout='UIListLayout'}
local checked=0
assert(Instance.new('TextButton').Active and Instance.new('TextBox').Selectable)
assert(Instance.new('UISizeConstraint').MaxSize==Vector2.new(math.huge,math.huge))
for owner,fields in R.uiCatalog.classes do
    for key,record in fields do
        local object=Instance.new(representatives[owner] or owner)
        local previous=object[key]
        assert(previous~=nil or record.kind=='Instance?',owner..'.'..key)
        local value
        local kind=record.kind
        if kind=='boolean' then value=not previous
        elseif kind=='number' then value=previous+1
        elseif kind=='string' then value='test://ui/asset'
        elseif kind=='Vector2' then value=Vector2.new(7,9)
        elseif kind=='Vector3' then value=Vector3.new(1,2,3)
        elseif kind=='Color3' then value=Color3.new(0.2,0.4,0.6)
        elseif kind=='UDim' then value=UDim.new(0.25,12)
        elseif kind=='UDim2' then value=UDim2.new(0.2,8,0.3,9)
        elseif kind=='Rect' then value=Rect.new(2,3,20,30)
        elseif kind=='Font' then value=Font.fromName('Arial',Enum.FontWeight.Bold)
        elseif kind=='ColorSequence' then value=ColorSequence.new(Color3.new(1,0,0),Color3.new(0,0,1))
        elseif kind=='NumberSequence' then value=NumberSequence.new(0.1,0.9)
        elseif kind=='Instance?' then value=R.new(if record.target=='GuiObject' then 'Frame' else record.target,nil,true)
        elseif string.sub(kind,1,5)=='Enum.' then
            local items=Enum[string.sub(kind,6)]:GetEnumItems()
            value=items[1];if value==previous and #items>1 then value=items[2] end
        else error('Uncovered UI property kind '..kind) end
        local changed=0
        object:GetPropertyChangedSignal(key):Connect(function() changed+=1 end)
        object[key]=value
        local stored=object[key]
        assert(typeof(stored)==(if kind=='Instance?' then 'Instance' elseif string.sub(kind,1,5)=='Enum.' then 'EnumItem' else kind))
        assert(changed==(if stored==previous then 0 else 1),owner..'.'..key..' notification')
        assert(object:Clone()[key]==stored,owner..'.'..key..' clone')
        rejects(function() object[key]={} end)
        object:Destroy()
        if kind=='Instance?' then value:Destroy() end
        checked+=1
    end
end
assert(checked==199,checked)
local gui=Instance.new('ScreenGui',R.player.PlayerGui)
gui.IgnoreGuiInset=true
local outer=Instance.new('Frame',gui)
outer.Size=UDim2.new(0.5,0,0.5,0)
outer.Position=UDim2.fromOffset(20,30)
local inner=Instance.new('TextButton',outer)
inner.Size=UDim2.new(0.5,10,0.5,20)
inner.Position=UDim2.fromScale(0.5,0.5)
inner.AnchorPoint=Vector2.new(0.5,0.5)
equal(gui.AbsoluteSize,Vector2.new(1280,720))
equal(outer.AbsoluteSize,Vector2.new(640,360))
equal(inner.AbsoluteSize,Vector2.new(330,200))
equal(inner.AbsolutePosition,Vector2.new(175,110))
local old=inner.AbsoluteSize
local sizeChanged=0
inner:GetPropertyChangedSignal('AbsoluteSize'):Connect(function() sizeChanged+=1 end)
outer.Size=UDim2.fromOffset(800,400)
equal(inner.AbsoluteSize,Vector2.new(410,220))
task.wait()
assert(sizeChanged==1)
local scale=Instance.new('UIScale',outer);scale.Scale=2
equal(outer.AbsoluteSize,Vector2.new(1600,800))
equal(inner.AbsoluteSize,Vector2.new(820,440))
scale:Destroy()
local padding=Instance.new('UIPadding',outer)
padding.PaddingLeft=UDim.new(0,10);padding.PaddingRight=UDim.new(0,20)
padding.PaddingTop=UDim.new(0,5);padding.PaddingBottom=UDim.new(0,15)
equal(inner.AbsoluteSize,Vector2.new(395,210))
equal(inner.AbsolutePosition,Vector2.new(217.5,120))
padding:Destroy()
local limit=Instance.new('UISizeConstraint',inner)
limit.MinSize=Vector2.new(500,250);limit.MaxSize=Vector2.new(550,300)
equal(inner.AbsoluteSize,Vector2.new(500,250))
limit:Destroy()
local aspect=Instance.new('UIAspectRatioConstraint',inner)
aspect.AspectRatio=2;aspect.DominantAxis=Enum.DominantAxis.Width
equal(inner.AbsoluteSize,Vector2.new(410,205))
aspect:Destroy()
rejects(function() inner.AbsoluteSize=Vector2.zero end)
inner.AutomaticSize=Enum.AutomaticSize.X
rejects(function() return inner.AbsoluteSize end)
inner.AutomaticSize=Enum.AutomaticSize.None
inner.Font=Enum.Font.ArialBold
assert(inner.FontFace==Font.fromEnum(Enum.Font.ArialBold))
local font=inner.FontFace;font.Bold=false
assert(inner.FontFace.Bold,'Font getter must copy')
local clone=inner:Clone();font=clone.FontFace;font.Family='other';clone.FontFace=font
assert(inner.FontFace.Family~=clone.FontFace.Family)
inner.NextSelectionDown=inner
assert(inner:Clone().NextSelectionDown.Name==inner.Name)
rejects(function() inner.NextSelectionDown=Instance.new('Part') end)
local text=Instance.new('TextBox',outer);text.ClearTextOnFocus=false;text.Text='hello'
local gained,lost=0,0
text.Focused:Connect(function() gained+=1 end)
text.FocusLost:Connect(function(entered) assert(entered);lost+=1 end)
text:CaptureFocus()
assert(text:IsFocused() and game:GetService('UserInputService'):GetFocusedTextBox()==text and text.CursorPosition==6)
text:ReleaseFocus(true)
assert(not text:IsFocused() and gained==1 and lost==1 and text.CursorPosition==-1)
local scroll=Instance.new('ScrollingFrame',gui)
scroll.Size=UDim2.fromOffset(200,100);scroll.CanvasSize=UDim2.fromOffset(400,300)
equal(scroll.AbsoluteCanvasSize,Vector2.new(400,300))
scroll.CanvasPosition=Vector2.new(20,30)
local child=Instance.new('Frame',scroll);child.Size=UDim2.fromOffset(10,10)
equal(child.AbsolutePosition,Vector2.new(-20,-30))
inner.ZIndex=10
local hits=R.player.PlayerGui:GetGuiObjectsAtPosition(outer.AbsolutePosition.X+inner.Position.X.Scale*outer.AbsoluteSize.X,
    outer.AbsolutePosition.Y+inner.Position.Y.Scale*outer.AbsoluteSize.Y)
assert(table.find(hits,inner))
inner.Visible=false
assert(not table.find(R.player.PlayerGui:GetGuiObjectsAtPosition(420,230),inner))
local front=Instance.new('Frame',gui);front.Size=UDim2.fromOffset(50,50);front.ZIndex=10
local lowChild=Instance.new('Frame',front);lowChild.Size=UDim2.fromOffset(50,50);lowChild.ZIndex=1
local back=Instance.new('Frame',gui);back.Size=UDim2.fromOffset(50,50);back.ZIndex=5
gui.ZIndexBehavior=Enum.ZIndexBehavior.Sibling
assert(R.player.PlayerGui:GetGuiObjectsAtPosition(5,5)[1]==lowChild)
gui.ZIndexBehavior=Enum.ZIndexBehavior.Global
assert(R.player.PlayerGui:GetGuiObjectsAtPosition(5,5)[1]==front)
front.ClipsDescendants=true;lowChild.Position=UDim2.fromOffset(100,100)
assert(not table.find(R.player.PlayerGui:GetGuiObjectsAtPosition(110,110),lowChild))
lowChild.Rotation=10
rejects(function() R.player.PlayerGui:GetGuiObjectsAtPosition(110,110) end)
gui:Destroy()
print('UI CONFIGURATION, GEOMETRY, FOCUS AND CLONE CHECKS PASSED',checked)
