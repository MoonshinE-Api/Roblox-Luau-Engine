"""Bundle compiled tools and generated metadata for checked-in distribution."""
import hashlib,json,zipfile
from pathlib import Path

GROUPS={
    'asset-codec.zip':['recovery-asset-codec.exe'],
    'vm-and-compiler.zip':['vm0735.dll','recovery-luau-compile.exe'],
    'reference-metadata.zip':['evidence/api_reference.json','evidence/datetime_format_vectors.json',
        'evidence/enum_catalog.json','evidence/recovery.json','evidence/vm_core.json'],
}


def main():
    root=Path(__file__).resolve().parent;directory=root/'bundled';directory.mkdir(exist_ok=True)
    manifest={'format':1,'archives':{}}
    for name,files in GROUPS.items():
        path=directory/name;entries={}
        # Stable timestamps keep unchanged bundles reproducible.
        with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
            for relative in files:
                data=(root/relative).read_bytes();info=zipfile.ZipInfo(relative,date_time=(2026,1,1,0,0,0))
                info.compress_type=zipfile.ZIP_DEFLATED;archive.writestr(info,data,compresslevel=9)
                entries[relative]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
        manifest['archives'][name]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'files':entries}
        print(f'{name}: {path.stat().st_size} bytes, {len(files)} files')
    (directory/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')


if __name__=='__main__':main()
