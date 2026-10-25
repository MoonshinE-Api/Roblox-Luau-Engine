"""Local SQLite data stores. No Roblox cloud API or credentials are involved."""
import json
import math
from pathlib import Path
import sqlite3
import threading
import time
import uuid

VALUE_LIMIT=4*1024*1024


def encode(value):
    return json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False)


class DataStores:
    def __init__(self,path=None):
        self.lock=threading.RLock()
        self.closed=False
        if path is not None:
            path=Path(path).expanduser().resolve();path.parent.mkdir(parents=True,exist_ok=True)
        self.connection=sqlite3.connect(str(path) if path is not None else ':memory:',check_same_thread=False,timeout=5)
        self.connection.row_factory=sqlite3.Row
        self.connection.executescript('''
CREATE TABLE IF NOT EXISTS entries (
 ordered INTEGER NOT NULL, name TEXT NOT NULL, scope TEXT NOT NULL, key TEXT NOT NULL,
 value TEXT, users TEXT NOT NULL, metadata TEXT NOT NULL, created INTEGER NOT NULL,
 updated INTEGER NOT NULL, version TEXT NOT NULL, deleted INTEGER NOT NULL,
 PRIMARY KEY (ordered,name,scope,key));
CREATE TABLE IF NOT EXISTS versions (
 ordered INTEGER NOT NULL, name TEXT NOT NULL, scope TEXT NOT NULL, key TEXT NOT NULL,
 value TEXT, users TEXT NOT NULL, metadata TEXT NOT NULL, created INTEGER NOT NULL,
 updated INTEGER NOT NULL, version TEXT PRIMARY KEY, deleted INTEGER NOT NULL);
''')

    @staticmethod
    def identity(options):
        def component(value):
            if not isinstance(value,str) or not 0<len(value.encode('utf-8'))<=50 or '\0' in value:
                raise ValueError('Data store name, scope and key must contain 1..50 UTF-8 bytes')
            return value
        return (int(bool(options.get('Ordered',False))),component(options.get('Name')),
                component(options.get('Scope')),component(options.get('Key')))

    @staticmethod
    def record(row):
        if row is None:return {'Exists':False,'Version':''}
        result={'Exists':not bool(row['deleted']),'Version':row['version'],
                'CreatedTime':row['created'],'UpdatedTime':row['updated'],
                'UserIds':json.loads(row['users']),'Metadata':json.loads(row['metadata'])}
        if not row['deleted']:result['Value']=json.loads(row['value'])
        return result

    def request(self,options,body):
        if len(body)>VALUE_LIMIT+65536:raise ValueError('Data store request exceeds local size limit')
        def invalid(value):raise ValueError('Nonfinite JSON value '+value)
        data=json.loads(body.decode('utf-8'),parse_constant=invalid) if body else {}
        if data==[]:data={}
        if not isinstance(data,dict):raise ValueError('Expected data store request dictionary')
        operation=options.get('Operation')
        if operation in ('keys','sorted'):
            ordered=int(bool(options.get('Ordered',False)))
            name,scope=options.get('Name'),options.get('Scope')
            self.identity(dict(options,Key='_',Scope='global' if scope=='*' else scope))
            with self.lock:
                if self.closed:raise RuntimeError('Data store is closed')
                columns='key,scope,deleted'+(',value' if operation=='sorted' else '')
                sql=f'SELECT {columns} FROM entries WHERE ordered=? AND name=?';params=[ordered,name]
                if scope!='*':sql+=' AND scope=?';params.append(scope)
                rows=self.connection.execute(sql+' LIMIT 10001',params).fetchall()
            if len(rows)>10000:raise ValueError('Local data store listing exceeds 10000 entries')
            output=[]
            if operation=='keys':
                prefix=data.get('Prefix','')
                if not isinstance(prefix,str):raise ValueError('Invalid key prefix')
                for row in rows:
                    key=row['scope']+'/'+row['key'] if scope=='*' else row['key']
                    if key.startswith(prefix) and (not data.get('ExcludeDeleted') or not row['deleted']):output.append({'KeyName':key})
                output.sort(key=lambda item:item['KeyName'])
            else:
                for row in rows:
                    if row['deleted']:continue
                    value=json.loads(row['value'])
                    if data.get('Min') is not None and value<data['Min']:continue
                    if data.get('Max') is not None and value>data['Max']:continue
                    output.append({'key':row['key'],'value':value})
                output.sort(key=lambda item:(item['value'],item['key']),reverse=not data.get('Ascending',False))
            return {},encode({'Items':output}).encode('utf-8')
        identity=self.identity(options)
        with self.lock:
            if self.closed:raise RuntimeError('Data store is closed')
            connection=self.connection
            connection.execute('BEGIN IMMEDIATE')
            try:
                row=connection.execute('SELECT * FROM entries WHERE ordered=? AND name=? AND scope=? AND key=?',identity).fetchone()
                old=self.record(row)
                if operation=='get':result=old
                elif operation=='version':
                    if identity[0]:raise ValueError('Ordered data stores do not support versions')
                    version=data.get('Version')
                    if not isinstance(version,str):raise ValueError('Expected version string')
                    result=self.record(connection.execute('SELECT * FROM versions WHERE ordered=? AND name=? AND scope=? AND key=? AND version=?',(*identity,version)).fetchone())
                elif operation in ('set','cas','increment','remove'):
                    if operation=='cas' and old['Version']!=data.get('ExpectedVersion',''):
                        result={'Conflict':True}
                    elif operation=='remove' and not old['Exists']:result={'Previous':old,'Record':old}
                    else:
                        deleted=operation=='remove'
                        value=None if deleted else data.get('Value')
                        if operation=='increment':
                            before=old.get('Value',0)
                            delta=data.get('Delta',1)
                            if any(isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) or int(x)!=x for x in (before,delta)):
                                raise ValueError('IncrementAsync requires integer values')
                            value=before+delta
                        if not deleted and value is None:raise ValueError('Cannot store nil')
                        if identity[0] and not deleted and (isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or int(value)!=value):
                            raise ValueError('Ordered data stores require integer values')
                        if isinstance(value,(int,float)) and (not math.isfinite(value) or ((identity[0] or operation=='increment') and abs(value)>9007199254740991)):
                            raise ValueError('Local numeric value exceeds exact Luau integer range')
                        encoded=None if deleted else encode(value)
                        if encoded is not None and len(encoded.encode('utf-8'))>VALUE_LIMIT:raise ValueError('Data store value exceeds 4 MiB')
                        users=data.get('UserIds',[]);metadata=data.get('Metadata',{})
                        if metadata==[]:metadata={}
                        if not isinstance(users,list) or any(isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) or x!=int(x) for x in users):
                            raise ValueError('Invalid data store UserIds')
                        if not isinstance(metadata,dict):raise ValueError('Data store metadata must be a dictionary')
                        now=time.time_ns()//1000000
                        version=uuid.uuid4().hex
                        columns=(*identity,encoded,encode(users),encode(metadata),old.get('CreatedTime',now),now,version,int(deleted))
                        connection.execute('INSERT OR REPLACE INTO entries VALUES (?,?,?,?,?,?,?,?,?,?,?)',columns)
                        if not identity[0]:connection.execute('INSERT INTO versions VALUES (?,?,?,?,?,?,?,?,?,?,?)',columns)
                        updated=connection.execute('SELECT * FROM entries WHERE ordered=? AND name=? AND scope=? AND key=?',identity).fetchone()
                        result={'Record':self.record(updated)}
                        if operation=='remove':result['Previous']=old
                else:raise ValueError('Unknown local data store operation')
                connection.commit()
            except BaseException:
                connection.rollback();raise
        return {},encode(result).encode('utf-8')

    def close(self):
        with self.lock:
            if not self.closed:self.closed=True;self.connection.close()
