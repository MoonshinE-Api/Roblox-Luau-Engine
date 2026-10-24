"""Verify documented fallback links without overriding dump-backed inheritance."""
import argparse,hashlib,json,sys,tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from run import bootstrap,execute_source
from vm_runtime import Runtime
p=argparse.ArgumentParser();p.add_argument('--binary',type=Path,default=Path('D:/Release-RobloxStudioApp/RobloxStudio.app/Contents/MacOS/RobloxStudio'));args=p.parse_args()
report=json.loads((root/'evidence/hierarchy_fallback.json').read_text(encoding='utf-8'))
catalog=json.loads((root/'evidence/class_catalog.json').read_text(encoding='utf-8'))['classes']
for name,parent in report['parents'].items():assert not catalog[name].get('parent') and parent in catalog
for name,expected in report['source_sha256'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==expected
runtime=Runtime(args.binary)
try:
    runtime.open_libraries()
    with tempfile.TemporaryDirectory(prefix='hierarchy-') as directory:
        work=Path(directory)
        execute_source(runtime,root,bootstrap(root,{'side':'server','duration':0,'testHierarchyFallback':report['parents']}),work,'bootstrap')
        execute_source(runtime,root,(root/'tests/hierarchy.luau').read_text(encoding='utf-8'),work,'hierarchy')
finally:runtime.close()
result={'status':'PASS','official_fallback_links':len(report['parents']),'dump_parent_links_preserved':report['source_parent_count'],
        'missing_parent_candidates_skipped':len(report['skipped_missing_runtime_parent']),
        'meaning':'Hierarchy only. No implementation is inferred for missing members.'}
(root/'evidence/hierarchy_comparison.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('HIERARCHY SOURCE/FALLBACK CHECKS PASSED')
