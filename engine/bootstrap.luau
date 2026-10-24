return function(R)
    local function output(...)
        local args=table.pack(...)
        for i=1,args.n do args[i]=tostring(args[i]) end
        __host_print(table.unpack(args,1,args.n))
    end
    print,warn=output,output
    Instance,game,workspace=R.Instance,R.game,R.workspace
    Enum=R.Enum
    task=R.task
    for name,value in R.datatypes do getfenv()[name]=value end
    shared={}
    tick=function() return if R.config.realtime then __host_datetime(0)/1000 else os.time()+R.now end
    time=function() return R.syncTime() end
    wait=function(seconds) local elapsed=task.wait(seconds);return elapsed,R.now end
    delay,spawn=task.delay,task.spawn
    collectgarbage=function(mode) assert(mode==nil or mode=="count","Only collectgarbage('count') is supported");return gcinfo() end
    local moduleCache={server={},client={}}
    local loading={server={},client={}}
    local moduleSources=setmetatable({}, {__mode="k"})
    local environments=setmetatable({}, {__mode="k"})
    local base=getfenv()
    local function environment(scriptObject,side)
        local env={script=scriptObject}
        setmetatable(env,{__index=base})
        environments[scriptObject]=environments[scriptObject] or {}
        environments[scriptObject][side]=env
        return env
    end
    require=function(module)
        if type(module)=='number' then return R.requireAsset(module) end
        assert(typeof(module)=="Instance" and module:IsA("ModuleScript"),"require expects a ModuleScript")
        local side=R.current().side
        if moduleCache[side][module] then return moduleCache[side][module].value end
        assert(not loading[side][module],"Recursive module dependency")
        local source=moduleSources[module];assert(source,"ModuleScript has no loaded source")
        loading[side][module]=true
        local fn=source()
        setfenv(fn,environment(module,side))
        local result=table.pack(pcall(fn))
        loading[side][module]=nil
        if not result[1] then error(result[2],2) end
        assert(result.n==2,"Module code did not return exactly one value")
        moduleCache[side][module]={value=result[2]}
        return result[2]
    end
    function R.registerModule(object,factory) moduleSources[object]=factory end
    function R.run(fn,name,side,scriptObject)
        side=side or R.config.side
        scriptObject=scriptObject or R.new(if side=="client" then "LocalScript" else "Script",if side=="client" then R.player.PlayerScripts else game:GetService("ServerScriptService"),true)
        scriptObject.Name=name or "Script"
        setfenv(fn,environment(scriptObject,side))
        return R.spawnWith({side=side,name=scriptObject.Name,script=scriptObject},fn)
    end
    __engine=R
end
