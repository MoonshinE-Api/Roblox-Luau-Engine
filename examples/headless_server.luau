-- Finite preview: --no-player --realtime --duration 5
-- Continuous host: --no-player --run-forever (Ctrl+C to stop)
local run=game:GetService('RunService')
local lighting=game:GetService('Lighting')
local players=game:GetService('Players')
assert(run:IsServer() and #players:GetPlayers()==0,'Run with --no-player --mode server')
lighting.TimeOfDay='06:00:00'
local frames=0
run.Heartbeat:Connect(function() frames+=1 end)
task.spawn(function()
    while true do
        local elapsed=task.wait(1)
        -- A day/night cycle is explicitly scripted, as it is in Studio.
        lighting:SetMinutesAfterMidnight(lighting:GetMinutesAfterMidnight()+elapsed*30)
        print('HEADLESS SERVER',time(),'frames',frames,lighting.TimeOfDay,'sun',lighting:GetSunDirection())
    end
end)
print('HEADLESS SERVER STARTED WITHOUT A PLAYER')
