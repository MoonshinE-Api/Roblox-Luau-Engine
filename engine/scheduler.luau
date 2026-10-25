return function(R)
    R.now,R.errors=0,{}
    local contexts=setmetatable({}, {__mode="k"})
    local cancelled=setmetatable({}, {__mode="k"})
    local active,queue={},{}
    local sequence=0
    local clockOrigin
    function R.syncTime()
        if R.config.realtime then
            clockOrigin=clockOrigin or os.clock()-R.now
            R.now=math.max(R.now,os.clock()-clockOrigin)
        end
        return R.now
    end
    local fallback={side=R.config.side or "server",name="bootstrap"}
    function R.current() return contexts[coroutine.running()] or fallback end
    function R.withContext(context,callback,...)
        local thread=coroutine.running()
        local previous=contexts[thread]
        contexts[thread]=context
        local result=table.pack(pcall(callback,...))
        contexts[thread]=previous
        if not result[1] then error(result[2],2) end
        return table.unpack(result,2,result.n)
    end
    function R.report(message)
        table.insert(R.errors,tostring(message))
        __host_print("ERROR: "..tostring(message))
    end
    local function earlier(a,b) return a.time<b.time or a.time==b.time and a.sequence<b.sequence end
    function R.enqueue(thread,args,at,context,ticket,sleepStarted)
        sequence+=1
        local item={thread=thread,args=args,time=at,context=context,sequence=sequence,ticket=ticket,sleepStarted=sleepStarted}
        local i=#queue+1
        while i>1 do local parent=math.floor(i/2);if not earlier(item,queue[parent]) then break end;queue[i]=queue[parent];i=parent end
        queue[i]=item;active[thread]=true
    end
    local function pop()
        local first,last=queue[1],table.remove(queue)
        if #queue>0 then
            local i=1
            while i*2<=#queue do
                local child=i*2
                if child<#queue and earlier(queue[child+1],queue[child]) then child+=1 end
                if not earlier(queue[child],last) then break end
                queue[i]=queue[child];i=child
            end
            queue[i]=last
        end
        return first
    end
    function R.resume(thread,args,context)
        if cancelled[thread] or coroutine.status(thread)=="dead" then active[thread]=nil;return end
        R.syncTime();contexts[thread]=context;active[thread]=true
        local result=table.pack(coroutine.resume(thread,table.unpack(args,1,args.n)))
        R.syncTime()
        local suspendedContext=contexts[thread] or context
        if not result[1] then
            active[thread]=nil
            R.report(debug.traceback(thread,tostring(result[2])))
        elseif coroutine.status(thread)=="dead" then active[thread]=nil
        elseif type(result[2])=="table" and result[2].kind=="sleep" then
            local duration=math.max(result[2].duration,1/60)
            R.enqueue(thread,table.pack(duration),R.now+duration,suspendedContext,nil,result[2].started)
        elseif type(result[2])=="table" and result[2].kind=="signal" then
            local request=result[2]
            local waiter={thread=thread,context=suspendedContext,done=false}
            table.insert(request.signal.waiters,waiter)
            if request.timeout then R.enqueue(thread,table.pack(nil),R.now+request.timeout,suspendedContext,waiter) end
        end
    end
    function R.spawnWith(context,fn,...)
        local thread=if type(fn)=="thread" then fn else coroutine.create(fn)
        R.resume(thread,table.pack(...),context);return thread
    end
    local tasklib={}
    function tasklib.spawn(fn,...) return R.spawnWith(R.current(),fn,...) end
    function tasklib.defer(fn,...)
        local thread=if type(fn)=="thread" then fn else coroutine.create(fn)
        R.enqueue(thread,table.pack(...),R.syncTime(),R.current());return thread
    end
    function tasklib.delay(seconds,fn,...)
        assert(type(seconds)=="number" and seconds==seconds and seconds<math.huge,"Invalid delay")
        local thread=if type(fn)=="thread" then fn else coroutine.create(fn)
        R.enqueue(thread,table.pack(...),R.syncTime()+math.max(seconds,0),R.current());return thread
    end
    function tasklib.wait(seconds)
        seconds=seconds or 0
        assert(type(seconds)=="number" and seconds==seconds and seconds<math.huge,"Invalid wait duration")
        return coroutine.yield({kind="sleep",duration=math.max(seconds,0),started=R.syncTime()})
    end
    function tasklib.cancel(thread)
        cancelled[thread]=true;active[thread]=nil
        if coroutine.status(thread)=="suspended" then coroutine.close(thread) end
    end
    R.task=table.freeze(tasklib)
    R.signals=setmetatable({}, {__mode="k"})
    function R.newSignal()
        local data={connections={},waiters={}}
        local methods={}
        function methods:Connect(callback)
            assert(type(callback)=="function","Connect expects a function")
            local state={connected=true,callback=callback,context=R.current()}
            local connection=R.makeValue("RBXScriptConnection",state,function(_,key)
                if key=="Connected" then return state.connected end
                if key=="Disconnect" or key=="disconnect" then return function() state.connected=false end end
                error(key.." is not a valid member of RBXScriptConnection",2)
            end,{__tostring=function() return "Connection" end})
            state.object=connection;table.insert(data.connections,state)
            return connection
        end
        methods.connect=methods.Connect
        function methods:Once(callback)
            local connection
            connection=self:Connect(function(...) connection:Disconnect();callback(...) end)
            return connection
        end
        function methods:Wait() return coroutine.yield({kind="signal",signal=data}) end
        methods.wait=methods.Wait
        local signal=R.makeValue("RBXScriptSignal",data,function(_,key)
            if methods[key] then return methods[key] end
            error(key.." is not a valid member of RBXScriptSignal",2)
        end,{__tostring=function() return "Signal" end})
        R.signals[signal]=data
        return signal
    end
    function R.fireSignal(signal,...)
        R.syncTime()
        local data=R.signals[signal];local args=table.pack(...)
        local waiters=data.waiters;data.waiters={}
        for _,waiter in waiters do
            if not waiter.done then waiter.done=true;R.enqueue(waiter.thread,args,R.now,waiter.context) end
        end
        for _,state in table.clone(data.connections) do
            if state.connected then R.spawnWith(state.context,state.callback,table.unpack(args,1,args.n)) end
        end
    end
    function R.disconnectSignal(signal)
        for _,state in R.signals[signal].connections do state.connected=false end
    end
    function R.pendingCount()
        local count=0
        for thread in active do if not cancelled[thread] and coroutine.status(thread)~='dead' then count+=1 end end
        return count
    end
    function R.drain(options)
        options=options or {}
        R.syncTime()
        local frame=R.now+1/60
        local lastFrame=R.now
        local limit=options.limit or (if R.config.forever then math.huge else R.config.duration or 1)
        local steps=0
        local early=false
        while true do
            if (options.done and options.done()) or (options.wallDeadline and os.clock()>=options.wallDeadline)
                or (not options.ignoreHostStop and R.stopRequested and R.stopRequested()) then early=true;break end
            if R.pollExternal then R.pollExternal() end
            local nextTime=if queue[1] then queue[1].time else math.huge
            if not R.config.realtime and R.externalPending and R.externalPending() and nextTime>R.now then
                -- External completions are not timestamped in virtual time.
                -- Process ready jobs, then await I/O before advancing to future
                -- timers. Otherwise a request consumes the whole simulated
                -- duration before a subsequent task.wait can ever resume.
                R.waitExternal(20);continue
            end
            local at=math.min(nextTime,frame)
            if at>limit then break end
            if R.config.realtime then
                local remaining=at-R.syncTime()
                while remaining>0 do __host_sleep(remaining);remaining=at-R.syncTime() end
            else R.now=at end
            steps+=1
            -- Perpetual mode is wall-paced and must not expire after a fixed
            -- lifetime event count. Finite virtual runs retain their guard.
            if not R.config.forever and steps>200000 then R.report("Scheduler operation limit exceeded");break end
            -- A task waking on a frame boundary observes that frame's update.
            -- In particular PrimaryPart cleanup / tween updates precede wakeup.
            if nextTime<frame then
                local item=pop()
                if not item.ticket or not item.ticket.done then
                    if item.ticket then item.ticket.done=true end
                    if item.sleepStarted then item.args=table.pack(R.now-item.sleepStarted) end
                    R.resume(item.thread,item.args,item.context)
                end
            else
                if R.step then R.step(if R.config.realtime then R.now-lastFrame else 1/60) end
                lastFrame=R.now
                frame=if R.config.realtime then R.now+1/60 else frame+1/60
            end
        end
        if not early and R.config.realtime then
            local remaining=limit-R.syncTime()
            while remaining>0 do __host_sleep(remaining);remaining=limit-R.syncTime() end
        elseif not early then R.now=limit end
        return {errors=#R.errors,pending=R.pendingCount()}
    end
end
