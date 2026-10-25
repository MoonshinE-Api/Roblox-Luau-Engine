"""Snapshot supported model property types from the implemented runtime itself."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
from run import bootstrap,execute_source,lua_literal
from vm_runtime import Runtime

CLASSES=['ModuleScript','Script','LocalScript','Folder','Model','Part','Configuration',
    'BoolValue','NumberValue','IntValue','StringValue','ObjectValue','Vector3Value',
    'CFrameValue','Color3Value','BrickColorValue','Camera','Humanoid',
    'BindableEvent','BindableFunction','RemoteEvent','RemoteFunction','MaterialVariant','WedgePart','CornerWedgePart']
CLASSES+=['ScreenGui','Frame','CanvasGroup','TextLabel','TextButton','TextBox','ImageLabel','ImageButton',
    'ScrollingFrame','ViewportFrame','UICorner','UIStroke','UIGradient','UIScale','UIPadding',
    'UISizeConstraint','UIAspectRatioConstraint','UITextSizeConstraint','UIListLayout','UIGridLayout']
CLASSES+=['Attachment','Bone','RopeConstraint','PointLight','SpotLight','SurfaceLight','BloomEffect','BlurEffect',
    'ColorCorrectionEffect','DepthOfFieldEffect','SunRaysEffect','Atmosphere','Sky','ParticleEmitter','Beam','Trail','Smoke','Fire','Sparkles']

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binary',type=Path,default=Path('D:/Release-RobloxStudioApp/RobloxStudio.app/Contents/MacOS/RobloxStudio'))
    args=parser.parse_args();root=Path(__file__).resolve().parents[1]
    runtime=Runtime(args.binary)
    try:
        runtime.open_libraries()
        with tempfile.TemporaryDirectory(prefix='model-schema-') as directory:
            working=Path(directory)
            execute_source(runtime,root,bootstrap(root,{'side':'server','duration':0}),working,'bootstrap')
            source='''local R=__engine;local classes={}
for _,name in CLASSES do
    assert(R.knownClasses[name],name)
    local object=R.new(name,nil,true)
    classes[name]=table.clone(R.instances[object].propertyTypes)
end
classes.Part.Position='Vector3';classes.Part.BrickColor='BrickColor'
for _,name in {'TextLabel','TextButton','TextBox'} do classes[name].Font='Enum.Font' end
return R.jsonEncode(classes)'''.replace('CLASSES',lua_literal(CLASSES))
            classes=json.loads(execute_source(runtime,root,source,working,'schema')[0])
    finally:runtime.close()
    # Empty Lua dictionaries serialize as [], normalize before publishing.
    classes={key:(value or {}) for key,value in classes.items()}
    report={'meaning':'Explicit import class allowlist; property types observed from implemented runtime, not full engine support.',
        'runtime_version':'0.735.19.7351131','classes':classes,
        'source_sha256':{name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in ('engine/instances.luau','engine/services.luau','engine/callbacks.luau','engine/attachments.luau','engine/environment.luau','engine/sky.luau','engine/ui.luau','engine/ui_layout.luau','engine/camera.luau','data/ui_property_catalog.json','data/environment_property_catalog.json')}}
    (root/'data/model_property_schema.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'classes':len(classes),'property_declarations':sum(len(x) for x in classes.values())}))

if __name__=='__main__':main()
