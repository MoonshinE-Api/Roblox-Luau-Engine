local run=game:GetService('RunService')
if run:IsClient() then
    local ok,message=pcall(function() game:BindToClose(function() end) end)
    assert(not ok and string.find(message,'only be called on the server',1,true))
    print('CLIENT SHUTDOWN CALLBACK REGISTRATION REJECTED')
    return
end
assert(not pcall(function() game:BindToClose(12) end))
local signal=Instance.new('BindableEvent')
local firstStarted,secondStarted=false,false
game:BindToClose(function(reason)
    assert(run:IsServer() and reason==Enum.CloseReason.DeveloperShutdown)
    firstStarted=true
    local value=signal.Event:Wait()
    assert(secondStarted and value=='released')
    local ok,message=pcall(function() game:BindToClose(function() end) end)
    assert(not ok and string.find(message,'already being closed',1,true))
    task.wait(0.02)
    print('FIRST SHUTDOWN CALLBACK FINISHED')
end)
game:BindToClose(function(reason)
    assert(run:IsServer() and reason==Enum.CloseReason.DeveloperShutdown)
    secondStarted=true
    task.wait(0.02)
    assert(firstStarted)
    signal:Fire('released')
    print('SECOND SHUTDOWN CALLBACK FINISHED')
end)
print('PARALLEL SHUTDOWN CALLBACKS REGISTERED')
