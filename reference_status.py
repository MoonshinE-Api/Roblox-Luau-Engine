"""Report declared runtime surfaces against official signatures, without claiming parity."""
import argparse
import json
import re
from pathlib import Path
import tempfile

from run import bootstrap, execute_source, lua_literal
from vm_runtime import Runtime


def member_name(name):
    return re.split(r'[.:]',name)[-1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binary', type=Path, default=Path(r'D:/Release-RobloxStudioApp/RobloxStudio.app/Contents/MacOS/RobloxStudio'))
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    reference = json.loads((root/'evidence/api_reference.json').read_text(encoding='utf-8'))
    globals_ = sorted({m['name'] for doc in reference['globals'].values()
                       for category in ('functions', 'properties') for m in doc.get(category, [])})
    libraries = {name: sorted({m['name'].split('.')[-1] for category in ('functions', 'properties')
                              for m in doc.get(category, [])}) for name, doc in reference['libraries'].items()}
    probe = r'''
local R=__engine
local result={}
local function row(kind,owner,member) table.insert(result,kind.."\t"..owner.."\t"..member) end
for name,library in R.datatypes do
    row("datatype",name,"")
    for key in library do row("export",name,key) end
end
for _,name in {"Instance","Enum","EnumItem","Enums","RBXScriptSignal","RBXScriptConnection"} do row("datatype",name,"") end
if R.classMethods.WorldRoot and R.classMethods.WorldRoot.Raycast then row("datatype","RaycastResult","") end
for key in Instance do row("export","Instance",key) end
for _,name in GLOBALS do
    if name=="script" or getfenv()[name]~=nil then row("global",name,"") end
end
for name,members in LIBRARIES do
    local library=getfenv()[name]
    if type(library)=="table" then
        for _,member in members do if library[member]~=nil then row("library",name,member) end end
    end
end
for name in R.knownClasses do
    local object=R.new(name,nil,true)
    local declared={Name=true,Parent=true,ClassName=true,Archivable=true,Changed=true,ChildAdded=true,ChildRemoved=true,
        DescendantAdded=true,DescendantRemoving=true,AncestryChanged=true,Destroying=true,AttributeChanged=true}
    for member in R.instanceMethods do declared[member]=true end
    for member in R.instances[object].propertyTypes do declared[member]=true end
    local class,seen=name,{}
    while class and not seen[class] do
        seen[class]=true
        for _,registry in {R.classMethods,R.classGetters,R.classSetters,R.classEvents} do
            for member in registry[class] or {} do declared[member]=true end
        end
        class=R.classes[class]
    end
    row("class",name,"")
    for member in declared do row("member",name,member) end
end
return table.concat(result,"\n")
'''.replace('GLOBALS', lua_literal(globals_)).replace('LIBRARIES', lua_literal(libraries))
    runtime = Runtime(args.binary)
    try:
        runtime.open_libraries()
        with tempfile.TemporaryDirectory(prefix='reference-status-') as directory:
            working = Path(directory)
            execute_source(runtime, root, bootstrap(root, {'side':'server','duration':0}), working, 'engine-bootstrap')
            rows = execute_source(runtime, root, probe, working, 'reference-probe')[0].splitlines()
    finally:
        runtime.close()
    assert not runtime.owned and not runtime.backing_errors
    observed = {}
    for row in rows:
        kind, owner, member = row.split('\t')
        observed.setdefault(kind, {}).setdefault(owner, set()).add(member)
    types = {}
    for name, doc in reference['datatypes'].items():
        available = observed.get('export', {}).get(name, set())
        constructors = sorted({m['name'].split('.')[-1] for m in doc.get('constructors', [])})
        types[name] = {
            'status': 'partial' if name in observed['datatype'] else 'missing',
            'constructor_names_present': sorted(set(constructors) & available),
            'constructor_names_missing': sorted(set(constructors) - available),
            'note': 'Name presence only; overloads and behavioral equivalence require separate tests.',
        }
    classes = {}
    for name, doc in reference['classes'].items():
        available = observed.get('member', {}).get(name, set())
        declared = sorted({member_name(m['name']) for category in ('properties','methods','events','callbacks')
                           for m in doc.get(category, [])})
        classes[name] = {'class_known': name in observed['class'],
                         'declared_member_names_present': sorted(set(declared) & available),
                         'declared_member_names_missing': sorted(set(declared) - available)}
    source_enums = json.loads((root/'evidence/enum_catalog.json').read_text(encoding='utf-8'))['enums']
    members_present=sum(len(x['declared_member_names_present']) for x in classes.values())
    members_total=members_present+sum(len(x['declared_member_names_missing']) for x in classes.values())
    output = {
        'reference_revision': reference['revision'],
        'documentation_studio_version': reference['documentation_studio_version'],
        'runtime_studio_version': reference['runtime_studio_version'],
        'meaning': 'Observed declaration names, not full compatibility. Every present type remains partial; no behavior is inferred from documentation.',
        'datatypes': types,
        'classes': classes,
        'declaration_metrics':{'class_member_names_present':members_present,
            'class_member_names_documented':members_total,
            'class_member_name_presence_percent':round(100*members_present/members_total,2),
            'meaning':'Name declarations only; not behavioral completeness or overall engine progress.'},
        'global_names_present': sorted(observed['global']),
        'global_names_missing': sorted(set(globals_) - observed['global'].keys()),
        'libraries': {name:{'names_present': sorted(observed.get('library',{}).get(name,set())),
                           'names_missing': sorted(set(members)-observed.get('library',{}).get(name,set()))}
                      for name,members in libraries.items()},
        'enum_names_only_in_docs': sorted(set(reference['enums'])-source_enums.keys()),
        'enum_names_only_in_build': sorted(set(source_enums)-reference['enums'].keys()),
    }
    (root/'evidence/api_coverage.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines = ['# API status against the official reference', '',
             'Name presence indicates declarations only. Full behavior is not established.', '',
             f"Documentation: `{reference['documentation_studio_version'].splitlines()[0]}`; runtime: `0.735.19.7351131`.", '',
             '| Datatype | Status | Observed constructors |', '| --- | --- | --- |']
    for name, record in types.items():
        lines.append(f"| {name} | {'partial' if record['status']=='partial' else 'missing'} | {', '.join(record['constructor_names_present'])} |")
    lines += ['', 'Missing global names: '+', '.join(output['global_names_missing'])+'.', '',
              f'Declared {members_present} of {members_total} documented class-member names ({100*members_present/members_total:.2f}%).',
              'This measures name declarations, not full compatibility or overall engine completion.', '',
              'Detailed class/library gaps: `evidence/api_coverage.json`.',
              'Signatures and sources: `evidence/api_reference.json`.']
    (root/'API_STATUS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'documented_types': len(types), 'types_partial': sum(x['status']=='partial' for x in types.values()),
                      'documented_classes':len(classes), 'globals_missing':output['global_names_missing']},ensure_ascii=False))


if __name__=='__main__':
    main()
