import {readFileSync} from 'node:fs';
import {describe,expect,it} from 'vitest';
import {STATIONS,positionAt,tangentAt} from '../src/data/route';
import {platformInboardShift} from '../src/render/platform-layout';
import {CAB_TO_CAR_CENTRE,CAR_SPACING} from '../src/render/train-layout';

type Point={x:number;z:number};
type Vertex=Point&{name:string};
type Car='front'|'trailer'|'rear';
const bytes=readFileSync(new URL('../public/models/melbourne-commuter.glb',import.meta.url));
const length=bytes.readUInt32LE(12),gltf=JSON.parse(bytes.subarray(20,20+length).toString()),binary=bytes.subarray(28+length);
const vertices:Vertex[]=[];
for(const node of gltf.nodes){
  if(node.matrix||node.translation||node.rotation||node.scale)throw new Error('Update clearance audit for transformed train asset nodes');
  for(const primitive of gltf.meshes[node.mesh].primitives){
    const accessor=gltf.accessors[primitive.attributes.POSITION],view=gltf.bufferViews[accessor.bufferView];
    if(accessor.type!=='VEC3'||accessor.componentType!==5126||accessor.sparse)throw new Error('Expected dense float train positions');
    for(let i=0;i<accessor.count;i++){
      const at=(view.byteOffset??0)+(accessor.byteOffset??0)+i*(view.byteStride??12);
      // Including every height is conservative for the platform-level body.
      vertices.push({x:binary.readFloatLE(at),z:binary.readFloatLE(at+8),name:node.name});
    }
  }
}
function hull(points:Point[]){
  const sorted=[...new Map(points.map(p=>[`${p.x},${p.z}`,p])).values()].sort((a,b)=>a.x-b.x||a.z-b.z);
  const cross=(o:Point,a:Point,b:Point)=>(a.x-o.x)*(b.z-o.z)-(a.z-o.z)*(b.x-o.x);
  const half=(points:Point[])=>{const result:Point[]=[];for(const p of points){while(result.length>=2&&cross(result.at(-2)!,result.at(-1)!,p)<=0)result.pop();result.push(p);}return result.slice(0,-1);};
  const boundary=[...half(sorted),...half([...sorted].reverse())];
  // Edge samples catch mid-car intrusion on a curved platform, not just corners.
  return boundary.flatMap((p,i)=>{
    const q=boundary[(i+1)%boundary.length],count=Math.ceil(Math.hypot(q.x-p.x,q.z-p.z)/.5);
    return Array.from({length:count},(_,j)=>({x:p.x+(q.x-p.x)*j/count,z:p.z+(q.z-p.z)*j/count}));
  });
}
const cached=new Map<string,Point[]>();
function carHull(car:Car,openSide=0){
  const key=car+openSide;if(cached.has(key))return cached.get(key)!;
  const result=hull(vertices.filter(v=>!(car==='trailer'?v.name.startsWith('nose_'):v.name.startsWith('trailer_'))).map(v=>{
    let{x,z}=v;
    if(openSide&&v.name.startsWith(openSide<0?'door_L_':'door_R_'))z+=(v.name.includes('_minus_')?-1:1)*.67;
    if(car==='rear'){x=-x;z=-z;}return {x,z};
  }));cached.set(key,result);return result;
}
function frame(distance:number){
  const p=positionAt(distance),t=tangentAt(distance),n=Math.hypot(t.x,t.z);
  if(distance<0){p.x+=t.x*distance;p.z+=t.z*distance;}
  return {...p,tx:t.x/n,tz:t.z/n};
}

describe('authored platform clearance against the shipped train',()=>{
  for(const [index,station] of STATIONS.entries())it(`${station.code} visit ${index+1}: moving hull and open doors clear the rendered coping`,()=>{
    // station-details.ts builds a 0.24m coping at x2.25, length198m, with3m
    // subdivisions. Measure those actual straight edge segments after warping.
    const side=station.code==='FSS'?-1:1,inner=2.25-.24/2-platformInboardShift(station.code),start=station.distance-65-99;
    const edge=Array.from({length:67},(_,i)=>{const p=frame(start+i*3);return {x:p.x+p.tz*inner*side,z:p.z-p.tx*inner*side};});
    let minimum=Infinity;
    function check(centre:number,local:Point[]){
      const p=frame(centre);
      for(const v of local){
        const x=p.x-p.tz*v.x-p.tx*v.z,z=p.z+p.tx*v.x-p.tz*v.z;
        const near=Math.floor((centre-v.z-start)/3);
        for(let i=Math.max(0,near-1);i<=Math.min(65,near+1);i++){
          const a=edge[i],b=edge[i+1],dx=b.x-a.x,dz=b.z-a.z,length=Math.hypot(dx,dz),u=((x-a.x)*dx+(z-a.z)*dz)/(length*length);
          if(u<0||u>1)continue;
          minimum=Math.min(minimum,-side*((x-a.x)*dz-(z-a.z)*dx)/length);
        }
      }
    }
    // Every middle car shares one hull. Sweeping each of the three distinct
    // bodies through the whole platform covers all seven approach/departure cars.
    for(const car of ['front','trailer','rear'] as const)for(let centre=start-14;centre<=start+212;centre+=1)check(centre,carHull(car));
    for(let car=0;car<7;car++)for(const error of [-8,-4,0,4,8]){
      const kind=car===0?'front':car===6?'rear':'trailer',openSide=(station.code==='FSS'?1:-1)*(car===6?-1:1);
      check(station.distance+error-CAB_TO_CAR_CENTRE-car*CAR_SPACING,carHull(kind,openSide));
    }
    // Preserve a visible geometry margin rather than merely accepting contact.
    // This is a game regression guard, not an operational loading-gauge claim.
    expect(minimum).toBeGreaterThan(.08);
  },10_000);
});
