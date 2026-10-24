"""Bind validation to the code, binaries, and fixed evidence it actually read."""
import argparse
from datetime import datetime,timezone
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SNAPSHOT='evidence/validation_inputs.json'
OUTPUTS={'BUILD.json',SNAPSHOT,'evidence/runtime_capabilities.json','evidence/api_coverage.json',
    'evidence/differential.json','evidence/bootstrap.json','evidence/allocator.json','evidence/initialization.json'}


def inputs(root=ROOT):
    result={}
    for path in sorted(root.rglob('*')):
        if not path.is_file() or any(part in {'__pycache__','target'} for part in path.relative_to(root).parts):continue
        relative=path.relative_to(root).as_posix()
        if relative in OUTPUTS or path.name.endswith('_comparison.json'):continue
        if path.suffix in {'.py','.lua','.luau','.ps1','.rs','.toml','.lock','.exe','.dll'} or (path.suffix=='.json' and relative.startswith('evidence/')):
            result[relative]=hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def verify(root=ROOT,require_complete=True):
    record=json.loads((root/SNAPSHOT).read_text(encoding='utf-8'))
    if require_complete and not record.get('complete'):raise ValueError('Validation did not complete')
    current=inputs(root);expected=record['files']
    changed=sorted(key for key in current.keys()|expected.keys() if current.get(key)!=expected.get(key))
    if changed:raise ValueError('Validation inputs changed: '+', '.join(changed[:12]))
    return record


def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['start','finish']);args=parser.parse_args()
    if args.action=='start':
        record={'started_utc':datetime.now(timezone.utc).isoformat(),'complete':False,'files':inputs()}
    else:
        record=verify(require_complete=False);record['complete']=True;record['finished_utc']=datetime.now(timezone.utc).isoformat()
    (ROOT/SNAPSHOT).write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    print(f'Validation input hashes: {len(record["files"])}; complete={record["complete"]}')


if __name__=='__main__':main()
