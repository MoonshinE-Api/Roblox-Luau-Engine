local function rejects(fn) assert(not pcall(fn),'Expected failure') end
local service=game:GetService('DataStoreService')
if game:GetService('RunService'):IsClient() then
    rejects(function() service:GetDataStore('Profiles') end)
    print('CLIENT DATA STORE ACCESS REJECTED');return
end
local store=service:GetDataStore('Profiles')
assert(store==service:GetDataStore('Profiles') and store:IsA('GlobalDataStore'))
store:SetAsync('false',false);assert(store:GetAsync('false')==false)
store:UpdateAsync('false',function(value) assert(value==false);return true end)
assert(store:GetAsync('false')==true)
assert(service:GetGlobalDataStore().Scope=='u')
local options=Instance.new('DataStoreSetOptions');options:SetMetadata({schema=2})
local version=store:SetAsync('player',{coins=10,inventory={'a','b'}},{123,456},options)
assert(type(version)=='string')
local data,info=store:GetAsync('player')
assert(data.coins==10 and info.Version==version and info.CreatedTime>0 and info.UpdatedTime>=info.CreatedTime)
assert(info:GetMetadata().schema==2 and info:GetUserIds()[2]==456)
data.coins=999;local ids=info:GetUserIds();ids[1]=0
assert(store:GetAsync('player').coins==10 and info:GetUserIds()[1]==123)
rejects(function() info.Version='other' end)
local updated,newInfo=store:UpdateAsync('player',function(old,key)
    old.coins+=5;return old,key:GetUserIds(),key:GetMetadata()
end)
assert(updated.coins==15 and newInfo:GetMetadata().schema==2 and newInfo.Version~=version)
local historic,historicInfo=store:GetVersionAsync('player',version)
assert(historic.coins==10 and historicInfo.Version==version)
assert(store:UpdateAsync('player',function() return nil end)==nil)
assert(store:GetAsync('player').coins==15)
rejects(function() store:UpdateAsync('player',function() task.wait();return 0 end) end)
rejects(function() store:UpdateAsync('player',function() error('callback failed') end) end)
assert(store:GetAsync('player').coins==15)
local cycle={};cycle.self=cycle
for _,value in {cycle,Vector3.one,0/0,math.huge,function()end,{[1]='a',[3]='c'},{a=1,[1]='b'},'\255'} do
    rejects(function() store:SetAsync('invalid',value) end)
end
rejects(function() store:SetAsync('',1) end)
rejects(function() store:SetAsync('bad',nil) end)
store:SetAsync('counter',0)
local finished=0
for i=1,20 do
    task.spawn(function()
        store:UpdateAsync('counter',function(n) return n+1 end)
        finished+=1
    end)
end
repeat task.wait() until finished==20
local fresh=Instance.new('DataStoreGetOptions');fresh.UseCache=false
assert(store:GetAsync('counter',fresh)==20)
assert(store:IncrementAsync('counter',3)==23)
local before,removedInfo=store:RemoveAsync('player')
assert(before.coins==15 and removedInfo.Version==newInfo.Version)
local missing,missingInfo=store:GetAsync('player');assert(missing==nil and missingInfo==nil)
assert(store:GetVersionAsync('player',version).coins==10)
local scoped=service:GetDataStore('Profiles','season2');scoped:SetAsync('u',42)
local allOptions=Instance.new('DataStoreOptions');allOptions.AllScopes=true
local all=service:GetDataStore('Profiles','global',allOptions)
assert(all:GetAsync('season2/u')==42 and all:GetOptions().AllScopes)
store:SetAsync('prefix_A',1);store:SetAsync('prefix_B',2)
local keys=store:ListKeysAsync('prefix_',1,'',true)
assert(not keys.IsFinished and keys:GetCurrentPage()[1].KeyName=='prefix_A')
local cursor=keys.Cursor
keys:AdvanceToNextPageAsync()
assert(keys.IsFinished and keys:GetCurrentPage()[1].KeyName=='prefix_B')
assert(store:ListKeysAsync('prefix_',1,cursor,true):GetCurrentPage()[1].KeyName=='prefix_B')
rejects(function() keys:AdvanceToNextPageAsync() end)
local ordered=service:GetOrderedDataStore('Scores')
ordered:SetAsync('a',20);ordered:SetAsync('b',10);ordered:SetAsync('c',30)
rejects(function() ordered:SetAsync('fraction',1.5) end)
rejects(function() ordered:SetAsync('table',{}) end)
local scores=ordered:GetSortedAsync(false,2)
assert(scores:GetCurrentPage()[1].key=='c' and scores:GetCurrentPage()[2].value==20)
scores:AdvanceToNextPageAsync();assert(scores.IsFinished and scores:GetCurrentPage()[1].key=='b')
local filtered=ordered:GetSortedAsync(true,100,15,25):GetCurrentPage()
assert(#filtered==1 and filtered[1].key=='a')
assert(select(2,ordered:GetAsync('a'))==nil)
print('LOCAL DATA STORE VALUES, METADATA, VERSIONS, CAS, SCOPES AND PAGES PASSED')
