local model=workspace.ImportedModel
assert(model.PrimaryPart==model.Root and model.Target.Value==model.TargetPart)
local center,size=model:GetBoundingBox()
print('Imported model bounds:',center.Position,size)
local clone=model:Clone();clone.Name='ClonedModel';clone.Parent=workspace
assert(clone.PrimaryPart==clone.Root and clone.Target.Value==clone.TargetPart)
clone:PivotTo(CFrame.new(20,5,0)*CFrame.Angles(0,math.pi/2,0))
assert((clone:GetPivot().Position-Vector3.new(20,5,0)).Magnitude<1e-6)
local hit=workspace:Raycast(Vector3.new(0,20,0),Vector3.new(0,-30,0))
assert(hit and hit.Instance==model.Root)
print('Raycast hit:',hit.Instance:GetFullName(),hit.Position)
print('BINARY MODEL IMPORT EXAMPLE PASSED')
