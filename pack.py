"""Package the current project and verification evidence, excluding supplied Studio files."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import os
import shutil
import tempfile
import zipfile
from validation_inputs import verify


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--validation-log',type=Path,required=True)
    parser.add_argument('--binary',type=Path,default=Path(r'D:/Release-RobloxStudioApp/RobloxStudio.app/Contents/MacOS/RobloxStudio'))
    args=parser.parse_args()
    root=Path(__file__).resolve().parent
    verified=verify(root)
    log=args.validation_log.read_text(encoding='utf-8-sig')
    if 'All eight differential checks and thirty-five runtime/CLI checks passed.' not in log:
        raise ValueError('Validation log has no complete success result')
    shutil.copyfile(args.validation_log,root/'evidence/validation.txt')
    with args.binary.open('rb') as source:
        original_hash=hashlib.file_digest(source,'sha256').hexdigest()
    if original_hash!='6b01d19b7fdfab0528621680e0b8760aa10c54fc917c79bf1f1f6eb92c373b6d':
        raise ValueError('Unexpected source binary')
    def included(path):
        return (path.is_file() and '__pycache__' not in path.parts and 'target' not in path.parts
                and path.suffix not in {'.pdb','.lib','.exp','.pyc','.zip','.dpapi'} and path.name not in {'BUILD.json','.env'})
    files=sorted(path for path in root.rglob('*') if included(path))
    manifest={
        'generated_utc':datetime.now(timezone.utc).isoformat(),
        'python':platform.python_version(),
        'architecture':'Original Luau 0.735 image adapter, Rust host ABI bridge, developing Luau Engine API',
        'full_roblox_compatibility':False,
        'original_binary':{'path':str(args.binary),'bytes':args.binary.stat().st_size,'sha256':original_hash,'included':False},
        'validation':'Eight differential suites and thirty-five runtime/CLI scenarios passed; see evidence/validation.txt',
        'validated_input_hashes':len(verified['files']),
        'files':{str(path.relative_to(root)).replace('\\','/'):hashlib.sha256(path.read_bytes()).hexdigest() for path in files},
    }
    (root/'BUILD.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    destination=root.parent/(root.name+'.zip')
    # Cargo registry sources can carry normalized 1970 timestamps. Clamp ZIP
    # dates without changing the source files, and publish only a verified ZIP.
    with tempfile.NamedTemporaryFile(prefix=root.name+'-',suffix='.zip',dir=destination.parent,delete=False) as temp:
        temporary=Path(temp.name)
    try:
        with zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED,strict_timestamps=False) as archive:
            for path in files+[root/'BUILD.json']:
                archive.write(path,root.name+'/'+path.relative_to(root).as_posix())
        with zipfile.ZipFile(temporary) as archive:
            assert archive.testzip() is None
        os.replace(temporary,destination)
    finally:temporary.unlink(missing_ok=True)
    print(json.dumps({'archive':str(destination),'bytes':destination.stat().st_size,'files':len(files)+1}))


if __name__=='__main__':
    main()
