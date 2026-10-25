local function rejects(fn) assert(not pcall(fn),'Expected failure') end
local R=__engine
local lighting=game:GetService('Lighting')
assert(lighting.TimeOfDay=='14:00:00' and lighting.ClockTime==14 and lighting:GetMoonPhase()==0.75)
local representatives={Light='PointLight',PostEffect='BloomEffect'}
local checked=0
for owner,fields in R.environmentCatalog.classes do
    for key,record in fields do
        local object=if owner=='Lighting' then lighting else Instance.new(representatives[owner] or owner)
        local previous=object[key];local kind=record.kind;local value
        if kind=='boolean' then value=not previous
        elseif kind=='number' then value=previous+1
        elseif kind=='string' then value=if key=='TimeOfDay' then '17:20:03' else 'rbxassetid://1234'
        elseif kind=='Color3' then value=Color3.new(0.2,0.4,0.6)
        elseif kind=='Vector2' then value=Vector2.new(12,20)
        elseif kind=='Vector3' then value=Vector3.new(1,2,3)
        elseif kind=='NumberRange' then value=NumberRange.new(2,5)
        elseif kind=='NumberSequence' then value=NumberSequence.new({NumberSequenceKeypoint.new(0,0.2,0.1),NumberSequenceKeypoint.new(1,0.8,0.2)})
        elseif kind=='ColorSequence' then value=ColorSequence.new(Color3.new(1,0,0),Color3.new(0,0,1))
        elseif kind=='BrickColor' then value=BrickColor.new(21)
        elseif kind=='Instance?' then value=Instance.new(record.target)
        elseif string.sub(kind,1,5)=='Enum.' then
            local items=Enum[string.sub(kind,6)]:GetEnumItems()
            value=items[1];if value==previous and #items>1 then value=items[2] end
        else error('Uncovered environment type '..kind) end
        local changes=0
        local connection=object:GetPropertyChangedSignal(key):Connect(function() changes+=1 end)
        object[key]=value
        local stored=object[key]
        assert(changes==(if stored==previous then 0 else 1),owner..'.'..key..' notification')
        local cloned=object:Clone();assert(cloned[key]==stored,owner..'.'..key..' clone');cloned:Destroy()
        rejects(function() object[key]={} end)
        connection:Disconnect()
        if object~=lighting then object:Destroy() end
        if kind=='Instance?' then value:Destroy() end
        checked+=1
    end
end
assert(checked==149,checked)
rejects(function() Instance.new('Light') end);rejects(function() Instance.new('PostEffect') end)
local point=Instance.new('PointLight')
point.Range=1e6;assert(point.Range==120);point.Range=-1;assert(point.Range==0)
point.Brightness=-4;assert(point.Brightness==0)
point.Color=Color3.new(0.1,0.2,0.3);assert(point.Color.R~=0.1)
local spot=Instance.new('SpotLight');spot.Angle=1000;assert(spot.Angle==180)
local atmosphere=Instance.new('Atmosphere');atmosphere.Density=3;assert(atmosphere.Density==1)
local beam=Instance.new('Beam');beam.Segments=5000;assert(beam.Segments==1000)
beam.Segments=-1;assert(beam.Segments==1)
beam.Transparency=NumberSequence.new({NumberSequenceKeypoint.new(0,0.2,1),NumberSequenceKeypoint.new(1,0.7,2)})
assert(beam.Transparency.Keypoints[1].Envelope==0 and beam.Transparency.Keypoints[2].Envelope==0)
local trail=Instance.new('Trail');trail.Lifetime=100;assert(trail.Lifetime==20)
beam.Width0=-2;assert(beam.Width0==0)
local dof=Instance.new('DepthOfFieldEffect');dof.InFocusRadius=-2;assert(dof.InFocusRadius==-2)
local fire=Instance.new('Fire');fire.Heat=100;assert(fire.Heat==25)
lighting.EnvironmentDiffuseScale=2;assert(lighting.EnvironmentDiffuseScale==1)
rejects(function() beam.Attachment0=Instance.new('Folder') end)
lighting.ClockTime=14
local changed=0;local skies=0
lighting.LightingChanged:Connect(function(skyboxChanged) assert(type(skyboxChanged)=='boolean');changed+=1;if skyboxChanged then skies+=1 end end)
lighting.ClockTime=14.00001;assert(lighting.TimeOfDay=='14:00:00' and changed==0)
lighting.ClockTime=25;assert(lighting.TimeOfDay=='00:00:00')
lighting.TimeOfDay='-00:00:01.9';assert(lighting.TimeOfDay=='23:59:59')
lighting.TimeOfDay='25:02:03.9';assert(lighting.TimeOfDay=='01:02:03')
lighting:setMinutesAfterMidnight(-1);assert(lighting.TimeOfDay=='23:59:00' and lighting:getMinutesAfterMidnight()==1439)
lighting:SetMinutesAfterMidnight(1440);assert(lighting.ClockTime==0)
local sky=Instance.new('Sky',lighting);assert(skies==1)
sky.StarCount+=1;assert(skies==2)
sky.Parent=nil;assert(skies==3)
for _,bad in {'noon','12','12:00','12:00:bad','12:00:1.2.3'} do rejects(function() lighting.TimeOfDay=bad end) end
local tween=game:GetService('TweenService'):Create(lighting,TweenInfo.new(0.05,Enum.EasingStyle.Linear),{ClockTime=18})
tween:Play();tween.Completed:Wait();assert(lighting.TimeOfDay=='18:00:00')
point:Destroy();spot:Destroy();atmosphere:Destroy();beam:Destroy();trail:Destroy();sky:Destroy()
dof:Destroy();fire:Destroy()
print('ENVIRONMENT CONFIGURATION, CLAMPS, CLONE, CLOCK, SKY EVENTS AND TWEEN CHECKS PASSED',checked)
