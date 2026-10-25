local lighting=game:GetService('Lighting')
local function near(a,b) assert((a-b).Magnitude<4e-6,tostring(a)..' ~= '..tostring(b)) end
lighting.GeographicLatitude=0
lighting.TimeOfDay='00:00:00'
local midnight=lighting:GetSunDirection()
local moon=lighting:GetMoonDirection()
assert(typeof(midnight)=='Vector3' and midnight.Y<0 and moon.Y>0)
near(midnight,Vector3.new(0,-0.917060077,-0.39874908))
-- Native build 735 calculates moon phase separately; it is not -sun.
assert((moon+midnight).Magnitude>0.7)
assert(not pcall(function() midnight.X=1 end))
lighting.TimeOfDay='12:00:00'
local noon=lighting:GetSunDirection()
assert(noon.Y>0 and lighting:GetMoonDirection().Y<0)
assert((noon-midnight).Magnitude>1)
lighting.GeographicLatitude=70
assert((lighting:GetSunDirection()-noon).Magnitude>0.5)
local cloned=lighting:Clone()
near(cloned:GetSunDirection(),lighting:GetSunDirection())
cloned.TimeOfDay='18:00:00'
assert((cloned:GetSunDirection()-lighting:GetSunDirection()).Magnitude>0.5)
for _,latitude in {-90,-66.5,0,23.5,41.7333,66.5,90} do
    lighting.GeographicLatitude=latitude
    for _,second in {0,1,21599,21600,43199,43200,64800,86399} do
        lighting.TimeOfDay=string.format('%02d:%02d:%02d',math.floor(second/3600),math.floor(second/60)%60,second%60)
        for _,direction in {lighting:GetSunDirection(),lighting:GetMoonDirection()} do
            assert(math.abs(direction.Magnitude-1)<4e-6)
        end
    end
end
lighting:SetMinutesAfterMidnight(0)
local start=lighting:GetSunDirection()
lighting:SetMinutesAfterMidnight(1440)
near(lighting:GetSunDirection(),start)
lighting:SetMinutesAfterMidnight(-1)
local endOfDay=lighting:GetSunDirection()
lighting.TimeOfDay='23:59:00'
near(lighting:GetSunDirection(),endOfDay)
-- Minute conversion follows native integer microsecond quantization first.
lighting:SetMinutesAfterMidnight(65/60)
assert(lighting.TimeOfDay=='00:01:04')
cloned:Destroy()
print('SUN AND MOON DIRECTION, LATITUDE, CLONE AND CLOCK CHECKS PASSED')
