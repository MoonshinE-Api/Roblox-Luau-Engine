"""Restore bundled support files with bounded, verified extraction; no network."""
import hashlib,json,os,tempfile,zipfile
from pathlib import Path,PurePosixPath


def restore(root):
    root=root.resolve();directory=root/'bundled'
    manifest=json.loads((directory/'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('format')!=1:raise ValueError('Unsupported bundle manifest')
    pending=[];total=0
    for name,record in manifest['archives'].items():
        if Path(name).name!=name:raise ValueError('Invalid archive name')
        path=directory/name
        if hashlib.sha256(path.read_bytes()).hexdigest()!=record['sha256']:raise ValueError(f'Archive hash mismatch: {name}')
        with zipfile.ZipFile(path) as archive:
            names=archive.namelist()
            if len(names)!=len(set(names)) or set(names)!=set(record['files']):raise ValueError('Unexpected archive entries')
            for relative,expected in record['files'].items():
                parts=PurePosixPath(relative)
                if parts.is_absolute() or '..' in parts.parts or '\\' in relative:raise ValueError('Invalid bundle path')
                target=(root/relative).resolve()
                if not target.is_relative_to(root):raise ValueError('Bundle path leaves repository')
                info=archive.getinfo(relative);total+=info.file_size
                if info.file_size!=expected['bytes'] or total>32*1024*1024:raise ValueError('Invalid bundle size')
                data=archive.read(info)
                if hashlib.sha256(data).hexdigest()!=expected['sha256']:raise ValueError(f'File hash mismatch: {relative}')
                if target.exists():
                    if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest()!=expected['sha256']:
                        raise ValueError(f'Existing file differs: {relative}. Move it aside before restoring the bundle.')
                else:pending.append((target,data))
    # Verify every archive and entry before writing any support files.
    for target,data in pending:
        target.parent.mkdir(parents=True,exist_ok=True)
        temporary=None
        try:
            with tempfile.NamedTemporaryFile(dir=target.parent,prefix=target.name+'-',delete=False) as file:
                temporary=Path(file.name);file.write(data)
            os.replace(temporary,target)
        finally:
            if temporary is not None:temporary.unlink(missing_ok=True)
    print(f'Runtime support ready: {len(pending)} files restored; all bundle hashes verified.')


if __name__=='__main__':restore(Path(__file__).resolve().parent)
