-- Process-local MemoryStore simulation using scheduler time. No distributed
-- service, persistence across VMs, or Roblox capacity/billing model is implied.
return function(R)
    local M,G=R.classMethods,R.classGetters
    local objects,spaces={},{}
    local states=setmetatable({}, {__mode='k'})
    local pageStates=setmetatable({}, {__mode='k'})
    local function server() assert(R.current().side=='server','Memory stores are only accessible from server scripts') end
    local function text(value,label)
        assert(type(value)=='string' and #value>0 and #value<=128 and utf8.len(value) and not string.find(value,'\0',1,true),
            label..' must contain 1..128 UTF-8 bytes');return value
    end
    local function finite(value) return type(value)=='number' and value==value and math.abs(value)<math.huge end
    local function expiration(value)
        assert(finite(value) and value%1==0 and value>=0 and value<=3888000,'Expiration must be an integer in 0..3888000 seconds')
        return R.syncTime()+value
    end
    local function encode(value)
        local encoded=R.serializeStoreValue(value);assert(#encoded<=32768,'Memory store values exceed local limit 32 KiB');return encoded
    end
    local function sortKey(value)
        assert(value==nil or type(value)=='string' and utf8.len(value) or finite(value),'Sort key must be a finite number, UTF-8 string, or nil')
        return value
    end
    local function state(object)
        server();return assert(states[object],'Memory store must be obtained from MemoryStoreService')
    end
    local function purge(d)
        local now=R.syncTime()
        for key,row in d.space.rows do if row.expires<=now then d.space.rows[key]=nil end end
        for id,ticket in d.space.tickets or {} do if ticket.expires<now then d.space.tickets[id]=nil end end
        return now
    end
    local function get(class,name,invisibility)
        server();text(name,'Name')
        local id=class..'\0'..name
        if not spaces[id] then spaces[id]={rows={},tickets={},sequence=0} end
        local objectId=id..'\0'..tostring(invisibility)
        if not objects[objectId] then
            local object=R.new(class,nil,true);object.Name=name;object.Archivable=false
            states[object]={space=spaces[id],invisibility=invisibility};objects[objectId]=object
        end
        return objects[objectId]
    end
    for _,class in {'MemoryStoreHashMap','MemoryStoreSortedMap','MemoryStoreQueue','MemoryStoreHashMapPages'} do R.noncreatable[class]=true end
    M.MemoryStoreService={GetHashMap=function(_,name) return get('MemoryStoreHashMap',name) end,
        GetSortedMap=function(_,name) return get('MemoryStoreSortedMap',name) end,
        GetQueue=function(_,name,timeout)
            timeout=if timeout==nil then 30 else timeout
            assert(finite(timeout) and timeout%1==0 and timeout>=0,'Invisibility timeout must be a nonnegative integer')
            return get('MemoryStoreQueue',name,timeout)
        end}
    local hash,sorted={},{}
    M.MemoryStoreHashMap=hash;M.MemoryStoreSortedMap=sorted
    function hash:GetAsync(key)
        local d=state(self);text(key,'Key');purge(d)
        local row=d.space.rows[key];return if row then R.jsonDecode(row.value) else nil
    end
    function sorted:GetAsync(key)
        local d=state(self);text(key,'Key');purge(d)
        local row=d.space.rows[key]
        if row then return R.jsonDecode(row.value),row.sortKey end
        return nil,nil
    end
    function hash:SetAsync(key,value,ttl)
        local d=state(self);text(key,'Key');local untilTime=expiration(ttl);local encoded=encode(value)
        d.space.rows[key]={value=encoded,expires=untilTime};return true
    end
    function sorted:SetAsync(key,value,ttl,ordering)
        local d=state(self);text(key,'Key');local untilTime=expiration(ttl);local encoded=encode(value)
        d.space.rows[key]={value=encoded,expires=untilTime,sortKey=sortKey(ordering)};return true
    end
    function hash:RemoveAsync(key) local d=state(self);text(key,'Key');d.space.rows[key]=nil end
    sorted.RemoveAsync=hash.RemoveAsync
    function hash:UpdateAsync(key,callback,ttl)
        local d=state(self);text(key,'Key');expiration(ttl)
        assert(type(callback)=='function','Expected callback function')
        for _=1,128 do
            purge(d);local previous=d.space.rows[key]
            local value=R.invokeStoreTransform(callback,if previous then R.jsonDecode(previous.value) else nil,nil)
            if value==nil then return nil end
            local encoded=encode(value);purge(d)
            if d.space.rows[key]==previous then
                d.space.rows[key]={value=encoded,expires=expiration(ttl)};return R.jsonDecode(encoded)
            end
        end
        error('UpdateAsync exceeded local contention retry limit 128',2)
    end
    function sorted:UpdateAsync(key,callback,ttl)
        local d=state(self);text(key,'Key');expiration(ttl)
        assert(type(callback)=='function','Expected callback function')
        for _=1,128 do
            purge(d);local previous=d.space.rows[key]
            local value,ordering=R.invokeStoreTransform(callback,if previous then R.jsonDecode(previous.value) else nil,previous and previous.sortKey or nil)
            if value==nil then return nil end
            local encoded=encode(value);sortKey(ordering);purge(d)
            if d.space.rows[key]==previous then
                d.space.rows[key]={value=encoded,expires=expiration(ttl),sortKey=ordering}
                return R.jsonDecode(encoded),ordering
            end
        end
        error('UpdateAsync exceeded local contention retry limit 128',2)
    end
    function sorted:GetSizeAsync() local d=state(self);purge(d);local n=0;for _ in d.space.rows do n+=1 end;return n end
    local function compare(a,b)
        local function rank(value) return if value==nil then 0 elseif type(value)=='number' then 1 else 2 end
        local x,y=rank(a),rank(b)
        if x~=y then return if x<y then -1 else 1 end
        if a==b then return 0 end
        return if a<b then -1 else 1
    end
    local function bounds(row,bound)
        if bound.sortKey~=nil then
            sortKey(bound.sortKey);local c=compare(row.sortKey,bound.sortKey)
            if c~=0 or bound.key==nil then return c end
        end
        assert(bound.key~=nil,'Range bound needs a key or sortKey');text(bound.key,'Bound key')
        return compare(row.key,bound.key)
    end
    function sorted:GetRangeAsync(direction,count,lower,upper)
        local d=state(self);purge(d)
        assert(direction==R.Enum.SortDirection.Ascending or direction==R.Enum.SortDirection.Descending,'Expected Enum.SortDirection')
        assert(type(count)=='number' and count%1==0 and count>=1 and count<=200,'Count must be an integer in 1..200')
        assert(lower==nil or type(lower)=='table','Expected lower bound dictionary')
        assert(upper==nil or type(upper)=='table','Expected upper bound dictionary')
        local rows={}
        for key,value in d.space.rows do
            local row={key=key,value=R.jsonDecode(value.value),sortKey=value.sortKey}
            if (not lower or bounds(row,lower)>0) and (not upper or bounds(row,upper)<0) then table.insert(rows,row) end
        end
        table.sort(rows,function(a,b)
            local c=compare(a.sortKey,b.sortKey);if c==0 then c=compare(a.key,b.key) end
            return if direction==R.Enum.SortDirection.Ascending then c<0 else c>0
        end)
        while #rows>count do table.remove(rows) end
        return rows
    end
    function hash:ListItemsAsync(count)
        local d=state(self);purge(d)
        assert(type(count)=='number' and count%1==0 and count>=1 and count<=200,'Count must be an integer in 1..200')
        local rows={};for key,row in d.space.rows do table.insert(rows,{key=key,value=R.jsonDecode(row.value)}) end
        table.sort(rows,function(a,b) return a.key<b.key end)
        local object=R.new('MemoryStoreHashMapPages',nil,true);object.Archivable=false
        pageStates[object]={rows=rows,size=count,offset=1};return object
    end
    G.MemoryStoreHashMapPages={IsFinished=function(self) local p=pageStates[self];return p.offset+p.size>#p.rows end}
    M.MemoryStoreHashMapPages={GetCurrentPage=function(self)
        local p=pageStates[self];local result={}
        for i=p.offset,math.min(#p.rows,p.offset+p.size-1) do table.insert(result,R.jsonDecode(R.jsonEncode(p.rows[i]))) end
        return result
    end,AdvanceToNextPageAsync=function(self)
        server();assert(not self.IsFinished,'No more pages');local p=pageStates[self];p.offset+=p.size
    end}
    local queue={};M.MemoryStoreQueue=queue
    function queue:AddAsync(value,ttl,priority)
        local d=state(self);local untilTime=expiration(ttl);local encoded=encode(value)
        priority=if priority==nil then 0 else priority;assert(finite(priority),'Priority must be a finite number')
        d.space.sequence+=1
        d.space.rows[d.space.sequence]={value=encoded,expires=untilTime,priority=priority,sequence=d.space.sequence,visibleUntil=0}
    end
    function queue:GetSizeAsync(excludeInvisible)
        local d=state(self);local now=purge(d)
        assert(excludeInvisible==nil or type(excludeInvisible)=='boolean','Expected boolean')
        local n=0;for _,row in d.space.rows do if not excludeInvisible or row.visibleUntil<=now then n+=1 end end;return n
    end
    function queue:ReadAsync(count,allOrNothing,timeout)
        local d=state(self)
        assert(type(count)=='number' and count%1==0 and count>=1 and count<=100,'Count must be an integer in 1..100')
        assert(allOrNothing==nil or type(allOrNothing)=='boolean','Expected allOrNothing boolean')
        timeout=if timeout==nil then -1 else timeout
        assert(finite(timeout) and (timeout==-1 or timeout>=0),'Wait timeout must be -1 or a nonnegative number')
        local deadline=if timeout==-1 then math.huge else R.syncTime()+timeout
        while true do
            local now=purge(d);local available={}
            for _,row in d.space.rows do if row.visibleUntil<=now then table.insert(available,row) end end
            table.sort(available,function(a,b) return if a.priority~=b.priority then a.priority>b.priority else a.sequence<b.sequence end)
            if #available>0 and (not allOrNothing or #available>=count) then
                local id=R.game:GetService('HttpService'):GenerateGUID(false)
                local ticket={expires=now+d.invisibility,items={}}
                local result={}
                for i=1,math.min(count,#available) do
                    local row=available[i];row.visibleUntil=ticket.expires;row.ticket=id
                    table.insert(ticket.items,row);table.insert(result,R.jsonDecode(row.value))
                end
                d.space.tickets[id]=ticket;return result,id
            end
            if now>=deadline then return {},nil end
            R.task.wait(math.min(2,deadline-now))
        end
    end
    function queue:RemoveAsync(id)
        local d=state(self);assert(type(id)=='string','Expected read identifier')
        local now=purge(d);local ticket=d.space.tickets[id]
        if not ticket or now>ticket.expires then return end
        for _,row in ticket.items do if row.ticket==id then d.space.rows[row.sequence]=nil end end
        d.space.tickets[id]=nil
    end
end
