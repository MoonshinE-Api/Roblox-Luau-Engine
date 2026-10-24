//! Float32 Manhattan lookup, matching RBX::BrickColor::closest(Color4).
//! Catalog rows are packed by the Luau bootstrap from binary-verified literals.
pub unsafe extern "sysv64" fn host_brickcolor(lua:usize)->i32 {
    unsafe {
        let buffer:unsafe extern "sysv64" fn(usize,i32,*mut usize)->*const u8=std::mem::transmute(super::random::lua_api(0));
        let get:unsafe extern "sysv64" fn(usize,i32,*mut i32)->f64=std::mem::transmute(super::random::lua_api(1));
        let push:unsafe extern "sysv64" fn(usize,f64)=std::mem::transmute(super::random::lua_api(2));
        let nil:unsafe extern "sysv64" fn(usize)=std::mem::transmute(super::random::lua_api(3));
        let mut length=0;let catalog=buffer(lua,1,&mut length);
        if catalog.is_null() || length%16!=0 || length>16384 {nil(lua);return 1;}
        let r=get(lua,2,std::ptr::null_mut()) as f32;
        let g=get(lua,3,std::ptr::null_mut()) as f32;
        let b=get(lua,4,std::ptr::null_mut()) as f32;
        let mut selected=194;let mut distance=10000_f32;
        for offset in (0..length).step_by(16) {
            let row=catalog.add(offset);
            let red=row.add(4).cast::<f32>().read_unaligned();
            let green=row.add(8).cast::<f32>().read_unaligned();
            let blue=row.add(12).cast::<f32>().read_unaligned();
            let delta=((red-r).abs()+(green-g).abs())+(blue-b).abs();
            if delta<distance {
                selected=row.cast::<u32>().read_unaligned();distance=delta;
                if delta==0.0 {break;}
            }
        }
        push(lua,selected as f64);1
    }
}
