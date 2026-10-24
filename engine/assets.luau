-- Public asset transport and scripting-tree materialization. This does not
-- reproduce Studio authentication, cloud ownership checks or capabilities.
return function(R)
    local required={}
    local requiring={}
    local function assetId(id)
        assert(type(id)=='number' and id>0 and id<=9007199254740991 and id==math.floor(id),'Asset ID must be a positive exact integer')
        assert(R.current().side=='server','Asset loading by ID requires server context')
        return id
    end
    local function factory(encoded,label)
        local bytes=R.jsonDecode('{"m":null,"t":"buffer","base64":"'..encoded..'"}')
        local loaded={}
        return function()
            local side=R.current().side
            if not loaded[side] then
                local value,status=__host_loadbytecode(bytes,'@'..label)
                if status~=0 then error('Asset bytecode load failed: '..tostring(value),2) end
                loaded[side]=value
            end
            return loaded[side]
        end
    end
    local function load(id,version)
        assetId(id)
        local response=R.hostRequest({Kind='Asset',AssetId=id,AssetVersion=version or false,Timeout=30})
        local tree=R.jsonDecode(response.Body)
        local roots,references,records={},{},{}
        local function create(record,parent)
            assert(R.knownClasses[record.class],'Unknown asset class '..record.class)
            local object=R.new(record.class,parent,true);object.Name=record.name
            references[record.id]=object;table.insert(records,{object,record})
            for key,value in record.properties do
                if key=='RunContext' then value=R.Enum.RunContext:GetEnumItems()[value+1] end
                object[key]=value
            end
            for _,tag in record.tags do object:AddTag(tag) end
            R.applyAttributes(object,record.attributes)
            -- Loaded Script/LocalScript instances remain dormant. Automatic
            -- activation and real Sandboxed/Capabilities semantics are pending.
            for _,child in record.children do create(child,object) end
            return object
        end
        for _,record in tree.items do table.insert(roots,create(record,nil)) end
        for _,pair in records do R.applyModelProperties(pair[1],pair[2].typed_properties,references) end
        for _,pair in records do
            if pair[2].class=='ModuleScript' then R.registerModule(pair[1],factory(pair[2].bytecode,pair[2].label)) end
        end
        return roots
    end
    local function wrapped(id,version)
        local model=R.new('Model',nil,true)
        local ok,roots=pcall(load,id,version)
        if not ok then model:Destroy();error(roots,2) end
        for _,object in roots do object.Parent=model end
        return model
    end
    R.classMethods.InsertService={LoadAsset=function(_,id) return wrapped(id,false) end,
        LoadAssetVersion=function(_,id) return wrapped(id,true) end}
    R.classMethods.InsertService.loadAsset=R.classMethods.InsertService.LoadAsset
    R.classMethods.AssetService={LoadAssetAsync=function(_,id) return wrapped(id,false) end}
    function R.classMethods.DataModel:GetObjects(content)
        assert(type(content)=='string','GetObjects expects an rbxassetid:// URL')
        local id=string.match(content,'^rbxassetid://(%d+)$')
        assert(id,'GetObjects currently requires rbxassetid://<id>')
        return load(tonumber(id),false)
    end
    function R.requireAsset(id)
        assetId(id)
        if required[id] then return required[id].value end
        if requiring[id] then
            local request=requiring[id]
            assert(request.thread~=coroutine.running(),'Recursive numeric module dependency')
            local ok,value=request.signal:Wait()
            if not ok then error(value,2) end
            return value
        end
        local request={thread=coroutine.running(),signal=R.newSignal()};requiring[id]=request
        local ok,value=pcall(function()
            local model=wrapped(id,false)
            local module=model:FindFirstChild('MainModule')
            if not module or not module:IsA('ModuleScript') then model:Destroy();error('Asset '..id..' has no top-level MainModule ModuleScript',2) end
            return require(module)
        end)
        if ok then required[id]={value=value} end
        requiring[id]=nil;R.fireSignal(request.signal,ok,value)
        if not ok then error(value,2) end
        return value
    end
end
