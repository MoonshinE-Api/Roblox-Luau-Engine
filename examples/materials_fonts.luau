-- Run with run.py. This example calculates engine values without a renderer.
local materials=game:GetService('MaterialService')
local variant=Instance.new('MaterialVariant',materials)
variant.Name='DemoMetal';variant.BaseMaterial=Enum.Material.Metal
variant.CustomPhysicalProperties=PhysicalProperties.new(3,.4,.2,1,1,.5)

local model=Instance.new('Model',workspace);model.Name='MaterialsDemo'
local block=Instance.new('Part',model);block.Name='Block';block.Size=Vector3.new(2,4,6)
block.Material=Enum.Material.Metal;block.MaterialVariant=variant.Name
local wedge=Instance.new('WedgePart',model);wedge.Name='Wedge';wedge.Size=block.Size
wedge.CFrame=CFrame.new(5,0,0);wedge.CustomPhysicalProperties=PhysicalProperties.new(2,.5,.25)
local corner=Instance.new('CornerWedgePart',model);corner.Name='Corner';corner.Size=block.Size
corner.CFrame=CFrame.new(-5,0,0);corner.CustomPhysicalProperties=PhysicalProperties.new(4,.5,.25)
model.PrimaryPart=block

local function totalMass(container)
    local total=0
    for _,part in container:GetDescendants() do if part:IsA('BasePart') then total+=part:GetMass() end end
    return total
end
assert(math.abs(totalMass(model)-256)<.001)
local title=Font.fromEnum(Enum.Font.ArialBold)
model:SetAttribute('UI/title.Font',title)
title.Bold=false
assert(model:GetAttribute('UI/title.Font').Bold)
local clone=model:Clone();clone.Name='CopiedMaterialsDemo';clone.Parent=workspace
local cloneTitle=clone:GetAttribute('UI/title.Font');cloneTitle.Style=Enum.FontStyle.Italic
clone:SetAttribute('UI/title.Font',cloneTitle)
assert(model:GetAttribute('UI/title.Font').Style==Enum.FontStyle.Normal)
assert(clone.PrimaryPart==clone.Block and math.abs(totalMass(clone)-256)<.001)

variant.CustomPhysicalProperties=PhysicalProperties.new(5,.4,.2)
assert(math.abs(totalMass(model)-352)<.001 and math.abs(totalMass(clone)-352)<.001)
local center,size=model:GetBoundingBox()
assert(size.X>=12 and size.Y>=4 and size.Z>=6)
print('Mass after variant update:',totalMass(model))
print('Copied title:',clone:GetAttribute('UI/title.Font'))
print('Bounds:',center.Position,size)
clone:Destroy();model:Destroy();variant:Destroy()
print('MATERIALS AND FONT EXAMPLE PASSED')
