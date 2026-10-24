local run=game:GetService("RunService")
return {side=if run:IsServer() then "server" else "client"}
