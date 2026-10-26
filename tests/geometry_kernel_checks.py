"""Independent analytic/SAT references and malformed-buffer checks for convex queries."""
import ctypes as C
import itertools
import math
from pathlib import Path
import random
import struct

ROOT=Path(__file__).resolve().parents[1]
IDENTITY=[1,0,0,0,1,0,0,0,1]
WEDGE=[(.5,.5,.5),(.5,-.5,.5),(.5,-.5,-.5),(-.5,.5,.5),(-.5,-.5,.5),(-.5,-.5,-.5)]
CORNER=[(.5,-.5,.5),(.5,-.5,-.5),(-.5,-.5,-.5),(-.5,-.5,.5),(.5,.5,-.5)]

def add(a,b):return tuple(x+y for x,y in zip(a,b))
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def scale(a,s):return tuple(x*s for x in a)
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def norm(a):return math.sqrt(dot(a,a))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def unit(a):return scale(a,1/norm(a))
def transform(r,p):return tuple(dot(r[i:i+3],p) for i in (0,3,6))
def transpose(r):return [r[i+3*j] for i in range(3) for j in range(3)]

def rotation(rng):
    x,y,z=unit(tuple(rng.uniform(-1,1) for _ in range(3)));a=rng.uniform(-math.pi,math.pi)
    c,s=math.cos(a),math.sin(a);v=1-c
    return [x*x*v+c,x*y*v-z*s,x*z*v+y*s,y*x*v+z*s,y*y*v+c,y*z*v-x*s,z*x*v-y*s,z*y*v+x*s,z*z*v+c]

def record(kind,size=(1,1,1),position=(0,0,0),rotation=IDENTITY):
    return struct.pack('<II15d',kind,0,*size,*position,*rotation)

def packet(mode,actor,targets,direction,maximum=0):
    return struct.pack('<IIII3d24x',0x31514752,mode,len(targets),maximum,*direction)+actor+b''.join(targets)

class Kernel:
    def __init__(self):
        self.dll=C.CDLL(str(ROOT/'vm0735.dll'))
        self.dll.geometry_query.argtypes=[C.c_void_p,C.c_size_t,C.c_void_p,C.c_size_t]
        self.dll.geometry_query.restype=C.c_int
    def run(self,data,count=1):
        inp=C.create_string_buffer(bytes(data));size=64+4*count
        output=C.create_string_buffer(b'X'*16+b'\0'*size+b'Y'*16)
        status=self.dll.geometry_query(inp,len(data),C.addressof(output)+16,size)
        assert output.raw[:16]==b'X'*16 and output.raw[16+size:16+size+16]==b'Y'*16
        return status,bytes(output.raw[16:16+size])
    def hit(self,data,count=1):
        status,out=self.run(data,count);assert status==0,status
        index=struct.unpack_from('<I',out)[0]
        return None if not index else (struct.unpack_from('<d',out,8)[0],struct.unpack_from('<3d',out,16),struct.unpack_from('<3d',out,40))

def planes(kind,size):
    points=[tuple(a*b for a,b in zip(point,size)) for point in (WEDGE if kind==4 else CORNER)]
    result=[]
    for a,b,c in itertools.combinations(points,3):
        n=cross(sub(b,a),sub(c,a))
        if norm(n)<1e-9:continue
        n=unit(n);d=dot(n,a);distances=[dot(n,p)-d for p in points]
        if max(distances)>1e-8:
            if min(distances)<-1e-8:continue
            n=scale(n,-1);d=-d
        if not any(norm(sub(n,other))<1e-8 and abs(d-value)<1e-8 for other,value in result):result.append((n,d))
    return result

def ray(kind,size,o,v):
    hits=[]
    if kind in (1,4,5):
        faces=[(tuple(sign if j==i else 0 for j in range(3)),size[i]/2) for i in range(3) for sign in (-1,1)] if kind==1 else planes(kind,size)
        if all(dot(n,o)<d-1e-9 for n,d in faces):return None
        low,high=0,1;normal=None
        for n,d in faces:
            distance=d-dot(n,o);velocity=dot(n,v)
            if abs(velocity)<1e-12:
                if distance<0:return None
            elif velocity<0:
                t=distance/velocity
                if t>=low:low,normal=t,n
            else:high=min(high,distance/velocity)
            if low>high:return None
        return (low,add(o,scale(v,low)),normal) if normal is not None and 0<=low<=1 else None
    if kind==2:
        r=min(size)/2
        if dot(o,o)<r*r-1e-9:return None
        a,b,c=dot(v,v),2*dot(o,v),dot(o,o)-r*r
        discriminant=b*b-4*a*c
        if discriminant<0:return None
        for t in ((-b-math.sqrt(discriminant))/(2*a),(-b+math.sqrt(discriminant))/(2*a)):
            if 0<=t<=1:
                point=add(o,scale(v,t));return t,point,unit(point)
        return None
    h,r=size[0]/2,min(size[1:])/2
    if abs(o[0])<h-1e-9 and o[1]**2+o[2]**2<r*r-1e-9:return None
    a=v[1]**2+v[2]**2;b=2*(o[1]*v[1]+o[2]*v[2]);c=o[1]**2+o[2]**2-r*r
    if a>1e-12 and b*b-4*a*c>=0:
        for t in ((-b-math.sqrt(b*b-4*a*c))/(2*a),(-b+math.sqrt(b*b-4*a*c))/(2*a)):
            point=add(o,scale(v,t))
            if 0<=t<=1 and abs(point[0])<=h:hits.append((t,point,unit((0,point[1],point[2]))))
    if abs(v[0])>1e-12:
        for sign in (-1,1):
            t=(sign*h-o[0])/v[0];point=add(o,scale(v,t))
            if 0<=t<=1 and point[1]**2+point[2]**2<=r*r:hits.append((t,point,(sign,0,0)))
    return min(hits,key=lambda h:h[0]) if hits else None

def sphere_box(origin,direction,half,radius):
    def closest(p):return tuple(max(-h,min(h,x)) for x,h in zip(p,half))
    if norm(sub(origin,closest(origin)))<=radius+1e-10:return None
    stops=[0.,1.]
    for o,v,h in zip(origin,direction,half):
        if abs(v)>1e-12:
            stops.extend(t for t in ((-h-o)/v,(h-o)/v) if 0<t<1)
    stops=sorted(set(stops))
    for low,high in zip(stops,stops[1:]):
        middle=(low+high)/2;a=b=0.;c=-radius*radius
        for o,v,h in zip(origin,direction,half):
            coordinate=o+v*middle
            if abs(coordinate)>h:
                delta=o-math.copysign(h,coordinate);a+=v*v;b+=2*v*delta;c+=delta*delta
        if a<1e-20:continue
        disc=b*b-4*a*c
        if disc<0:continue
        t=(-b-math.sqrt(disc))/(2*a)
        if low-1e-9<=t<=high+1e-9:
            center=add(origin,scale(direction,t));point=closest(center);return t,point,unit(sub(center,point))
    return None

def swept_boxes(pa,ra,ha,pb,rb,hb,direction):
    aa=[tuple(ra[i+3*j] for j in range(3)) for i in range(3)]
    ba=[tuple(rb[i+3*j] for j in range(3)) for i in range(3)]
    axes=aa+ba+[cross(a,b) for a in aa for b in ba]
    low,high=0.,1.;initial=True
    for axis in axes:
        if norm(axis)<1e-10:continue
        radius=sum(h*abs(dot(a,axis)) for h,a in zip(ha,aa))+sum(h*abs(dot(a,axis)) for h,a in zip(hb,ba))
        offset=dot(sub(pa,pb),axis);speed=dot(direction,axis)
        if abs(offset)>radius:initial=False
        if abs(speed)<1e-12:
            if abs(offset)>radius:return None
        else:
            a,b=sorted(((-radius-offset)/speed,(radius-offset)/speed));low=max(low,a);high=min(high,b)
            if low>high:return None
    return None if initial else low if 0<=low<=high and low<=1 else None

def compare(actual,expected,label,tolerance=2e-5):
    assert (actual is None)==(expected is None),(label,actual,expected)
    if expected:
        assert abs(actual[0]-expected[0])<tolerance,(label,actual,expected)
        assert norm(sub(actual[1],expected[1]))<tolerance*10,(label,actual,expected)
        assert norm(sub(actual[2],expected[2]))<tolerance*10,(label,actual,expected)

def main():
    k=Kernel();rng=random.Random(735987);rays=spheres=boxes=0
    for kind in range(1,6):
        for case in range(300):
            size=tuple(rng.randrange(1,30)/4 for _ in range(3));r=rotation(rng);p=tuple(rng.uniform(-100,100) for _ in range(3))
            origin=tuple(rng.uniform(-12,12) for _ in range(3));end=tuple(rng.uniform(-4,4) for _ in range(3));velocity=sub(end,origin)
            expected=ray(kind,size,origin,velocity)
            if expected:expected=(expected[0],add(p,transform(r,expected[1])),transform(r,expected[2]))
            o=add(p,transform(r,origin));v=transform(r,velocity)
            actual=k.hit(packet(0,record(0,position=o),[record(kind,size,p,r)],v))
            compare(actual,expected,(kind,case));rays+=1
    for case in range(700):
        size=tuple(rng.randrange(1,30)/4 for _ in range(3));radius=rng.randrange(1,17)/4
        o=tuple(rng.uniform(-15,15) for _ in range(3));v=sub(tuple(rng.uniform(-3,3) for _ in range(3)),o)
        expected=sphere_box(o,v,scale(size,.5),radius)
        r=rotation(rng);p=tuple(rng.uniform(-100,100) for _ in range(3));wo=add(p,transform(r,o));wv=transform(r,v)
        if expected:expected=(expected[0],add(p,transform(r,expected[1])),transform(r,expected[2]))
        compare(k.hit(packet(1,record(2,(radius*2,)*3,wo),[record(1,size,p,r)],wv)),expected,('sphere-box',case));spheres+=1
    for case in range(900):
        sa=tuple(rng.randrange(1,20)/4 for _ in range(3));sb=tuple(rng.randrange(1,20)/4 for _ in range(3))
        ra,rb=rotation(rng),rotation(rng);pa=tuple(rng.uniform(-10,10) for _ in range(3));pb=tuple(rng.uniform(-3,3) for _ in range(3))
        v=sub(tuple(rng.uniform(-3,3) for _ in range(3)),pa)
        expected=swept_boxes(pa,ra,scale(sa,.5),pb,rb,scale(sb,.5),v)
        actual=k.hit(packet(1,record(1,sa,pa,ra),[record(1,sb,pb,rb)],v))
        assert (actual is None)==(expected is None),(case,actual,expected)
        if expected is not None:assert abs(actual[0]-expected)<2e-5,(case,actual,expected)
        boxes+=1
    valid=packet(0,record(0,position=(0,0,10)),[record(1)],(0,0,-20))
    for x in (3,3-1e-7,3+1e-7):
        origin=(x,0,10);velocity=(0,0,-20)
        compare(k.hit(packet(1,record(2,(4,4,4),origin),[record(1,(2,2,2))],velocity)),sphere_box(origin,velocity,(1,1,1),2),('grazing',x),1e-4)
    for size in ((0,2,2),(0,0,2),(2,2,0)):
        hit=k.hit(packet(1,record(1,size),[record(1,(2,2,2),(0,0,-10))],(0,0,-20)))
        assert hit and abs(hit[0]-(9-size[2]/2)/20)<1e-6,(size,hit)
    for length in range(0,len(valid),7):assert k.run(valid[:length])[0]!=0
    for offset,fmt,value in ((0,'I',0),(4,'I',3),(8,'I',100001),(16,'d',float('nan')),(64,'I',99),(72,'d',-1),(128,'d',float('inf'))):
        data=bytearray(valid);struct.pack_into('<'+fmt,data,offset,value);assert k.run(data)[0]!=0
    alias=C.create_string_buffer(valid)
    assert k.dll.geometry_query(alias,len(valid),alias,len(valid))==-1
    assert k.dll.geometry_query(None,0,None,0)==-1
    print('ANALYTIC CONVEX RAYS, ROUNDED-BOX SPHERE SWEEPS, INDEPENDENT SWEPT SAT AND PACKET CANARIES PASSED',rays,spheres,boxes)

if __name__=='__main__':main()
