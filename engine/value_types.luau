return function(R)
    local make=R.makeValue
    local scratch=buffer.create(4)
    function R.float32(value) buffer.writef32(scratch,0,value);return buffer.readf32(scratch,0) end
    local function record(name,fields,extra)
        return make(name,fields,function(self,key,data)
            if data[key]~=nil then return data[key] end
            if extra and extra[key] then return extra[key] end
            error(key.." is not a valid member of "..name,2)
        end,{__tostring=function() return name end,
            __eq=function(a,b)
                if typeof(a)~=name or typeof(b)~=name then return false end
                for key,value in R.values[a] do if R.values[b][key]~=value then return false end end
                return true
            end})
    end
    R.makeRecord=record
    local UDim,UDim2={},{}
    local function wrapOffset(value)
        value%=4294967296
        return if value>=2147483648 then value-4294967296 else value
    end
    function R.toInt32(value)
        value=math.modf(tonumber(value) or 0)
        return if value~=value or value < -2147483648 or value>2147483647 then -2147483648 else value
    end
    function UDim.new(scale,offset)
        scale,offset=tonumber(scale) or 0,R.toInt32(offset)
        return make("UDim",{Scale=scale,Offset=offset},function(_,key,d)
            if d[key]~=nil then return d[key] end;error(key.." is not a valid member of UDim",2)
        end,{
            __tostring=function(self) return tostring(self.Scale)..", "..tostring(self.Offset) end,
            __eq=function(a,b) return typeof(a)=="UDim" and typeof(b)=="UDim" and a.Scale==b.Scale and a.Offset==b.Offset end,
            __add=function(a,b) return UDim.new(a.Scale+b.Scale,wrapOffset(a.Offset+b.Offset)) end,
            __sub=function(a,b) return UDim.new(a.Scale-b.Scale,wrapOffset(a.Offset-b.Offset)) end,
            __unm=function(a) return UDim.new(-a.Scale,-a.Offset) end,
        })
    end
    local udimMethods={}
    function UDim2.new(a,b,c,d)
        local x,y
        if typeof(a)=="UDim" then x,y=a,b;assert(typeof(y)=="UDim","Expected UDim")
        else x,y=UDim.new(a,b),UDim.new(c,d) end
        return make("UDim2",{X=x,Y=y},function(_,key,values)
            if key=="Width" then return values.X elseif key=="Height" then return values.Y end
            if values[key] then return values[key] end
            if udimMethods[key] then return udimMethods[key] end
            error(key.." is not a valid member of UDim2",2)
        end,{
            __tostring=function(self) return "{"..tostring(self.X).."}, {"..tostring(self.Y).."}" end,
            __eq=function(a,b) return typeof(a)=="UDim2" and typeof(b)=="UDim2" and a.X==b.X and a.Y==b.Y end,
            __add=function(a,b) return UDim2.new(a.X+b.X,a.Y+b.Y) end,
            __sub=function(a,b) return UDim2.new(a.X-b.X,a.Y-b.Y) end,
        })
    end
    function UDim2.fromScale(x,y) return UDim2.new(x,0,y,0) end
    function UDim2.fromOffset(x,y) return UDim2.new(0,x,0,y) end
    function udimMethods:Lerp(other,t)
        return UDim2.new(self.X.Scale+(other.X.Scale-self.X.Scale)*t,self.X.Offset+(other.X.Offset-self.X.Offset)*t,
            self.Y.Scale+(other.Y.Scale-self.Y.Scale)*t,self.Y.Offset+(other.Y.Offset-self.Y.Offset)*t)
    end
    R.datatypes.UDim,R.datatypes.UDim2=table.freeze(UDim),table.freeze(UDim2)
    local NumberRange={}
    function NumberRange.new(min,max)
        min=min or 0;max=if max==nil then min else max
        assert(type(min)=="number" and type(max)=="number" and min<=max,"Invalid NumberRange")
        return record("NumberRange",{Min=min,Max=max})
    end
    R.datatypes.NumberRange=table.freeze(NumberRange)
    local Rect={}
    function Rect.new(a,b,c,d)
        local V2=R.datatypes.Vector2
        local min,max
        if typeof(a)=="Vector2" then min,max=a,b else min,max=V2.new(a,b),V2.new(c,d) end
        return record("Rect",{Min=min,Max=max,Width=max.X-min.X,Height=max.Y-min.Y})
    end
    R.datatypes.Rect=table.freeze(Rect)
    local Ray,rayMethods={},{}
    function rayMethods:ClosestPoint(point)
        assert(typeof(point)=='Vector3','Expected Vector3')
        local square=self.Direction:Dot(self.Direction)
        if square<=(square+1)*0.00001 then return self.Origin end
        return self.Origin+self.Direction*(math.max(0,(point-self.Origin):Dot(self.Direction))/square)
    end
    function rayMethods:Distance(point) return (point-self:ClosestPoint(point)).Magnitude end
    function Ray.new(origin,direction)
        local V3=R.datatypes.Vector3
        origin,direction=origin or V3.zero,direction or V3.zero
        assert(typeof(origin)=="Vector3" and typeof(direction)=="Vector3","Ray requires Vector3")
        return make("Ray",{Origin=origin,Direction=direction},function(_,key,d)
            if d[key] then return d[key] end
            if key=="Unit" then return Ray.new(origin,direction.Unit) end
            if rayMethods[key] then return rayMethods[key] end
            error(key.." is not a valid member of Ray",2)
        end,{__tostring=function() return "{"..tostring(origin).."}, {"..tostring(direction).."}" end})
    end
    R.datatypes.Ray=table.freeze(Ray)
    local TweenInfo={}
    function TweenInfo.new(time,style,direction,repeats,reverses,delay)
        time,style,direction,repeats,reverses,delay=time or 1,style or R.Enum.EasingStyle.Quad,direction or R.Enum.EasingDirection.Out,repeats or 0,reverses or false,delay or 0
        assert(type(time)=="number" and time>=0 and type(delay)=="number" and delay>=0,"Invalid tween time")
        assert(style.EnumType==R.Enum.EasingStyle and direction.EnumType==R.Enum.EasingDirection,"Invalid easing enum")
        assert(type(repeats)=="number" and repeats>=-1 and repeats%1==0 and type(reverses)=="boolean","Invalid tween repetition")
        return record("TweenInfo",{Time=time,EasingStyle=style,EasingDirection=direction,RepeatCount=repeats,Reverses=reverses,DelayTime=delay})
    end
    R.datatypes.TweenInfo=table.freeze(TweenInfo)
end
