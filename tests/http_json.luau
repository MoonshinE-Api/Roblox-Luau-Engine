local http=game:GetService('HttpService')
assert(http.HttpEnabled==false)
assert(http:JSONEncode({})=='[]')
assert(http:JSONEncode(nil)=='null')
assert(http:JSONDecode('null')==nil)
assert(http:JSONEncode({1,2,ignored='yes'})=='[1,2]')
assert(http:JSONEncode({value=math.huge}):find('null'))
assert(http:JSONEncode(function() end)=='null')
local cycle={};cycle.self=cycle
assert(not pcall(function() http:JSONEncode(cycle) end))
local shared={key='ok'}
assert(http:JSONDecode(http:JSONEncode({shared,shared}))[2].key=='ok')
local dangerous=setmetatable({7},{__len=function() error('len called') end,__index=function() error('index called') end,__iter=function() error('iter called') end})
assert(http:JSONEncode(dangerous)=='[7]')
assert(http:JSONDecode(' { "text": "hello, \\u041c\\u0438\\u0440 \\ud83d\\ude80", "ok":false, "a":[1,null,3] } ').text=='hello, Мир 🚀')
local object=http:JSONDecode('{"ok":false,"a":[1,null,3],"n":null,"duplicate":5,"duplicate":null}')
assert(object.ok==false and object.a[1]==1 and object.a[2]==nil and object.a[3]==3 and object.n==nil and object.duplicate==5)
assert(http:JSONEncode(http:JSONDecode('[null,true]'))=='[null,true]')
assert(http:JSONDecode('{"m":null,"t":"numeric","v":"inf"}')==math.huge)
assert(http:JSONDecode('{"m":null,"t":"numeric","v":"-inf"}')==-math.huge)
local nan=http:JSONDecode('{"m":null,"t":"numeric","v":"nan"}');assert(nan~=nan)
for _,invalid in {'','[1,]','{"a":1,}','01','+1','1.','1e','[true false]','null x','NaN','Infinity','1e9999','"\\ud800"','"\\udc00"','"a\n"','"\\x20"',string.char(34,255,34)} do
    assert(not pcall(function() http:JSONDecode(invalid) end),'Accepted invalid JSON '..invalid)
end
local control='quote" slash\\ newline\n\0 end\t'
assert(http:JSONDecode(http:JSONEncode(control))==control)
assert(not pcall(function() http:JSONEncode(string.char(255)) end))
for length=0,260 do
    local bytes={};for i=1,length do bytes[i]=string.char((i*67)%256) end
    local text=table.concat(bytes)
    assert(buffer.tostring(http:JSONDecode(http:JSONEncode(buffer.fromstring(text))))==text)
end
local seen={}
for i=1,1000 do
    local id=http:GenerateGUID(false)
    assert(#id==36 and id:match('^%x%x%x%x%x%x%x%x%-%x%x%x%x%-4%x%x%x%-[89ab]%x%x%x%-%x%x%x%x%x%x%x%x%x%x%x%x$'))
    assert(not seen[id]);seen[id]=true
end
assert(#http:GenerateGUID()==38 and http:GenerateGUID():sub(1,1)=='{')
assert(not pcall(function() http:GenerateGUID('true') end))
local bytes,expected={},{}
for i=0,255 do
    bytes[i+1]=string.char(i)
    expected[i+1]=if i>=48 and i<=57 or i>=65 and i<=90 or i>=97 and i<=122 then string.char(i) else string.format('%%%02X',i)
end
assert(http:UrlEncode(table.concat(bytes))==table.concat(expected))
assert(http:UrlEncode('hello, chatgpt')=='hello%2C%20chatgpt')
assert(http:UrlEncode('._-~')=='%2E%5F%2D%7E')
assert(not pcall(function() http:GetAsync('http://127.0.0.1/') end))
print('HTTP JSON/GUID/URL CHECKS PASSED')
