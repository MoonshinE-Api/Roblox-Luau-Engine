-- Server-side demo. --data-store inventory.sqlite3 persists visits across runs.
-- MemoryStore coordination is local to this VM; SQLite is a local backend.
local player=game:GetService('Players'):GetPlayers()[1]
local key='player:'..player.UserId
local memory=game:GetService('MemoryStoreService')
local locks=memory:GetHashMap('InventoryLocks')
local token=game:GetService('HttpService'):GenerateGUID(false)
local acquired=locks:UpdateAsync(key,function(owner) if owner==nil then return token end end,30)
assert(acquired==token,'Profile is already being used in this runtime')
local store=game:GetService('DataStoreService'):GetDataStore('InventoryDemo')
local profile,info=store:UpdateAsync(key,function(old)
    old=old or {visits=0,items={'Sword','Shield','Potion','Map','Key','Bow','Helmet','Boots','Ring','Gem','Torch','Book'}}
    old.visits+=1;return old,{player.UserId},{schema=1}
end)
local screen=Instance.new('ScreenGui',player.PlayerGui);screen.IgnoreGuiInset=true
local panel=Instance.new('Frame',screen)
panel.Size=UDim2.fromOffset(240,0);panel.AutomaticSize=Enum.AutomaticSize.Y
local padding=Instance.new('UIPadding',panel)
padding.PaddingTop=UDim.new(0,10);padding.PaddingBottom=UDim.new(0,10)
local list=Instance.new('UIListLayout',panel)
list.SortOrder=Enum.SortOrder.LayoutOrder;list.Padding=UDim.new(0,8)
list.HorizontalAlignment=Enum.HorizontalAlignment.Center
local title=Instance.new('TextLabel',panel);title.LayoutOrder=1
title.Size=UDim2.fromOffset(220,30);title.Text='Inventory / visit '..profile.visits
local scroll=Instance.new('ScrollingFrame',panel);scroll.LayoutOrder=2
scroll.Size=UDim2.fromOffset(200,100);scroll.CanvasSize=UDim2.fromOffset(0,0)
scroll.AutomaticCanvasSize=Enum.AutomaticSize.Y
local grid=Instance.new('UIGridLayout',scroll)
grid.CellSize=UDim2.fromOffset(60,36);grid.CellPadding=UDim2.fromOffset(6,6)
grid.SortOrder=Enum.SortOrder.LayoutOrder
for index,item in profile.items do
    local slot=Instance.new('Frame',scroll);slot.Name=item;slot.LayoutOrder=index
    slot.BackgroundColor3=Color3.fromHSV(index/#profile.items,0.4,0.7)
    local text=Instance.new('TextLabel',slot);text.Size=UDim2.fromScale(1,1)
    text.Text=item;text.TextSize=14;text.BackgroundTransparency=1
end
assert(grid.AbsoluteCellCount==Vector2.new(3,4))
assert(scroll.AbsoluteCanvasSize==Vector2.new(200,162))
assert(panel.AbsoluteSize==Vector2.new(240,158))
local queue=memory:GetQueue('InventorySaves',30)
queue:AddAsync({userId=player.UserId,version=info.Version,visits=profile.visits},60,1)
local messages,id=queue:ReadAsync(1,true,0)
assert(messages[1].version==info.Version);queue:RemoveAsync(id)
locks:RemoveAsync(key)
print('PERSISTENT INVENTORY / GRID / AUTOSIZE / MEMORY QUEUE PASSED',profile.visits,#profile.items)
screen:Destroy()
