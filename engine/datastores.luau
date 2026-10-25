-- Local SQLite-backed compatibility layer. No cloud connection, quota model,
-- cloud version-retention policy, or distributed Roblox service is implied.
return function(R)
    local M,G=R.classMethods,R.classGetters
    R.classes.DataStore='GlobalDataStore'
    R.classes.GlobalDataStore='Instance'
    local states,info,pages=setmetatable({}, {__mode='k'}),setmetatable({}, {__mode='k'}),setmetatable({}, {__mode='k'})
    local stores,cache={},{}
    local initialize=R.initializeProperties
    function R.initializeProperties(object,d)
        initialize(object,d)
        if d.class=='DataStoreOptions' then d.propertyTypes.AllScopes='boolean';d.props.AllScopes=false end
        if d.class=='DataStoreGetOptions' then d.propertyTypes.UseCache='boolean';d.props.UseCache=true end
        if d.class=='DataStoreSetOptions' then d.props.__dataStoreMetadata='{}' end
    end
    for _,class in {'GlobalDataStore','DataStore','OrderedDataStore','DataStoreKeyInfo','DataStoreKey',
        'Pages','DataStorePages','DataStoreKeyPages','DataStoreVersionPages'} do R.noncreatable[class]=true end
    local function server() assert(R.current().side=='server','Data stores are only accessible from server scripts') end
    local function name(value,label)
        assert(type(value)=='string' and #value>0 and #value<=50 and not string.find(value,'\0',1,true) and utf8.len(value),
            label..' must contain 1..50 UTF-8 bytes')
        return value
    end
    local function validate(value,seen,depth)
        local kind=type(value)
        assert(depth<=64,'Data store value exceeds nesting limit 64')
        if kind=='number' then assert(value==value and math.abs(value)<math.huge,'Data store numbers must be finite')
        elseif kind=='string' then assert(utf8.len(value),'Data store strings must be valid UTF-8')
        elseif kind=='table' then
            assert(not seen[value],'Cyclic data store table');seen[value]=true
            local count,maximum,strings=0,0,0
            for key,item in next,value do
                if type(key)=='number' then
                    assert(key>=1 and key%1==0,'Invalid data store array index');maximum=math.max(maximum,key)
                else assert(type(key)=='string' and utf8.len(key),'Data store dictionary keys must be UTF-8 strings');strings+=1 end
                count+=1;assert(count<=100000,'Data store table exceeds local entry limit')
                validate(item,seen,depth+1)
            end
            assert(strings==count or strings==0 and maximum==count,'Mixed or sparse data store tables are unsupported')
            seen[value]=nil
        else assert(kind=='boolean','Unsupported data store value type '..kind) end
    end
    local function serialized(value)
        validate(value,{},0)
        local encoded=R.jsonEncode(value);assert(#encoded<=4*1024*1024,'Data store value exceeds 4 MiB')
        return encoded
    end
    R.serializeStoreValue=serialized
    M.DataStoreSetOptions={GetMetadata=function(self) return R.jsonDecode(R.instances[self].props.__dataStoreMetadata) end,
        SetMetadata=function(self,value)
            assert(type(value)=='table','Metadata must be a dictionary')
            for key in next,value do assert(type(key)=='string','Metadata must be a dictionary') end
            R.instances[self].props.__dataStoreMetadata=serialized(value)
        end}
    local function keyInfo(record,ordered)
        if not record or not record.Exists or ordered then return nil end
        local object=R.new('DataStoreKeyInfo',nil,true);object.Archivable=false
        info[object]={Version=record.Version,CreatedTime=record.CreatedTime,UpdatedTime=record.UpdatedTime,
            UserIds=record.UserIds,Metadata=record.Metadata}
        return object
    end
    local function copy(value) return R.jsonDecode(R.jsonEncode(value)) end
    G.DataStoreKeyInfo={CreatedTime=function(self) return info[self].CreatedTime end,
        UpdatedTime=function(self) return info[self].UpdatedTime end,Version=function(self) return info[self].Version end}
    M.DataStoreKeyInfo={GetMetadata=function(self) return copy(info[self].Metadata) end,
        GetUserIds=function(self) return copy(info[self].UserIds) end}
    local function state(object) return assert(states[object],'Data store must be obtained from DataStoreService') end
    local function identity(object,key)
        local d=state(object);local scope=d.scope
        if d.allScopes then
            assert(type(key)=='string','Key must be a string')
            scope,key=string.match(key,'^([^/]+)/(.+)$')
            name(scope,'Scope')
        end
        name(key,'Key')
        return d,scope,key,tostring(d.ordered)..'\0'..d.name..'\0'..scope..'\0'..key
    end
    local function request(d,scope,key,operation,data)
        server()
        local response=R.hostRequest({Kind='DataStore',Operation=operation,Ordered=d.ordered,
            Name=d.name,Scope=scope,Key=key,Timeout=30},R.jsonEncode(data or {}))
        return R.jsonDecode(response.Body),response.Body
    end
    local function metadata(userIds,options)
        if userIds~=nil then
            assert(type(userIds)=='table','Expected UserIds array')
            for i,id in userIds do assert(type(i)=='number' and i>=1 and i<=#userIds and type(id)=='number' and id%1==0 and math.abs(id)<=9007199254740991,'Invalid UserIds array') end
        end
        if options~=nil then assert(R.instances[options] and options:IsA('DataStoreSetOptions'),'Expected DataStoreSetOptions') end
        return userIds or {},options and options:GetMetadata() or {}
    end
    local function remember(cacheKey,record)
        cache[cacheKey]={at=R.syncTime(),encoded=R.jsonEncode(record)}
    end
    local step=R.step
    function R.step(dt)
        step(dt)
        local now=R.syncTime()
        for key,item in cache do if now-item.at>=4 then cache[key]=nil end end
    end
    M.GlobalDataStore={}
    function M.GlobalDataStore:GetAsync(key,options)
        server();local d,scope,entry,cacheKey=identity(self,key)
        assert(options==nil or R.instances[options] and options:IsA('DataStoreGetOptions'),'Expected DataStoreGetOptions')
        local record
        local cached=cache[cacheKey]
        if (not options or options.UseCache) and cached and R.syncTime()-cached.at<4 then record=R.jsonDecode(cached.encoded)
        else record=request(d,scope,entry,'get');remember(cacheKey,record) end
        return record.Value,keyInfo(record,d.ordered)
    end
    function M.GlobalDataStore:SetAsync(key,value,userIds,options)
        local d,scope,entry,cacheKey=identity(self,key)
        serialized(value);local users,meta=metadata(userIds,options)
        local result=request(d,scope,entry,'set',{Value=value,UserIds=users,Metadata=meta})
        remember(cacheKey,result.Record)
        return if d.ordered then nil else result.Record.Version
    end
    function M.GlobalDataStore:IncrementAsync(key,delta,userIds,options)
        delta=if delta==nil then 1 else delta
        assert(type(delta)=='number' and delta%1==0 and math.abs(delta)<=9007199254740991,'Increment must be an exact integer')
        local d,scope,entry,cacheKey=identity(self,key);local users,meta=metadata(userIds,options)
        local result=request(d,scope,entry,'increment',{Delta=delta,UserIds=users,Metadata=meta})
        remember(cacheKey,result.Record);return result.Record.Value
    end
    function M.GlobalDataStore:RemoveAsync(key)
        local d,scope,entry,cacheKey=identity(self,key)
        local result=request(d,scope,entry,'remove');remember(cacheKey,result.Record)
        return result.Previous.Value,keyInfo(result.Previous,d.ordered)
    end
    local function transform(callback,value,key)
        local context=R.current()
        local thread=coroutine.create(function() return R.withContext(context,callback,value,key) end)
        local result=table.pack(coroutine.resume(thread))
        if not result[1] then error(result[2],3) end
        if coroutine.status(thread)~='dead' then
            if coroutine.close then coroutine.close(thread) end
            error('UpdateAsync callback cannot yield',3)
        end
        return table.unpack(result,2,result.n)
    end
    R.invokeStoreTransform=transform
    function M.GlobalDataStore:UpdateAsync(key,callback)
        assert(type(callback)=='function','UpdateAsync requires a function')
        local d,scope,entry,cacheKey=identity(self,key)
        for _=1,128 do
            local previous=request(d,scope,entry,'get')
            local value,users,meta=transform(callback,previous.Value,keyInfo(previous,d.ordered))
            if value==nil then return nil end
            serialized(value)
            local options=R.new('DataStoreSetOptions',nil,true)
            options:SetMetadata(meta or {})
            local ids,attributes=metadata(users,options)
            local result=request(d,scope,entry,'cas',{ExpectedVersion=previous.Version,Value=value,UserIds=ids,Metadata=attributes})
            if not result.Conflict then remember(cacheKey,result.Record);return result.Record.Value,keyInfo(result.Record,d.ordered) end
        end
        error('UpdateAsync exceeded local contention retry limit 128',2)
    end
    G.GlobalDataStore={Scope=function(self) return state(self).scope end}
    M.DataStore={}
    function M.DataStore:GetVersionAsync(key,version)
        local d,scope,entry=identity(self,key);assert(not d.ordered,'Ordered stores do not support versions')
        assert(type(version)=='string','Expected version string')
        local record=request(d,scope,entry,'version',{Version=version})
        return record.Value,keyInfo(record,false)
    end
    function M.DataStore:GetOptions()
        local result=R.new('DataStoreOptions',nil,true);result.AllScopes=state(self).allScopes;return result
    end
    local function pageSize(value)
        value=if value==nil then 50 else value;assert(type(value)=='number' and value%1==0 and value>=1 and value<=100,'Page size must be an integer in 1..100');return value
    end
    local function pageObject(class,items,size,keyObjects,cursor)
        local object=R.new(class,nil,true);object.Archivable=false
        local offset=cursor and tonumber(cursor) or 1
        assert(offset and offset>=1 and offset%1==0,'Invalid local page cursor')
        pages[object]={items=items,size=size,offset=offset,keyObjects=keyObjects};return object
    end
    G.Pages={IsFinished=function(self) local d=assert(pages[self]);return d.offset+d.size>#d.items end}
    G.DataStoreKeyPages={Cursor=function(self) local d=assert(pages[self]);return if self.IsFinished then '' else tostring(d.offset+d.size) end}
    M.Pages={GetCurrentPage=function(self)
        local d=assert(pages[self]);local result={}
        for i=d.offset,math.min(#d.items,d.offset+d.size-1) do
            if d.keyObjects then
                local key=R.new('DataStoreKey',nil,true);key.Archivable=false;info[key]=d.items[i];table.insert(result,key)
            else table.insert(result,copy(d.items[i])) end
        end
        return result
    end,AdvanceToNextPageAsync=function(self)
        server();assert(not self.IsFinished,'No more pages');local d=pages[self];d.offset+=d.size
    end}
    G.DataStoreKey={KeyName=function(self) return info[self].KeyName end}
    function M.DataStore:ListKeysAsync(prefix,size,cursor,excludeDeleted)
        local d=state(self);assert(not d.ordered,'Ordered key listing is not implemented')
        prefix=prefix or '';assert(type(prefix)=='string','Expected prefix string')
        assert(excludeDeleted==nil or type(excludeDeleted)=='boolean','Expected excludeDeleted boolean')
        assert(cursor==nil or type(cursor)=='string','Expected cursor string')
        local result=request(d,if d.allScopes then '*' else d.scope,'_','keys',{Prefix=prefix,ExcludeDeleted=excludeDeleted or false})
        return pageObject('DataStoreKeyPages',result.Items,pageSize(size),true,if cursor=='' then nil else cursor)
    end
    M.OrderedDataStore={GetSortedAsync=function(self,ascending,size,minimum,maximum)
        assert(type(ascending)=='boolean','Expected ascending boolean')
        for _,v in {minimum,maximum} do assert(type(v)=='number' and v%1==0 and math.abs(v)<=9007199254740991,'Invalid ordered value bound') end
        assert(minimum==nil or maximum==nil or minimum<=maximum,'Minimum exceeds maximum')
        local d=state(self);local result=request(d,d.scope,'_','sorted',{Ascending=ascending,Min=minimum,Max=maximum})
        return pageObject('DataStorePages',result.Items,pageSize(size),false)
    end}
    local function get(nameValue,scope,options,ordered)
        server();name(nameValue,'Name');scope=if scope==nil then 'global' else scope;name(scope,'Scope')
        assert(options==nil or R.instances[options] and options:IsA('DataStoreOptions'),'Expected DataStoreOptions')
        local all=options and options.AllScopes or false
        local id=tostring(ordered)..'\0'..nameValue..'\0'..scope..'\0'..tostring(all)
        if stores[id] then return stores[id] end
        local object=R.new(if ordered then 'OrderedDataStore' else 'DataStore',nil,true)
        object.Name=nameValue;object.Archivable=false
        states[object]={name=nameValue,scope=scope,ordered=ordered,allScopes=all};stores[id]=object
        return object
    end
    M.DataStoreService={GetDataStore=function(_,n,s,o) return get(n,s,o,false) end,
        GetGlobalDataStore=function() return get('__global','u',nil,false) end,
        GetOrderedDataStore=function(_,n,s) return get(n,s,nil,true) end}
end
