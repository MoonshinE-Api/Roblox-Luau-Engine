-- Headless server shutdown. Graceful termination requires yielding Luau;
-- the supervising process enforces the real-time interrupt/kill boundary.
return function(R)
    local handlers={}
    function R.classMethods.DataModel:BindToClose(callback)
        assert(not R.closing,'BindToClose failed because the model is already being closed.')
        assert(R.current().side=='server','BindToClose can only be called on the server.')
        assert(type(callback)=='function','BindToClose expects a function')
        table.insert(handlers,{callback=callback,context=R.current()})
    end
    function R.stopRequested() return __host_http(5,0)==1 end
    function R.shutdown()
        if R.closing then return end
        R.closing=true
        local limit,wallDeadline=R.syncTime()+30,os.clock()+30
        local remaining=0
        for _,handler in handlers do
            local owner=handler.context.script
            if owner and R.instances[owner].locked then
                __host_print('WARNING: Script with BindToClose callback was destroyed; callback cannot be called!')
            else
                remaining+=1
                R.spawnWith(handler.context,function()
                    local ok,message=pcall(handler.callback,R.Enum.CloseReason.DeveloperShutdown)
                    if not ok then R.report(message) end
                    remaining-=1
                end)
            end
        end
        if remaining>0 then
            R.drain({limit=limit,wallDeadline=wallDeadline,ignoreHostStop=true,done=function() return remaining==0 end})
        end
        if remaining>0 then __host_print('WARNING: Server shutdown callback budget exceeded; unfinished callbacks: '..remaining) end
    end
end
