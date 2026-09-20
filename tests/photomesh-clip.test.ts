import { describe, expect, it } from 'vitest';
import { ClearanceIndex, clipPhotomesh, facadeSamples, prism, subtractVolume, type PhotomeshGeometry } from '../src/render/photomesh-clip';
import { conflictsWithStationClearance, createPhotomeshClearance, insideFootprint, SOUTHERN_CROSS_CLEARANCE } from '../src/render/photomesh-clearance';

function mesh(vertices:number[][]):PhotomeshGeometry {
  return {position:new Float32Array(vertices.flat()),normal:new Float32Array(vertices.flatMap(()=>[0,1,0])),uv:new Float32Array(vertices.flatMap(([x,,z])=>[x/10,z/10])),index:new Uint32Array(vertices.map((_,i)=>i)),offset:[0,0,0]};
}
function area(geometry:PhotomeshGeometry){
  let result=0;const p=geometry.position;
  for(let i=0;i<geometry.index.length;i+=3){const a=geometry.index[i]*3,b=geometry.index[i+1]*3,c=geometry.index[i+2]*3;result+=Math.abs((p[b]-p[a])*(p[c+2]-p[a+2])-(p[b+2]-p[a+2])*(p[c]-p[a]))/2;}
  return result;
}
const square=prism([[0,0],[2,0],[2,2],[0,2]],-Infinity,10);

describe('photographic clearance clipping',()=>{
  it('cuts the intruding part of a long triangle whose centroid is outside the hall',()=>{
    // Centroid (-1, 1) previously kept the entire tooth inside the platform.
    const source=mesh([[-4,5,0],[2,5,0],[-1,5,3]]),result=clipPhotomesh(source,new ClearanceIndex([square]));
    expect(result.splitTriangles).toBe(1);expect(area(result)).toBeCloseTo(7,5);
    for(let i=0;i<result.index.length;i+=3){
      const points=[0,1,2].map(j=>{const id=result.index[i+j]*3;return Array.from(result.position.slice(id,id+3));});
      const inside=subtractVolume(points,square);let remaining=0;
      for(const polygon of inside)for(let j=1;j<polygon.length-1;j++)remaining+=area(mesh([polygon[0],polygon[j],polygon[j+1]]));
      expect(remaining).toBeCloseTo(area(mesh(points)),5);
    }
  });
  it('subtracts a small clearance enclosed by a triangle, preserving the exterior',()=>{
    const source=mesh([[-10,2,-10],[12,2,-10],[1,2,12]]),result=clipPhotomesh(source,new ClearanceIndex([square]));
    expect(area(result)).toBeCloseTo(area(source)-4,4);
  });
  it('preserves photo UVs, winding and normals at newly created boundaries',()=>{
    const result=clipPhotomesh(mesh([[-4,5,0],[2,5,0],[-1,5,3]]),new ClearanceIndex([square]));
    for(const id of result.index){
      expect(result.uv[id*2]).toBeCloseTo(result.position[id*3]/10,6);
      expect(result.uv[id*2+1]).toBeCloseTo(result.position[id*3+2]/10,6);
      expect(Math.hypot(...result.normal.slice(id*3,id*3+3))).toBeCloseTo(1,6);
    }
    for(let i=0;i<result.index.length;i+=3){const p=result.position,a=result.index[i]*3,b=result.index[i+1]*3,c=result.index[i+2]*3;expect((p[b]-p[a])*(p[c+2]-p[a+2])-(p[b+2]-p[a+2])*(p[c]-p[a])).toBeGreaterThan(0);}
  });
  it('keeps local node translations and geometry above low clearance ceilings intact',()=>{
    const source=mesh([[-100,20,-100],[-99,20,-100],[-100,20,-99]]);source.offset=[100,0,100];
    const result=clipPhotomesh(source,new ClearanceIndex([square]));
    expect(Array.from(result.position)).toEqual(Array.from(source.position));expect(Array.from(result.index)).toEqual([0,1,2]);
    expect(result.affectedBounds.length).toBe(0);
    source.position[1]=source.position[4]=source.position[7]=5;
    const removed=clipPhotomesh(source,new ClearanceIndex([square]));
    expect(removed.index.length).toBe(0);expect(Array.from(removed.affectedBounds)).toEqual([0,5,0,1,5,1]);
  });
  it('subtracts overlapping masks once without duplicate or missing surfaces',()=>{
    const source=mesh([[-10,2,-10],[12,2,-10],[1,2,12]]);
    const second=prism([[1,0],[3,0],[3,2],[1,2]],-Infinity,10);
    expect(area(clipPhotomesh(source,new ClearanceIndex([square,second])))).toBeCloseTo(area(source)-6,4);
  });
  it('does not retain upper tower slices over the approximate Southern Cross hall',()=>{
    const x=SOUTHERN_CROSS_CLEARANCE.reduce((s,p)=>s+p[0],0)/4,z=SOUTHERN_CROSS_CLEARANCE.reduce((s,p)=>s+p[1],0)/4;
    expect(insideFootprint(x,z,SOUTHERN_CROSS_CLEARANCE)).toBe(true);
    // The prior mask ended at 45 m and created suspended upper facade slices.
    const source=mesh([[x,46,z],[x+1,55,z],[x,55,z+1]]);
    expect(clipPhotomesh(source,createPhotomeshClearance()).index.length).toBe(0);
    expect(conflictsWithStationClearance([[x-1,z-1],[x+1,z-1],[x+1,z+1],[x-1,z+1]])).toBe(true);
    expect(conflictsWithStationClearance([[500,500],[510,500],[510,510],[500,510]])).toBe(false);
  });
  it('indexes only surviving steep surfaces as facade support, excluding roofs and removed lower storeys',()=>{
    const source=mesh([[0,1,0],[0,5,0],[0,5,4],[0,5,0],[4,5,0],[0,5,4]]);
    expect(Array.from(facadeSamples(source))).toEqual([0,4/3,1,5].map(Math.fround));
    const mask=prism([[-1,-1],[5,-1],[5,5],[-1,5]],-Infinity,3);
    const retained=facadeSamples(clipPhotomesh(source,new ClearanceIndex([mask])));
    expect(retained.length).toBeGreaterThan(0);
    for(let i=2;i<retained.length;i+=4)expect(retained[i]).toBeGreaterThanOrEqual(3);
  });
  it('removes the folded low station context while preserving tall and remote photographic surfaces',()=>{
    // West of the authored hall, the source sheets remain attached to towers.
    const mask=createPhotomeshClearance();
    const low=mesh([[-1700,30,0],[-1695,30,0],[-1700,30,5]]);
    expect(clipPhotomesh(low,mask).index.length).toBe(0);
    const high=mesh([[-1700,41,0],[-1695,41,0],[-1700,41,5]]);
    expect(Array.from(clipPhotomesh(high,mask).index)).toEqual([0,1,2]);
    const remote=mesh([[500,30,500],[505,30,500],[500,30,505]]);
    expect(Array.from(clipPhotomesh(remote,mask).index)).toEqual([0,1,2]);
  });
});
