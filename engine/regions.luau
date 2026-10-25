-- Axis-aligned regions preserve signed sizes and build 735 float32 operations.
return function(R)
    local V3,CF,V16=R.datatypes.Vector3,R.datatypes.CFrame,R.datatypes.Vector3int16
    local f32=R.float32
    local Region3,methods={},{}
    local function componentMap(vector,operation) return V3.new(operation(vector.X),operation(vector.Y),operation(vector.Z)) end
    function Region3.new(...)
        local n=select('#',...);local minimum,maximum=...
        if n==0 then minimum=V3.zero end
        if n<2 then maximum=V3.zero end
        assert(typeof(minimum)=='Vector3' and typeof(maximum)=='Vector3','Region3 requires Vector3 bounds')
        minimum,maximum=componentMap(minimum,f32),componentMap(maximum,f32)
        local center=componentMap(componentMap(minimum+maximum,f32)*0.5,f32)
        local size=componentMap(maximum-minimum,f32)
        return R.makeRecord('Region3',{CFrame=CF.new(center),Size=size},methods)
    end
    function methods:ExpandToGrid(resolution)
        resolution=tonumber(resolution)
        assert(resolution,'Expected resolution number');resolution=f32(resolution)
        assert(resolution>0 and resolution<math.huge,'Resolution has to be a positive number')
        local center,size=self.CFrame.Position,self.Size
        local minimum=componentMap(center+componentMap(size*(-0.5),f32),f32)
        local maximum=componentMap(center+componentMap(size*0.5,f32),f32)
        local reciprocal=f32(1/resolution)
        return Region3.new(componentMap(minimum,function(x) return f32(math.floor(f32(x*reciprocal))*resolution) end),
            componentMap(maximum,function(x) return f32(math.ceil(f32(x*reciprocal))*resolution) end))
    end
    local Region3int16={}
    function Region3int16.new(...)
        local n=select('#',...);local minimum,maximum=...
        if n==0 then minimum=V16.new() end
        if n<2 then maximum=V16.new() end
        assert(typeof(minimum)=='Vector3int16' and typeof(maximum)=='Vector3int16','Region3int16 requires Vector3int16 bounds')
        return R.makeRecord('Region3int16',{Min=minimum,Max=maximum})
    end
    R.datatypes.Region3,R.datatypes.Region3int16=table.freeze(Region3),table.freeze(Region3int16)
end
