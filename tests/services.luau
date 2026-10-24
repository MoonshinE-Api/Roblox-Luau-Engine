local collection=game:GetService("CollectionService")
local added,removed=0,0
collection:GetInstanceAddedSignal("RegressionTag"):Connect(function(object) assert(typeof(object)=="Instance");added+=1 end)
collection:GetInstanceRemovedSignal("RegressionTag"):Connect(function(object) assert(typeof(object)=="Instance");removed+=1 end)
local parent=Instance.new("Folder")
local child=Instance.new("Folder",parent)
collection:AddTag(child,"RegressionTag")
assert(#collection:GetTagged("RegressionTag")==0 and added==0)
parent.Parent=workspace
assert(added==1 and #collection:GetTagged("RegressionTag")==1)
assert(table.find(collection:GetAllTags(),"RegressionTag"))
parent.Parent=game:GetService("ReplicatedStorage")
assert(added==1 and removed==0)
parent.Parent=nil
assert(removed==1 and #collection:GetTagged("RegressionTag")==0)
parent.Parent=workspace
assert(added==2)
local cloned=parent:Clone();cloned.Parent=workspace
assert(added==3 and #collection:GetTagged("RegressionTag")==2)
collection:RemoveTag(child,"RegressionTag")
assert(removed==2 and not collection:HasTag(child,"RegressionTag"))
-- CollectionService inherits the Instance tag names; call its own methods with
-- an explicit target to avoid a virtual-method name collision during enumeration.
collection:AddTag(collection,"RegressionTag")
assert(added==4 and #collection:GetTagged("RegressionTag")==2)
collection:RemoveTag(collection,"RegressionTag")
cloned:Destroy();parent:Destroy()
assert(removed==4 and #collection:GetTagged("RegressionTag")==0)
for _,class in {"IntValue","NumberValue","BoolValue","StringValue"} do
    local value=Instance.new(class)
    assert(value:IsA("ValueBase"))
    local changed,names,parents=0,0,0
    value.Changed:Connect(function(newValue) changed+=1;assert(newValue==value.Value) end)
    value:GetPropertyChangedSignal("Name"):Connect(function() names+=1 end)
    value:GetPropertyChangedSignal("Parent"):Connect(function() parents+=1 end)
    value.Name="Checked";value.Parent=workspace
    assert(changed==0 and names==1 and parents==1)
    value.Value=if class=="BoolValue" then true elseif class=="StringValue" then "text" else 7
    assert(changed==1)
    value:Destroy();assert(changed==1 and parents==2)
end
local a=Instance.new("Part",workspace)
a.Name="suck"
local b=a:Clone()
assert(b.Name=="suck" and b~=a and b.Parent==nil)
a:Destroy();b:Destroy()
print("TAG, VALUE EVENT AND CLONE CHECKS PASSED")
