"""Compare finite constructor/clamp values with unchanged original x64 functions."""
import argparse
import ctypes as C
import json
from pathlib import Path
import random
import struct
import tempfile
from macho import MachO
from original import Original
from run import bootstrap,execute_source,lua_literal
from vm_runtime import Runtime

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--binary',type=Path,default=Path('D:/Release-RobloxStudioApp/RobloxStudio.app/Contents/MacOS/RobloxStudio'))
    args=p.parse_args();root=Path(__file__).resolve().parent
    report=json.loads((root/'data/physical_recovery.json').read_text(encoding='utf-8'))
    rng=random.Random(735);inputs=[]
    for _ in range(1000):inputs.append([rng.uniform(-10,120),rng.uniform(-2,4),rng.uniform(-1,2),rng.uniform(-5,110),rng.uniform(-5,110),rng.uniform(-1,2)])
    inputs += [[0,0,0,0,0,0],[100,2,1,100,100,1],[.7,.3,.5,1,1,1],[1e300,-1e300,1e-300,1e300,-1e300,1e300]]
    for field in range(6):
        for value in (-1,0,.00009999999,.0001,.00010000001,.99999999,1,1.00000001,2,100,100.00001):
            row=[1,.5,.5,1,1,.5];row[field]=value;inputs.append(row)
    answers=[];indices={};geometries=[]
    dll=C.CDLL(str(root/'vm0735.dll'))
    dll.original_call_physical.argtypes=[C.c_size_t,C.c_void_p]+[C.c_float]*6;dll.original_call_physical.restype=None
    with MachO(args.binary) as binary:
        with Original(binary,report,dll,enabled=Original.ENGINE_PHYSICAL) as image:
            function=image.functions['physical_constructor']+image.slide
            for row in inputs:
                output=C.create_string_buffer(28)
                dll.original_call_physical(function,output,*row)
                assert output.raw[0]==1
                values=struct.unpack_from('<6f',output.raw,4)
                answers.append([values[i] for i in (0,2,1,3,4,5)])
            for name,record in report['materials'].items():
                index=image.call_u('material_index',record['enum_value'],0)
                assert index==record['native_index'];indices[name]=index
            for kind,name in enumerate(('Ball','Cylinder','Block','Wedge','CornerWedge')):
                output=C.create_string_buffer(52)
                image.call_u('physical_unit_inertia',C.addressof(output),kind)
                volume,*center=struct.unpack_from('<4f',output.raw)
                assert volume==report['unit_volume'].get(name,1)
                assert center==report['unit_center'].get(name,[0,0,0])
                geometries.append(name)
    runtime=Runtime(args.binary)
    try:
        runtime.open_libraries()
        with tempfile.TemporaryDirectory(prefix='physical-oracle-') as directory:
            working=Path(directory);execute_source(runtime,root,bootstrap(root,{'side':'server','duration':0}),working,'bootstrap')
            source='local cases='+lua_literal([list(row) for row in zip(inputs,answers)])+'''
local savedWarn=warn;warn=function()end
local fields={'Density','Friction','Elasticity','FrictionWeight','ElasticityWeight','AcousticAbsorption'}
for i,row in cases do
    local value=PhysicalProperties.new(table.unpack(row[1]))
    for j,key in fields do assert(value[key]==row[2][j],'Native constructor mismatch '..i..' '..key) end
end
for _,material in Enum.Material:GetEnumItems() do
    local expected=__engine.physicalCatalog.materials[material.Name].properties
    local value=PhysicalProperties.new(material)
    for j,key in fields do assert(value[key]==expected[j],'Material mismatch '..material.Name..' '..key)end
end
warn=savedWarn
return true
'''
            assert execute_source(runtime,root,source,working,'physical-vectors')==[True]
    finally:runtime.close()
    result={'status':'PASS','original_constructor_cases':len(inputs),'original_material_indices':len(indices),
        'binary_material_vectors_verified':report['verified_binary_argument_vectors'],'original_unit_geometry':geometries,
        'original_function_bytes_unchanged':True,
        'limits':['Lua bridge nonnumeric/NaN coercion and warning text are not compared.','MaterialVariant precedence and mass calculations have separate semantic tests.']}
    (root/'data/physical_comparison.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))

if __name__=='__main__':main()
