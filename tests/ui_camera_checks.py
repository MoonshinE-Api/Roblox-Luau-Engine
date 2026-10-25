"""Non-default viewport, GUI inset, camera FOV and scalar UI import checks."""
import argparse
import json
import math
from pathlib import Path
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from run import bootstrap,execute_source,lua_literal
from vm_runtime import Runtime


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--binary',default='D:/Release-RobloxStudioApp/RobloxStudio.app/Contents/MacOS/RobloxStudio')
    args=parser.parse_args()
    def invalid_constant(value):raise ValueError('Non-standard JSON number '+value)
    json.loads((ROOT/'data/ui_property_catalog.json').read_text(),parse_constant=invalid_constant)
    runtime=Runtime(args.binary)
    try:
        runtime.open_libraries()
        with tempfile.TemporaryDirectory(prefix='ui-insets-') as folder:
            work=Path(folder)
            numbers=execute_source(runtime,ROOT,'return '+','.join(lua_literal(v) for v in [float('inf'),float('-inf'),float('nan')]),work,'numeric-constants')
            assert numbers[0]==float('inf') and numbers[1]==float('-inf') and math.isnan(numbers[2])
            execute_source(runtime,ROOT,bootstrap(ROOT,{'side':'client','duration':0,'viewportSize':[800,600],'guiInset':[0,36]}),work,'bootstrap')
            execute_source(runtime,ROOT,'''local c=workspace.CurrentCamera
c.CFrame=CFrame.new();c.FieldOfView=90
assert(c.ViewportSize==Vector2.new(800,600))
local p,ok=c:WorldToScreenPoint(Vector3.new(0,0,-10))
assert(ok and (p-Vector3.new(400,264,10)).Magnitude<1e-8)
local ray=c:ScreenPointToRay(400,264)
assert((ray.Direction-Vector3.new(0,0,-1)).Magnitude<1e-8)
local screen=Instance.new('ScreenGui',game:GetService('Players').LocalPlayer.PlayerGui)
assert(screen.AbsolutePosition==Vector2.new(0,36) and screen.AbsoluteSize==Vector2.new(800,564))
screen.IgnoreGuiInset=true
assert(screen.AbsolutePosition==Vector2.zero and screen.AbsoluteSize==Vector2.new(800,600))
screen.ScreenInsets=Enum.ScreenInsets.CoreUISafeInsets
assert(not screen.IgnoreGuiInset and screen.AbsolutePosition.Y==36)
local changed=0
c:GetPropertyChangedSignal('ViewportSize'):Connect(function() changed+=1 end)
workspace.CurrentCamera=nil
assert(changed==1 and c.ViewportSize==Vector2.one)
workspace.CurrentCamera=c
assert(changed==2 and c.ViewportSize==Vector2.new(800,600))
return true
''',work,'inset-checks')
    finally:runtime.close()
    assert not runtime.owned and not runtime.backing_errors
    print('UI/CAMERA INSET, VIEWPORT AND CLEANUP CHECKS PASSED')


if __name__=='__main__':main()
