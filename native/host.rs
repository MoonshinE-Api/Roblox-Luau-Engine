//! System-V entry points for portable host services and Lua protected transfers.
use std::{cell::Cell,ffi::{c_char,c_void,CStr},time::{Instant,SystemTime,UNIX_EPOCH},sync::OnceLock};
use std::arch::global_asm;
use std::sync::atomic::{AtomicUsize,Ordering};
#[path="calendar.rs"]
mod calendar;

static PROXY_API:[AtomicUsize;3]=[const {AtomicUsize::new(0)};3];
#[unsafe(no_mangle)]
pub extern "C" fn host_setup_proxy(new_userdata:usize,create_table:usize,set_metatable:usize) {
    for (slot,address) in PROXY_API.iter().zip([new_userdata,create_table,set_metatable]) {slot.store(address,Ordering::SeqCst);}
}
unsafe extern "sysv64" fn host_proxy(state:usize)->i32 {
    unsafe {
        let new:unsafe extern "sysv64" fn(usize,usize,i32)->usize=std::mem::transmute(PROXY_API[0].load(Ordering::SeqCst));
        let table:unsafe extern "sysv64" fn(usize,i32,i32)=std::mem::transmute(PROXY_API[1].load(Ordering::SeqCst));
        let metatable:unsafe extern "sysv64" fn(usize,i32)->i32=std::mem::transmute(PROXY_API[2].load(Ordering::SeqCst));
        new(state,0,0);table(state,0,0);metatable(state,-2);1
    }
}

#[link(name="ucrt")]
unsafe extern "C" {
    fn __stdio_common_vsprintf(options:u64,destination:*mut c_char,size:usize,format:*const c_char,locale:*const c_void,args:*const u64)->i32;
    fn frexp(value:f64,exponent:*mut i32)->f64;
    fn ldexp(value:f64,exponent:i32)->f64;
    fn modf(value:f64,integer:*mut f64)->f64;
    fn strcmp(a:*const c_char,b:*const c_char)->i32;
    fn strchr(a:*const c_char,b:i32)->*mut c_char;
    fn memchr(a:*const c_void,b:i32,n:usize)->*mut c_void;
    fn strncpy(a:*mut c_char,b:*const c_char,n:usize)->*mut c_char;
    fn strncat(a:*mut c_char,b:*const c_char,n:usize)->*mut c_char;
    fn strcat(a:*mut c_char,b:*const c_char)->*mut c_char;
    fn strcspn(a:*const c_char,b:*const c_char)->usize;
    fn strpbrk(a:*const c_char,b:*const c_char)->*mut c_char;
    fn strtod(a:*const c_char,end:*mut *mut c_char)->f64;
    fn strtoll(a:*const c_char,end:*mut *mut c_char,base:i32)->i64;
    fn strtoull(a:*const c_char,end:*mut *mut c_char,base:i32)->u64;
}

macro_rules! unary {
    ($($name:ident => $method:ident),*) => {$(unsafe extern "sysv64" fn $name(a:f64)->f64 {a.$method()})*};
}
unary!(h_acos=>acos,h_asin=>asin,h_atan=>atan,h_cos=>cos,h_cosh=>cosh,h_exp=>exp,
       h_log=>ln,h_log10=>log10,h_log2=>log2,h_sin=>sin,h_sinh=>sinh,h_tan=>tan,h_tanh=>tanh);
unsafe extern "sysv64" fn h_atan2(a:f64,b:f64)->f64 {a.atan2(b)}
unsafe extern "sysv64" fn h_atan2f(a:f32,b:f32)->f32 {a.atan2(b)}
unsafe extern "sysv64" fn h_asinf(a:f32)->f32 {a.asin()}
unsafe extern "sysv64" fn h_pow(a:f64,b:f64)->f64 {a.powf(b)}
unsafe extern "sysv64" fn h_fmod(a:f64,b:f64)->f64 {a%b}
unsafe extern "sysv64" fn h_frexp(a:f64,b:*mut i32)->f64 {unsafe {frexp(a,b)}}
unsafe extern "sysv64" fn h_ldexp(a:f64,b:i32)->f64 {unsafe {ldexp(a,b)}}
unsafe extern "sysv64" fn h_modf(a:f64,b:*mut f64)->f64 {unsafe {modf(a,b)}}
unsafe extern "sysv64" fn h_strcmp(a:*const c_char,b:*const c_char)->i32 {unsafe {strcmp(a,b)}}
unsafe extern "sysv64" fn h_strchr(a:*const c_char,b:i32)->*mut c_char {unsafe {strchr(a,b)}}
unsafe extern "sysv64" fn h_memchr(a:*const c_void,b:i32,n:usize)->*mut c_void {unsafe {memchr(a,b,n)}}
unsafe extern "sysv64" fn h_strncpy(a:*mut c_char,b:*const c_char,n:usize)->*mut c_char {unsafe {strncpy(a,b,n)}}
unsafe extern "sysv64" fn h_strncat(a:*mut c_char,b:*const c_char,n:usize)->*mut c_char {unsafe {strncat(a,b,n)}}
unsafe extern "sysv64" fn h_strcat(a:*mut c_char,b:*const c_char)->*mut c_char {unsafe {strcat(a,b)}}
unsafe extern "sysv64" fn h_strcspn(a:*const c_char,b:*const c_char)->usize {unsafe {strcspn(a,b)}}
unsafe extern "sysv64" fn h_strpbrk(a:*const c_char,b:*const c_char)->*mut c_char {unsafe {strpbrk(a,b)}}
unsafe extern "sysv64" fn h_strtod(a:*const c_char,b:*mut *mut c_char)->f64 {unsafe {strtod(a,b)}}
unsafe extern "sysv64" fn h_strtoll(a:*const c_char,b:*mut *mut c_char,c:i32)->i64 {unsafe {strtoll(a,b,c)}}
unsafe extern "sysv64" fn h_strtoull(a:*const c_char,b:*mut *mut c_char,c:i32)->u64 {unsafe {strtoull(a,b,c)}}
unsafe extern "sysv64" fn h_time(destination:*mut i64)->i64 {
    let value=SystemTime::now().duration_since(UNIX_EPOCH).unwrap_or_default().as_secs() as i64;
    if !destination.is_null() {unsafe {*destination=value};} value
}
fn nanos()->u64 {static START:OnceLock<Instant>=OnceLock::new();START.get_or_init(Instant::now).elapsed().as_nanos() as u64}
unsafe extern "sysv64" fn h_clock()->i64 {(nanos()/1000) as i64}
unsafe extern "sysv64" fn h_absolute_time()->u64 {nanos()}
unsafe extern "sysv64" fn h_timebase(pointer:*mut u32)->i32 {unsafe {*pointer=1;*pointer.add(1)=1};0}
unsafe extern "sysv64" fn h_guard_acquire(pointer:*mut u8)->i32 {i32::from(unsafe {*pointer}==0)}
unsafe extern "sysv64" fn h_guard_release(pointer:*mut u8) {unsafe {*pointer=1};}
unsafe extern "sysv64" fn h_guard_abort(pointer:*mut u8) {unsafe {*pointer=0};}
unsafe extern "sysv64" fn oracle_noop()->usize {0}

// Darwin's C-locale table layout/bit values are documented in Apple's runetype.h
// and _ctype.h. Construct our own ASCII classifications; no libc code is copied.
fn rune_locale()->&'static [u32;800] {
    static TABLE:OnceLock<[u32;800]>=OnceLock::new();
    TABLE.get_or_init(|| {
        let mut table=[0_u32;800];
        for i in 0..256 {
            let c=i as u8;
            let mut flags=0;
            if c.is_ascii_alphabetic(){flags|=0x100;}
            if c.is_ascii_control(){flags|=0x200;}
            if c.is_ascii_digit(){flags|=0x400;}
            if c.is_ascii_graphic(){flags|=0x800;}
            if c.is_ascii_lowercase(){flags|=0x1000;}
            if c.is_ascii_punctuation(){flags|=0x2000;}
            if c.is_ascii_whitespace() || c==11 {flags|=0x4000;}
            if c.is_ascii_uppercase(){flags|=0x8000;}
            if c.is_ascii_hexdigit(){flags|=0x10000;flags|=(c as char).to_digit(16).unwrap();}
            if c==b' ' || c==b'\t'{flags|=0x20000;}
            if (32..127).contains(&i){flags|=0x40000;}
            table[15+i]=flags;
            table[271+i]=c.to_ascii_lowercase() as u32;
            table[527+i]=c.to_ascii_uppercase() as u32;
        }
        table
    })
}
unsafe extern "sysv64" fn h_maskrune(c:i32,mask:u64)->i32 {
    if (0..256).contains(&c) {(rune_locale()[15+c as usize] & mask as u32) as i32} else {0}
}
unsafe extern "sysv64" fn h_tolower(c:i32)->i32 {if (0..256).contains(&c){(c as u8).to_ascii_lowercase() as i32}else{c}}
unsafe extern "sysv64" fn h_toupper(c:i32)->i32 {if (0..256).contains(&c){(c as u8).to_ascii_uppercase() as i32}else{c}}
#[unsafe(no_mangle)]
pub extern "C" fn host_rune_locale()->usize {rune_locale().as_ptr() as usize}

// Convert Darwin/SysV va_list to Windows' linear 8-byte argument slots. Parsing
// chooses the GP vs XMM register bank; actual formatting is delegated to UCRT.
#[repr(C)]
struct VaList {gp:u32,fp:u32,overflow:*const u8,registers:*const u8}
unsafe fn next_argument(list:&mut VaList,float:bool)->u64 {
    unsafe {
        if float && list.fp<176 {
            let value=std::ptr::read_unaligned(list.registers.add(list.fp as usize).cast());
            list.fp+=16;value
        } else if !float && list.gp<48 {
            let value=std::ptr::read_unaligned(list.registers.add(list.gp as usize).cast());
            list.gp+=8;value
        } else {
            let value=std::ptr::read_unaligned(list.overflow.cast());
            list.overflow=list.overflow.add(8);value
        }
    }
}
#[unsafe(no_mangle)]
unsafe extern "sysv64" fn host_vsnprintf(destination:*mut c_char,size:usize,format:*const c_char,arguments:*const VaList)->i32 {
    unsafe {
        let source=&*arguments;
        let mut list=VaList{gp:source.gp,fp:source.fp,overflow:source.overflow,registers:source.registers};
        let text=CStr::from_ptr(format).to_bytes();
        let mut slots=Vec::<u64>::new();
        let mut at=0;
        while at<text.len() {
            if text[at]!=b'%' {at+=1;continue;}
            at+=1;
            if at<text.len() && text[at]==b'%' {at+=1;continue;}
            while at<text.len() && b"-+ #0'".contains(&text[at]) {at+=1;}
            if at<text.len() && text[at]==b'*' {slots.push(next_argument(&mut list,false));at+=1;}
            else {while at<text.len() && text[at].is_ascii_digit() {at+=1;}}
            if at<text.len() && text[at]==b'.' {
                at+=1;
                if at<text.len() && text[at]==b'*' {slots.push(next_argument(&mut list,false));at+=1;}
                else {while at<text.len() && text[at].is_ascii_digit() {at+=1;}}
            }
            while at<text.len() && b"hljztL".contains(&text[at]) {at+=1;}
            if at>=text.len() {break;}
            if text[at]!=b'%' {slots.push(next_argument(&mut list,b"aAeEfFgG".contains(&text[at])));}
            at+=1;
        }
        __stdio_common_vsprintf(2,destination,size,format,std::ptr::null(),slots.as_ptr())
    }
}

// All transfers stay within original VM machine code / these assembly frames.
// No C++ unwinding is attempted through a Mach-O image in a Windows process.
#[repr(C)]
struct ProtectedContext {previous:*mut ProtectedContext,state:usize,status:usize,rsp:usize,rbp:usize,
                        rbx:usize,r12:usize,r13:usize,r14:usize,r15:usize}
thread_local! {static PROTECTED:Cell<*mut ProtectedContext>=const {Cell::new(std::ptr::null_mut())};}
#[unsafe(no_mangle)]
unsafe extern "sysv64" fn host_push_context(context:*mut ProtectedContext) {
    PROTECTED.with(|current|unsafe {(*context).previous=current.replace(context)});
}
#[unsafe(no_mangle)]
unsafe extern "sysv64" fn host_pop_context(context:*mut ProtectedContext) {
    PROTECTED.with(|current|current.set(unsafe {(*context).previous}));
}
#[unsafe(no_mangle)]
unsafe extern "sysv64" fn host_current_context()->*mut ProtectedContext {PROTECTED.with(Cell::get)}
#[unsafe(no_mangle)]
unsafe extern "sysv64" fn host_unprotected_error()->! {eprintln!("Lua error outside a protected call");std::process::abort()}

global_asm!(r#"
.text
.global host_snprintf_bridge
host_snprintf_bridge:
    push rbp
    mov rbp,rsp
    sub rsp,208
    mov [rsp+32],rdi
    mov [rsp+40],rsi
    mov [rsp+48],rdx
    mov [rsp+56],rcx
    mov [rsp+64],r8
    mov [rsp+72],r9
    movups [rsp+80],xmm0
    movups [rsp+96],xmm1
    movups [rsp+112],xmm2
    movups [rsp+128],xmm3
    movups [rsp+144],xmm4
    movups [rsp+160],xmm5
    movups [rsp+176],xmm6
    movups [rsp+192],xmm7
    mov dword ptr [rsp],24
    mov dword ptr [rsp+4],48
    lea rax,[rbp+16]
    mov [rsp+8],rax
    lea rax,[rsp+32]
    mov [rsp+16],rax
    mov rcx,rsp
    call host_vsnprintf
    mov rsp,rbp
    pop rbp
    ret
.global host_rawprotected
host_rawprotected:
    sub rsp,104
    mov [rsp+8],rdi
    mov qword ptr [rsp+16],0
    mov [rsp+24],rsp
    mov [rsp+32],rbp
    mov [rsp+40],rbx
    mov [rsp+48],r12
    mov [rsp+56],r13
    mov [rsp+64],r14
    mov [rsp+72],r15
    mov [rsp+80],rsi
    mov [rsp+88],rdx
    mov rdi,rsp
    call host_push_context
    mov rdi,[rsp+8]
    mov rsi,[rsp+88]
    call qword ptr [rsp+80]
host_protected_return:
    mov rdi,rsp
    call host_pop_context
    mov rax,[rsp+16]
    mov rbp,[rsp+32]
    mov rbx,[rsp+40]
    mov r12,[rsp+48]
    mov r13,[rsp+56]
    mov r14,[rsp+64]
    mov r15,[rsp+72]
    add rsp,104
    ret
.global host_throw
host_throw:
    sub rsp,24
    mov [rsp],rsi
    call host_current_context
    test rax,rax
    jz host_throw_no_context
    mov rdx,[rsp]
    mov [rax+16],rdx
    mov rsp,[rax+24]
    jmp host_protected_return
host_throw_no_context:
    add rsp,24
    jmp host_unprotected_error
"#);
unsafe extern "sysv64" {
    fn host_snprintf_bridge();
    fn host_rawprotected();
    fn host_throw();
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn host_import_address(name:*const u8,length:usize)->usize {
    let name=unsafe {std::slice::from_raw_parts(name,length)};
    macro_rules! ptr {($function:ident)=>{$function as *const () as usize};}
    match name {
        b"_acos"=>ptr!(h_acos),b"_asin"=>ptr!(h_asin),b"_atan"=>ptr!(h_atan),b"_atan2"=>ptr!(h_atan2),
        b"_asinf"=>ptr!(h_asinf),b"_atan2f"=>ptr!(h_atan2f),
        b"_cos"=>ptr!(h_cos),b"_cosh"=>ptr!(h_cosh),b"_exp"=>ptr!(h_exp),b"_log"=>ptr!(h_log),
        b"_log10"=>ptr!(h_log10),b"_log2"=>ptr!(h_log2),b"_sin"=>ptr!(h_sin),b"_sinh"=>ptr!(h_sinh),
        b"_tan"=>ptr!(h_tan),b"_tanh"=>ptr!(h_tanh),b"_pow"=>ptr!(h_pow),b"_fmod"=>ptr!(h_fmod),
        b"_frexp"=>ptr!(h_frexp),b"_ldexp"=>ptr!(h_ldexp),b"_modf"=>ptr!(h_modf),
        b"_strcmp"=>ptr!(h_strcmp),b"_strchr"=>ptr!(h_strchr),b"_memchr"=>ptr!(h_memchr),
        b"_strncpy"=>ptr!(h_strncpy),b"_strncat"=>ptr!(h_strncat),b"_strcat"=>ptr!(h_strcat),
        b"_strcspn"=>ptr!(h_strcspn),b"_strpbrk"=>ptr!(h_strpbrk),b"_strtod"=>ptr!(h_strtod),
        b"_strtoll"=>ptr!(h_strtoll),b"_strtoull"=>ptr!(h_strtoull),
        // Darwin unsigned long is 64-bit; UCRT strtoul is only 32-bit.
        b"_strtoul"=>ptr!(h_strtoull),
        b"_time"=>ptr!(h_time),b"_clock"=>ptr!(h_clock),b"_mach_absolute_time"=>ptr!(h_absolute_time),
        b"_gmtime_r"=>calendar::gmtime_r as *const () as usize,
        b"_localtime_r"=>calendar::localtime_r as *const () as usize,
        b"_strftime"=>calendar::format as *const () as usize,
        b"_difftime"=>calendar::difftime as *const () as usize,
        b"_mach_timebase_info"=>ptr!(h_timebase),b"___cxa_guard_acquire"=>ptr!(h_guard_acquire),
        b"___cxa_guard_release"=>ptr!(h_guard_release),b"___cxa_guard_abort"=>ptr!(h_guard_abort),
        b"___maskrune"=>ptr!(h_maskrune),b"___tolower"=>ptr!(h_tolower),b"___toupper"=>ptr!(h_toupper),
        b"_snprintf"=>ptr!(host_snprintf_bridge),b"_vsnprintf"=>ptr!(host_vsnprintf),
        b"luaD_rawrunprotected"=>ptr!(host_rawprotected),b"luaD_throw"=>ptr!(host_throw),
        b"__host_proxy"=>ptr!(host_proxy),
        b"__host_random"=>super::random::host_random as *const () as usize,
        b"__host_brickcolor"=>super::brickcolor::host_brickcolor as *const () as usize,
        b"__host_datetime"=>super::datetime::host_datetime as *const () as usize,
        b"__host_sleep"=>super::datetime::host_sleep as *const () as usize,
        b"__host_http"=>super::http::host_http as *const () as usize,
        b"__host_guid"=>super::http::host_guid as *const () as usize,
        b"__host_loadbytecode"=>super::http::host_loadbytecode as *const () as usize,
        b"oracle_noop"=>ptr!(oracle_noop),
        _=>0,
    }
}
