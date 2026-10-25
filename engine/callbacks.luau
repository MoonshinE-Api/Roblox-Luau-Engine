-- Yielding function callbacks. The host still shares one object tree between
-- contexts; this module does not implement network serialization/replication.
return function(R)
    local M,G,S=R.classMethods,R.classGetters,R.classSetters
    local slots=setmetatable({}, {__mode='k'})
    local function state(self,key)
        if key=='OnInvoke' then key=key..':'..R.current().side end
        local object=slots[self]
        if not object then object={};slots[self]=object end
        if not object[key] then object[key]={pending={},head=1,tail=0} end
        return object[key]
    end
    local function dispatch(callback,request)
        -- A callee has its own coroutine and retains the context in which its
        -- callback was assigned, even when the invoking thread is cancelled.
        R.spawnWith(callback.context,function()
            request.result=table.pack(pcall(callback.fn,table.unpack(request.args,1,request.args.n)))
            R.fireSignal(request.reply)
        end)
    end
    local function install(class,key,side)
        G[class]=G[class] or {};S[class]=S[class] or {}
        G[class][key]=function()
            error(key..' is a callback member of '..class..'; you can only set the callback value, get is not available',2)
        end
        S[class][key]=function(self,fn)
            assert(not side or R.current().side==side,key..' can only be implemented on the '..(side or 'current context'))
            assert(fn==nil or type(fn)=='function','Expected callback function')
            local slot=state(self,key)
            slot.callback=if fn then {fn=fn,context=R.current()} else nil
            -- Native BindableFunction processes its invocation queue when a
            -- callback is assigned. Reentrant assignments affect later calls.
            while slot.callback and slot.head<=slot.tail do
                local request=slot.pending[slot.head]
                slot.pending[slot.head]=nil;slot.head+=1
                dispatch(slot.callback,request)
            end
            if slot.head>slot.tail then slot.head=1;slot.tail=0 end
        end
    end
    install('BindableFunction','OnInvoke')
    install('RemoteFunction','OnServerInvoke','server')
    install('RemoteFunction','OnClientInvoke','client')
    local function invoke(self,key,...)
        local slot=state(self,key)
        local request={args=table.pack(...),reply=R.newSignal()}
        if slot.callback then dispatch(slot.callback,request)
        else slot.tail+=1;slot.pending[slot.tail]=request end
        if not request.result then request.reply:Wait() end
        local result=request.result
        if not result[1] then error(result[2],2) end
        return table.unpack(result,2,result.n)
    end
    M.BindableFunction={Invoke=function(self,...) return invoke(self,'OnInvoke',...) end}
    M.RemoteFunction={
        InvokeServer=function(self,...)
            assert(R.current().side=='client','InvokeServer requires client context')
            return invoke(self,'OnServerInvoke',R.player,...)
        end,
        InvokeClient=function(self,player,...)
            assert(R.current().side=='server','InvokeClient requires server context')
            assert(R.player and player==R.player and player.Parent==R.game:GetService('Players'),'Unknown player')
            return invoke(self,'OnClientInvoke',...)
        end,
    }
end
