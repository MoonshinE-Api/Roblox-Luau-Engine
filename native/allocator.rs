//! 0.735 nongarbage-collected allocator, successful-allocation paths only.
//! Original Lua exceptions on OOM are not portable yet; this slice returns NULL.
use super::{read,write,Allocate};
use std::sync::OnceLock;

#[unsafe(no_mangle)]
pub unsafe extern "C" fn recovered_sizeclassconfig(config: *mut u8) {
    unsafe {
        std::ptr::write_bytes(config, 0, 160);
        std::ptr::write_bytes(config.add(160), 255, 1025);
        let mut count = 0;
        for size in (8..=56).step_by(8).chain((64..=240).step_by(16))
            .chain((256..=480).step_by(32)).chain((512..=1024).step_by(64)) {
            write(config, count*4, size as u32);
            *config.add(160+size) = count as u8;
            count += 1;
        }
        write(config, 1188, count as u32);
        for at in (160..1184).rev() {
            if (*config.add(at) as i8) < 0 { *config.add(at) = *config.add(at+1); }
        }
    }
}

fn config() -> &'static [u8;1192] {
    static CONFIG: OnceLock<[u8;1192]> = OnceLock::new();
    CONFIG.get_or_init(|| {
        let mut table = [0_u8;1192];
        unsafe { recovered_sizeclassconfig(table.as_mut_ptr()) };
        table
    })
}

unsafe fn page(state: *mut u8, chain: usize, bytes: usize, stride: u32, count: u32) -> usize {
    unsafe {
        let global: usize = read(state,48);
        let allocate: Allocate = std::mem::transmute(read::<usize>(global as *const u8,56));
        let result = allocate(read(global as *const u8,64),0,0,bytes);
        if result == 0 { return 0; }
        let pointer = result as *mut u8;
        std::ptr::write_bytes(pointer,0,32);
        write(pointer,32,bytes as u32);
        write(pointer,36,stride);
        write(pointer,40,0_usize);
        write(pointer,48,stride.wrapping_mul(count.wrapping_sub(1)) as u64);
        if chain != 0 {
            let previous: usize = read(chain as *const u8,0);
            write(pointer,8,previous);
            if previous != 0 { write(previous as *mut u8,0,result); }
            write(chain as *mut u8,0,result);
        }
        result
    }
}

unsafe fn block(state: *mut u8, class: usize) -> usize {
    unsafe {
        let global: usize = read(state,48);
        let head = (global+144+class*8) as *mut u8;
        let mut address: usize = read(head,0);
        if address == 0 {
            let size: u32 = read(config().as_ptr(),class*4);
            let bytes = if size >= 513 { 0x7fe8 } else { 0x3fe8 };
            let stride = size+8;
            address = page(state,0,bytes,stride,((bytes-64)/(stride as usize)) as u32);
            if address == 0 { return 0; }
            write(head,0,address);
        }
        let page = address as *mut u8;
        let offset: i32 = read(page,48);
        let pointer;
        if offset < 0 {
            pointer = read::<usize>(page,40);
            write(page,40,read::<usize>(pointer as *const u8,0));
        } else {
            pointer = address+offset as usize+64;
            write(page,48,offset.wrapping_sub(read::<u32>(page,36) as i32));
        }
        write(page,52,read::<u32>(page,52).wrapping_add(1));
        write(pointer as *mut u8,0,address);
        if read::<usize>(page,40) == 0 && read::<i32>(page,48) < 0 {
            let next: usize = read(page,24);
            write(head,0,next);
            if next != 0 { write(next as *mut u8,16,0_usize); }
            write(page,24,0_usize);
        }
        pointer+8
    }
}

unsafe fn allocate(state: *mut u8, bytes: usize, category: u8) -> usize {
    unsafe {
        let global = read::<usize>(state,48) as *mut u8;
        let class = if (1..=1024).contains(&bytes) { config()[160+bytes] as i8 } else { -1 };
        let result = if class >= 0 { block(state,class as usize) } else {
            let function: Allocate = std::mem::transmute(read::<usize>(global,56));
            function(read(global,64),0,0,bytes)
        };
        // The original throws LUA_ERRMEM here; that exception path is not restored.
        if bytes != 0 && result == 0 { return 0; }
        write(global,88,read::<usize>(global,88).wrapping_add(bytes));
        let category_offset = 11328+category as usize*8;
        write(global,category_offset,read::<usize>(global,category_offset).wrapping_add(bytes));
        let notify: usize = read(global,1336);
        if notify != 0 {
            let function: unsafe extern "sysv64" fn(usize,usize,usize) = std::mem::transmute(notify);
            function(state as usize,0,bytes);
        }
        result
    }
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn recovered_allocate_successpath(state: *mut u8, bytes: usize, category: u8) -> usize {
    unsafe { allocate(state,bytes,category) }
}

unsafe extern "sysv64" fn allocation_entry(state: *mut u8, bytes: usize, category: u8) -> usize {
    unsafe { allocate(state,bytes,category) }
}

#[unsafe(no_mangle)]
pub extern "C" fn recovered_allocation_entry() -> usize { allocation_entry as *const () as usize }

unsafe fn release_block(state: *mut u8, class: usize, pointer: usize) {
    unsafe {
        let global: usize = read(state,48);
        let header = (pointer-8) as *mut u8;
        let page = read::<usize>(header,0) as *mut u8;
        let head = (global+144+class*8) as *mut u8;
        let mut free: usize = read(page,40);
        if free == 0 && read::<i32>(page,48) < 0 {
            let old_head: usize = read(head,0);
            write(page,24,old_head);
            if old_head != 0 { write(old_head as *mut u8,16,page as usize); }
            write(head,0,page as usize);
            free = read(page,40);
        }
        write(header,0,free);
        write(page,40,header as usize);
        let used: u32 = read(page,52);
        write(page,52,used.wrapping_sub(1));
        if used == 1 {
            let previous: usize = read(page,16);
            let next: usize = read(page,24);
            if next != 0 { write(next as *mut u8,16,previous); }
            if previous != 0 { write(previous as *mut u8,24,next); }
            else if read::<usize>(head,0) == page as usize { write(head,0,next); }
            let allocate: Allocate = std::mem::transmute(read::<usize>(global as *const u8,56));
            allocate(read(global as *const u8,64),page as usize,read::<i32>(page,32) as usize,0);
        }
    }
}

fn class(bytes: usize) -> i8 {
    if (1..=1024).contains(&bytes) { config()[160+bytes] as i8 } else { -1 }
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn recovered_free(state: *mut u8, pointer: usize, bytes: usize, category: u8) {
    unsafe {
        let global = read::<usize>(state,48) as *mut u8;
        let sizeclass = class(bytes);
        if sizeclass < 0 {
            let allocate: Allocate = std::mem::transmute(read::<usize>(global,56));
            allocate(read(global,64),pointer,bytes,0);
        } else { release_block(state,sizeclass as usize,pointer); }
        write(global,88,read::<usize>(global,88).wrapping_sub(bytes));
        let offset = 11328+category as usize*8;
        write(global,offset,read::<usize>(global,offset).wrapping_sub(bytes));
    }
}

/// Port of luaM_realloc_, preserving bytes and updating counters once. OOM returns
/// NULL without freeing the old allocation; original exception unwinding is pending.
#[unsafe(no_mangle)]
pub unsafe extern "C" fn recovered_realloc_successpath(
    state: *mut u8, pointer: usize, old_bytes: usize, new_bytes: usize, category: u8,
) -> usize {
    unsafe {
        let old_class = class(old_bytes);
        let new_class = class(new_bytes);
        let global = read::<usize>(state,48) as *mut u8;
        let allocate: Allocate = std::mem::transmute(read::<usize>(global,56));
        let userdata = read(global,64);
        let result;
        if (old_class & new_class) < 0 {
            result = allocate(userdata,pointer,old_bytes,new_bytes);
            if new_bytes != 0 && result == 0 { return 0; }
        } else {
            result = if new_class < 0 { allocate(userdata,0,0,new_bytes) }
                     else { block(state,new_class as usize) };
            if new_bytes != 0 && result == 0 { return 0; }
            if old_bytes != 0 && new_bytes != 0 {
                std::ptr::copy_nonoverlapping(pointer as *const u8,result as *mut u8,old_bytes.min(new_bytes));
            }
            if old_class < 0 { allocate(userdata,pointer,old_bytes,0); }
            else { release_block(state,old_class as usize,pointer); }
        }
        let delta = new_bytes.wrapping_sub(old_bytes);
        write(global,88,read::<usize>(global,88).wrapping_add(delta));
        let offset = 11328+category as usize*8;
        write(global,offset,read::<usize>(global,offset).wrapping_add(delta));
        let notify: usize = read(global,1336);
        if notify != 0 {
            let callback: unsafe extern "sysv64" fn(usize,usize,usize) = std::mem::transmute(notify);
            callback(state as usize,old_bytes,new_bytes);
        }
        result
    }
}

unsafe fn release_page(state: *mut u8, chain: usize, address: usize) {
    unsafe {
        let global = read::<usize>(state,48) as *const u8;
        let page = address as *mut u8;
        if chain != 0 {
            let previous: usize = read(page,0);
            let next: usize = read(page,8);
            if next != 0 { write(next as *mut u8,0,previous); }
            if previous != 0 { write(previous as *mut u8,8,next); }
            else if read::<usize>(chain as *const u8,0) == address { write(chain as *mut u8,0,next); }
        }
        let allocate: Allocate = std::mem::transmute(read::<usize>(global,56));
        allocate(read(global,64),address,read::<i32>(page,32) as usize,0);
    }
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn recovered_allocate_gco_successpath(state: *mut u8, bytes: usize, category: u8) -> usize {
    unsafe {
        let global = read::<usize>(state,48) as *mut u8;
        let sizeclass = class(bytes);
        let address;
        let pointer;
        if sizeclass < 0 {
            address = page(state,global as usize+800,bytes+64,bytes as u32,1);
            if address == 0 { return 0; }
            pointer = address+64;
            write(address as *mut u8,48,0_i32.wrapping_sub(bytes as i32));
        } else {
            let head = global.add(480+sizeclass as usize*8);
            let mut current: usize = read(head,0);
            if current == 0 {
                let stride: u32 = read(config().as_ptr(),sizeclass as usize*4);
                let bytes = if stride >= 513 { 0x7fe8 } else { 0x3fe8 };
                current = page(state,global as usize+800,bytes,stride,((bytes-64)/stride as usize) as u32);
                if current == 0 { return 0; }
                write(head,0,current);
            }
            address = current;
            let page = address as *mut u8;
            let offset: i32 = read(page,48);
            if offset < 0 {
                pointer = read(page,40);
                write(page,40,read::<usize>(pointer as *const u8,8));
            } else {
                pointer = address+offset as usize+64;
                write(page,48,offset.wrapping_sub(read::<u32>(page,36) as i32));
            }
            if read::<usize>(page,40) == 0 && read::<i32>(page,48) < 0 {
                let next: usize = read(page,24);
                write(head,0,next);
                if next != 0 { write(next as *mut u8,16,0_usize); }
                write(page,24,0_usize);
            }
        }
        let page = address as *mut u8;
        write(page,52,read::<u32>(page,52).wrapping_add(1));
        write(global,88,read::<usize>(global,88).wrapping_add(bytes));
        let offset = 11328+category as usize*8;
        write(global,offset,read::<usize>(global,offset).wrapping_add(bytes));
        let notify: usize = read(global,1336);
        if notify != 0 {
            let callback: unsafe extern "sysv64" fn(usize,usize,usize) = std::mem::transmute(notify);
            callback(state as usize,0,bytes);
        }
        pointer
    }
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn recovered_free_gco(state: *mut u8, pointer: usize, bytes: usize, category: u8, address: usize) {
    unsafe {
        let global = read::<usize>(state,48) as *mut u8;
        let sizeclass = class(bytes);
        let page = address as *mut u8;
        if sizeclass < 0 { release_page(state,global as usize+800,address); }
        else {
            write(pointer as *mut u8,0,0_u8);
            let head = global.add(480+sizeclass as usize*8);
            let mut free: usize = read(page,40);
            if free == 0 && read::<i32>(page,48) < 0 {
                let old_head: usize = read(head,0);
                write(page,24,old_head);
                if old_head != 0 { write(old_head as *mut u8,16,address); }
                write(head,0,address);
                free = read(page,40);
            }
            write(pointer as *mut u8,8,free);
            write(page,40,pointer);
            let used: u32 = read(page,52);
            write(page,52,used.wrapping_sub(1));
            if used == 1 {
                let previous: usize = read(page,16);
                let next: usize = read(page,24);
                if next != 0 { write(next as *mut u8,16,previous); }
                if previous != 0 { write(previous as *mut u8,24,next); }
                else if read::<usize>(head,0) == address { write(head,0,next); }
                release_page(state,global as usize+800,address);
            }
        }
        write(global,88,read::<usize>(global,88).wrapping_sub(bytes));
        let offset = 11328+category as usize*8;
        write(global,offset,read::<usize>(global,offset).wrapping_sub(bytes));
    }
}
