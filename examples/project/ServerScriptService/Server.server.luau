local store = game:GetService("ReplicatedStorage")
local nextCount = require(store.Counter)
assert(nextCount() == 1 and require(store.Counter)() == 2)
assert(game:GetService("RunService"):IsServer())
assert(game:GetService("Players").LocalPlayer == nil)
local remote = Instance.new("RemoteEvent", store)
remote.Name = "TestRemote"
remote.OnServerEvent:Connect(function(player, value)
    assert(player:IsA("Player") and value == 10)
    remote:FireClient(player, value + 1)
end)
local part = Instance.new("Part", workspace)
part.Name = "ServerPart"
part.Anchored = true
print("Server and ModuleScript passed", script.ClassName)
