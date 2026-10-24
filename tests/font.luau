local function fails(fn) assert(not pcall(fn),'Expected error') end
local family='rbxasset://fonts/families/SourceSansPro.json'
local font=Font.new(family)
assert(typeof(font)=='Font' and font.Family==family)
assert(font.Weight==Enum.FontWeight.Regular and font.Style==Enum.FontStyle.Normal and not font.Bold)
assert(font==Font.fromName('SourceSansPro') and font==Font.fromEnum(Enum.Font.SourceSans))
assert(Font.new('a\\b\0ignored').Family=='a/b')
assert(Font.fromName('A_2-b\0ignored').Family=='rbxasset://fonts/families/A_2-b.json')
font.Weight=Enum.FontWeight.Heavy;font.Bold=true;assert(font.Weight==Enum.FontWeight.Heavy)
font.Bold=false;assert(font.Weight==Enum.FontWeight.Regular)
font.Weight=Enum.FontWeight.Thin;font.Bold=false;assert(font.Weight==Enum.FontWeight.Thin)
font.Bold=true;assert(font.Weight==Enum.FontWeight.Bold)
font.Weight=Enum.FontWeight.SemiBold;assert(font.Bold)
font.Style=Enum.FontStyle.Italic;font.Family='rbxassetid://123'
assert(font.Style==Enum.FontStyle.Italic and font.Family=='rbxassetid://123')
for _,pair in {{1,1},{1.9,1},{2147483647,2147483647},{2147483648,2147483648},
    {-1,4294967295},{-1.9,4294967295},{-2147483649,2147483648},{math.huge,2147483648},
    {-math.huge,2147483648},{0/0,2147483648},{11702779409,2147483648}} do
    assert(Font.fromId(pair[1]).Family=='rbxassetid://'..string.format('%.0f',pair[2]))
end
for _,fn in {function()Font.new()end,function()Font.new(1)end,function()Font.new('a',Enum.Material.Plastic)end,
    function()Font.fromEnum(Enum.Font.Unknown)end,function()Font.fromEnum(Enum.FontWeight.Bold)end,
    function()Font.fromName('')end,function()Font.fromName('../a')end,function()Font.fromName('шрифт')end,
    function()Font.fromId(0)end,function()Font.fromId(.9)end,function()Font.fromId(-.9)end,
    function()font.Weight=nil end,function()font.Style=1 end,function()font.Bold=1 end,
    function()font.Family={}end,function()return font.IsLoaded end,function()font.Other=true end} do fails(fn) end
local object=Instance.new('Folder');local source=Font.fromEnum(Enum.Font.Arial)
for _,name in {'UI/fonts.Main-1','-','/','.',string.rep('a',100)} do object:SetAttribute(name,source);assert(object:GetAttribute(name)==source) end
for _,name in {'',string.rep('a',101),'bad name','bad!','RBXreserved','Юникод','nul\0suffix'} do fails(function()object:SetAttribute(name,source)end) end
object:SetAttribute('Font',source);source.Bold=true
assert(not object:GetAttribute('Font').Bold)
local result=object:GetAttribute('Font');result.Bold=true
assert(not object:GetAttribute('Font').Bold)
local all=object:GetAttributes();all.Font.Bold=true
assert(not object:GetAttribute('Font').Bold)
local changed=0;object:GetAttributeChangedSignal('Font'):Connect(function()changed+=1 end)
object:SetAttribute('Font',Font.fromEnum(Enum.Font.Arial));task.wait();assert(changed==0)
object:SetAttribute('Font',result);task.wait();assert(changed==1)
local clone=object:Clone();local c=clone:GetAttribute('Font');c.Bold=false;clone:SetAttribute('Font',c)
assert(object:GetAttribute('Font').Bold and not clone:GetAttribute('Font').Bold)
object:Destroy();clone:Destroy()
print('FONT VALUE AND COPY CHECKS PASSED')
