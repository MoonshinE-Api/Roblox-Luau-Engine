local player=game:GetService('Players'):GetPlayers()[1]
local screen=Instance.new('ScreenGui',player.PlayerGui);screen.IgnoreGuiInset=true
local panel=Instance.new('Frame',screen)
panel.Size=UDim2.fromOffset(240,0);panel.AutomaticSize=Enum.AutomaticSize.Y
panel.Position=UDim2.fromOffset(20,20)
local list=Instance.new('UIListLayout',panel)
list.SortOrder=Enum.SortOrder.LayoutOrder;list.Padding=UDim.new(0,6)
for i=1,4 do
    local row=Instance.new('Frame',panel);row.Name='Row'..i;row.LayoutOrder=i
    row.Size=UDim2.fromOffset(240,24+i*4)
    row.BackgroundColor3=Color3.fromHSV(i/4,0.4,0.8)
    local label=Instance.new('TextLabel',row)
    label.Size=UDim2.fromScale(1,1);label.Text=row.Name;label.BackgroundTransparency=1
end
assert(panel.AbsoluteSize==Vector2.new(240,154))
assert(list.AbsoluteContentSize==Vector2.new(240,154))
panel.Row2.Visible=false
assert(panel.AbsoluteSize==Vector2.new(240,116))
panel.Row2.Visible=true
local clone=panel:Clone();clone.Position=UDim2.fromOffset(300,20);clone.Parent=screen
assert(clone.AbsoluteSize==panel.AbsoluteSize)
print('LAYOUT GALLERY / DYNAMIC CONTENT / CLONE PASSED',list.AbsoluteContentSize)
screen:Destroy()
