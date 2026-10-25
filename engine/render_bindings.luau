-- Client render callbacks. Equal priorities use stable registration order in
-- this runtime; callers must not depend on tie order in Roblox.
return function(R)
    local methods=R.classMethods.RunService
    local bindings={}
    local sequence=0
    local function client() assert(R.current().side=='client','Render-step bindings require a client script') end
    function methods:BindToRenderStep(name,priority,callback)
        client();assert(type(name)=='string','Binding name must be a string')
        assert(type(priority)=='number' and priority%1==0 and priority>=-2147483648 and priority<=2147483647,
            'Render priority must be a signed 32-bit integer')
        assert(type(callback)=='function','Expected callback function')
        sequence+=1
        bindings[sequence]={name=name,priority=priority,callback=callback,context=R.current(),sequence=sequence}
    end
    function methods:UnbindFromRenderStep(name)
        client();assert(type(name)=='string','Binding name must be a string')
        -- The inspected native implementation permits duplicate names and
        -- removes all matching callbacks, including those at other priorities.
        for id,binding in bindings do if binding.name==name then bindings[id]=nil end end
    end
    function R.renderBindings(dt)
        local snapshot={}
        for _,binding in bindings do table.insert(snapshot,binding) end
        table.sort(snapshot,function(a,b)
            return if a.priority~=b.priority then a.priority<b.priority else a.sequence<b.sequence
        end)
        for _,binding in snapshot do
            if bindings[binding.sequence]==binding then
                local owner=binding.context.script
                local d=owner and R.instances[owner]
                if d and (d.locked or d.props.Disabled or d.props.Enabled==false) then bindings[binding.sequence]=nil
                else
                    local thread=coroutine.create(function() return R.withContext(binding.context,binding.callback,dt) end)
                    local ok,message=coroutine.resume(thread)
                    if not ok then R.report('Render binding '..binding.name..': '..tostring(message))
                    elseif coroutine.status(thread)~='dead' then
                        coroutine.close(thread)
                        R.report('Render binding '..binding.name..' callback cannot yield')
                    end
                end
            end
        end
    end
    local signal=R.signal
    function R.signal(object,name)
        if object.ClassName=='RunService' and (name=='PreRender' or name=='RenderStepped') then client() end
        return signal(object,name)
    end
end
