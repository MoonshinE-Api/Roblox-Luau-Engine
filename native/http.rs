//! No Python frame is active when a Lua allocation can throw. Response memory
//! remains pinned by the host until the Lua caller explicitly releases its ID.
use std::sync::atomic::{AtomicUsize,Ordering};
static CALLBACK:AtomicUsize=AtomicUsize::new(0);
static GET_STRING:AtomicUsize=AtomicUsize::new(0);
static PUSH_STRING:AtomicUsize=AtomicUsize::new(0);
static LOAD_BYTECODE:AtomicUsize=AtomicUsize::new(0);
#[repr(C)]
struct Transfer {metadata:usize,metadata_len:usize,body:usize,body_len:usize}
#[unsafe(no_mangle)]
pub extern "C" fn host_setup_http(callback:usize,get:usize,push:usize,load:usize) {
    CALLBACK.store(callback,Ordering::Relaxed);
    GET_STRING.store(get,Ordering::Relaxed);PUSH_STRING.store(push,Ordering::Relaxed);
    LOAD_BYTECODE.store(load,Ordering::Relaxed);
}
pub unsafe extern "sysv64" fn host_loadbytecode(lua:usize)->i32 {
    unsafe {
        let buffer:unsafe extern "sysv64" fn(usize,i32,*mut usize)->usize=std::mem::transmute(super::random::lua_api(0));
        let text:unsafe extern "sysv64" fn(usize,i32,*mut usize)->usize=std::mem::transmute(GET_STRING.load(Ordering::Relaxed));
        let load:unsafe extern "sysv64" fn(usize,usize,usize,usize,i32)->i32=std::mem::transmute(LOAD_BYTECODE.load(Ordering::Relaxed));
        let push:unsafe extern "sysv64" fn(usize,f64)=std::mem::transmute(super::random::lua_api(2));
        let nil:unsafe extern "sysv64" fn(usize)=std::mem::transmute(super::random::lua_api(3));
        let mut len=0;let bytes=buffer(lua,1,&mut len);let name=text(lua,2,std::ptr::null_mut());
        if bytes==0 || name==0 {nil(lua);push(lua,-1.0);return 2;}
        let status=load(lua,name,bytes,len,0);
        push(lua,status as f64);2
    }
}
pub unsafe extern "sysv64" fn host_http(lua:usize)->i32 {
    unsafe {
        let get:unsafe extern "sysv64" fn(usize,i32,*mut i32)->f64=std::mem::transmute(super::random::lua_api(1));
        let push:unsafe extern "sysv64" fn(usize,f64)=std::mem::transmute(super::random::lua_api(2));
        let nil:unsafe extern "sysv64" fn(usize)=std::mem::transmute(super::random::lua_api(3));
        let callback:unsafe extern "C" fn(usize,usize)->usize=std::mem::transmute(CALLBACK.load(Ordering::Relaxed));
        let op=get(lua,1,std::ptr::null_mut()) as usize;
        if op==0 || op==4 {
            let text:unsafe extern "sysv64" fn(usize,i32,*mut usize)->usize=std::mem::transmute(GET_STRING.load(Ordering::Relaxed));
            let mut input=Transfer{metadata:0,metadata_len:0,body:0,body_len:0};
            input.metadata=text(lua,2,&mut input.metadata_len);
            input.body=text(lua,3,&mut input.body_len);
            let id=callback(op,&input as *const Transfer as usize);
            push(lua,id as f64);return 1;
        }
        let arg=get(lua,2,std::ptr::null_mut()) as usize;
        let result=callback(op,arg);
        if op==5 {push(lua,result as f64);return 1;}
        if op==1 {
            if result==0 {nil(lua);return 1;}
            let response=&*(result as *const Transfer);
            let string:unsafe extern "sysv64" fn(usize,usize,usize)=std::mem::transmute(PUSH_STRING.load(Ordering::Relaxed));
            string(lua,response.body,response.body_len);
            string(lua,response.metadata,response.metadata_len);
            return 2;
        }
        0
    }
}
#[link(name="bcrypt")]
unsafe extern "system" {fn BCryptGenRandom(algorithm:usize,buffer:*mut u8,len:u32,flags:u32)->i32;}
pub unsafe extern "sysv64" fn host_guid(lua:usize)->i32 {
    unsafe {
        let get:unsafe extern "sysv64" fn(usize,i32,*mut usize)->*mut u8=std::mem::transmute(super::random::lua_api(0));
        let push:unsafe extern "sysv64" fn(usize,f64)=std::mem::transmute(super::random::lua_api(2));
        let mut len=0;let bytes=get(lua,1,&mut len);
        let result=if !bytes.is_null() && len==16 {BCryptGenRandom(0,bytes,16,2)}else{-1};
        if result>=0 { *bytes.add(6)=(*bytes.add(6)&15)|64; *bytes.add(8)=(*bytes.add(8)&63)|128; }
        push(lua,result as f64);1
    }
}
