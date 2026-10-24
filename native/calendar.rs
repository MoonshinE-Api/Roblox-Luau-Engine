//! Darwin time ABI adapters for the original VM's os library.
//! ABI facts: Apple _time.h; Microsoft _gmtime64_s/strftime documentation.
use std::ffi::{c_char,CStr};

#[repr(C)]
pub struct DarwinTm {
    fields:[i32;9],
    gmtoff:i64,
    zone:*const c_char,
}
const _:()=assert!(std::mem::size_of::<DarwinTm>()==56);

#[link(name="ucrt")]
unsafe extern "C" {
    fn _gmtime64_s(destination:*mut i32,source:*const i64)->i32;
    fn _localtime64_s(destination:*mut i32,source:*const i64)->i32;
    fn strftime(destination:*mut c_char,capacity:usize,format:*const c_char,time:*const i32)->usize;
}

fn wall_seconds(fields:&[i32;9])->i64 {
    let year=fields[5] as i64+1900;
    let month=fields[4] as i64+1;
    let adjusted=year-i64::from(month<=2);
    let era=adjusted.div_euclid(400);
    let within=adjusted-era*400;
    let shifted=month+if month>2 {-3} else {9};
    let day=(153*shifted+2)/5+fields[3] as i64-1;
    let days=era*146097+within*365+within/4-within/100+day-719468;
    days*86400+fields[2] as i64*3600+fields[1] as i64*60+fields[0] as i64
}

pub unsafe extern "sysv64" fn gmtime_r(source:*const i64,destination:*mut DarwinTm)->*mut DarwinTm {
    if source.is_null() || destination.is_null() {return std::ptr::null_mut();}
    let mut fields=[0_i32;9];
    if unsafe {_gmtime64_s(fields.as_mut_ptr(),source)}!=0 {return std::ptr::null_mut();}
    unsafe {destination.write(DarwinTm{fields,gmtoff:0,zone:c"UTC".as_ptr()});}
    destination
}
pub unsafe extern "sysv64" fn localtime_r(source:*const i64,destination:*mut DarwinTm)->*mut DarwinTm {
    if source.is_null() || destination.is_null() {return std::ptr::null_mut();}
    let mut fields=[0_i32;9];
    if unsafe {_localtime64_s(fields.as_mut_ptr(),source)}!=0 {return std::ptr::null_mut();}
    let offset=wall_seconds(&fields)-unsafe {*source};
    unsafe {destination.write(DarwinTm{fields,gmtoff:offset,zone:std::ptr::null()});}
    destination
}
pub unsafe extern "sysv64" fn difftime(a:i64,b:i64)->f64 {a as f64-b as f64}

unsafe fn crt_piece(specifier:u8,time:&DarwinTm,output:&mut Vec<u8>)->bool {
    let format=[b'%',specifier,0];
    let mut buffer=[0_u8;256];
    let length=unsafe {strftime(buffer.as_mut_ptr().cast(),buffer.len(),format.as_ptr().cast(),time.fields.as_ptr())};
    if length==0 {return false;}
    output.extend_from_slice(&buffer[..length]);true
}
pub unsafe extern "sysv64" fn format(destination:*mut c_char,capacity:usize,pattern:*const c_char,time:*const DarwinTm)->usize {
    if destination.is_null() || pattern.is_null() || time.is_null() || capacity==0 {return 0;}
    let time=unsafe {&*time};
    let pattern=unsafe {CStr::from_ptr(pattern)}.to_bytes();
    let mut output=Vec::new();
    let mut i=0;
    while i<pattern.len() {
        if pattern[i]!=b'%' {output.push(pattern[i]);i+=1;continue;}
        i+=1;
        if i==pattern.len() {return 0;}
        let specifier=pattern[i];i+=1;
        match specifier {
            b'%'=>output.push(b'%'),
            b'z'=>{
                let offset=time.gmtoff;
                let text=std::format!("{}{:02}{:02}",if offset<0 {'-'} else {'+'},offset.abs()/3600,offset.abs()%3600/60);
                output.extend_from_slice(text.as_bytes());
            }
            b'Z' if !time.zone.is_null()=>output.extend_from_slice(unsafe {CStr::from_ptr(time.zone)}.to_bytes()),
            b'c'=>{
                // C/POSIX representation, including a space-padded day of month.
                if !unsafe {crt_piece(b'a',time,&mut output)} {return 0;}
                output.push(b' ');
                if !unsafe {crt_piece(b'b',time,&mut output)} {return 0;}
                output.extend_from_slice(std::format!(" {:2} ",time.fields[3]).as_bytes());
                for (j,specifier) in [b'H',b'M',b'S',b'Y'].into_iter().enumerate() {
                    if j>0 {output.push(if j==3 {b' '} else {b':'});}
                    if !unsafe {crt_piece(specifier,time,&mut output)} {return 0;}
                }
            }
            value if b"aAbBdHIjmMpSUwWxXyYZ".contains(&value)=>{
                if !unsafe {crt_piece(value,time,&mut output)} {return 0;}
            }
            _=>return 0,
        }
    }
    if output.len()>=capacity {return 0;}
    unsafe {
        std::ptr::copy_nonoverlapping(output.as_ptr(),destination.cast::<u8>(),output.len());
        destination.add(output.len()).write(0);
    }
    output.len()
}
