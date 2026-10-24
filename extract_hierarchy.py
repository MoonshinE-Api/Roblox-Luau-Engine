"""Fill missing class inheritance evidence using the pinned official reference."""
import hashlib,json
from pathlib import Path

def main():
    root=Path(__file__).resolve().parent
    catalog=json.loads((root/'evidence/class_catalog.json').read_text(encoding='utf-8'))
    reference=json.loads((root/'evidence/api_reference.json').read_text(encoding='utf-8'))
    classes=catalog['classes'];fallback={};skipped={}
    for name,doc in reference['classes'].items():
        if name in classes and not classes[name].get('parent') and doc.get('inherits'):
            parent=doc['inherits'][0]
            if parent not in classes:
                skipped[name]=parent;continue
            fallback[name]=parent
    merged={n:d['parent'] for n,d in classes.items() if d.get('parent')};merged.update(fallback)
    for name in classes:
        seen=set();current=name
        while current in merged:
            if current in seen:raise ValueError('Cyclic class inheritance: '+name)
            seen.add(current);current=merged[current]
    report={'runtime_version':catalog['version'],'reference_revision':reference['revision'],
        'documentation_studio_version':reference['documentation_studio_version'],
        'meaning':'Official reference fills only missing parent links. Supplied dump evidence always takes precedence. This does not implement missing members.',
        'source_parent_count':len(merged)-len(fallback),'fallback_parent_count':len(fallback),'parents':fallback,
        'skipped_missing_runtime_parent':skipped,
        'source_sha256':{name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in ('evidence/class_catalog.json','evidence/api_reference.json')}}
    (root/'evidence/hierarchy_fallback.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'source_parents':report['source_parent_count'],'official_fallback_parents':len(fallback),'acyclic':True}))

if __name__=='__main__':main()
