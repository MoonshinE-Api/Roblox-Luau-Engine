"""Compare UDim offsets with lua_tointegerx in the supplied original VM."""
import argparse
import ctypes
from pathlib import Path
import random
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from run import bootstrap,compile_source,execute_source
from vm_runtime import Runtime


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--binary',default='D:/Release-RobloxStudioApp/RobloxStudio.app/Contents/MacOS/RobloxStudio')
    args=parser.parse_args()
    expressions=['1.9','-1.9','2147483647','2147483648','4294967299','-2147483649',
        'math.huge','-math.huge','0/0',"'12.9'",'false','{}','nil','-2147483648.9','2147483647.9']
    rng=random.Random(735)
    expressions.extend(repr(rng.uniform(-3e9,3e9)) for _ in range(80))
    runtime=Runtime(args.binary)
    try:
        runtime.open_libraries()
        symbol=next(name for name in runtime.functions if name.startswith('__Z14lua_tointegerx'))
        with tempfile.TemporaryDirectory(prefix='native-int32-') as folder:
            work=Path(folder)
            runtime.load(compile_source(ROOT,'return '+','.join(expressions),work,'native-int32'))
            assert runtime.execute()==0
            native=[ctypes.c_int32(runtime.image.call3(symbol,runtime.state,i,0)).value for i in range(1,len(expressions)+1)]
            runtime.image.call('__Z10lua_settopP9lua_Statei',runtime.state,argument=0)
            execute_source(runtime,ROOT,bootstrap(ROOT,{'side':'server','duration':0}),work,'bootstrap')
            offsets=execute_source(runtime,ROOT,'return '+','.join('UDim.new(0,'+v+').Offset' for v in expressions),work,'udim-offsets')
            assert offsets==native,[(e,a,b) for e,a,b in zip(expressions,offsets,native) if a!=b]
            expected=[ctypes.c_int16(v).value for v in native]
            for vector in ['Vector2int16','Vector3int16']:
                offsets=execute_source(runtime,ROOT,'return '+','.join(vector+'.new('+v+').X' for v in expressions),work,vector)
                assert offsets==expected,vector
    finally:runtime.close()
    assert not runtime.owned and not runtime.backing_errors
    print('UDIM AND INT16 VECTORS / ORIGINAL VM CONVERSION CHECKS PASSED',len(expressions)*3)


if __name__=='__main__':main()
