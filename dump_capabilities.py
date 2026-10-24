"""Read the actual runtime declarations; names are not a claim of full Roblox behavior."""
import argparse
import json
from pathlib import Path
import tempfile

from run import bootstrap,execute_source
from vm_runtime import Runtime

PROBE=r'''
local R=__engine
local lines={}
local function row(kind,owner,member,value)
    local text=tostring(value or ""):gsub("\t","\\t"):gsub("\n","\\n"):gsub("\r","\\r")
    table.insert(lines,kind.."\t"..owner.."\t"..member.."\t"..text)
end
for key,value in getfenv() do
    if not key:match("^__") then row("global","",key,typeof(value)) end
end
row("global","","script","Instance (per script environment)")
for _,name in {"bit32","buffer","coroutine","debug","math","os","string","table","task","utf8","vector"} do
    local library=getfenv()[name]
    if type(library)=="table" then for key,value in library do row("library",name,key,typeof(value)) end end
end
for name,library in R.datatypes do for key,value in library do row("constructor",name,key,typeof(value)) end end
for key in R.instanceMethods do row("instance","Instance",key,"method") end
for name in R.serviceClasses do row("service",name,"","") end
for _,registry in {{"method",R.classMethods},{"getter",R.classGetters},{"setter",R.classSetters},{"event",R.classEvents}} do
    for class,members in registry[2] do for member in members do row(registry[1],class,member,"") end end
end
for name in R.knownClasses do
    row("class",name,"parent",R.classes[name] or "")
    row("class",name,"creation",if R.noncreatable[name] then "not directly creatable" else "permitted by current runtime (native rules incomplete)")
    local object=R.new(name,nil,true)
    for key,kind in R.instances[object].propertyTypes do row("property",name,key,kind.." = "..tostring(R.instances[object].props[key])) end
end
return table.concat(lines,"\n")
'''


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binary',type=Path,default=Path(r'D:/Release-RobloxStudioApp/RobloxStudio.app/Contents/MacOS/RobloxStudio'))
    args=parser.parse_args()
    root=Path(__file__).resolve().parent
    runtime=Runtime(args.binary)
    try:
        runtime.open_libraries()
        with tempfile.TemporaryDirectory(prefix='capabilities-') as folder:
            working=Path(folder)
            execute_source(runtime,root,bootstrap(root,{'side':'server','duration':0}),working,'engine-bootstrap')
            rows=execute_source(runtime,root,PROBE,working,'capability-inventory')[0].splitlines()
    finally:runtime.close()
    assert not runtime.owned and not runtime.backing_errors
    inventory={}
    for line in rows:
        kind,owner,member,value=line.split('\t',3)
        inventory.setdefault(kind,{}).setdefault(owner,{})[member]=value
    inventory={kind:{owner:dict(sorted(members.items())) for owner,members in sorted(owners.items())}
               for kind,owners in sorted(inventory.items())}
    (root/'evidence/runtime_capabilities.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# Current runtime declaration inventory','',
           'Observed from a running VM. A declared name does not guarantee full Roblox semantics.',
           'Behavior and limits: CAPABILITIES.md.', '',
           '## Global names','',', '.join('`'+x+'`' for x in inventory['global'][''])+'.', '',
           '## Libraries: observed members','']
    for name,members in inventory['library'].items():
        lines += ['### '+name,'',', '.join('`'+x+'`' for x in members)+'.','']
    lines += ['## Exported datatype constructors and constants','']
    for name,members in inventory['constructor'].items():
        lines += ['- **'+name+'**: '+', '.join('`'+x+'`' for x in members)+'.']
    lines += ['','## Methods, getters, setters, and events by owner','',
              'This lists explicit declarations. Inheritance adds shared Instance members.',
              'Events such as Touched/PlayerAdded may be declared without a physics/network producer.','']
    owners=set().union(*(inventory[kind].keys() for kind in ('instance','method','getter','setter','event')))
    for name in sorted(owners):
        lines += ['### '+name,'']
        for kind in ('instance','method','getter','setter','event'):
            members=inventory.get(kind,{}).get(name,{})
            if members:lines += ['- '+kind+': '+', '.join('`'+x+'`' for x in members)+'.']
        lines += ['']
    lines += ['## Service names accepted by GetService','',
              'Most are containers. This list does not imply implemented APIs for every service.','',
              ', '.join('`'+x+'`' for x in inventory['service'])+'.','',
              '## Known classes and implemented properties','',
              'This combines class metadata with runtime fields. Many classes only have Instance behavior.',
              'Native creation rules, abstractness, and defaults remain incomplete.','']
    for name,metadata in inventory['class'].items():
        lines += ['### '+name,'',f"Parent class: `{metadata['parent']}`; creation: {metadata['creation']}.",'']
        props=inventory['property'].get(name,{})
        if props:
            lines += ['| Property | Current type/default |','| --- | --- |']
            lines += [f'| `{key}` | `{value}` |' for key,value in props.items()]
            lines += ['']
        else:lines += ['Only base Instance properties and separately declared members/getters.','']
    enums=json.loads((root/'evidence/enum_catalog.json').read_text(encoding='utf-8'))['enums']
    lines += ['## Enum catalog: names and values','',
              '620 types and 3585 items from the target build. Enum presence does not implement the related engine behavior.','']
    for name,members in sorted(enums.items()):
        lines += ['### Enum.'+name,'',', '.join(f'`{key}={value}`' for key,value in sorted(members.items(),key=lambda x:(x[1],x[0])))+'.','']
    (root/'RUNTIME_INVENTORY.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'globals':len(inventory['global']['']),'libraries':{name:len(x) for name,x in inventory['library'].items()},
                      'known_classes':len(inventory['class']),'enum_types':len(enums),'enum_items':sum(map(len,enums.values()))}))


if __name__=='__main__':main()
