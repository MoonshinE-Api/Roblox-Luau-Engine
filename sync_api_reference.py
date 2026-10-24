"""Extract interface facts from a pinned revision of Roblox's official docs.

Descriptions/examples stay in the external cache. This is a reference inventory,
not a declaration that any listed member has been implemented by this runtime.
Requires PyYAML for extraction only; the runner remains dependency-free.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
import urllib.error
import urllib.request

import yaml

REPO = 'Roblox/creator-docs'
PREFIX = 'content/en-us/reference/engine'
SECTIONS = ('classes', 'datatypes', 'enums', 'globals', 'libraries')


def download(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'EngineRecovery0735-reference-sync'})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            if attempt == 3:
                raise
            time.sleep(attempt + 1)


def api(path):
    return json.loads(download('https://api.github.com/repos/' + REPO + '/' + path))


def signature(member):
    keys = ('name', 'type', 'value', 'default', 'tags', 'security', 'thread_safety', 'capabilities')
    result = {key: member[key] for key in keys if key in member}
    for key in ('parameters', 'returns'):
        if key in member:
            result[key] = [{k: x[k] for k in ('name', 'type', 'default') if k in x}
                           for x in (member[key] or [])]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, required=True)
    parser.add_argument('--revision', default='main')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    commit = api('commits/' + args.revision)['sha']
    entries = api('contents/' + PREFIX + '?ref=' + commit)
    directories = {entry['name']: entry['sha'] for entry in entries if entry['type'] == 'dir'}
    jobs = []
    for section in SECTIONS:
        tree = api('git/trees/' + directories[section])['tree']
        jobs.extend((section, x['path'], x['sha']) for x in tree
                    if x['type'] == 'blob' and x['path'].endswith('.yaml'))
    cache = args.cache.resolve() / commit
    cache.mkdir(parents=True, exist_ok=True)
    result = {section: {} for section in SECTIONS}

    def load(job):
        section, name, blob = job
        relative = section + '/' + name
        url = f'https://raw.githubusercontent.com/{REPO}/{commit}/{PREFIX}/{relative}'
        path = cache / relative
        if path.exists():
            content = path.read_bytes()
        else:
            content = download(url)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        actual_blob = hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest()
        if actual_blob != blob:
            raise ValueError('Git blob verification failed: ' + relative)
        document = yaml.load(content, Loader=yaml.CSafeLoader)
        record = {key: document[key] for key in ('name', 'type', 'inherits', 'tags') if key in document}
        for category in ('constructors', 'constants', 'properties', 'methods', 'functions', 'events', 'callbacks', 'items', 'math_operations'):
            if category in document:
                record[category] = [signature(item) for item in (document[category] or [])]
        record['source'] = url
        record['sha256'] = hashlib.sha256(content).hexdigest()
        return section, name[:-5], record

    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(load, job) for job in jobs]
        for number, future in enumerate(as_completed(futures), 1):
            section, name, record = future.result()
            result[section][name] = record
            if number % 100 == 0:
                print(f'Reference interfaces: {number}/{len(jobs)}', flush=True)
    version = download(f'https://raw.githubusercontent.com/{REPO}/{commit}/{PREFIX}/STUDIO_VERSION').decode().strip()
    output = {
        'repository': 'https://github.com/' + REPO,
        'revision': commit,
        'retrieved_utc': datetime.now(timezone.utc).isoformat(),
        'documentation_studio_version': version,
        'runtime_studio_version': '0.735.19.7351131',
        'meaning': 'Documented interface facts only. Presence does not imply implementation or availability in build 0.735.',
        'counts': {section: len(result[section]) for section in SECTIONS},
        **{section: dict(sorted(result[section].items())) for section in SECTIONS},
    }
    destination = root / 'evidence/api_reference.json'
    destination.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'revision': commit, 'version': version, 'counts': output['counts'], 'output': str(destination)}), flush=True)


if __name__ == '__main__':
    main()
