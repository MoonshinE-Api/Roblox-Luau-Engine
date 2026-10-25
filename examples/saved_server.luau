-- Run with --no-player --run-forever --data-store <local SQLite file>.
-- Ctrl+C saves this world's state before the process exits.
local run=game:GetService('RunService')
local lighting=game:GetService('Lighting')
assert(run:IsServer() and #game:GetService('Players'):GetPlayers()==0,'Run as a server with --no-player')
local store=game:GetService('DataStoreService'):GetDataStore('SavedHeadlessWorld')
local profile=store:GetAsync('world') or {minutes=360,seconds=0,starts=0}
profile.starts+=1
lighting:SetMinutesAfterMidnight(profile.minutes)
run.Heartbeat:Connect(function(dt) profile.seconds+=dt end)
game:BindToClose(function(reason)
    profile.minutes=lighting:GetMinutesAfterMidnight()
    profile.closeReason=reason.Name
    store:SetAsync('world',profile)
    print('WORLD SNAPSHOT SAVED',profile.starts,profile.seconds,lighting.TimeOfDay,reason.Name)
end)
task.spawn(function()
    while true do
        local elapsed=task.wait(1)
        lighting:SetMinutesAfterMidnight(lighting:GetMinutesAfterMidnight()+elapsed*30)
        print('SAVED SERVER',profile.starts,profile.seconds,lighting.TimeOfDay)
    end
end)
print('SAVED SERVER STARTED',profile.starts,lighting.TimeOfDay)
