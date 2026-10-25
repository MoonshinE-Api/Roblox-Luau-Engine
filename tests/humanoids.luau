local run=game:GetService('RunService')
local h=Instance.new('Humanoid')
local changes={}
h.HealthChanged:Connect(function(value) table.insert(changes,value) end)
h.Health=250;assert(h.Health==100 and #changes==1)
h.MaxHealth=300;assert(h.Health==250 and #changes==2)
h.MaxHealth=50;assert(h.Health==50 and #changes==3)
h.MaxHealth=300;assert(h.Health==250 and #changes==4)
h.Health=250;assert(#changes==4)
h:TakeDamage(10);assert(h.Health==240)
h.MaxHealth=100;h:TakeDamage(-10);assert(h.Health==100)
h.MaxHealth=300;assert(h.Health==110,'TakeDamage must subtract from the visible health')
h.Health=-1;h.Health=-2;assert(h.Health==0 and changes[#changes]==0)
h.MaxHealth=-20;assert(h.MaxHealth==0)
h.MaxHealth=0/0;assert(h.MaxHealth==0)
h.MaxHealth=100;h.Health=0/0;assert(h.Health~=h.Health)
h.Health=100
assert(not pcall(function() h.Health={} end))
assert(not pcall(function() h:TakeDamage('bad') end))
assert(not pcall(function() h:SetStateEnabled(Enum.Material.Plastic,true) end))
assert(not pcall(function() h:SetStateEnabled(Enum.HumanoidStateType.Dead,1) end))
assert(h:GetStateEnabled(Enum.HumanoidStateType.None))
h:SetStateEnabled(Enum.HumanoidStateType.None,false)

local ancestor=Instance.new('Folder',workspace)
local model=Instance.new('Model',ancestor)
local root=Instance.new('Part',model);root.Name='HumanoidRootPart'
local head=Instance.new('Part',model);head.Name='Head'
h.Parent=model
assert(h.RootPart==root)
assert(not pcall(function() h.RootPart=nil end))
local field=Instance.new('ForceField',model)
assert(field.Visible==true);field.Visible=false
assert(not pcall(function() field.Visible=12 end))
h:TakeDamage(20);h:TakeDamage(-20);assert(h.Health==100)
h.Health=90;assert(h.Health==90,'Direct writes bypass force fields')
h:TakeDamage(-5);assert(h.Health==90,'Force fields must also block healing')
field.Parent=head;h:TakeDamage(10);assert(h.Health==80,'Head force field must not protect the humanoid root')
field.Parent=root;h:TakeDamage(20);assert(h.Health==80)
field.Parent=ancestor;h:TakeDamage(20);assert(h.Health==80)
assert(not pcall(function() field.Parent=workspace end));assert(field.Parent==ancestor)
field.Parent=nil
assert(not pcall(function() Instance.new('ForceField',workspace) end))
h:takeDamage(-10);assert(h.Health==90)
local duplicate=field:Clone();assert(duplicate.Visible==false);duplicate:Destroy()

local died=0
h.Died:Connect(function() died+=1 end)
h.Health=0;assert(died==0,'Death must run in the simulation phase')
task.wait(.02);assert(died==1)
h.Health=50;task.wait(.02);assert(h.Health==0 and died==1)

local otherModel=Instance.new('Model',workspace)
local otherRoot=Instance.new('Part',otherModel);otherRoot.Name='HumanoidRootPart'
local other=Instance.new('Humanoid',otherModel)
local otherDeaths,stateChanges=0,0
other.Died:Connect(function() otherDeaths+=1 end)
other.StateEnabledChanged:Connect(function(state,enabled)
    assert(state==Enum.HumanoidStateType.Dead and type(enabled)=='boolean')
    stateChanges+=1
end)
other:SetStateEnabled(Enum.HumanoidStateType.Dead,false)
other.Health=0;task.wait(.02);assert(otherDeaths==0)
local clone=other:Clone();clone.Health=100
assert(clone:GetStateEnabled(Enum.HumanoidStateType.Dead) and clone.Health==100)
clone:Destroy()
other:SetStateEnabled(Enum.HumanoidStateType.Dead,true)
other:SetStateEnabled(Enum.HumanoidStateType.Dead,true)
assert(stateChanges==3)
task.wait(.02);assert(otherDeaths==1)

local stored=Instance.new('Model',game:GetService('ReplicatedStorage'))
local storedH=Instance.new('Humanoid',stored)
local storedDeaths=0;storedH.Died:Connect(function() storedDeaths+=1 end)
storedH.Health=0;task.wait(.02);assert(storedDeaths==0)
stored.Parent=workspace;task.wait(.02);assert(storedDeaths==1)
field:Destroy();ancestor:Destroy();otherModel:Destroy();stored:Destroy()
print('HUMANOID HEALTH, RAW VIEW, FORCE FIELDS, STATE FLAGS AND DEATH CHECKS PASSED',#changes)
