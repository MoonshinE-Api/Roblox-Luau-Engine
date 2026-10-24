local http = game:GetService("HttpService")
http.HttpEnabled = true

-- Public HTTP test endpoint: its body is the base64-decoded path argument.
local response = http:RequestAsync({
    Url = "https://httpbin.org/base64/aGVsbG8sIGNoYXRncHQ=",
    Method = "GET",
    Timeout = 15,
})
assert(response.Success, "HTTP " .. response.StatusCode)
assert(response.Body == "hello, chatgpt")
print(response.Body)
print("HTTPS check passed", response.StatusCode)

local text = http:GetAsync("https://httpbin.org/base64/aGVsbG8sIGNoYXRncHQ=", true)
assert(text == "hello, chatgpt")
print("GetAsync check passed", text)
