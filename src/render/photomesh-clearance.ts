import { ShapeUtils, Vector2 } from 'three';
import riverSource from '../data/river-source.json';
import stationClearance from '../data/station-clearance.json';
import { positionAt, project, STATIONS, tangentAt } from '../data/route';
import { ClearanceIndex, prism, type ClearanceVolume } from './photomesh-clip';

export type Ring=readonly (readonly number[])[];
export function insideFootprint(x:number,z:number,ring:Ring){
  let hit=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++){
    const a=ring[i],b=ring[j];if((a[1]>z)!==(b[1]>z)&&x<(b[0]-a[0])*(z-a[1])/(b[1]-a[1])+a[0])hit=!hit;
  }return hit;
}
function cleanRing(ring:Ring):number[][]{
  const result=ring.map(p=>[p[0],p[1]]);
  if(result.length>1&&Math.hypot(result[0][0]-result.at(-1)![0],result[0][1]-result.at(-1)![1])<1e-5)result.pop();
  return result;
}
function polygonVolumes(rings:Ring[],minY:number,maxY:number,name:string):ClearanceVolume[]{
  const points=rings.map(cleanRing),vectors=points.map(r=>r.map(p=>new Vector2(p[0],p[1])));
  const indices=ShapeUtils.triangulateShape(vectors[0],vectors.slice(1)),flat=points.flat();
  return indices.map(triangle=>prism(triangle.map(i=>flat[i]),minY,maxY,name));
}
function rectangle(center:{x:number;z:number},along:{x:number;z:number},minAcross:number,maxAcross:number,halfLength:number){
  return [[minAcross,-halfLength],[maxAcross,-halfLength],[maxAcross,halfLength],[minAcross,halfLength]].map(([x,z])=>[center.x+x*along.z+z*along.x,center.z-x*along.x+z*along.z]);
}
const crossCenter=positionAt(STATIONS[1].distance-65),crossTangent=tangentAt(STATIONS[1].distance-65);
export const SOUTHERN_CROSS_CLEARANCE=rectangle(crossCenter,crossTangent,-95,65,165);
const landmark=project(144.96714,-37.81793),co=Math.cos(.22),si=Math.sin(.22);
const flinders=[[-303,-18],[20,-18],[20,18],[-303,18]].map(([x,z])=>[landmark.x+co*x+si*z,landmark.z-si*x+co*z]);

/** Existing station approximation intersects these footprints. Keep this
 * explicit omission separate from photographic replacement evidence. */
export function conflictsWithStationClearance(ring:Ring){
  return [SOUTHERN_CROSS_CLEARANCE,...stationClearance.features.map(f=>f.ring)].some(mask=>ringsIntersect(ring,mask));
}
export function ringsIntersect(a:Ring,b:Ring){
  let ax0=Infinity,ax1=-Infinity,az0=Infinity,az1=-Infinity,bx0=Infinity,bx1=-Infinity,bz0=Infinity,bz1=-Infinity;
  for(const p of a){ax0=Math.min(ax0,p[0]);ax1=Math.max(ax1,p[0]);az0=Math.min(az0,p[1]);az1=Math.max(az1,p[1]);}
  for(const p of b){bx0=Math.min(bx0,p[0]);bx1=Math.max(bx1,p[0]);bz0=Math.min(bz0,p[1]);bz1=Math.max(bz1,p[1]);}
  if(ax1<bx0||ax0>bx1||az1<bz0||az0>bz1)return false;
  if(a.some(p=>insideFootprint(p[0],p[1],b))||b.some(p=>insideFootprint(p[0],p[1],a)))return true;
  for(let i=0;i<a.length;i++)for(let j=0;j<b.length;j++){
    const p=a[i],q=a[(i+1)%a.length],r=b[j],s=b[(j+1)%b.length],dx=q[0]-p[0],dz=q[1]-p[1],ex=s[0]-r[0],ez=s[1]-r[1],den=dx*ez-dz*ex;
    if(Math.abs(den)<1e-8)continue;
    const t=((r[0]-p[0])*ez-(r[1]-p[1])*ex)/den,u=((r[0]-p[0])*dz-(r[1]-p[1])*dx)/den;
    if(t>=0&&t<=1&&u>=0&&u<=1)return true;
  }return false;
}
function disk(x:number,z:number,radius:number,maxY:number,name:string){
  // Circumscribed 24-gon: the historic radial clearance is never narrowed;
  // its largest excess is 0.33m at radius 38m (0.22m for the bank).
  const radiusOut=radius/Math.cos(Math.PI/24);
  return prism(Array.from({length:24},(_,i)=>[x+Math.cos(i*Math.PI/12)*radiusOut,z+Math.sin(i*Math.PI/12)*radiusOut]),-Infinity,maxY,name);
}
export function createPhotomeshClearance():ClearanceIndex {
  const volumes:ClearanceVolume[]=[
    prism(flinders,0,Infinity,'Flinders authored landmark'),
    prism(SOUTHERN_CROSS_CLEARANCE,-Infinity,Infinity,'Southern Cross authored hall'),
    // Aerial streets/roof undersides here start as much as 19m above the
    // authored rail ground. Keep the tall photographic context and let the
    // complete surveyed procedural facades provide the station-scale detail.
    prism([[-1800,-450],[-1050,-450],[-1050,260],[-1800,260]],-Infinity,40,'Southern Cross low aerial context'),
  ];
  for(const feature of stationClearance.features)volumes.push(...polygonVolumes([feature.ring],-Infinity,Infinity,`survey conflict ${feature.objectId}`));
  const river=riverSource.geometry.coordinates.map(r=>r.map(([lon,lat])=>{const p=project(lon,lat);return [p.x,p.z];}));
  volumes.push(...polygonVolumes(river,-Infinity,18,'Yarra water'));
  const bank=cleanRing(river[0]);
  for(let i=0;i<bank.length;i++){
    const a=bank[i],b=bank[(i+1)%bank.length],dx=b[0]-a[0],dz=b[1]-a[1],length=Math.hypot(dx,dz);
    if(length>1e-5)volumes.push(prism(rectangle({x:(a[0]+b[0])/2,z:(a[1]+b[1])/2},{x:dx/length,z:dz/length},-25,25,length/2),-Infinity,18,'Yarra bank'));
    volumes.push(disk(a[0],a[1],25,18,'Yarra bank join'));
  }
  const railway=Array.from({length:176},(_,i)=>positionAt(i*10));
  for(let i=0;i<railway.length;i++){
    const a=railway[i];volumes.push(disk(a.x,a.z,38,Math.min(18,a.y+9.5),'railway join'));
    if(i===railway.length-1)continue;
    const b=railway[i+1],dx=b.x-a.x,dz=b.z-a.z,length=Math.hypot(dx,dz);
    if(length<1e-5)continue;
    const volume=prism(rectangle({x:(a.x+b.x)/2,z:(a.z+b.z)/2},{x:dx/length,z:dz/length},-38,38,length/2),-Infinity,18,'railway');
    const gx=(b.y-a.y)*dx/(length*length),gz=(b.y-a.y)*dz/(length*length);
    volume.planes.push([gx,-1,gz,a.y+9.5-gx*a.x-gz*a.z]);volumes.push(volume);
  }
  return new ClearanceIndex(volumes);
}
