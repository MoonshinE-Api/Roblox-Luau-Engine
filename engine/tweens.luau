-- Semantic TweenService reconstruction. Curves use double precision, not the
-- original float32 pipeline. Engine job ordering and every native type are pending.
return function(R)
    local playback=R.Enum.PlaybackState
    local active,states,owners={},setmetatable({}, {__mode="k"}),setmetatable({}, {__mode="k"})
    local function bounceOut(x)
        local n,d=7.5625,2.75
        if x<1/d then return n*x*x
        elseif x<2/d then x-=1.5/d;return n*x*x+0.75
        elseif x<2.5/d then x-=2.25/d;return n*x*x+0.9375
        else x-=2.625/d;return n*x*x+0.984375 end
    end
    local function easeIn(x,style)
        if x==0 or x==1 then return x end
        local name=style.Name
        if name=="Linear" then return x
        elseif name=="Sine" then return 1-math.cos(x*math.pi/2)
        elseif name=="Quad" then return x*x
        elseif name=="Cubic" then return x^3
        elseif name=="Quart" then return x^4
        elseif name=="Quint" then return x^5
        elseif name=="Exponential" then return 2^(10*(x-1))
        elseif name=="Circular" then return 1-math.sqrt(1-x*x)
        elseif name=="Back" then return (1.70158+1)*x^3-1.70158*x*x
        elseif name=="Bounce" then return 1-bounceOut(1-x)
        elseif name=="Elastic" then return -2^(10*x-10)*math.sin((10*x-10.75)*(2*math.pi/3)) end
        error("Unsupported easing style",2)
    end
    local service={}
    function service:GetValue(alpha,style,direction)
        assert(type(alpha)=="number" and alpha==alpha,"Expected number alpha")
        assert(typeof(style)=="EnumItem" and style.EnumType==R.Enum.EasingStyle,"Expected Enum.EasingStyle")
        assert(typeof(direction)=="EnumItem" and direction.EnumType==R.Enum.EasingDirection,"Expected Enum.EasingDirection")
        alpha=math.clamp(alpha,0,1)
        if direction==R.Enum.EasingDirection.In then return easeIn(alpha,style)
        elseif direction==R.Enum.EasingDirection.Out then return 1-easeIn(1-alpha,style)
        elseif alpha<0.5 then return easeIn(alpha*2,style)/2
        else return 1-easeIn((1-alpha)*2,style)/2 end
    end
    local supported={number=true,Vector2=true,Vector3=true,CFrame=true,Color3=true,UDim=true,UDim2=true,Rect=true}
    local function interpolate(a,b,t)
        local kind=typeof(a)
        if t==0 then return a elseif t==1 then return b end
        if kind=="number" then return a+(b-a)*t
        elseif kind=="UDim" then return R.datatypes.UDim.new(a.Scale+(b.Scale-a.Scale)*t,a.Offset+(b.Offset-a.Offset)*t)
        elseif kind=="Rect" then return R.datatypes.Rect.new(a.Min:Lerp(b.Min,t),a.Max:Lerp(b.Max,t))
        else return a:Lerp(b,t) end
    end
    local function state(object) local data=states[object];assert(data,"Tween was not created by TweenService");return data end
    local function release(object,data)
        active[object]=nil
        local owned=owners[data.target]
        if owned then for key in data.goals do if owned[key]==object then owned[key]=nil end end end
    end
    local function status(object,value)
        local data=state(object)
        if data.playback~=value then
            data.playback=value;R.changed(object,"PlaybackState")
            if value==playback.Completed or value==playback.Cancelled then R.fire(object,"Completed",value) end
        end
    end
    local methods={}
    function methods:Cancel()
        local data=state(self)
        if data.playback==playback.Begin or data.playback==playback.Cancelled then return end
        release(self,data);data.elapsed=0;data.cycle=0
        status(self,playback.Cancelled)
    end
    function methods:Pause()
        local data=state(self)
        if data.playback==playback.Playing then active[self]=nil;status(self,playback.Paused) end
    end
    function methods:Play()
        local data=state(self)
        if data.playback==playback.Playing or data.playback==playback.Delayed then return end
        assert(not R.instances[self].locked and not R.instances[data.target].locked,"Cannot play a destroyed tween/target")
        owners[data.target]=owners[data.target] or {}
        local owned=owners[data.target]
        for key in data.goals do
            local other=owned[key]
            if other and other~=self then methods.Cancel(other) end
            owned[key]=self
        end
        if data.playback~=playback.Paused then
            data.elapsed,data.cycle,data.start=0,0,{}
            for key in data.goals do data.start[key]=data.target[key] end
        end
        active[self]=data
        status(self,if data.elapsed<data.info.DelayTime then playback.Delayed else playback.Playing)
    end
    function service:Create(target,info,goals)
        assert(typeof(target)=="Instance" and R.instances[target],"Expected Instance")
        assert(typeof(info)=="TweenInfo","Expected TweenInfo")
        assert(type(goals)=="table","Expected property dictionary")
        local copy={}
        for key,value in goals do
            assert(type(key)=="string","Property name must be a string")
            local current=target[key]
            assert(supported[typeof(current)] and typeof(current)==typeof(value),"Property cannot be tweened or has the wrong type: "..key)
            local writable=R.instances[target].propertyTypes[key]
            local class,seen=target.ClassName,{}
            while not writable and class and not seen[class] do
                seen[class]=true;writable=R.classSetters[class] and R.classSetters[class][key];class=R.classes[class]
            end
            assert(writable,"Property is read only: "..key)
            copy[key]=value
        end
        local object=R.new("Tween",nil,true)
        states[object]={target=target,info=info,goals=copy,playback=playback.Begin,elapsed=0,cycle=0,start={}}
        return object
    end
    R.classMethods.TweenService=service
    R.classMethods.TweenBase=methods
    R.classEvents.TweenBase={Completed=true}
    R.classGetters.TweenBase={PlaybackState=function(self) return state(self).playback end}
    R.classGetters.Tween={Instance=function(self) return state(self).target end,TweenInfo=function(self) return state(self).info end}
    R.noncreatable.Tween,R.noncreatable.TweenBase=true,true
    local function apply(object,data,alpha)
        local eased=service:GetValue(alpha,data.info.EasingStyle,data.info.EasingDirection)
        for key,goal in data.goals do
            if active[object]~=data then return end
            data.target[key]=interpolate(data.start[key],goal,eased)
        end
    end
    local previousStep=R.step
    R.step=function(dt)
        for object,data in table.clone(active) do
            if active[object]==data then
                if R.instances[object].locked or R.instances[data.target].locked then
                    release(object,data)
                else
                    data.elapsed+=dt
                    local info=data.info
                    local span=info.Time*(if info.Reverses then 2 else 1)
                    local total=info.DelayTime+span
                    local completed=false
                    if total>0 then
                        local cycles=math.floor(data.elapsed/total+1e-9)
                        if info.RepeatCount>=0 and data.cycle+cycles>info.RepeatCount then completed=true
                        elseif cycles>0 then
                            data.elapsed=if cycles==math.huge then data.elapsed%total else math.max(0,data.elapsed-cycles*total)
                            data.cycle+=cycles
                        end
                    elseif info.RepeatCount>=0 then completed=true end
                    if completed then
                        apply(object,data,if info.Reverses then 0 else 1)
                        if active[object]==data then release(object,data);status(object,playback.Completed) end
                    elseif data.elapsed<info.DelayTime then
                        status(object,playback.Delayed)
                    else
                        status(object,playback.Playing)
                        local progress=if info.Time==0 then 1 else (data.elapsed-info.DelayTime)/info.Time
                        if info.Reverses and progress>1 then progress=2-progress end
                        apply(object,data,math.clamp(progress,0,1))
                    end
                end
            end
        end
        previousStep(dt)
    end
end
