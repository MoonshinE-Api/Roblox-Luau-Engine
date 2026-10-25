"""Extract typed headless environment defaults and simple source-backed clamps."""
import argparse
import hashlib
import json
from pathlib import Path
import re

import msgpack
from extract_ui_catalog import extract

ROOT=Path(__file__).resolve().parents[1]
CLASSES=('Lighting','Light','PointLight','SpotLight','SurfaceLight','PostEffect',
         'BloomEffect','BlurEffect','ColorCorrectionEffect','DepthOfFieldEffect','SunRaysEffect',
         'Atmosphere','Sky','ParticleEmitter','Beam','Trail','Smoke','Fire','Sparkles')
NATIVE={'ParticleEmitter':'CustomParticleEmitter'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database',type=Path,required=True)
    parser.add_argument('--reference',type=Path,required=True)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--out',type=Path,default=ROOT/'data/environment_property_catalog.json')
    args=parser.parse_args()
    report=extract(args.database,args.reference,classes_to_extract=CLASSES,
                   representative={'Light':'PointLight','PostEffect':'BloomEffect'},
                   aliases={'Texture':'TextureContent','MoonTextureId':'MoonTextureContent','SunTextureId':'SunTextureContent',
                            'SkyboxBk':'SkyboxBackContent','SkyboxDn':'SkyboxDownContent','SkyboxFt':'SkyboxFrontContent',
                            'SkyboxLf':'SkyboxLeftContent','SkyboxRt':'SkyboxRightContent','SkyboxUp':'SkyboxUpContent'})
    _,database,*_=msgpack.unpackb(args.database.read_bytes(),raw=False,strict_map_key=False)
    default_time=report['classes']['Lighting']['TimeOfDay']['values']
    report['classes']['Lighting']['ClockTime']={'kind':'number','values':sum(float(v)*s for v,s in zip(default_time.split(':'),[1,1/60,1/3600])),
                                               'storage':'Float32','derived':'TimeOfDay'}
    report['skipped'].remove('Lighting.ClockTime: no default')
    evidence={};clamps={}
    number=r'(-?\d+(?:\.\d+)?(?:e[+-]?\d+)?)'
    for name,fields in report['classes'].items():
        for key,item in fields.items():item.setdefault('storage',database[name][3][key][2].get('Value','Enum'))
        native=NATIVE.get(name,name)
        candidates=[args.source/directory/(candidate+'Prop.c') for directory in ['rbx','v8datamodel'] for candidate in [native,name]]
        source=next((path for path in candidates if path.exists()),None)
        if source:
            raw=source.read_bytes();evidence[source.relative_to(args.source).as_posix()]=hashlib.sha256(raw).hexdigest()
            for section in raw.decode('utf-8',errors='replace').split('// Address:'):
                found=re.search(re.escape(source.stem)+r'::set([A-Z]\w*)\(',section)
                if not found:continue
                key=found[1]
                key={'IBLDiffuseScale':'EnvironmentDiffuseScale','IBLSpecularScale':'EnvironmentSpecularScale'}.get(key,key)
                if key.endswith('Ui') and key[:-2] in fields:key=key[:-2]
                if key not in fields or fields[key]['kind']!='number':continue
                bounds=re.search(r'fminf\('+number+r', fmaxf\('+number+r', \w+\)\)',section,re.I)
                if bounds:clamps.setdefault(name,{})[key]=[float(bounds[2]),float(bounds[1])]
                else:
                    for function,lower in [('fmaxf',True),('fminf',False)]:
                        bound=re.search(function+r'\('+number+r', \w+\)',section,re.I)
                        if not bound:bound=re.search(function+r'\(\w+, '+number+r'\)',section,re.I)
                        if bound:clamps.setdefault(name,{})[key]=[float(bound[1]),None] if lower else [None,float(bound[1])]
    # Light's nonnegative brightness transform is inherited by concrete lights.
    light=args.source/'v8datamodel/Light.c'
    raw=light.read_bytes();assert b'transformBrightnessCallback' in raw and b'fmaxf(0.0, a2)' in raw
    evidence['v8datamodel/Light.c']=hashlib.sha256(raw).hexdigest()
    clamps.setdefault('Light',{})['Brightness']=[0,None]
    beam=args.source/'rbx/BeamProp.c'
    raw=beam.read_bytes()
    assert b'::setSegments' in raw and b'result = 1000;' in raw and b'v7 = 1;' in raw
    clamps.setdefault('Beam',{})['Segments']=[1,1000]
    report.update(clamps=clamps,clamp_source_sha256=evidence,
                  limits='Typed headless configuration, source-backed scalar clamps and float32 storage. No rendering, particle simulation or asset textures. Defaults use reflection build 741; engine behavior targets build 735.')
    args.out.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'classes':len(report['classes']),'declarations':sum(map(len,report['classes'].values())),
                      'scalar_clamps':sum(map(len,clamps.values())),'skipped':report['skipped']}))


if __name__=='__main__':main()
