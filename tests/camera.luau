local function near(a,b) assert(math.abs(a-b)<1e-7,tostring(a)..' ~= '..tostring(b)) end
local function vector(a,b) assert((a-b).Magnitude<1e-7,tostring(a)..' ~= '..tostring(b)) end
local function rejects(fn) assert(not pcall(fn),'Expected failure') end
local camera=Instance.new('Camera')
assert(camera.ViewportSize==Vector2.one)
workspace.CurrentCamera=camera
assert(camera.ViewportSize==Vector2.new(1280,720))
camera.CFrame=CFrame.new();camera.FieldOfView=90
local point,onScreen=camera:WorldToViewportPoint(Vector3.new(0,0,-10))
vector(point,Vector3.new(640,360,10));assert(onScreen)
local off,visible=camera:WorldToViewportPoint(Vector3.new(100,0,-10));assert(not visible and off.X>1280)
local behind,front=camera:WorldToViewportPoint(Vector3.new(0,0,10));assert(not front and behind.Z==-10)
local ray=camera:ViewportPointToRay(640,360)
vector(ray.Origin,Vector3.new(0,0,camera.NearPlaneZ));vector(ray.Direction,Vector3.new(0,0,-1))
vector(camera:ViewportPointToRay(640,360,5).Origin,Vector3.new(0,0,camera.NearPlaneZ-5))
local random=Random.new(2026)
for i=1,200 do
    camera.CFrame=CFrame.new(random:NextNumber(-20,20),random:NextNumber(-20,20),random:NextNumber(-20,20))
        *CFrame.Angles(random:NextNumber(-2,2),random:NextNumber(-2,2),random:NextNumber(-2,2))
    camera.FieldOfView=random:NextNumber(10,120)
    local x,y=random:NextNumber(-300,1500),random:NextNumber(-200,1000)
    local sample=camera:ViewportPointToRay(x,y,random:NextNumber(0,10))
    near(sample.Direction.Magnitude,1)
    local screen,inside=camera:WorldToViewportPoint(sample.Origin+sample.Direction*20)
    near(screen.X,x);near(screen.Y,y)
    assert(inside==(x>=0 and x<=1280 and y>=0 and y<=720))
end
camera.FieldOfView=70
local vertical=camera.FieldOfView
camera.FieldOfViewMode=Enum.FieldOfViewMode.Diagonal
near(camera.FieldOfView,vertical)
local diagonal=camera.DiagonalFieldOfView
workspace.CurrentCamera=nil
assert(camera.ViewportSize==Vector2.one)
near(camera.DiagonalFieldOfView,diagonal)
workspace.CurrentCamera=camera
near(camera.FieldOfView,70)
camera.DiagonalFieldOfView=100;near(camera.DiagonalFieldOfView,100)
camera.FieldOfViewMode=Enum.FieldOfViewMode.MaxAxis
camera.MaxAxisFieldOfView=110;near(camera.MaxAxisFieldOfView,110)
local beforeClone=camera.FieldOfView
local clone=camera:Clone();workspace.CurrentCamera=clone
near(clone.FieldOfView,beforeClone)
near(clone.MaxAxisFieldOfView,camera.MaxAxisFieldOfView)
assert(clone:GetRenderCFrame()==clone.CFrame)
clone.FieldOfViewMode=Enum.FieldOfViewMode.Vertical
clone.FieldOfView=1000;assert(clone.FieldOfView==120)
clone.FieldOfView=-20;assert(clone.FieldOfView==1)
rejects(function() clone.ViewportSize=Vector2.zero end)
rejects(function() clone.NearPlaneZ=-1 end)
rejects(function() clone.FieldOfView=0/0 end)
rejects(function() workspace.CurrentCamera=Instance.new('Part') end)
rejects(function() clone:ViewportPointToRay('x',0) end)
local r=Ray.new(Vector3.new(1,2,3),Vector3.new(2,0,0))
vector(r:ClosestPoint(Vector3.new(7,5,3)),Vector3.new(7,2,3));near(r:Distance(Vector3.new(7,5,3)),3)
vector(r:ClosestPoint(Vector3.new(-7,5,3)),r.Origin)
vector(Ray.new(Vector3.one,Vector3.zero):ClosestPoint(Vector3.zero),Vector3.one)
vector(Ray.new(Vector3.one,Vector3.new(1e-8,0,0)):ClosestPoint(Vector3.zero),Vector3.one)
rejects(function() r:ClosestPoint('point') end)
print('CAMERA PROJECTION, FOV, RAY AND 200 ROUNDTRIP CHECKS PASSED')
