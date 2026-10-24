-- Import the user's unmodified XML with --model before running this driver.
local compile = require(workspace:WaitForChild("Loadstr1ng"))
local execute, compileError = compile([[
    local a,b = ...
    assert(a == 11 and b == 31)
    local function factorial(n)
        if n < 2 then return 1 end
        return n * factorial(n - 1)
    end
    assert(factorial(8) == 40320)
    local part = Instance.new("Part", workspace)
    part.Name = "CompiledInsideOurRuntime"
    part.Anchored = true
    part.Position = Vector3.new(3, 4, 5)
    part:SetAttribute("Result", a + b)
    local clone = part:Clone()
    assert(clone.Name == part.Name and clone:GetAttribute("Result") == 42)
    clone:Destroy()
    local event = Instance.new("BindableEvent")
    local count = 0
    event.Event:Connect(function(value) count = count + value end)
    event:Fire(42)
    assert(count == 42)
    local h = game:GetService("HttpService")
    assert(h:JSONDecode(h:JSONEncode({result=count})).result == 42)
    task.wait(0.02)
    part:Destroy()
    print("XML COMPILER AND LUA 5.1 VM ENGINE CHECK PASSED", count)
    return count, nil, "compiled-inside"
]], getfenv())
assert(execute, compileError)
local a,b,c = execute(11,31)
assert(a==42 and b==nil and c=="compiled-inside")
local invalid, reason = compile("local a += 1", getfenv())
assert(invalid==nil and type(reason)=="string", "Lua 5.1 compiler unexpectedly accepted Luau +=")
