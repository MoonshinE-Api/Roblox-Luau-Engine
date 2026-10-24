local calls = 0
return function()
    calls += 1
    return calls
end
