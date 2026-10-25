"""Extract supported UI configuration defaults from an explicit reflection database.

The database version is recorded separately from the VM version. This produces
typed configuration data, not a renderer or a claim of behavioral equivalence.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

import msgpack
import yaml

ROOT = Path(__file__).resolve().parents[1]
CLASSES = ('GuiBase2d', 'LayerCollector', 'GuiObject', 'GuiButton', 'Frame',
           'CanvasGroup', 'ScreenGui', 'TextLabel', 'TextButton', 'TextBox',
           'ImageLabel', 'ImageButton', 'ScrollingFrame', 'ViewportFrame',
           'UICorner', 'UIStroke', 'UIGradient', 'UIScale', 'UIPadding',
           'UISizeConstraint', 'UIAspectRatioConstraint', 'UITextSizeConstraint',
           'UIGridStyleLayout', 'UIListLayout', 'UIGridLayout')
SUPPORTED = {'Bool': 'boolean', 'String': 'string', 'Content': 'string',
             'Float32': 'number', 'Float64': 'number', 'Int32': 'number',
             'Vector2': 'Vector2', 'Vector3': 'Vector3', 'Color3': 'Color3',
             'UDim': 'UDim', 'UDim2': 'UDim2', 'Rect': 'Rect',
             'NumberSequence': 'NumberSequence', 'ColorSequence': 'ColorSequence',
             'Font': 'Font', 'NumberRange': 'NumberRange', 'BrickColor': 'BrickColor'}
REPRESENTATIVE = {'GuiBase2d': 'Frame', 'LayerCollector': 'ScreenGui',
                  'GuiObject': 'Frame', 'GuiButton': 'TextButton', 'UIGridStyleLayout': 'UIListLayout'}
ALIASES = {'InputSink': 'Sink', 'Image': 'ImageContent', 'HoverImage': 'HoverImageContent',
           'PressedImage': 'PressedImageContent', 'BottomImage': 'BottomImageContent',
           'MidImage': 'MidImageContent', 'TopImage': 'TopImageContent',
           'CornerRadius': 'TopLeftRadius'}


def extract(database, reference, *, classes_to_extract=None, representative=None, aliases=None):
    selection=CLASSES if classes_to_extract is None else tuple(classes_to_extract)
    representative=REPRESENTATIVE if representative is None else representative
    aliases=ALIASES if aliases is None else aliases
    raw = database.read_bytes()
    version, classes, *_ = msgpack.unpackb(raw, raw=False, strict_map_key=False)
    enums = json.loads((ROOT/'data/enum_catalog.json').read_text(encoding='utf-8'))['enums']
    known = json.loads((ROOT/'data/class_catalog.json').read_text(encoding='utf-8'))['classes']
    result, skipped = {}, []
    for name in selection:
        assert name in known, name
        doc = yaml.safe_load((reference/'classes'/f'{name}.yaml').read_text(encoding='utf-8'))
        public = {p['name'].split('.', 1)[1]: p for p in doc.get('properties', [])}
        declarations = {}
        for key, descriptor in classes[name][3].items():
            field = public.get(key)
            if (not field or descriptor[1] != 'ReadWrite' or
                    field.get('security', {}).get('write') != 'None' or
                    any(tag in field.get('tags', []) for tag in ('Deprecated', 'Hidden', 'NotScriptable'))):
                continue
            if field['type'] == 'Content':
                skipped.append(f'{name}.{key}: Content datatype not implemented')
                continue
            current, default = representative.get(name, name), None
            while current:
                entry = classes[current]
                stored_key = key if key in entry[4] else aliases.get(key, key)
                if stored_key in entry[4]:
                    default = entry[4][stored_key]
                    break
                current = entry[2]
            if default is None:
                if key in ('CursorPosition', 'SelectionStart'):
                    default = {'Int32': -1}
                elif key == 'IgnoreGuiInset':
                    default = {'Bool': False}
            if default is None:
                # Reference-valued defaults are nil and are not stored by the DB.
                if descriptor[2].get('Value') == 'Ref':
                    declarations[key] = {'kind': 'Instance?', 'values': None, 'target': field['type']}
                else:
                    skipped.append(f'{name}.{key}: no default')
                continue
            tag, value = next(iter(default.items()))
            if tag == 'Enum':
                kind = descriptor[2].get('Enum')
                if kind not in enums or value not in enums[kind].values():
                    skipped.append(f'{name}.{key}: enum unavailable in target VM catalog')
                    continue
                declarations[key] = {'kind': 'Enum.'+kind, 'values': value}
            elif tag in SUPPORTED:
                if tag == 'Content':
                    if value == 'None': value = ''
                    elif isinstance(value, dict) and 'Uri' in value: value = value['Uri']
                    else:
                        skipped.append(f'{name}.{key}: non-URI Content')
                        continue
                declarations[key] = {'kind': SUPPORTED[tag], 'values': value}
            else:
                skipped.append(f'{name}.{key}: unsupported {tag}')
        result[name] = declarations
    overrides = {}
    for name in result:
        if name in representative: continue
        parent = classes[name][2]
        while parent:
            for key, record in result.get(parent, {}).items():
                default = classes[name][4].get(key)
                if default is None: continue
                tag, value = next(iter(default.items()))
                if tag not in SUPPORTED and tag != 'Enum': continue
                if value != record['values']:
                    overrides.setdefault(name, {})[key] = dict(record, values=value)
            parent = classes[parent][2]
    return {'reflection_version': version, 'vm_version': '0.735.19.7351131',
            'source': 'rbx_reflection_database 3.0.1+roblox-741 (rbx-dom)',
            'source_revision': '03a3e1f63db883c42a2d0929c6058234d0f0785d',
            'source_sha256': hashlib.sha256(raw).hexdigest(),
            'reference_revision': reference.name, 'classes': result, 'default_overrides': overrides, 'skipped': skipped,
            'limits': 'Typed headless configuration. Rendering, text shaping and input hardware are not implemented. Defaults come from the recorded reflection version, not native 0.735 verification.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', type=Path, required=True)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--out', type=Path, default=ROOT/'data/ui_property_catalog.json')
    args = parser.parse_args()
    report = extract(args.database, args.reference)
    def strict(value):
        if isinstance(value,float) and not math.isfinite(value):
            return {'$number': 'NaN' if math.isnan(value) else 'Infinity' if value>0 else '-Infinity'}
        if isinstance(value,list):return [strict(item) for item in value]
        if isinstance(value,dict):return {key:strict(item) for key,item in value.items()}
        return value
    args.out.write_text(json.dumps(strict(report), indent=2, allow_nan=False)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({'classes': len(report['classes']), 'declarations': sum(map(len, report['classes'].values())), 'skipped': len(report['skipped'])}))


if __name__ == '__main__':
    main()
