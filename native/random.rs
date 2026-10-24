//! RBX::Random recovered from the supplied 0.735 Random.c and x86-64 instructions.
//! Eight-byte PCG state; no dependency on the host's math.random implementation.
use std::sync::atomic::{AtomicUsize,AtomicU64,Ordering};
const MULT:u64=0x5851f42d4c957f2d;
#[unsafe(no_mangle)]
pub unsafe extern "C" fn recovered_random_seed(state:*mut u64,seed:u64) {
    unsafe {state.write_unaligned(seed.wrapping_mul(MULT).wrapping_add(0x399d2694695129de));}
}
fn next(state:&mut u64)->u32 {
    let old=*state;
    *state=old.wrapping_mul(MULT).wrapping_add(105);
    (((old>>27)^(old>>45)) as u32).rotate_right((old>>59) as u32)
}
fn number(state:&mut u64)->f64 {
    let low=next(state) as u64;
    let high=next(state) as u64;
    ((high<<32|low) as f64)*2.0_f64.powi(-64)
}
fn integer(state:&mut u64,a:i64,b:i64)->i64 {
    let min=a.min(b) as u64;
    let diff=(a.max(b) as u64).wrapping_sub(min);
    let low=next(state) as u64;
    if diff>>1<=0x7ffffffe {return min.wrapping_add((low*(diff+1))>>32) as i64;}
    let high=next(state) as u64;
    let span=diff.wrapping_add(1);
    if span==0 {return (low|high<<32) as i64;}
    min.wrapping_add((high*(span as u32 as u64))>>32)
        .wrapping_add(high*(span>>32)).wrapping_add((low*(span>>32))>>32) as i64
}
#[unsafe(no_mangle)]
pub unsafe extern "C" fn recovered_random_number(state:*mut u64)->f64 {
    let mut value=unsafe {state.read_unaligned()};let result=number(&mut value);
    unsafe {state.write_unaligned(value)};result
}
#[unsafe(no_mangle)]
pub unsafe extern "C" fn recovered_random_range(state:*mut u64,a:f64,b:f64)->f64 {
    let t=unsafe {recovered_random_number(state)};
    // Preserve operand order of minsd(b,a)/maxsd(a,b), including NaN and -0.
    let min=if b<a {b}else{a};let max=if a>b {a}else{b};
    let result=t*max+(1.0-t)*min;
    if min>result {min} else if result>max {max} else {result}
}
#[unsafe(no_mangle)]
pub unsafe extern "C" fn recovered_random_integer(state:*mut u64,a:i64,b:i64)->i64 {
    let mut value=unsafe {state.read_unaligned()};let result=integer(&mut value,a,b);
    unsafe {state.write_unaligned(value)};result
}
// Lua's number-to-int bridge uses cvttsd2si, whose invalid sentinel is INT64_MIN.
fn truncate(value:f64)->i64 {
    if !value.is_finite() || value< -((1_u64<<63) as f64) || value>=(1_u64<<63) as f64 {i64::MIN}
    else {value as i64}
}
static API:[AtomicUsize;4]=[const {AtomicUsize::new(0)};4];
pub(crate) fn lua_api(index:usize)->usize {API[index].load(Ordering::SeqCst)}
#[unsafe(no_mangle)]
pub extern "C" fn host_setup_random(buffer:usize,number:usize,push:usize,nil:usize) {
    for (slot,address) in API.iter().zip([buffer,number,push,nil]) {slot.store(address,Ordering::SeqCst);}
}
pub unsafe extern "sysv64" fn host_random(lua:usize)->i32 {
    unsafe {
        let buffer:unsafe extern "sysv64" fn(usize,i32,*mut usize)->*mut u64=std::mem::transmute(API[0].load(Ordering::SeqCst));
        let get:unsafe extern "sysv64" fn(usize,i32,*mut i32)->f64=std::mem::transmute(API[1].load(Ordering::SeqCst));
        let push:unsafe extern "sysv64" fn(usize,f64)=std::mem::transmute(API[2].load(Ordering::SeqCst));
        let nil:unsafe extern "sysv64" fn(usize)=std::mem::transmute(API[3].load(Ordering::SeqCst));
        let mut length=0;let state=buffer(lua,1,&mut length);
        if state.is_null() || length!=8 {nil(lua);return 1;}
        match get(lua,2,std::ptr::null_mut()) as i32 {
            0=>{recovered_random_seed(state,truncate(get(lua,3,std::ptr::null_mut())) as u64);0},
            1=>{push(lua,recovered_random_number(state));1},
            2=>{let a=get(lua,3,std::ptr::null_mut());let b=get(lua,4,std::ptr::null_mut());push(lua,recovered_random_range(state,a,b));1},
            3=>{let a=truncate(get(lua,3,std::ptr::null_mut()));let b=truncate(get(lua,4,std::ptr::null_mut()));push(lua,recovered_random_integer(state,a,b) as f64);1},
            4=>{
                let mut s=state.read_unaligned();
                let angle=((next(&mut s) as f64)*2.0_f64.powi(-32)) as f32*std::f32::consts::TAU;
                let t=((next(&mut s) as f64)*2.0_f64.powi(-32)) as f32;
                let z=(t+t)-1.0;let radius=(1.0-z*z).sqrt();
                let (sin,cos)=angle.sin_cos();
                state.write_unaligned(s);push(lua,(cos*radius) as f64);push(lua,(sin*radius) as f64);push(lua,z as f64);3
            },
            5=>{
                // Seedless construction uses host entropy, not Studio's shared RNG.
                static COUNTER:AtomicU64=AtomicU64::new(0);
                let tick=std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap_or_default().as_nanos() as u64;
                recovered_random_seed(state,tick^COUNTER.fetch_add(0x9e3779b97f4a7c15,Ordering::Relaxed));0
            },
            _=>{nil(lua);1}
        }
    }
}
