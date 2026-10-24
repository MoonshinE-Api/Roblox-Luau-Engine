-- Run with --realtime --duration 1 to align task.wait with actual clock readings.
local start=DateTime.now().UnixTimestampMillis
for i=1,3 do
    local elapsed=task.wait(0.1)
    local now=DateTime.now()
    print(i,now:FormatUniversalTime("YYYY-MM-DD HH:mm:ss.SSS","en-us"),"waited",elapsed)
end
assert(DateTime.now().UnixTimestampMillis-start>=290)
print("REALTIME COOLDOWN PASSED")
