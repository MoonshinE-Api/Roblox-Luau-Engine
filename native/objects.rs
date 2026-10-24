//! Original-layout strings and table construction. GC tracing/execution is separate.
use super::{read,write,recovered_stringhash,recovered_stack_init};
use super::allocator::{recovered_allocate_successpath as alloc,recovered_free as free,
    recovered_allocate_gco_successpath as gco,recovered_allocation_entry};

#[unsafe(no_mangle)]
pub unsafe extern "C" fn recovered_string_resize(state: *mut u8, buckets: u32) {
    unsafe {
        let global = read::<usize>(state,48) as *mut u8;
        let new = alloc(state,buckets as usize*8,0) as *mut u8;
        std::ptr::write_bytes(new,0,buckets as usize*8);
        let old = read::<usize>(global,0) as *const u8;
        let old_size: u32 = read(global,8);
        for index in 0..old_size as usize {
            let mut string: usize = read(old,index*8);
            while string != 0 {
                let current = string as *mut u8;
                let next: usize = read(current,8);
                let bucket = (read::<u32>(current,16) & buckets.wrapping_sub(1)) as usize*8;
                write(current,8,read::<usize>(new,bucket));
                write(new,bucket,string);
                string = next;
            }
        }
        free(state,old as usize,old_size as usize*8,0);
        write(global,8,buckets);
        write(global,0,new as usize);
    }
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn recovered_intern(state: *mut u8, data: *const u8, length: usize) -> usize {
    unsafe {
        let hash = recovered_stringhash(data,length);
        let global = read::<usize>(state,48) as *mut u8;
        let buckets: u32 = read(global,8);
        let table = read::<usize>(global,0) as *mut u8;
        let mut current: usize = read(table,((buckets-1)&hash) as usize*8);
        while current != 0 {
            let string = current as *mut u8;
            if read::<u32>(string,20) as usize == length &&
                std::slice::from_raw_parts(string.add(24),length) == std::slice::from_raw_parts(data,length) {
                let mark: u8 = read(string,1);
                if ((mark & 0xb) ^ (read::<u8>(global,72)&3)) == 3 { write(string,1,mark^3); }
                return current;
            }
            current = read(string,8);
        }
        let address = gco(state,length+25,read(state,4));
        let string = address as *mut u8;
        write(string,1,read::<u8>(global,72)&3);
        write(string,0,6_u8);
        write(string,2,read::<u8>(state,4));
        write(string,4,0x8000ffff_u32);
        write(string,16,hash);
        write(string,20,length as u32);
        std::ptr::copy_nonoverlapping(data,string.add(24),length);
        write(string,24+length,0_u8);
        let bucket = (hash&(buckets-1)) as usize*8;
        write(string,8,read::<usize>(table,bucket));
        write(table,bucket,address);
        let count = read::<u32>(global,12).wrapping_add(1);
        write(global,12,count);
        if count > buckets && buckets < 0x40000000 { recovered_string_resize(state,buckets*2); }
        address
    }
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn recovered_table_new(state: *mut u8, array: u32, nodes: u32, dummy: usize) -> usize {
    unsafe {
        let address = gco(state,48,read(state,4));
        let table = address as *mut u8;
        let global = read::<usize>(state,48) as *const u8;
        write(table,1,read::<u8>(global,72)&3);
        write(table,0,7_u8);
        write(table,2,read::<u8>(state,4));
        write(table,5,255_u8);
        std::ptr::write_bytes(table.add(24),0,16);
        write(table,3,0_u16);
        write(table,14,0_u16);
        write(table,6,0_u64);
        write(table,16,dummy);
        if array != 0 {
            let values = alloc(state,array as usize*16,read(table,2)) as *mut u8;
            write(table,24,values as usize);
            write(table,8,array);
            for slot in 0..array as usize { write(values,slot*16+12,0_u32); }
        }
        if nodes != 0 {
            let log = 32-(nodes-1).leading_zeros();
            let count = 1_usize << log;
            let values = alloc(state,count*32,read(table,2)) as *mut u8;
            write(table,16,values as usize);
            for slot in 0..count {
                write(values,slot*32+28,0_u32);
                write(values,slot*32+12,0_u32);
            }
            write(table,4,log as u8);
            write(table,7,((1_u32<<log)-1) as u8);
            write(table,12,count as u32);
        }
        address
    }
}

/// f_luaopen successful path with LuauGcTraceUdata disabled. Names/dummy are supplied
/// from the inspected original constant tables, with addresses already relocated.
#[unsafe(no_mangle)]
pub unsafe extern "C" fn recovered_open_successpath(state: *mut u8, dummy: usize, types: *const usize, events: *const usize) {
    unsafe {
        let global = read::<usize>(state,48) as *mut u8;
        recovered_stack_init(state,state as usize,recovered_allocation_entry());
        write(state,112,recovered_table_new(state,0,2,dummy));
        write(global,1216,recovered_table_new(state,0,2,dummy));
        write(global,1228,7_u32);
        recovered_string_resize(state,32);
        for (list,count,offset) in [(types,14,1088),(events,21,920)] {
            for index in 0..count {
                let data = *list.add(index) as *const u8;
                let mut length = 0;
                while *data.add(length) != 0 { length += 1; }
                let string = recovered_intern(state,data,length);
                write(global,offset+index*8,string);
                write(string as *mut u8,1,read::<u8>(string as *const u8,1)|8);
            }
        }
        for data in [b"not enough memory".as_slice(),b"error in error handling".as_slice()] {
            let string = recovered_intern(state,data.as_ptr(),data.len());
            write(string as *mut u8,1,read::<u8>(string as *const u8,1)|8);
        }
        write(global,80,read::<usize>(global,88).wrapping_mul(4));
    }
}
