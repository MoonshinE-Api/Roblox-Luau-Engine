local checks=0
local function fails(fn)
    local ok,message=pcall(fn)
    assert(not ok and type(message)=="string" and #message>0)
    checks+=1
end
local frozen=table.freeze({value=1})
fails(function() frozen.value=2 end)
fails(function() frozen.extra=2 end)
fails(function() rawset(frozen,"value",2) end)
fails(function() table.insert(frozen,1) end)
fails(function() Vector3.new=nil end)
fails(function() ColorSequence.new=nil end)
fails(function() local x=nil;return x.value end)
fails(function() local x=nil;x.value=1 end)
fails(function() local x=5;return x.value end)
fails(function() local x={};return x() end)
fails(function() local x={};return x:MissingMethod() end)
fails(function() return "text"-{} end)
fails(function() return string.find("abc","[") end)
fails(function() return string.match("abc",string.rep("(",40)) end)
local proxy=newproxy(true)
getmetatable(proxy).__newindex=function() error("metamethod-write") end
fails(function() proxy.field=1 end)
local co=coroutine.create(function()
    for _=1,20 do
        fails(function() error("nested") end)
        coroutine.yield()
    end
    return 42
end)
for _=1,20 do assert(coroutine.resume(co)) end
local ok,result=coroutine.resume(co)
assert(ok and result==42 and frozen.value==1)
assert(Instance.new("Part").Size.X==4)
print("VM ERROR BRANCH CHECKS PASSED",checks)
