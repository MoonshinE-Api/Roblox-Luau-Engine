"""Host-only asset credentials. Windows DPAPI storage lives outside the project.

No browser/session discovery, no credential fields are sent to the Lua VM.
Environment overrides are explicit and never persisted by ordinary execution.
"""
import argparse
import ctypes as C
from ctypes import wintypes as W
import getpass
import json
import os
from pathlib import Path
import tempfile
import sys

COOKIE_ENV='ROBLOX_ASSET_COOKIE'
KEY_ENV='ROBLOX_ASSET_API_KEY'
MAGIC=b'EngineRecovery0735-DPAPI-v1\0'


def credential(mode,value):
    if mode not in ('cookie','api-key') or not isinstance(value,str):
        raise ValueError('Invalid asset credential configuration')
    value=value.strip()
    if mode=='cookie':value=value.removeprefix('.ROBLOSECURITY=')
    if not value or len(value)>16384 or any(ord(c)<=32 or ord(c)>=127 for c in value):
        raise ValueError('Credential must be a nonempty printable value without whitespace')
    if mode=='cookie' and any(c in value for c in ';,'):
        raise ValueError('Enter only the .ROBLOSECURITY value, not a complete Cookie header')
    return mode,value


def store_path():
    # Never fall back to the current directory (which may be packaged/shared).
    base=os.environ.get('LOCALAPPDATA')
    if not base or not Path(base).is_absolute():
        raise ValueError('Windows LOCALAPPDATA is unavailable for credential storage')
    return Path(base)/'EngineRecovery0735'/'auth.dpapi'


class Blob(C.Structure):
    _fields_=[('size',W.DWORD),('data',C.POINTER(C.c_ubyte))]


def protect(data,decrypt=False):
    if os.name!='nt':raise ValueError('Saved login requires Windows DPAPI; use environment credentials on other hosts')
    crypt=C.WinDLL('crypt32',use_last_error=True)
    kernel=C.WinDLL('kernel32',use_last_error=True)
    kernel.LocalFree.argtypes=[C.c_void_p];kernel.LocalFree.restype=C.c_void_p
    buffer=C.create_string_buffer(data)
    source=Blob(len(data),C.cast(buffer,C.POINTER(C.c_ubyte)));target=Blob()
    if decrypt:
        function=crypt.CryptUnprotectData
        function.argtypes=[C.POINTER(Blob),C.c_void_p,C.c_void_p,C.c_void_p,C.c_void_p,W.DWORD,C.POINTER(Blob)]
        arguments=(C.byref(source),None,None,None,None,1,C.byref(target))
    else:
        function=crypt.CryptProtectData
        function.argtypes=[C.POINTER(Blob),W.LPCWSTR,C.c_void_p,C.c_void_p,C.c_void_p,W.DWORD,C.POINTER(Blob)]
        arguments=(C.byref(source),'EngineRecovery0735 asset login',None,None,None,1,C.byref(target))
    function.restype=W.BOOL
    if not function(*arguments):raise ValueError('Windows could not decrypt the saved login' if decrypt else 'Windows could not protect the login')
    try:return C.string_at(target.data,target.size)
    finally:kernel.LocalFree(C.cast(target.data,C.c_void_p))


def save(mode,value):
    mode,value=credential(mode,value)
    encrypted=MAGIC+protect(json.dumps({'mode':mode,'value':value},separators=(',',':')).encode())
    path=store_path();path.parent.mkdir(parents=True,exist_ok=True)
    temporary=None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent,prefix='auth-',delete=False) as output:
            temporary=Path(output.name);output.write(encrypted)
        os.replace(temporary,path)
    finally:
        if temporary is not None:temporary.unlink(missing_ok=True)


def saved():
    path=store_path()
    if not path.exists():return None
    try:
        if path.stat().st_size>65536:raise ValueError()
        data=path.read_bytes()
        if not data.startswith(MAGIC):raise ValueError()
        record=json.loads(protect(data[len(MAGIC):],decrypt=True))
        return credential(record['mode'],record['value'])
    except (OSError,ValueError,KeyError,TypeError):
        raise ValueError('Saved asset login is unreadable; run .logout and .login again') from None


def configured():
    cookie=os.environ.get(COOKIE_ENV,'');key=os.environ.get(KEY_ENV,'')
    if cookie and key:raise ValueError('Set only one of ROBLOX_ASSET_COOKIE and ROBLOX_ASSET_API_KEY')
    if cookie:return credential('cookie',cookie),'environment'
    if key:return credential('api-key',key),'environment'
    record=saved()
    return (record,'saved Windows login') if record else (None,'anonymous')


def command(arguments):
    """Handle dot commands before loading a Mach-O or creating a VM."""
    parser=argparse.ArgumentParser(prog='run.py '+arguments[0])
    if arguments[0]=='.login':
        parser.add_argument('--api-key',action='store_true',help='Save an Open Cloud API key instead of a session cookie')
        parser.add_argument('value',nargs='?',help='Optional credential; omit to use hidden input')
    args=parser.parse_args(arguments[1:])
    try:
        if arguments[0]=='.logout':
            store_path().unlink(missing_ok=True)
            print('Saved asset login removed. Environment credentials, if set, still apply.')
        elif arguments[0]=='.auth':
            record,source=configured()
            print('Asset authentication: '+(record[0] if record else 'none')+' ('+source+').')
            print('Configuration status only; account validity has not been checked with Roblox.')
        else:
            mode='api-key' if args.api_key else 'cookie'
            if args.value is None:
                if not sys.stdin.isatty():
                    raise ValueError('Hidden login requires an interactive terminal; environment credentials are also supported')
                value=getpass.getpass('Open Cloud API key: ' if args.api_key else '.ROBLOSECURITY cookie (hidden): ')
            else:value=args.value
            save(mode,value)
            print('Asset login saved with Windows DPAPI. Account validity has not been checked with Roblox.')
            if os.environ.get(COOKIE_ENV) or os.environ.get(KEY_ENV):
                print('An environment credential currently overrides the saved login.')
        return 0
    except (ValueError,OSError,EOFError,KeyboardInterrupt) as error:
        # Never include credential values or OS/crypto exception details here.
        print('Asset login failed: '+(str(error) if isinstance(error,ValueError) else type(error).__name__))
        return 1
