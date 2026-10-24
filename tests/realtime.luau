assert(__engine.config.realtime,"This check requires --realtime")
local before=DateTime.now().UnixTimestampMillis
local monotonic=os.clock()
local elapsedStart=time()
local tickStart=tick()
local delayed=false
task.delay(0.04,function()
    assert(DateTime.now().UnixTimestampMillis-before>=35)
    delayed=true
end)
local waited=task.wait(0.08)
local actual=os.clock()-monotonic
assert(waited>=0.08 and actual>=0.08 and math.abs(waited-actual)<0.03)
assert(DateTime.now().UnixTimestampMillis-before>=75 and time()-elapsedStart>=0.08)
assert(tick()-tickStart>=0.075 and delayed)
local dt=game:GetService("RunService").Heartbeat:Wait()
assert(dt>0 and dt<1)
local started=os.clock()
local tween=game:GetService("TweenService"):Create(Instance.new("NumberValue"),TweenInfo.new(0.06),{Value=1})
tween:Play();assert(tween.Completed:Wait()==Enum.PlaybackState.Completed)
assert(os.clock()-started>=0.055)
print("PASS realtime: DateTime/task clocks, actual wait elapsed, delay, Heartbeat and tween timing")
