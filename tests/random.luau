local function rejects(fn) assert(not pcall(fn),"Expected error") end
local expected={0.22072993115387124,0.9202737237894263,0.7635500080741559,0.5235603366883349,0.7878579242930221}
local a=Random.new(42)
assert(typeof(a)=="Random" and tostring(a)=="Random")
for _,value in expected do assert(a:NextNumber()==value) end
local b=a:Clone();assert(a==b and not rawequal(a,b))
assert(a:NextNumber()==b:NextNumber() and a==b)
a:NextInteger(1,6);assert(a~=b)
local c,d=Random.new(-123.9),Random.new(-123)
for _=1,100 do assert(c:NextInteger(-100,100)==d:NextInteger(100,-100)) end
local wide,narrow=Random.new(4294967303),Random.new(7)
assert(wide:NextNumber()~=narrow:NextNumber(),"Seed was truncated to 32 bits")
local e,f=Random.new(8),Random.new(8)
for _=1,500 do
    local v=e:NextUnitVector();assert(typeof(v)=="Vector3" and math.abs(v.Magnitude-1)<2e-7)
    f:NextNumber();assert(e==f,"UnitVector must consume two PCG samples")
end
local array={1,2,3,4,5,6,7,8,9,10,marker="preserve"}
local copy=table.clone(array);local p,q=Random.new(99),Random.new(99)
p:Shuffle(array)
for i=#copy,2,-1 do local j=q:NextInteger(1,i);copy[j],copy[i]=copy[i],copy[j] end
assert(p==q and array.marker=="preserve")
for i=1,#array do assert(array[i]==copy[i]) end
table.sort(array);for i=1,10 do assert(array[i]==i) end
local untouched=p:Clone();p:Shuffle({});p:Shuffle({1});assert(p==untouched)
rejects(function() Random.new({}) end)
rejects(function() a:NextNumber(1) end)
rejects(function() a:NextInteger(nil,2) end)
rejects(function() a:Shuffle(table.freeze({1,2})) end)
rejects(function() a.seed=1 end)
assert(Random.new(1e20)==Random.new(0))
assert(Random.new(0/0)==Random.new(0))
assert(Random.new("42")==Random.new(42))
assert(a:NextNumber(0/0,1)~=a:NextNumber(0/0,1))
assert(a:NextInteger(math.huge,math.huge)==-9223372036854775808)
print("PASS Random: native vectors, 64-bit seeds, clone/state equality, unit vectors, shuffle and errors")
