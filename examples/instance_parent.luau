local a = Instance.new("Part", workspace)
a.Parent = game.ServerStorage
print(a.Parent)
assert(a.Parent == game:GetService("ServerStorage"))
assert(typeof(a) == "Instance")
assert(a:IsA("BasePart"))

local changed = 0
a:GetPropertyChangedSignal("Name"):Connect(function() changed += 1 end)
a.Name = "ExamplePart"
assert(changed == 1)
a.Position = Vector3.new(1, 2, 3)
assert(a.Position == Vector3.new(1, 2, 3))
a:SetAttribute("Health", 100)
assert(a:GetAttribute("Health") == 100)

local copy = a:Clone()
assert(copy ~= a and copy.Name == a.Name and copy.Parent == nil)
assert(copy:GetAttribute("Health") == 100)
local ok = pcall(function() a.Parent = a end)
assert(not ok)
copy:Destroy()
assert(not pcall(function() copy.Parent = workspace end))
print("Instance checks passed", a:GetFullName(), a.Position)

task.delay(0.1, function()
    local folder = Instance.new("Folder", workspace)
    folder.Name = "DelayedChild"
end)
assert(workspace:WaitForChild("DelayedChild", 1) ~= nil)
print("WaitForChild passed")
