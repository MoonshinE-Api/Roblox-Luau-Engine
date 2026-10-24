//! Reconstructed from the supplied 0.735 binary/dump, not upstream Luau layouts.
//! Stack primitives, bootstrap boundaries, string hash, and the nongarbage allocator.
//! The runner executes the original VM/GC through host adapters; Rust subsets below
//! are independently compared with original functions, not a complete Rust VM.
use std::ptr::{read_unaligned, write_unaligned};
mod allocator;
mod objects;
mod host;
mod random;
mod brickcolor;
mod datetime;
mod http;

#[unsafe(no_mangle)]
pub unsafe extern "C" fn original_call_physical(address:usize,output:*mut u8,d:f32,f:f32,e:f32,fw:f32,ew:f32,a:f32) {
    let function:unsafe extern "sysv64" fn(*mut u8,f32,f32,f32,f32,f32,f32)=unsafe {std::mem::transmute(address)};
    unsafe {function(output,d,f,e,fw,ew,a)}
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn original_call_colors(address:usize,rg:f64,ba:f64)->usize {
    let function:unsafe extern "sysv64" fn(f64,f64)->usize=unsafe {std::mem::transmute(address)};
    unsafe {function(rg,ba)}
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn original_call_f64(address:usize,state:usize)->f64 {
    let function:unsafe extern "sysv64" fn(usize)->f64=unsafe {std::mem::transmute(address)};
    unsafe {function(state)}
}
#[unsafe(no_mangle)]
pub unsafe extern "C" fn original_call_f64_range(address:usize,state:usize,a:f64,b:f64)->f64 {
    let function:unsafe extern "sysv64" fn(usize,f64,f64)->f64=unsafe {std::mem::transmute(address)};
    unsafe {function(state,a,b)}
}

const BASE: usize = 56;
const CALL_INFO: usize = 80;
const TOP: usize = 88;
const SLOT: usize = 16;
const TAG: usize = 12;

unsafe fn read<T: Copy>(base: *const u8, offset: usize) -> T {
    unsafe { read_unaligned(base.add(offset).cast::<T>()) }
}
unsafe fn write<T: Copy>(base: *mut u8, offset: usize, value: T) {
    unsafe { write_unaligned(base.add(offset).cast::<T>(), value) }
}
unsafe fn index(state: *const u8, idx: i32) -> Option<*const u8> {
    let base: usize = unsafe { read(state, BASE) };
    let top: usize = unsafe { read(state, TOP) };
    if idx > 0 {
        let address = base.checked_add((idx as usize - 1).checked_mul(SLOT)?)?;
        if address < top { Some(address as *const u8) } else { None }
    } else if idx > -10000 {
        let address = top.checked_add_signed(idx as isize * SLOT as isize)?;
        if address >= base && address < top { Some(address as *const u8) } else { None }
    } else {
        None // pseudo2addr/registry/upvalues are deliberately not fabricated.
    }
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn recovered_gettop(state: *const u8) -> i32 {
    let base: usize = unsafe { read(state, BASE) };
    let top: usize = unsafe { read(state, TOP) };
    ((top - base) / SLOT) as i32
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn recovered_absindex(state: *const u8, idx: i32) -> i32 {
    if idx <= 0 && idx > -10000 {
        unsafe { recovered_gettop(state) }.wrapping_add(idx).wrapping_add(1)
    } else { idx }
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn recovered_type(state: *const u8, idx: i32) -> i32 {
    match unsafe { index(state, idx) } {
        Some(value) => (unsafe { read::<u32>(value, TAG) }) as i32,
        None => -1,
    }
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn recovered_toboolean(state: *const u8, idx: i32) -> i32 {
    let Some(value) = (unsafe { index(state, idx) }) else { return 0 };
    let tag: u32 = unsafe { read(value, TAG) };
    i32::from(tag != 0 && (tag != 1 || unsafe { read::<i32>(value, 0) } != 0))
}

unsafe fn available(state: *const u8, destination: usize) -> bool {
    let info: usize = unsafe { read(state, CALL_INFO) };
    let limit: usize = unsafe { read(info as *const u8, 0) };
    destination <= limit
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn recovered_settop(state: *mut u8, idx: i32) -> i32 {
    let base: usize = unsafe { read(state, BASE) };
    let old_top: usize = unsafe { read(state, TOP) };
    let destination = if idx >= 0 {
        base.checked_add(idx as usize * SLOT)
    } else { old_top.checked_add_signed((idx as isize + 1) * SLOT as isize) };
    let Some(destination) = destination else { return -1 };
    if destination < base || !unsafe { available(state, destination) } { return -1; }
    let mut cursor = old_top;
    while cursor < destination {
        unsafe { write(cursor as *mut u8, TAG, 0_u32) };
        cursor += SLOT;
    }
    unsafe { write(state, TOP, destination) };
    0
}

unsafe fn push(state: *mut u8, tag: u32, value: Option<u64>, boolean: Option<i32>) -> i32 {
    let top: usize = unsafe { read(state, TOP) };
    let Some(next) = top.checked_add(SLOT) else { return -1 };
    if !unsafe { available(state, next) } { return -1; }
    if let Some(bits) = value { unsafe { write(top as *mut u8, 0, bits) }; }
    if let Some(value) = boolean { unsafe { write(top as *mut u8, 0, i32::from(value != 0)) }; }
    unsafe {
        write(top as *mut u8, TAG, tag);
        write(state, TOP, next);
    }
    0
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn recovered_pushnil(state: *mut u8) -> i32 {
    unsafe { push(state, 0, None, None) }
}
#[unsafe(no_mangle)]
pub unsafe extern "C" fn recovered_pushnumber(state: *mut u8, number: f64) -> i32 {
    unsafe { push(state, 3, Some(number.to_bits()), None) }
}
#[unsafe(no_mangle)]
pub unsafe extern "C" fn recovered_pushboolean(state: *mut u8, boolean: i32) -> i32 {
    unsafe { push(state, 1, None, Some(boolean)) }
}

// The compiler generates the Windows-to-System-V register preservation/argument bridge.
// Only callers owning a valid, mapped function address may use these entry points.
#[unsafe(no_mangle)]
pub unsafe extern "C" fn original_call0(address: usize, state: *mut u8) -> usize {
    let function: unsafe extern "sysv64" fn(*mut u8) -> usize = unsafe { std::mem::transmute(address) };
    unsafe { function(state) }
}
#[unsafe(no_mangle)]
pub unsafe extern "C" fn original_call_i(address: usize, state: *mut u8, argument: i32) -> usize {
    let function: unsafe extern "sysv64" fn(*mut u8, i32) -> usize = unsafe { std::mem::transmute(address) };
    unsafe { function(state, argument) }
}
#[unsafe(no_mangle)]
pub unsafe extern "C" fn original_call_n(address: usize, state: *mut u8, argument: f64) -> usize {
    let function: unsafe extern "sysv64" fn(*mut u8, f64) -> usize = unsafe { std::mem::transmute(address) };
    unsafe { function(state, argument) }
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn original_call_u(address: usize, first: usize, second: usize) -> usize {
    let function: unsafe extern "sysv64" fn(usize, usize) -> usize = unsafe { std::mem::transmute(address) };
    unsafe { function(first, second) }
}
#[unsafe(no_mangle)]
pub unsafe extern "C" fn original_call3(address: usize, a: usize, b: usize, c: usize) -> usize {
    let function: unsafe extern "sysv64" fn(usize, usize, usize) -> usize = unsafe { std::mem::transmute(address) };
    unsafe { function(a,b,c) }
}
#[unsafe(no_mangle)]
pub unsafe extern "C" fn original_call5(address: usize, a: usize, b: usize, c: usize, d: usize, e: usize) -> usize {
    let function: unsafe extern "sysv64" fn(usize,usize,usize,usize,usize) -> usize = unsafe { std::mem::transmute(address) };
    unsafe { function(a,b,c,d,e) }
}

/// Original byte-string hash: wrapping 32-bit arithmetic, including embedded NULs.
#[unsafe(no_mangle)]
pub unsafe extern "C" fn recovered_stringhash(data: *const u8, length: usize) -> u32 {
    let mut hash = length as u32;
    let (mut left, mut middle) = (0_u32, 0_u32);
    let (mut offset, mut remaining) = (0, length);
    while remaining >= 32 {
        left = left.wrapping_add(unsafe { read::<u32>(data, offset) });
        middle = middle.wrapping_add(unsafe { read::<u32>(data, offset+4) });
        hash = hash.wrapping_add(unsafe { read::<u32>(data, offset+8) });
        left = (left ^ hash).wrapping_sub(hash.rotate_left(18));
        middle = (middle ^ left).wrapping_sub(left.rotate_left(21));
        hash = (hash ^ middle).wrapping_sub(middle.rotate_left(7));
        offset += 12;
        remaining -= 12;
    }
    while remaining != 0 {
        remaining -= 1;
        let byte = unsafe { *data.add(offset+remaining) } as u32;
        hash ^= hash.wrapping_shl(5).wrapping_add(hash >> 2).wrapping_add(byte);
    }
    hash
}

type Allocate = unsafe extern "sysv64" fn(usize, usize, usize, usize) -> usize;
type NewMemory = unsafe extern "sysv64" fn(usize, usize, u8) -> usize;
type Protected = unsafe extern "sysv64" fn(usize, usize, usize) -> i32;
type Close = unsafe extern "sysv64" fn(usize);

/// Exact initialization before f_luaopen. Callback dependencies are explicit so the
/// test can stop at that boundary. Returning nonnull here is NOT proof of a ready VM.
#[unsafe(no_mangle)]
pub unsafe extern "C" fn recovered_newstate_boundary(
    allocator: usize, userdata: usize, open_function: usize, protected: usize, close: usize,
) -> usize {
    let allocate: Allocate = unsafe { std::mem::transmute(allocator) };
    let address = unsafe { allocate(userdata, 0, 0, 19424) };
    if address == 0 { return 0; }
    let state = address as *mut u8;
    unsafe {
        write(state, 0, 0x090a_u16);
        write(state, 2, 0_u8);
        write(state, 200, 9_u8);
        write(state, 48, address+128);
        write(state, 64, 0_usize);
        write(state, 80, 0_usize);
        write(state, 3, 0_u32);
        for (at, len) in [(8,16),(32,16),(104,16),(1368,16),(144,16),(128,16),
                          (1392,16),(18688,64),(272,776),(13504,3072),(11464,2040),
                          (16608,2064),(1416,168),(1584,512),(18760,176),
                          (18672,16),(18952,472)] {
            std::ptr::write_bytes(state.add(at), 0, len);
        }
        for at in [120,208,1340,1356,16588,16600,160,1408,18936] {
            // 1340/1356 are 32-bit writes, including preservation of adjacent bytes.
            if at == 1340 || at == 1356 { write(state, at, 0_u32); }
            else { write(state, at, 0_usize); }
        }
        write(state, 184, allocator);
        write(state, 192, userdata);
        write(state, 264, address);
        write(state, 240, address+224);
        write(state, 248, address+224);
        write(state, 1360, 0x70000000_u32);
        write(state, 1384, 1_usize);
        write(state, 201, 0_u8);
        write(state, 18752, 0_u8);
        write(state, 216, 19424_usize);
        write(state, 172, 0x000000c8000000c8_u64);
        write(state, 168, 1024_u32);
        for at in (2140..11500).step_by(72) {
            write(state, at-32, 0_u32);
            write(state, at-16, 0_u32);
            std::ptr::write_bytes(state.add(at), 0, 28);
        }
        write(state, 11456, 19424_usize);
        write(state, 18944, 1_u32);
        let run: Protected = std::mem::transmute(protected);
        if run(address, open_function, 0) != 0 {
            let cleanup: Close = std::mem::transmute(close);
            cleanup(address);
            return 0;
        }
    }
    address
}

/// Original stack_init, with allocator supplied as an explicit testable dependency.
/// The allocator must succeed or transfer control without returning; NULL is invalid.
#[unsafe(no_mangle)]
pub unsafe extern "C" fn recovered_stack_init(state: *mut u8, parent: usize, new_memory: usize) {
    let allocate: NewMemory = unsafe { std::mem::transmute(new_memory) };
    unsafe {
        let category: u8 = read(state, 2);
        let info = allocate(parent, 384, category);
        write(state, 104, info);
        write(state, 80, info);
        write(state, 20, 8_u32);
        write(state, 96, info+336);
        let stack = allocate(parent, 720, category);
        write(state, 64, stack);
        write(state, 16, 45_u32);
        for slot in 0..45 { write(stack as *mut u8, slot*16+12, 0_u32); }
        write(state, 72, stack+640);
        let ci = info as *mut u8;
        write(ci, 24, stack);
        write(ci, 8, 0_usize);
        write(state, 88, stack+16);
        write(ci, 16, stack+16);
        write(state, 56, stack+16);
        write(ci, 0, stack+336);
    }
}

// Test dependencies: System-V entry -> Windows/Python callback. This keeps both
// directions ABI-correct. Tests are serial; configure callbacks before invocation.
use std::sync::atomic::{AtomicUsize, Ordering};
static CALLBACKS: [AtomicUsize; 4] = [const { AtomicUsize::new(0) }; 4];
#[unsafe(no_mangle)]
pub extern "C" fn oracle_set_callback(slot: u32, address: usize) {
    if let Some(callback) = CALLBACKS.get(slot as usize) { callback.store(address, Ordering::SeqCst); }
}
unsafe extern "sysv64" fn oracle_alloc(a: usize, b: usize, c: usize, d: usize) -> usize {
    let callback: unsafe extern "C" fn(usize,usize,usize,usize)->usize = unsafe { std::mem::transmute(CALLBACKS[0].load(Ordering::SeqCst)) };
    unsafe { callback(a,b,c,d) }
}
unsafe extern "sysv64" fn oracle_newmemory(a: usize, b: usize, c: u8) -> usize {
    let callback: unsafe extern "C" fn(usize,usize,u8)->usize = unsafe { std::mem::transmute(CALLBACKS[1].load(Ordering::SeqCst)) };
    unsafe { callback(a,b,c) }
}
unsafe extern "sysv64" fn oracle_protected(a: usize, b: usize, c: usize) -> i32 {
    let callback: unsafe extern "C" fn(usize,usize,usize)->i32 = unsafe { std::mem::transmute(CALLBACKS[2].load(Ordering::SeqCst)) };
    unsafe { callback(a,b,c) }
}
unsafe extern "sysv64" fn oracle_close(a: usize) {
    let callback: unsafe extern "C" fn(usize) = unsafe { std::mem::transmute(CALLBACKS[3].load(Ordering::SeqCst)) };
    unsafe { callback(a) }
}
unsafe extern "sysv64" fn oracle_bzero(address: *mut u8, length: usize) {
    unsafe { std::ptr::write_bytes(address, 0, length) };
}
unsafe extern "sysv64" fn oracle_memset(address: *mut u8, byte: i32, length: usize) -> *mut u8 {
    unsafe { std::ptr::write_bytes(address, byte as u8, length) };
    address
}
unsafe extern "sysv64" fn oracle_memcpy(destination: *mut u8, source: *const u8, length: usize) -> *mut u8 {
    unsafe { std::ptr::copy_nonoverlapping(source,destination,length) };
    destination
}
unsafe extern "sysv64" fn oracle_memcmp(left: *const u8, right: *const u8, length: usize) -> i32 {
    for index in 0..length {
        let (a,b) = unsafe { (*left.add(index),*right.add(index)) };
        if a != b { return a as i32-b as i32; }
    }
    0
}
unsafe extern "sysv64" fn oracle_strlen(string: *const u8) -> usize {
    let mut length = 0;
    while unsafe { *string.add(length) } != 0 { length += 1; }
    length
}
unsafe extern "sysv64" fn oracle_memmove(destination: *mut u8, source: *const u8, length: usize) -> *mut u8 {
    unsafe { std::ptr::copy(source,destination,length) };
    destination
}
unsafe extern "sysv64" fn oracle_luafunction(state: usize) -> i32 {
    let callback: unsafe extern "C" fn(usize,usize,usize)->i32 = unsafe {std::mem::transmute(CALLBACKS[2].load(Ordering::SeqCst))};
    unsafe {callback(state,0,0)}
}
#[unsafe(no_mangle)]
pub extern "C" fn oracle_dependency(slot: u32) -> usize {
    match slot {
        0 => oracle_alloc as *const () as usize,
        1 => oracle_newmemory as *const () as usize,
        2 => oracle_protected as *const () as usize,
        3 => oracle_close as *const () as usize,
        4 => oracle_bzero as *const () as usize,
        5 => oracle_memset as *const () as usize,
        6 => oracle_memcpy as *const () as usize,
        7 => oracle_memcmp as *const () as usize,
        8 => oracle_strlen as *const () as usize,
        9 => oracle_memmove as *const () as usize,
        10 => oracle_luafunction as *const () as usize,
        _ => 0,
    }
}

static STACK_GUARD: u64 = 0x7351131d26bda55a;
#[unsafe(no_mangle)]
pub extern "C" fn oracle_stack_guard() -> usize { &STACK_GUARD as *const u64 as usize }

#[repr(C)]
struct ExceptionRecord {
    code: u32, flags: u32, next: usize, address: usize, count: u32, padding: u32, information: [usize;15],
}
#[repr(C)]
struct ExceptionPointers { record: *const ExceptionRecord, context: usize }
#[link(name="kernel32")]
unsafe extern "system" {
    fn AddVectoredExceptionHandler(first: u32, handler: unsafe extern "system" fn(*const ExceptionPointers)->i32) -> usize;
}
unsafe extern "system" fn crash_report(pointers: *const ExceptionPointers) -> i32 {
    let record = unsafe { &*(*pointers).record };
    if record.code == 0xc0000005 || record.code == 0xc000001d {
        eprintln!("native fault code={:#x} ip={:#x} access={} address={:#x}",record.code,record.address,record.information[0],record.information[1]);
    }
    0
}
#[unsafe(no_mangle)]
pub unsafe extern "C" fn oracle_install_crash_reporter() -> usize {
    unsafe { AddVectoredExceptionHandler(1,crash_report) }
}
