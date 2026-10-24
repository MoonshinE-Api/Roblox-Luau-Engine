local R=__engine
local fallback=R.config.testHierarchyFallback
if fallback then
    for class,parent in fallback do
        local value=R.new(class,nil,true)
        assert(value:IsA(parent),class..' should inherit '..parent)
        value:Destroy()
    end
end
assert(Instance.new('WedgePart'):IsA('FormFactorPart'))
assert(Instance.new('CornerWedgePart'):IsA('BasePart'))
assert(Instance.new('Attachment'):IsA('Instance'))
print('HIERARCHY FALLBACK CHECKS PASSED')
