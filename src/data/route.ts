import routeSource from './route-source.json';
export type Vec3 = { x: number; y: number; z: number };
export const ORIGIN = { lon: 144.9671, lat: -37.8183 };
export function project(lon: number, lat: number, y = 0): Vec3 {
  return { x: (lon - ORIGIN.lon) * 87939, y, z: -(lat - ORIGIN.lat) * 111320 };
}
// Horizontal alignment derived from Victorian DTP public route shapes, CC BY 4.0.
// Two historical service shapes are joined into a fictional training circuit.
// Heights, tunnel transitions and stop markers remain authored approximations;
// this is neither surveyed track/signalling nor a current scheduled service.
// Raw selected features and derivation are retained in route-source.json.
const stationCoordinates=routeSource.sourceStops.map(s=>s.geometry.coordinates as [number,number]);
const anchors=routeSource.coordinates.slice(0,-1).map(([lon,lat])=>project(lon,lat));
const clamp = (v:number, a:number, b:number) => Math.max(a,Math.min(b,v));
const metric=(a:Vec3,b:Vec3)=>Math.hypot(a.x-b.x,a.z-b.z);
// Centripetal Catmull-Rom avoids loops/overshoot from widely varying source spacing.
function curve(a:Vec3,b:Vec3,c:Vec3,d:Vec3,u:number):Vec3 {
  const t0=0,t1=Math.sqrt(metric(a,b)),t2=t1+Math.sqrt(metric(b,c)),t3=t2+Math.sqrt(metric(c,d));
  const t=t1+u*(t2-t1);
  const mix=(p:Vec3,q:Vec3,start:number,end:number):Vec3=>({x:((end-t)*p.x+(t-start)*q.x)/(end-start),y:0,z:((end-t)*p.z+(t-start)*q.z)/(end-start)});
  const A1=mix(a,b,t0,t1),A2=mix(b,c,t1,t2),A3=mix(c,d,t2,t3);
  return mix(mix(A1,A2,t0,t2),mix(A2,A3,t1,t3),t1,t2);
}
const horizontal:(Vec3&{distance:number})[]=[];
let horizontalLength=0;
for(let i=0;i<anchors.length;i++){
  const a=anchors[(i+anchors.length-1)%anchors.length],b=anchors[i],c=anchors[(i+1)%anchors.length],d=anchors[(i+2)%anchors.length];
  const count=Math.max(4,Math.ceil(metric(b,c)/2));
  for(let j=0;j<count;j++){
    const point=curve(a,b,c,d,j/count),previous=horizontal.at(-1);
    if(previous)horizontalLength+=metric(previous,point);
    horizontal.push({...point,distance:horizontalLength});
  }
}
horizontalLength+=metric(horizontal.at(-1)!,horizontal[0]);
horizontal.push({...horizontal[0],distance:horizontalLength});
function horizontalStation(index:number){
  const point=project(...stationCoordinates[index]);
  return horizontal.reduce((best,p)=>metric(p,point)<metric(best,point)?p:best).distance;
}
const sc=horizontalStation(1),fg=horizontalStation(2),par=horizontalStation(4);
// Flat platforms with smooth, conservative grade transitions. No claimed survey heights.
const heightKnots=[[0,7],[250,7],[sc-120,3],[sc+120,3],[fg-120,-23],[par+120,-23],[horizontalLength-250,7],[horizontalLength,7]];
function heightAt(distance:number){
  const i=Math.max(1,heightKnots.findIndex(p=>p[0]>=distance));
  const a=heightKnots[i-1],b=heightKnots[i],t=clamp((distance-a[0])/(b[0]-a[0]),0,1);
  return a[1]+(b[1]-a[1])*t*t*(3-2*t);
}
const samples:(Vec3&{distance:number})[]=[];
let total=0;
for(const point of horizontal){
  const y=heightAt(point.distance),previous=samples.at(-1);
  if(previous)total+=Math.hypot(point.x-previous.x,y-previous.y,point.z-previous.z);
  samples.push({...point,y,distance:total});
}
export const ROUTE_LENGTH=total;
export function positionAt(distance:number):Vec3 {
  const s=clamp(distance,0,ROUTE_LENGTH);
  let lo=0,hi=samples.length-1;
  while(lo<hi){const mid=Math.floor((lo+hi)/2);if(samples[mid].distance<s)lo=mid+1;else hi=mid;}
  const b=samples[lo],a=samples[Math.max(0,lo-1)];
  const t=b.distance===a.distance?0:(s-a.distance)/(b.distance-a.distance);
  return {x:a.x+(b.x-a.x)*t,y:a.y+(b.y-a.y)*t,z:a.z+(b.z-a.z)*t};
}
export function tangentAt(s:number):Vec3 {
  // Carriages and platform furniture can extend behind the initial marker.
  // Sample the endpoint bearing there, rather than subtracting two identical
  // clamped points and collapsing their lateral/longitudinal offsets to zero.
  const center=clamp(s,0,ROUTE_LENGTH);
  const a=positionAt(center-1),b=positionAt(center+1),length=Math.hypot(b.x-a.x,b.y-a.y,b.z-a.z)||1;
  return {x:(b.x-a.x)/length,y:(b.y-a.y)/length,z:(b.z-a.z)/length};
}
function nearest(lon:number,lat:number,min=0){
  const p=project(lon,lat);let nearest=samples[0],best=Infinity;
  for(const v of samples) {if(v.distance<min)continue;const d=Math.hypot(v.x-p.x,v.z-p.z);if(d<best){best=d;nearest=v;}}
  return nearest.distance;
}
export const STATIONS=[
  {name:'Flinders Street',short:'Flinders St',distance:60,underground:false,code:'FSS',color:'#d3ad64'},
  {name:'Southern Cross',short:'Southern Cross',distance:nearest(...stationCoordinates[1]),underground:false,code:'SXS',color:'#8babb9'},
  {name:'Flagstaff',short:'Flagstaff',distance:nearest(...stationCoordinates[2]),underground:true,code:'FGS',color:'#b9bbb2'},
  {name:'Melbourne Central',short:'Melbourne Central',distance:nearest(...stationCoordinates[3]),underground:true,code:'MCE',color:'#c2beac'},
  {name:'Parliament',short:'Parliament',distance:nearest(...stationCoordinates[4]),underground:true,code:'PAR',color:'#174998'},
  {name:'Flinders Street',short:'Flinders St',distance:ROUTE_LENGTH-60,underground:false,code:'FSS',color:'#d3ad64'},
] as const;
export function isUnderground(s:number){return positionAt(s).y < -8;}
export function speedLimitAt(s:number){return isUnderground(s)?60:50;}
export const ROUTE_MAP = Array.from({length:240},(_,i)=>positionAt(i*ROUTE_LENGTH/239));
