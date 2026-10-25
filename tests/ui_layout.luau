local function eq(a,b) assert((a-b).Magnitude<0.0001,tostring(a)..' ~= '..tostring(b)) end
local function rejects(fn) assert(not pcall(fn),'Expected failure') end
local gui=Instance.new('ScreenGui',__engine.player.PlayerGui);gui.IgnoreGuiInset=true
local function frame(parent,name,x,y)
    local result=Instance.new('Frame',parent);result.Name=name;result.Size=UDim2.fromOffset(x,y);return result
end
local panel=frame(gui,'List',300,200)
local list=Instance.new('UIListLayout',panel)
list.SortOrder=Enum.SortOrder.LayoutOrder;list.FillDirection=Enum.FillDirection.Vertical;list.Padding=UDim.new(0,5)
local a=frame(panel,'A',80,20);a.LayoutOrder=2
local b=frame(panel,'B',100,30);b.LayoutOrder=1
local c=frame(panel,'C',60,40);c.LayoutOrder=3
eq(b.AbsolutePosition,Vector2.zero);eq(a.AbsolutePosition,Vector2.new(0,35));eq(c.AbsolutePosition,Vector2.new(0,60))
eq(list.AbsoluteContentSize,Vector2.new(100,100))
list.HorizontalAlignment=Enum.HorizontalAlignment.Center;list.VerticalAlignment=Enum.VerticalAlignment.Bottom
eq(b.AbsolutePosition,Vector2.new(100,100));eq(a.AbsolutePosition,Vector2.new(110,135))
c.Visible=false;eq(list.AbsoluteContentSize,Vector2.new(100,55));eq(b.AbsolutePosition,Vector2.new(100,145))
c.Visible=true;list.SortOrder=Enum.SortOrder.Name;c.Name='0'
list.HorizontalAlignment=Enum.HorizontalAlignment.Left;list.VerticalAlignment=Enum.VerticalAlignment.Top
eq(c.AbsolutePosition,Vector2.zero)
c:Destroy();eq(list.AbsoluteContentSize,Vector2.new(100,55))
list:SetCustomSortFunction(function(x,y) return x.Name>y.Name end);list.SortOrder=Enum.SortOrder.Custom
eq(b.AbsolutePosition,Vector2.zero)
list:ApplyLayout()
rejects(function() list.AbsoluteContentSize=Vector2.zero end)
local changed=0
list:GetPropertyChangedSignal('AbsoluteContentSize'):Connect(function() changed+=1 end)
a.Size=UDim2.fromOffset(80,40)
eq(list.AbsoluteContentSize,Vector2.new(100,75));task.wait();assert(changed==1)
list.FillDirection=Enum.FillDirection.Horizontal
eq(b.AbsolutePosition,Vector2.zero);eq(a.AbsolutePosition,Vector2.new(105,0))
eq(list.AbsoluteContentSize,Vector2.new(185,40))
list.HorizontalFlex=Enum.UIFlexAlignment.Fill
rejects(function() return list.AbsoluteContentSize end)
list.HorizontalFlex=Enum.UIFlexAlignment.None
panel.Size=UDim2.fromOffset(150,200);list.Wraps=true
eq(a.AbsolutePosition,Vector2.new(0,35));eq(list.AbsoluteContentSize,Vector2.new(100,75))
panel:Destroy()

local gridPanel=frame(gui,'Grid',130,100)
local grid=Instance.new('UIGridLayout',gridPanel)
grid.CellSize=UDim2.fromOffset(40,20);grid.CellPadding=UDim2.fromOffset(5,5)
grid.SortOrder=Enum.SortOrder.LayoutOrder
local items={}
for i=1,5 do local item=frame(gridPanel,tostring(i),1,1);item.LayoutOrder=i;items[i]=item end
eq(grid.AbsoluteCellSize,Vector2.new(40,20));eq(grid.AbsoluteCellCount,Vector2.new(3,2))
eq(grid.AbsoluteContentSize,Vector2.new(130,45))
eq(items[4].AbsolutePosition,Vector2.new(0,25));eq(items[1].AbsoluteSize,Vector2.new(40,20))
grid.StartCorner=Enum.StartCorner.BottomRight
eq(items[1].AbsolutePosition,Vector2.new(90,25));eq(items[5].AbsolutePosition,Vector2.new(45,0))
grid.FillDirectionMaxCells=2;grid.StartCorner=Enum.StartCorner.TopLeft
eq(grid.AbsoluteCellCount,Vector2.new(2,3));eq(grid.AbsoluteContentSize,Vector2.new(85,70))
grid.HorizontalAlignment=Enum.HorizontalAlignment.Center
eq(items[1].AbsolutePosition,Vector2.new(22.5,0))
grid.FillDirection=Enum.FillDirection.Vertical
eq(grid.AbsoluteCellCount,Vector2.new(3,2));eq(items[2].AbsolutePosition,Vector2.new(0,25))
for _,item in items do item:Destroy() end
grid.FillDirection=Enum.FillDirection.Horizontal;grid.FillDirectionMaxCells=0;grid.HorizontalAlignment=Enum.HorizontalAlignment.Left
local wide=frame(gridPanel,'Wide',1,1);wide.LayoutOrder=1
local minimum=Instance.new('UISizeConstraint',wide);minimum.MinSize=Vector2.new(90,30)
local nextItem=frame(gridPanel,'Next',1,1);nextItem.LayoutOrder=2
eq(grid.AbsoluteCellCount,Vector2.new(3,3));eq(wide.AbsoluteSize,Vector2.new(130,45))
eq(nextItem.AbsolutePosition,Vector2.new(0,50))
gridPanel:Destroy()

local auto=frame(gui,'Auto',100,0);auto.AutomaticSize=Enum.AutomaticSize.Y
local pad=Instance.new('UIPadding',auto)
pad.PaddingTop=UDim.new(0,10);pad.PaddingBottom=UDim.new(0,20)
local autoList=Instance.new('UIListLayout',auto);autoList.Padding=UDim.new(0,5)
autoList.SortOrder=Enum.SortOrder.LayoutOrder
local one=frame(auto,'One',80,20);one.LayoutOrder=1
local two=frame(auto,'Two',80,30);two.LayoutOrder=2
eq(auto.AbsoluteSize,Vector2.new(100,85));eq(two.AbsolutePosition,Vector2.new(0,35))
two:Destroy();eq(auto.AbsoluteSize,Vector2.new(100,50))
auto:Destroy()
local converge=frame(gui,'Converge',100,0);converge.AutomaticSize=Enum.AutomaticSize.Y
local scaled=frame(converge,'Child',30,20);scaled.Size=UDim2.new(0,30,0.5,20)
eq(converge.AbsoluteSize,Vector2.new(100,40))
scaled.Size=UDim2.new(0,30,1,1)
rejects(function() return converge.AbsoluteSize end)
converge:Destroy()
local scroll=Instance.new('ScrollingFrame',gui)
scroll.Size=UDim2.fromOffset(100,40);scroll.CanvasSize=UDim2.fromOffset(0,0);scroll.AutomaticCanvasSize=Enum.AutomaticSize.Y
local sl=Instance.new('UIListLayout',scroll);sl.Padding=UDim.new(0,5)
for i=1,3 do frame(scroll,tostring(i),80,20) end
eq(scroll.AbsoluteCanvasSize,Vector2.new(100,70))
scroll.CanvasPosition=Vector2.new(0,20)
eq(sl.AbsoluteContentSize,Vector2.new(80,70))
scroll:FindFirstChild('3'):Destroy();eq(scroll.AbsoluteCanvasSize,Vector2.new(100,45))
local clone=scroll:Clone();clone.Parent=gui;eq(clone.AbsoluteCanvasSize,Vector2.new(100,45))
gui:Destroy()
print('LIST, GRID, WRAP, SORT, SPAN, AUTOSIZE AND CANVAS CHECKS PASSED')
