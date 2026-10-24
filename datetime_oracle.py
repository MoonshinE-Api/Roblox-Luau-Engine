"""DateTime differential arithmetic and independent Gregorian reference checks."""
import argparse,ctypes as C,datetime as D,json,random,tempfile,os,subprocess,sys,time
from pathlib import Path
from macho import MachO
from original import Original
from run import bootstrap,execute_source,lua_literal
from vm_runtime import Runtime

def timezone_worker(args):
    """Fresh process: TZ is supplied by the parent, never changed on the user's system."""
    crt=C.CDLL('ucrtbase');crt._tzset()
    bias=C.c_long();crt._get_timezone(C.byref(bias))
    expected_bias={'UTC0':0,'PST8PDT':28800,'JST-9':-32400}[os.environ['TZ']]
    assert bias.value==expected_bias,(os.environ['TZ'],bias.value)
    root=Path(__file__).parent;epoch=D.datetime(1970,1,1);rng=random.Random(735)
    def seconds(dt):
        delta=dt-epoch;return delta.days*86400+delta.seconds
    now=int(time.time());current=time.localtime(now)
    offset=seconds(D.datetime(*current[:6]))-now
    stamps=[0,1,-1,seconds(D.datetime(1400,1,2)),seconds(D.datetime(3001,1,1)),seconds(D.datetime(9999,12,30))]
    stamps +=[seconds(D.datetime(rng.randint(1971,2999),rng.randint(1,12),15,rng.randint(0,23),12,34)) for _ in range(120)]
    utc=[];local=[]
    for stamp in stamps:
        if 0<=stamp<=32535215999:
            item=D.datetime(*time.localtime(stamp)[:6])
        else:item=epoch+D.timedelta(seconds=stamp+offset)
        utc.append([stamp*1000+321,[item.year,item.month,item.day,item.hour,item.minute,item.second,321]])
    local_fields=[[2024,3,10,2,30,0],[2024,11,3,1,30,0]]
    local_fields += [[(epoch+D.timedelta(seconds=s)).year,(epoch+D.timedelta(seconds=s)).month,
                      (epoch+D.timedelta(seconds=s)).day,(epoch+D.timedelta(seconds=s)).hour,12,34] for s in stamps]
    for fields in local_fields:
        wall=seconds(D.datetime(*fields))
        try:first=time.mktime((*fields,0,0,0))
        except (OverflowError,OSError,ValueError):first=-1
        if first<=0:result=wall-offset
        else:
            isdst=time.localtime(first).tm_isdst
            try:result=int(time.mktime((*fields,0,0,isdst)))
            except (OverflowError,OSError,ValueError):result=wall-offset
        local.append([fields+[321],result*1000+321])
    runtime=Runtime(args.binary)
    try:
        runtime.open_libraries()
        with tempfile.TemporaryDirectory(prefix='datetime-timezone-') as folder:
            working=Path(folder);execute_source(runtime,root,bootstrap(root,{'side':'server','duration':0}),working,'engine-bootstrap')
            probe='local utc='+lua_literal(utc)+'\nlocal localValues='+lua_literal(local)+'''
local names={"Year","Month","Day","Hour","Minute","Second","Millisecond"}
for i,row in utc do
 local fields=DateTime.fromUnixTimestampMillis(row[1]):ToLocalTime()
 for k,name in names do assert(fields[name]==row[2][k],"UTC/local bridge mismatch "..i.." "..name) end
end
for i,row in localValues do
 local date=DateTime.fromLocalTime(table.unpack(row[1]))
 assert(date.UnixTimestampMillis==row[2],"Local/UTC bridge mismatch "..i.." "..date.UnixTimestampMillis.." "..row[2])
 local fields=date:ToLocalTime()
 for k,name in names do assert(fields[name]==row[1][k],"Cached local fields mismatch "..i.." "..name) end
end
return #utc+#localValues
'''
            count=execute_source(runtime,root,probe,working,'timezone-bridge')[0]
    finally:runtime.close()
    assert not runtime.owned and not runtime.backing_errors
    print(json.dumps({'timezone':os.environ['TZ'],'cases':int(count),'offset_now':offset}))

def main():
    p=argparse.ArgumentParser();p.add_argument('--binary',type=Path,required=True)
    p.add_argument('--timezone-worker',action='store_true')
    args=p.parse_args();root=Path(__file__).parent
    if args.timezone_worker:return timezone_worker(args)
    report=json.loads((root/'data/datetime_recovery.json').read_text(encoding='utf-8'))
    dll=C.CDLL(str((root/'vm0735.dll').resolve()));rng=random.Random(7351131)
    epoch=D.datetime(1970,1,1);vectors=[];date_memory=C.c_uint32();state=C.c_int64()
    with MachO(args.binary) as binary,Original(binary,report,dll,enabled=report['functions']) as original:
        for i in range(3200):
            if i<4:
                dt=[D.datetime(1400,1,1),D.datetime(9999,12,31,23,59,59,999000),D.datetime(1969,12,31,23,59,59,999000),epoch][i]
            else:
                year=rng.randint(1400,9999);month=rng.randint(1,12)
                dt=D.datetime(year,month,1)+D.timedelta(days=rng.randrange(27),seconds=rng.randrange(86400),milliseconds=rng.randrange(1000))
            delta=dt-epoch;seconds=delta.days*86400+delta.seconds;micros=dt.microsecond
            ms=seconds*1000+micros//1000
            original.call5('datetime_gregorian',C.addressof(date_memory),dt.year,dt.month,dt.day,0)
            assert date_memory.value==2440588+(dt.date()-epoch.date()).days
            state.value=report['epoch_ticks']+seconds*1000000+micros
            native=C.c_int64(original.call('datetime_unix',C.addressof(state))).value
            expected=seconds+(1 if seconds<0 and micros else 0)
            assert native==expected,(dt,native,expected)
            fields=[dt.year,dt.month,dt.day,dt.hour,dt.minute,dt.second,micros//1000]
            fraction=f'.{micros:06d}' if micros else ''
            iso=dt.strftime('%Y-%m-%dT%H:%M:%S')+fraction+'Z'
            vectors.append([ms,fields,native,iso])
        # Check sign rules on the actual Boost to_tick_count function.
        duration=[]
        inputs=[[*[rng.randint(-30,30) for _ in range(3)],rng.randint(-2000,2000)] for _ in range(400)]
        inputs += [[0,0,0,ms] for ms in [2147484,2147483647,-2147483648,-2147484]]
        for h,m,s,ms in inputs:
            fraction=C.c_int32(ms*1000).value
            result=C.c_int64(original.call5('datetime_tick_count',h & 0xffffffff,m & 0xffffffff,s & 0xffffffff,fraction&(2**64-1),0)).value
            if abs(result)<10**14:duration.append([h,m,s,ms,result])
    runtime=Runtime(args.binary)
    try:
        runtime.open_libraries()
        with tempfile.TemporaryDirectory(prefix='datetime-oracle-') as folder:
            working=Path(folder);execute_source(runtime,root,bootstrap(root,{'side':'server','duration':0}),working,'engine-bootstrap')
            probe='local vectors='+lua_literal(vectors)+'\nlocal durations='+lua_literal(duration)+'''
for i,row in vectors do
 local date=DateTime.fromUnixTimestampMillis(row[1])
 local fields=date:ToUniversalTime()
 for k,name in {"Year","Month","Day","Hour","Minute","Second","Millisecond"} do assert(fields[name]==row[2][k],"Calendar field mismatch "..i.." "..name) end
 assert(date.UnixTimestamp==row[3] and date.UnixTimestampMillis==row[1],"Timestamp mismatch "..i)
 assert(date:ToIsoDate()==row[4],"ISO mismatch "..i.." "..date:ToIsoDate())
 assert(DateTime.fromUniversalTime(table.unpack(row[2]))==date,"Component constructor mismatch "..i)
 assert(DateTime.fromIsoDate(row[4])==date,"ISO roundtrip mismatch "..i)
end
local base=DateTime.fromUniversalTime(2024,1,15).UnixTimestampMillis
for i,row in durations do
 local date=DateTime.fromUniversalTime(2024,1,15,row[1],row[2],row[3],row[4])
 assert(date.UnixTimestampMillis==base+math.floor(row[5]/1000),"Native duration mismatch "..i)
end
return #vectors,#durations
'''
            counts=execute_source(runtime,root,probe,working,'datetime-differential')
            formatting=json.loads((root/'tests/fixtures/datetime_format_vectors.json').read_text(encoding='utf-8'))
            assert formatting['source_locale_sha256']==report['locale_file_sha256'],'Stale locale format vectors'
            format_probe='local rows='+lua_literal(formatting['vectors'])+'''
for i,row in rows do
 local actual=DateTime.fromUnixTimestampMillis(row[1]):FormatUniversalTime(row[3],row[2])
 assert(actual==row[4],"Locale format mismatch "..i.." "..row[2].." "..row[3].." expected="..row[4].." actual="..actual)
end
return #rows
'''
            format_count=execute_source(runtime,root,format_probe,working,'datetime-format-differential')[0]
    finally:runtime.close()
    assert not runtime.owned and not runtime.backing_errors
    zones=[]
    for name in ('UTC0','PST8PDT','JST-9'):
        environment=os.environ.copy();environment['TZ']=name
        child=subprocess.run([sys.executable,__file__,'--binary',str(args.binary),'--timezone-worker'],env=environment,capture_output=True,text=True)
        assert child.returncode==0,child.stdout+child.stderr
        zones.append(json.loads(child.stdout.strip()))
    result={'status':'PASS','calendar_timestamp_iso_vectors':int(counts[0]),'native_duration_cases':int(counts[1]),
            'format_vectors':int(format_count),'format_reference':formatting['reference'],
            'host_timezone_checks':zones,
            'original_comparisons':'Gregorian Julian days, DateTime::getUnixTimestamp, Boost duration ticks; original function bytes unchanged.',
            'independent_reference':'Python datetime for UTC fields, milliseconds and ISO strings.',
            'limits':'Original ISO/locale C++ stream pipeline and macOS timezone database are not executed.'}
    (root/'data/datetime_comparison.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
if __name__=='__main__':main()
