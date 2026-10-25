"""SQLite atomicity, rollback, process persistence, and Luau integration."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from datastore_runtime import DataStores,VALUE_LIMIT


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--binary',default='D:/Release-RobloxStudioApp/RobloxStudio.app/Contents/MacOS/RobloxStudio')
    args=parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='sqlite-datastore-') as directory:
        folder=Path(directory);database=folder/'store.sqlite3'
        backend=DataStores(database)
        base={'Name':'Unit','Scope':'global','Ordered':False,'Key':'counter'}
        def request(operation,data=None,**options):
            _,body=backend.request(dict(base,Operation=operation,**options),json.dumps(data or {},ensure_ascii=False).encode())
            return json.loads(body)
        request('set',{'Value':0})
        previous=request('get')
        request('increment',{'Delta':1})
        assert request('cas',{'ExpectedVersion':previous['Version'],'Value':100})=={'Conflict':True}
        assert request('get')['Value']==1
        for bad in [{'Value':'x'*(VALUE_LIMIT+1)},{'Value':20,'Metadata':[1]},{'Value':20,'UserIds':['bad']}]:
            try:request('set',bad)
            except ValueError:pass
            else:raise AssertionError('Invalid write accepted')
        assert request('get')['Value']==1
        quote="key'_%"
        saved=request('set',{'Value':{'text':'Привет','list':[1,2]},'Metadata':{'v':1},'UserIds':[7]},Key=quote)
        assert request('version',{'Version':saved['Record']['Version']},Key=quote)['Value']['text']=='Привет'
        assert request('keys',{'Prefix':"key'_"})['Items']==[{'KeyName':quote}]
        backend.close()
        def increment_worker(_):
            connection=DataStores(database)
            try:
                for _ in range(25):connection.request(dict(base,Operation='increment'),b'{"Delta":1}')
            finally:connection.close()
        with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(increment_worker,range(4)))
        backend=DataStores(database)
        assert request('get')['Value']==101
        backend.close()
        # Independent OS processes use the same explicit file and retain history.
        writer=folder/'write.luau';reader=folder/'read.luau'
        writer.write_text('''local d=game:GetService('DataStoreService'):GetDataStore('Persistent')
local version=d:SetAsync('save',{coins=99})
d:SetAsync('version',version);d:SetAsync('save',{coins=123})
print('SQLITE WRITER PASSED')
''')
        reader.write_text('''local d=game:GetService('DataStoreService'):GetDataStore('Persistent')
assert(d:GetAsync('save').coins==123)
assert(d:GetVersionAsync('save',d:GetAsync('version')).coins==99)
print('SQLITE READER AND VERSION PASSED')
''')
        for script in (writer,reader):
            subprocess.run([sys.executable,str(ROOT/'run.py'),str(script),'--binary',args.binary,
                '--data-store',str(database),'--duration','5','--wall-timeout','30'],check=True)
    print('SQLITE CONCURRENCY, ROLLBACK AND PROCESS PERSISTENCE CHECKS PASSED')


if __name__=='__main__':main()
