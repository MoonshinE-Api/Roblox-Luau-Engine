//! Clock and local-calendar bridge for DateTime. UTC arithmetic stays independent
//! of UCRT's restricted date range; outside that range the source uses today's offset.
use std::time::{SystemTime,UNIX_EPOCH};
#[link(name="ucrt")]
unsafe extern "C" {
    fn _localtime64_s(out:*mut i32,value:*const i64)->i32;
    fn _mktime64(fields:*mut i32)->i64;
}
#[link(name="kernel32")]
unsafe extern "system" {fn Sleep(milliseconds:u32);}
pub unsafe extern "sysv64" fn host_sleep(lua:usize)->i32 {
    unsafe {
        let get:unsafe extern "sysv64" fn(usize,i32,*mut i32)->f64=std::mem::transmute(super::random::lua_api(1));
        let seconds=get(lua,1,std::ptr::null_mut());
        if seconds.is_finite() && seconds>0.0 {Sleep((seconds.min(0.25)*1000.0).ceil() as u32);}
    }
    0
}
fn wall(fields:&[i32;9])->i64 {
    let year=fields[5] as i64+1900;let month=fields[4] as i64+1;
    let y=year-i64::from(month<=2);let era=y.div_euclid(400);let within=y-era*400;
    let day=(153*(month+if month>2 {-3}else{9})+2)/5+fields[3] as i64-1;
    (era*146097+within*365+within/4-within/100+day-719468)*86400+
        fields[2] as i64*3600+fields[1] as i64*60+fields[0] as i64
}
fn fields(seconds:i64)->[i32;9] {
    let days=seconds.div_euclid(86400)+719468;let era=days.div_euclid(146097);
    let doe=days-era*146097;let yoe=(doe-doe/1460+doe/36524-doe/146096)/365;
    let y=yoe+era*400;let doy=doe-(365*yoe+yoe/4-yoe/100);let mp=(5*doy+2)/153;
    let day=doy-(153*mp+2)/5+1;let month=mp+if mp<10 {3}else{-9};
    let year=y+i64::from(month<=2);let time=seconds.rem_euclid(86400);
    [(time%60) as i32,(time/60%60) as i32,(time/3600) as i32,day as i32,month as i32-1,year as i32-1900,0,0,0]
}
fn offset_now()->i64 {
    let now=SystemTime::now().duration_since(UNIX_EPOCH).unwrap_or_default().as_secs() as i64;
    let mut local=[0;9];
    if unsafe {_localtime64_s(local.as_mut_ptr(),&now)}==0 {wall(&local)-now}else{0}
}
pub unsafe extern "sysv64" fn host_datetime(lua:usize)->i32 {
    unsafe {
        let get:unsafe extern "sysv64" fn(usize,i32,*mut i32)->f64=std::mem::transmute(super::random::lua_api(1));
        let push:unsafe extern "sysv64" fn(usize,f64)=std::mem::transmute(super::random::lua_api(2));
        let nil:unsafe extern "sysv64" fn(usize)=std::mem::transmute(super::random::lua_api(3));
        let op=get(lua,1,std::ptr::null_mut()) as i32;
        if op==0 {
            let now=SystemTime::now().duration_since(UNIX_EPOCH).unwrap_or_default().as_millis();
            push(lua,now as f64);return 1;
        }
        let input=get(lua,2,std::ptr::null_mut());
        if !input.is_finite() || !(-17987529600.0..=253402387199.0).contains(&input) {nil(lua);return 1;}
        let seconds=input as i64;
        let result=match op {
            1=>{
                let mut local=[0;9];
                if (0..=32535215999).contains(&seconds) && _localtime64_s(local.as_mut_ptr(),&seconds)==0 {
                    wall(&local)
                }else{seconds+offset_now()}
            },
            2=>{
                let original=fields(seconds);let mut normalized=original;
                let first=_mktime64(normalized.as_mut_ptr());
                if first<=0 {seconds-offset_now()}else{
                    // Original fromComponents first determines isdst, then applies
                    // it to the original wall fields in a second mktime call.
                    let mut selected=original;selected[8]=normalized[8];
                    let second=_mktime64(selected.as_mut_ptr());
                    if second<0 {seconds-offset_now()}else{second}
                }
            },
            _=>{nil(lua);return 1;}
        };
        push(lua,result as f64);1
    }
}
