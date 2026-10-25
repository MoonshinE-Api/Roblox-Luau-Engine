-- A scripted headless combat scenario; parts do not use dynamic physics.
local model=Instance.new('Model',workspace);model.Name='TrainingTarget'
local root=Instance.new('Part',model);root.Name='HumanoidRootPart';root.Anchored=true
local head=Instance.new('Part',model);head.Name='Head';head.Anchored=true;head.Position=Vector3.new(0,3,0)
local humanoid=Instance.new('Humanoid',model)
local field=Instance.new('ForceField',model);field.Visible=false
local score=Instance.new('IntValue');score.Name='Score'
humanoid.HealthChanged:Connect(function(health) print('TARGET HEALTH',health) end)
humanoid.Died:Connect(function() score.Value+=100;print('TARGET DEFEATED',score.Value) end)
humanoid:TakeDamage(75);assert(humanoid.Health==100)
field:Destroy()
humanoid:TakeDamage(60);assert(humanoid.Health==40)
humanoid:TakeDamage(-10);assert(humanoid.Health==50)
humanoid:TakeDamage(50)
task.wait(.02);assert(score.Value==100)
humanoid.Health=100
task.wait(.02);assert(humanoid.Health==0 and score.Value==100)
model:Destroy();score:Destroy()
print('DAMAGE, PROTECTION, HEALING AND DEATH EXAMPLE PASSED')
