"""Extract editor names and C++ inheritance hints without reading entire large dumps.

ReflectionMetadata is editor metadata, not a complete API schema. Inheritance is
read only from explicit Described<Child,Parent> constructor template evidence.
"""
import argparse
import json
from pathlib import Path
import re
import xml.etree.ElementTree as E


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--dump',type=Path,required=True)
    p.add_argument('--metadata',type=Path,required=True)
    p.add_argument('--out',type=Path,default=Path(__file__).parent/'evidence/class_catalog.json')
    args=p.parse_args()
    classes={}
    root=E.parse(args.metadata).getroot()
    for element in root.findall('.//Item[@class="ReflectionMetadataClass"]'):
        name=element.find('./Properties/string[@name="Name"]')
        if name is None or not name.text:continue
        groups={}
        for group in element.findall('./Item'):
            groups[group.get('class')]=[s.text for s in group.findall('./Item/Properties/string[@name="Name"]')]
        classes[name.text]={'editor_members':groups}
    pattern=re.compile(r'RBX::(?:Described|DescribedCreatable|DescribedNonCreatable)<RBX::(\w+),RBX::(\w+)>')
    parents={};bytes_read=0;files_read=0
    for folder in ['rbx','v8datamodel','v8tree','script','humanoid','network']:
        for path in (args.dump/folder).glob('*.c'):
            with path.open('rb') as stream:data=stream.read(96*1024)
            bytes_read+=len(data);files_read+=1
            text=data.decode('utf-8','replace')
            for match in pattern.finditer(text):
                child,parent=match.groups()
                if child not in parents:
                    parents[child]={'parent':parent,'source':str(path.relative_to(args.dump)).replace('\\','/'),
                                    'line':text.count('\n',0,match.start())+1}
    aliases={'ModelInstance':'Model','MegaClusterInstance':'Terrain','HumanoidImpl':'Humanoid'}
    for child,evidence in parents.items():
        public=aliases.get(child,child)
        classes.setdefault(public,{})
        classes[public].update(parent=aliases.get(evidence['parent'],evidence['parent']),inheritance_evidence=evidence)
    result={'version':'0.735.19.7351131','classes':classes,'editor_class_count':len(root.findall('.//Item[@class="ReflectionMetadataClass"]')),
            'inheritance_pairs':len(parents),'bounded_source_files':files_read,'bounded_source_bytes':bytes_read,
            'limits':['Editor membership is incomplete','Inheritance hints are not instantiability, security, defaults or complete behavior']}
    args.out.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='classes'},indent=2))


if __name__=='__main__':main()
