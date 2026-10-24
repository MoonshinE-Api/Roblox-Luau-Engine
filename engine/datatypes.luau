return function(R)
    local values = setmetatable({}, {__mode="k"})
    local equalities = {}
    R.datatypes, R.values = {}, values
    local function object(name, data, index, operators)
        local value = R.proxy()
        values[value] = data
        local mt = getmetatable(value)
        mt.__type, mt.__metatable = name, name
        mt.__index = function(self,key) return index(self,key,values[self]) end
        mt.__newindex = function() error(name .. " is immutable",2) end
        for key,fn in operators do
            if key=="__eq" then equalities[name]=equalities[name] or fn;fn=equalities[name] end
            mt[key]=fn
        end
        return value
    end
    local function vectorType(name,dimensions)
        local methods, library = {}, {}
        local keys={X=1,Y=2,Z=3,x=1,y=2,z=3}
        local function components(a) assert(typeof(a)==name,"Expected "..name);return values[a] end
        local function make(...)
            local input={...};local data={}
            for i=1,dimensions do data[i]=input[i] or 0;assert(type(data[i])=="number","Expected number") end
            return object(name,data,function(self,key,v)
                local i=keys[key]
                if i and i<=dimensions then return v[i] end
                if key=="Magnitude" or key=="magnitude" then
                    local sum=0;for j=1,dimensions do sum+=v[j]^2 end;return math.sqrt(sum)
                elseif key=="Unit" or key=="unit" then return self/self.Magnitude end
                if methods[key] then return methods[key] end
                error(key.." is not a valid member of "..name,2)
            end,{
                __tostring=function(self) local a=values[self];return table.concat(a,", ") end,
                __eq=function(a,b)
                    if typeof(a)~=name or typeof(b)~=name then return false end
                    for j=1,dimensions do if values[a][j]~=values[b][j] then return false end end;return true
                end,
                __add=function(a,b) local x,y=components(a),components(b);local z={};for j=1,dimensions do z[j]=x[j]+y[j] end;return make(table.unpack(z)) end,
                __sub=function(a,b) local x,y=components(a),components(b);local z={};for j=1,dimensions do z[j]=x[j]-y[j] end;return make(table.unpack(z)) end,
                __unm=function(a) local x=components(a);local z={};for j=1,dimensions do z[j]=-x[j] end;return make(table.unpack(z)) end,
                __mul=function(a,b)
                    local z={}
                    if type(a)=="number" then local y=components(b);for j=1,dimensions do z[j]=a*y[j] end
                    elseif type(b)=="number" then local x=components(a);for j=1,dimensions do z[j]=x[j]*b end
                    else local x,y=components(a),components(b);for j=1,dimensions do z[j]=x[j]*y[j] end end
                    return make(table.unpack(z))
                end,
                __div=function(a,b)
                    local x=components(a);local z={}
                    if type(b)=="number" then for j=1,dimensions do z[j]=x[j]/b end
                    else local y=components(b);for j=1,dimensions do z[j]=x[j]/y[j] end end
                    return make(table.unpack(z))
                end,
            })
        end
        function methods:Dot(other) local a,b=components(self),components(other);local n=0;for i=1,dimensions do n+=a[i]*b[i] end;return n end
        function methods:Lerp(other,alpha) return self+(other-self)*alpha end
        function methods:FuzzyEq(other,epsilon) return (self-other).Magnitude <= (epsilon or 1e-5) end
        function methods:Min(other) local a,b=components(self),components(other);local c={};for i=1,dimensions do c[i]=math.min(a[i],b[i]) end;return make(table.unpack(c)) end
        function methods:Max(other) local a,b=components(self),components(other);local c={};for i=1,dimensions do c[i]=math.max(a[i],b[i]) end;return make(table.unpack(c)) end
        if dimensions==3 then
            function methods:Cross(other) local a,b=components(self),components(other);return make(a[2]*b[3]-a[3]*b[2],a[3]*b[1]-a[1]*b[3],a[1]*b[2]-a[2]*b[1]) end
        end
        library.new=make;library.zero=make();library.one=make(1,1,1)
        library.xAxis=make(1,0,0);library.yAxis=make(0,1,0)
        if dimensions==3 then library.zAxis=make(0,0,1) end
        R.datatypes[name]=table.freeze(library)
    end
    vectorType("Vector2",2);vectorType("Vector3",3)
    local V3=R.datatypes.Vector3
    local CF,cfMethods={},{}
    local function transform(c,v,position)
        return V3.new(c[4]*v.X+c[5]*v.Y+c[6]*v.Z+(if position then c[1] else 0),
            c[7]*v.X+c[8]*v.Y+c[9]*v.Z+(if position then c[2] else 0),
            c[10]*v.X+c[11]*v.Y+c[12]*v.Z+(if position then c[3] else 0))
    end
    local function cframe(c)
        return object("CFrame",c,function(self,key,v)
            if key=="Position" or key=="p" then return V3.new(v[1],v[2],v[3]) end
            if key=="X" or key=="x" then return v[1] elseif key=="Y" or key=="y" then return v[2] elseif key=="Z" or key=="z" then return v[3] end
            if key=="RightVector" or key=="XVector" then return V3.new(v[4],v[7],v[10]) end
            if key=="UpVector" or key=="YVector" then return V3.new(v[5],v[8],v[11]) end
            if key=="LookVector" then return V3.new(-v[6],-v[9],-v[12]) end
            if key=="ZVector" then return V3.new(v[6],v[9],v[12]) end
            if key=="Rotation" then local n=table.clone(v);n[1],n[2],n[3]=0,0,0;return cframe(n) end
            if cfMethods[key] then return cfMethods[key] end
            error(key.." is not a valid member of CFrame",2)
        end,{
            __tostring=function(a) return table.concat(values[a],", ") end,
            __eq=function(a,b) if typeof(a)~="CFrame" or typeof(b)~="CFrame" then return false end;for i=1,12 do if values[a][i]~=values[b][i] then return false end end;return true end,
            __mul=function(a,b)
                assert(typeof(a)=="CFrame","Expected CFrame")
                local x=values[a]
                if typeof(b)=="Vector3" then return transform(x,b,true) end
                assert(typeof(b)=="CFrame","Expected CFrame or Vector3")
                local y=values[b];local p=transform(x,V3.new(y[1],y[2],y[3]),true)
                local z={p.X,p.Y,p.Z}
                for row=0,2 do for col=0,2 do
                    z[4+row*3+col]=x[4+row*3]*y[4+col]+x[5+row*3]*y[7+col]+x[6+row*3]*y[10+col]
                end end
                return cframe(z)
            end,
            __add=function(a,b) assert(typeof(b)=="Vector3","Expected Vector3");local z=table.clone(values[a]);z[1]+=b.X;z[2]+=b.Y;z[3]+=b.Z;return cframe(z) end,
            __sub=function(a,b) return a+(-b) end,
        })
    end
    function CF.new(...)
        local a=table.pack(...)
        if a.n==12 then return cframe({...}) end
        if typeof(a[1])=="Vector3" then
            if a.n==2 then return CF.lookAt(a[1],a[2]) end
            return cframe({a[1].X,a[1].Y,a[1].Z,1,0,0,0,1,0,0,0,1})
        end
        assert(a.n==0 or a.n==3,"Unsupported CFrame.new overload")
        return cframe({a[1] or 0,a[2] or 0,a[3] or 0,1,0,0,0,1,0,0,0,1})
    end
    function CF.fromMatrix(position,right,up,back)
        back=back or right:Cross(up)
        return cframe({position.X,position.Y,position.Z,right.X,up.X,back.X,right.Y,up.Y,back.Y,right.Z,up.Z,back.Z})
    end
    function CF.lookAt(position,target,up)
        local back=(position-target).Unit
        local right=(up or V3.yAxis):Cross(back).Unit
        return CF.fromMatrix(position,right,back:Cross(right),back)
    end
    function CF.Angles(x,y,z)
        local a,b,c,d,e,f=math.cos(x),math.sin(x),math.cos(y),math.sin(y),math.cos(z),math.sin(z)
        return cframe({0,0,0,c*e,-c*f,d,a*f+b*d*e,a*e-b*d*f,-b*c,b*f-a*d*e,b*e+a*d*f,a*c})
    end
    CF.fromEulerAnglesXYZ=CF.Angles
    function cfMethods:Inverse()
        local c=values[self];local p=V3.new(c[1],c[2],c[3])
        return cframe({-p:Dot(V3.new(c[4],c[7],c[10])),-p:Dot(V3.new(c[5],c[8],c[11])),-p:Dot(V3.new(c[6],c[9],c[12])),
            c[4],c[7],c[10],c[5],c[8],c[11],c[6],c[9],c[12]})
    end
    cfMethods.inverse=cfMethods.Inverse
    function cfMethods:GetComponents() return table.unpack(values[self]) end
    cfMethods.components=cfMethods.GetComponents
    function cfMethods:ToWorldSpace(other) return self*other end
    function cfMethods:ToObjectSpace(other) return self:Inverse()*other end
    function cfMethods:PointToWorldSpace(v) return transform(values[self],v,true) end
    function cfMethods:PointToObjectSpace(v) return self:Inverse():PointToWorldSpace(v) end
    function cfMethods:VectorToWorldSpace(v) return transform(values[self],v,false) end
    function cfMethods:VectorToObjectSpace(v) return self:Inverse():VectorToWorldSpace(v) end
    local function quaternion(c)
        local x,y,z,w
        local trace=c[4]+c[8]+c[12]
        if trace>0 then
            local s=math.sqrt(trace+1)*2
            w,x,y,z=s/4,(c[11]-c[9])/s,(c[6]-c[10])/s,(c[7]-c[5])/s
        elseif c[4]>c[8] and c[4]>c[12] then
            local s=math.sqrt(1+c[4]-c[8]-c[12])*2
            w,x,y,z=(c[11]-c[9])/s,s/4,(c[5]+c[7])/s,(c[6]+c[10])/s
        elseif c[8]>c[12] then
            local s=math.sqrt(1+c[8]-c[4]-c[12])*2
            w,x,y,z=(c[6]-c[10])/s,(c[5]+c[7])/s,s/4,(c[9]+c[11])/s
        else
            local s=math.sqrt(1+c[12]-c[4]-c[8])*2
            w,x,y,z=(c[7]-c[5])/s,(c[6]+c[10])/s,(c[9]+c[11])/s,s/4
        end
        return {x,y,z,w}
    end
    function cfMethods:Lerp(other,alpha)
        assert(typeof(other)=="CFrame" and type(alpha)=="number","Expected CFrame and number")
        if alpha==0 then return self elseif alpha==1 then return other end
        local a,b=quaternion(values[self]),quaternion(values[other])
        local dot=0;for i=1,4 do dot+=a[i]*b[i] end
        if dot<0 then for i=1,4 do b[i]=-b[i] end;dot=-dot end
        local first,last=1-alpha,alpha
        if dot<0.9995 then
            local angle=math.acos(math.clamp(dot,-1,1))
            first,last=math.sin((1-alpha)*angle)/math.sin(angle),math.sin(alpha*angle)/math.sin(angle)
        end
        local q,length={},0
        for i=1,4 do q[i]=a[i]*first+b[i]*last;length+=q[i]^2 end
        length=math.sqrt(length)
        local x,y,z,w=q[1]/length,q[2]/length,q[3]/length,q[4]/length
        local p=self.Position:Lerp(other.Position,alpha)
        return cframe({p.X,p.Y,p.Z,1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w),
            2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w),2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)})
    end
    cfMethods.lerp=cfMethods.Lerp
    CF.identity=CF.new();R.datatypes.CFrame=table.freeze(CF)
    local Color3={};local colorMethods={}
    function Color3.new(r,g,b)
        return object("Color3",{r or 0,g or 0,b or 0},function(self,key,c)
            if key=="R" or key=="r" then return c[1] elseif key=="G" or key=="g" then return c[2] elseif key=="B" or key=="b" then return c[3] end
            if colorMethods[key] then return colorMethods[key] end;error(key.." is not a valid member of Color3",2)
        end,{
            __tostring=function(self) return table.concat(values[self],", ") end,
            __eq=function(a,b) return typeof(a)=="Color3" and typeof(b)=="Color3" and a.R==b.R and a.G==b.G and a.B==b.B end,
        })
    end
    function Color3.fromRGB(r,g,b) return Color3.new(r/255,g/255,b/255) end
    function Color3.fromHSV(h,s,v)
        local c=v*s;local x=c*(1-math.abs((h*6)%2-1));local m=v-c
        local rgb=({{c,x,0},{x,c,0},{0,c,x},{0,x,c},{x,0,c},{c,0,x}})[math.floor(h*6)%6+1]
        return Color3.new(rgb[1]+m,rgb[2]+m,rgb[3]+m)
    end
    function colorMethods:Lerp(other,t) return Color3.new(self.R+(other.R-self.R)*t,self.G+(other.G-self.G)*t,self.B+(other.B-self.B)*t) end
    function colorMethods:ToHex() return string.format("%02x%02x%02x",math.round(math.clamp(self.R,0,1)*255),math.round(math.clamp(self.G,0,1)*255),math.round(math.clamp(self.B,0,1)*255)) end
    R.datatypes.Color3=table.freeze(Color3)
    R.makeValue=object
end
