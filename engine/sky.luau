-- LightingParameters::setTime from build 735. Float32 phase/latitude operations
-- are preserved; vector components agree with the original within 3e-6.
return function(R)
    local f32,V3=R.float32,R.datatypes.Vector3
    local pi=f32(math.pi)
    local cache=setmetatable({}, {__mode='k'})
    local function directions(object)
        local seconds=R.instances[object].props._lightingSeconds
        local latitude=object.GeographicLatitude
        local previous=cache[object]
        if previous and previous.seconds==seconds and previous.latitude==latitude then return previous.sun,previous.moon end
        local phase=f32(f32(f32(seconds)*f32(2*math.pi))/86400)
        local day=f32(seconds/86400)
        local latitudeAngle=f32(f32(latitude*pi)/(-180))
        local tilt=f32(latitudeAngle+math.cos((day-182.6282)*math.pi/182.6282)*(-0.41015237421866746))
        local cosine,sine=f32(math.cos(tilt)),f32(math.sin(tilt))
        local function direction(angle)
            local s,c=f32(math.sin(angle)),f32(math.cos(angle))
            return V3.new(f32(s*cosine),f32(-c*cosine),-sine)
        end
        local sun,moon=direction(phase),direction(f32(phase+pi))
        cache[object]={seconds=seconds,latitude=latitude,sun=sun,moon=moon}
        return sun,moon
    end
    function R.classMethods.Lighting:GetSunDirection() local sun=directions(self);return sun end
    function R.classMethods.Lighting:GetMoonDirection() local _,moon=directions(self);return moon end
end
