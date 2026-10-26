//! Convex spatial queries, not a dynamics solver or a native Roblox physics port.
//! Packet v1: 64-byte header, 128-byte query, then 128 bytes per target.
//! All fields are little-endian. Shapes: 0 point, 1 box, 2 ball, 3 X-cylinder,
//! 4 wedge, 5 corner wedge. Dimensions and unit hull vertices follow build 735.
use parry3d_f64::{na::{Isometry3,Matrix3,Point3,Rotation3,Translation3,UnitQuaternion,Vector3},
    query::{self,Ray,ShapeCastOptions,ShapeCastStatus},
    shape::{Ball,Cuboid,Cylinder,ConvexPolyhedron,Shape}};
use std::{cell::RefCell,collections::HashMap,sync::Arc};

const HEADER:usize=64;
const RECORD:usize=128;
const LIMIT:usize=100_000;
const MAGIC:u32=0x31514752;
const WEDGE:[[f32;3];6]=[[0.5,0.5,0.5],[0.5,-0.5,0.5],[0.5,-0.5,-0.5],[-0.5,0.5,0.5],[-0.5,-0.5,0.5],[-0.5,-0.5,-0.5]];
const CORNER:[[f32;3];5]=[[0.5,-0.5,0.5],[0.5,-0.5,-0.5],[-0.5,-0.5,-0.5],[-0.5,-0.5,0.5],[0.5,0.5,-0.5]];

fn vertex(kind:u32,size:[f32;3],index:usize)->Option<[f32;3]> {
    let unit=match kind {
        1 if index<8=>[if index&4==0 {0.5}else{-0.5},if index&2==0 {0.5}else{-0.5},if index&1==0 {0.5}else{-0.5}],
        4=>*WEDGE.get(index)?,5=>*CORNER.get(index)?,_=>return None,
    };
    Some([unit[0]*size[0],unit[1]*size[1],unit[2]*size[2]])
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn geometry_vertex(kind:u32,size:*const f32,index:usize,output:*mut f32)->i32 {
    if size.is_null() || output.is_null() {return -1;}
    let dimensions=unsafe {[size.read_unaligned(),size.add(1).read_unaligned(),size.add(2).read_unaligned()]};
    if let Some(value)=vertex(kind,dimensions,index) {
        for (i,v) in value.iter().enumerate() {unsafe {output.add(i).write_unaligned(*v)}}
        0
    }else{-2}
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn geometry_radii(kind:u32,size:*const f32,output:*mut f32)->i32 {
    if size.is_null() || output.is_null() {return -1;}
    let [x,y,z]=unsafe {[size.read_unaligned(),size.add(1).read_unaligned(),size.add(2).read_unaligned()]};
    if ![x,y,z].iter().all(|v|v.is_finite() && *v>=0.0) {return -2;}
    let (radius,bounding)=match kind {
        2=>{let r=x.min(y.min(z))*0.5;(r,r)},
        3=>{let d=y.min(z);(d*0.5,(d*d+x*x).sqrt()*0.5)},
        _=>return -2,
    };
    unsafe {output.write_unaligned(radius);output.add(1).write_unaligned(bounding)};0
}

fn u32_at(bytes:&[u8],offset:usize)->u32 {u32::from_le_bytes(bytes[offset..offset+4].try_into().unwrap())}
fn f64_at(bytes:&[u8],offset:usize)->f64 {f64::from_le_bytes(bytes[offset..offset+8].try_into().unwrap())}
fn put_u32(bytes:&mut [u8],offset:usize,value:u32) {bytes[offset..offset+4].copy_from_slice(&value.to_le_bytes());}
fn put_f64(bytes:&mut [u8],offset:usize,value:f64) {bytes[offset..offset+8].copy_from_slice(&value.to_le_bytes());}

type ShapeCache=HashMap<[u64;4],Arc<dyn Shape>>;
thread_local! {static SHAPES:RefCell<ShapeCache>=RefCell::new(HashMap::new());}
struct Object {shape:Arc<dyn Shape>,pose:Isometry3<f64>}
fn object(record:&[u8])->Result<Object,i32> {
    let kind=u32_at(record,0);
    if kind>5 || u32_at(record,4)!=0 {return Err(-2);}
    let mut data=[0.0;15];
    for (i,value) in data.iter_mut().enumerate() {
        *value=f64_at(record,8+i*8);
        if !value.is_finite() || value.abs()>1.0e12 {return Err(-2);}
    }
    let [x,y,z]=[data[0],data[1],data[2]];
    if x<0.0 || y<0.0 || z<0.0 {return Err(-2);}
    let matrix=Matrix3::from_row_slice(&data[6..15]);
    // Luau frames are orthonormalized before packing. Reject malformed direct
    // host calls instead of silently changing their geometric interpretation.
    if (matrix.transpose()*matrix-Matrix3::identity()).norm()>1.0e-5 || matrix.determinant()<0.99999 {return Err(-2);}
    let rotation=Rotation3::from_matrix_unchecked(matrix);
    let mut pose=Isometry3::from_parts(Translation3::new(data[3],data[4],data[5]),UnitQuaternion::from_rotation_matrix(&rotation));
    if kind==3 {pose.rotation*=UnitQuaternion::from_axis_angle(&Vector3::z_axis(),-std::f64::consts::FRAC_PI_2);}
    let key=[kind as u64,x.to_bits(),y.to_bits(),z.to_bits()];
    let shape=SHAPES.with(|cache|->Result<Arc<dyn Shape>,i32> {
    let mut cache=cache.borrow_mut();
    if let Some(shape)=cache.get(&key) {return Ok(Arc::clone(shape));}
    let shape:Box<dyn Shape>=match kind {
        0=>Box::new(Ball::new(0.0)),
        1=>Box::new(Cuboid::new(Vector3::new(x*0.5,y*0.5,z*0.5))),
        2=>Box::new(Ball::new(x.min(y.min(z))*0.5)),
        3=>{
            // Parry's cylinder is along Y. Roblox's cylinder is along X.
            Box::new(Cylinder::new(x*0.5,y.min(z)*0.5))
        },
        4|5=>{
            let count=if kind==4 {6}else{5};
            let points:Vec<_>=(0..count).map(|i| {
                let p=vertex(kind,[x as f32,y as f32,z as f32],i).unwrap();
                Point3::new(p[0] as f64,p[1] as f64,p[2] as f64)
            }).collect();
            Box::new(ConvexPolyhedron::from_convex_hull(&points).ok_or(-2)?)
        },
        _=>return Err(-2),
    };
    let shape:Arc<dyn Shape>=Arc::from(shape);
    // A bounded cache keeps hull construction out of repeated scene queries.
    // Its allocations are independent of Luau, so its capacity must stay fixed.
    if cache.len()>=256 {cache.clear();}
    cache.insert(key,Arc::clone(&shape));Ok(shape)
    })?;
    Ok(Object{shape,pose})
}

fn execute(input:&[u8],output:&mut [u8])->Result<(),i32> {
    if input.len()<HEADER+RECORD || u32_at(input,0)!=MAGIC {return Err(-1);}
    let mode=u32_at(input,4);let count=u32_at(input,8) as usize;let maximum=u32_at(input,12) as usize;
    if mode>2 || count>LIMIT || input.len()!=HEADER+RECORD*(count+1) || output.len()<64+count*4 {return Err(-1);}
    let direction=Vector3::new(f64_at(input,16),f64_at(input,24),f64_at(input,32));
    if !direction.iter().all(|v|v.is_finite() && v.abs()<=1.0e12) {return Err(-2);}
    let actor=object(&input[HEADER..HEADER+RECORD])?;
    output[..64].fill(0);
    let mut best=1.0;let mut found=None;let mut matches=0;
    let ray=Ray::new(Point3::from(actor.pose.translation.vector),direction);
    for index in 0..count {
        let at=HEADER+RECORD*(index+1);let target=object(&input[at..at+RECORD])?;
        if mode==2 {
            if query::intersection_test(&actor.pose,actor.shape.as_ref(),&target.pose,target.shape.as_ref()).map_err(|_|-3)? {
                put_u32(output,64+matches*4,(index+1) as u32);matches+=1;
                if maximum>0 && matches>=maximum {break;}
            }
            continue;
        }
        if direction.norm_squared()==0.0 {continue;}
        if mode==0 || actor.shape.as_ball().is_some_and(|ball|ball.radius==0.0) {
            // Roblox rays ignore a solid that strictly contains their origin.
            if target.shape.distance_to_point(&target.pose,&ray.origin,false)< -1.0e-10 {continue;}
            if let Some(hit)=target.shape.cast_ray_and_get_normal(&target.pose,&ray,best,false) {
                if hit.time_of_impact<=1.0e-12 && hit.normal.dot(&direction)>=0.0 {continue;}
                if found.is_none() || hit.time_of_impact<best {
                    best=hit.time_of_impact;found=Some((index,ray.point_at(best),hit.normal));
                }
            }
        }else{
            // Initial intersections are excluded for the entire sweep, rather
            // than treating a later exit from the same solid as a fresh hit.
            if query::intersection_test(&actor.pose,actor.shape.as_ref(),&target.pose,target.shape.as_ref()).map_err(|_|-3)? {continue;}
            let options=ShapeCastOptions{max_time_of_impact:best,target_distance:0.0,
                stop_at_penetration:true,compute_impact_geometry_on_penetration:true};
            if let Some(hit)=query::cast_shapes(&actor.pose,&direction,actor.shape.as_ref(),&target.pose,&Vector3::zeros(),target.shape.as_ref(),options).map_err(|_|-3)? {
                if matches!(hit.status,ShapeCastStatus::Failed|ShapeCastStatus::OutOfIterations) {return Err(-4);}
                if found.is_none() || hit.time_of_impact<best {
                    best=hit.time_of_impact;let mut position=target.pose*hit.witness2;let mut normal=target.pose.rotation*hit.normal2.into_inner();
                    // A sphere has a unique surface contact. Project its impact
                    // center to remove lateral GJK witness drift on flat faces.
                    if actor.shape.as_ball().is_some() {
                        let center=Point3::from(actor.pose.translation.vector+direction*best);
                        let surface=target.shape.project_point(&target.pose,&center,false).point;
                        let delta=center-surface;
                        if delta.norm_squared()>1.0e-20 {position=surface;normal=delta.normalize();}
                    }
                    found=Some((index,position,normal));
                }
            }
        }
    }
    if mode==2 {put_u32(output,0,matches as u32);}
    else if let Some((index,position,normal))=found {
        if !best.is_finite() || !position.coords.iter().chain(normal.iter()).all(|v|v.is_finite()) {return Err(-4);}
        put_u32(output,0,(index+1) as u32);put_f64(output,8,best);
        for i in 0..3 {put_f64(output,16+i*8,position[i]);put_f64(output,40+i*8,normal[i]);}
    }
    Ok(())
}

/// Data-only checked buffer interface used by the VM and independent fixtures.
#[unsafe(no_mangle)]
pub unsafe extern "C" fn geometry_query(input:*const u8,input_len:usize,output:*mut u8,output_len:usize)->i32 {
    if input.is_null() || output.is_null() || input_len>HEADER+RECORD*(LIMIT+1) {return -1;}
    let Some(input_end)=(input as usize).checked_add(input_len) else {return -1;};
    let Some(output_end)=(output as usize).checked_add(output_len) else {return -1;};
    if (input as usize)<output_end && (output as usize)<input_end {return -1;}
    // All Rust allocations are dropped before any potentially throwing VM call.
    match std::panic::catch_unwind(||unsafe {
        execute(std::slice::from_raw_parts(input,input_len),std::slice::from_raw_parts_mut(output,output_len))
    }) {Ok(Ok(()))=>0,Ok(Err(code))=>code,Err(_)=>-4}
}

pub unsafe extern "sysv64" fn host_geometry(lua:usize)->i32 {
    unsafe {
        let buffer:unsafe extern "sysv64" fn(usize,i32,*mut usize)->*mut u8=std::mem::transmute(super::random::lua_api(0));
        let push:unsafe extern "sysv64" fn(usize,f64)=std::mem::transmute(super::random::lua_api(2));
        let mut input_len=0;let mut output_len=0;
        let input=buffer(lua,1,&mut input_len);let output=buffer(lua,2,&mut output_len);
        let status=geometry_query(input,input_len,output,output_len);
        push(lua,status as f64);1
    }
}
