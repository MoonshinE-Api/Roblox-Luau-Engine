local player=game:GetService('Players'):GetPlayers()[1]
local screen=Instance.new('ScreenGui',player.PlayerGui)
screen.IgnoreGuiInset=true
local panel=Instance.new('Frame',screen)
panel.Size=UDim2.fromOffset(400,160)
panel.Position=UDim2.fromScale(0.5,0.5)
panel.AnchorPoint=Vector2.new(0.5,0.5)
local title=Instance.new('TextLabel',panel)
title.Size=UDim2.new(1,0,0,40)
title.Text='Headless Roblox UI'
title.Font=Enum.Font.ArialBold
title.TextSize=24
local input=Instance.new('TextBox',panel)
input.Position=UDim2.fromOffset(20,60)
input.Size=UDim2.new(1,-40,0,36)
input.ClearTextOnFocus=false
input.Text='hello, chatgpt'
input.Focused:Connect(function() print('Focused:',input.Text) end)
input:CaptureFocus()
print('Panel pixels:',panel.AbsolutePosition,panel.AbsoluteSize)
local tween=game:GetService('TweenService'):Create(panel,TweenInfo.new(0.1),{Position=UDim2.fromScale(0.25,0.5)})
tween:Play();tween.Completed:Wait()
print('Tweened panel pixels:',panel.AbsolutePosition)
input:ReleaseFocus(true)
