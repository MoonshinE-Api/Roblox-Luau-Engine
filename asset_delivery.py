"""Fetch permitted asset content with explicit, endpoint-scoped host credentials."""
import json
import time
from urllib.parse import urlsplit
from asset_auth import configured

LEGACY_URL='https://assetdelivery.roblox.com/v1/asset/'
CLOUD_URL='https://apis.roblox.com/asset-delivery-api/v1/assetId/'


def download(identifier,version,timeout,request,legacy_url=LEGACY_URL):
    record,_=configured()
    mode,secret=record if record else ('anonymous',None)
    if mode!='anonymous' and legacy_url!=LEGACY_URL:
        raise ValueError('Asset credentials may only be sent to the fixed Roblox endpoint')
    if mode=='api-key' and version:
        # A Roblox asset-version ID is not an asset ID + a version number.
        raise ValueError('LoadAssetVersion(versionId) requires cookie authentication; Open Cloud uses assetId/versionNumber')
    deadline=time.monotonic()+timeout
    def fetch(url,headers,host_credentials=None):
        remaining=deadline-time.monotonic()
        if remaining<=0:raise ValueError('Asset delivery timeout exceeded')
        options={'Url':url,'Method':'GET','Headers':headers,'Timeout':remaining,'HasBody':False}
        if host_credentials:options['_HostCredentialHeaders']=host_credentials
        try:metadata,data=request(options,b'')
        except Exception as error:
            # Transport exceptions can reflect URLs, headers and signed query
            # strings. Never put their raw text into a Luau-visible error.
            raise ValueError('Asset delivery transport failed ('+type(error).__name__+')') from None
        if not metadata['Success']:
            status=int(metadata['StatusCode'])
            hint={401:'authentication required or credential rejected; use run.py .login',
                  403:'Roblox denied access to this asset',404:'asset not found',429:'Roblox rate limit reached'}.get(status,'request failed')
            raise ValueError(f'Asset delivery HTTP {status}: {hint}')
        if len(data)>50*1024*1024:raise ValueError('Asset exceeds 50 MiB')
        return data
    if mode=='api-key':
        payload=fetch(CLOUD_URL+str(identifier),{'Accept':'application/json'},{'x-api-key':secret})
        try:
            if len(payload)>1024*1024:raise ValueError()
            location=json.loads(payload)['location']
            if not isinstance(location,str):raise ValueError()
            parts=urlsplit(location)
            host=parts.hostname or ''
            if parts.scheme!='https' or parts.username is not None or parts.password is not None or parts.port not in (None,443):raise ValueError()
            if host!='rbxcdn.com' and not host.endswith('.rbxcdn.com'):raise ValueError()
            if any(ord(c)<=32 or ord(c)>=127 for c in location):raise ValueError()
        except (ValueError,KeyError,TypeError):
            raise ValueError('Asset delivery returned an invalid/unsupported CDN location') from None
        # Separate request: API key/cookie must not be attached to signed CDN URLs.
        return fetch(location,{'Accept':'application/octet-stream'})
    key='assetversionid' if version else 'id'
    return fetch(legacy_url+'?'+key+'='+str(identifier),{'Accept':'application/octet-stream'},
                 {'Cookie':'.ROBLOSECURITY='+secret} if mode=='cookie' else None)
