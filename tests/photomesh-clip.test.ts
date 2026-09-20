import { describe, expect, it } from 'vitest';
import { ClearanceIndex, clipPhotomesh, facadeSamples, prism, subtractVolume, type PhotomeshGeometry } from '../src/render/photomesh-clip';
import { conflictsWithStationClearance, createPhotomeshClearance, insideFootprint, northbankVegetationVolumes, SOUTHERN_CROSS_CLEARANCE } from '../src/render/photomesh-clearance';
import foreground from '../src/data/photomesh-foreground.json';
import northbank from '../src/data/photomesh-northbank.json';
import {positionAt,tangentAt} from '../src/data/route';

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
  it('cleans low viaduct sheets only in the immediate city-side strip',()=>{
    const all=createPhotomeshClearance(),mask=new ClearanceIndex(all.volumes.filter(v=>v.name==='viaduct low aerial context'));
    const p=positionAt(640),t=tangentAt(640),at=(across:number,y:number)=>mesh([[p.x+t.z*across,y,p.z-t.x*across],[p.x+t.z*across+1,y,p.z-t.x*across],[p.x+t.z*across,y,p.z-t.x*across+1]]);
    expect(clipPhotomesh(at(-70,30),mask).index.length).toBe(0);
    expect(clipPhotomesh(at(-70,45),mask).index.length).toBe(3);
    expect(clipPhotomesh(at(-180,30),mask).index.length).toBe(3);
  });
  it('removes photographic storeys throughout selected complete survey structures',()=>{
    const structure=foreground.structures.find(s=>s.structureId==='809141')!;
    expect(structure.objectIds).toEqual(['12196','12197','12198']);
    const ring=structure.photographicExclusionXZ,x=ring.reduce((sum,p)=>sum+p[0],0)/ring.length,z=ring.reduce((sum,p)=>sum+p[1],0)/ring.length;
    const mask=createPhotomeshClearance();
    for(const height of [10,50,90])expect(clipPhotomesh(mesh([[x,height,z],[x+1,height,z],[x,height,z+1]]),mask).index.length).toBe(0);
  });
  it('clears the measured I3S 141755 residual patch without widening every building envelope',()=>{
    expect(foreground.structures.find(s=>s.structureId==='817607')!.photographicMarginMetres).toBe(6);
    expect(foreground.structures.filter(s=>s.structureId!=='817607').every(s=>s.photographicMarginMetres===3)).toBe(true);
    // World point measured by a ray through screen (1020,385) in the viaduct
    // fixture, 2.48m outside this structure's original 3m exclusion envelope.
    const source=mesh([[-726.40,43.43,116.88],[-726.35,43.43,116.88],[-726.40,43.43,116.93]]);
    expect(clipPhotomesh(source,createPhotomeshClearance()).index.length).toBe(0);
  });
  it('removes only the measured detached seam fragments within finite vertical bounds',()=>{
    const all=createPhotomeshClearance(),mask=new ClearanceIndex(all.volumes.filter(v=>v.name.startsWith('measured residual ')));
    expect(foreground.residualFragments.map(f=>f.retainedTrianglesBeforeRepair)).toEqual([31,7]);
    expect(clipPhotomesh(mesh([[-734.43,46.37,110.42],[-734.38,46.37,110.42],[-734.43,46.37,110.47]]),mask).index.length).toBe(0);
    // Preserve roof/ground geometry directly above/below the same footprint;
    // this correction is not another full-height building or district mask.
    for(const y of [30,60])expect(clipPhotomesh(mesh([[-734.43,y,110.42],[-734.38,y,110.42],[-734.43,y,110.47]]),mask).index.length).toBe(3);
  });
  it('removes aerial crowns above the mapped northbank park trees, preserving higher context',()=>{
    const mask=new ClearanceIndex(northbankVegetationVolumes());
    expect(northbank.parcels.map(p=>p.veacId).sort()).toEqual(['P361466','P383229']);
    expect(northbank.mappedTrees.length).toBeGreaterThan(40);
    for(const tree of northbank.mappedTrees){
      const [x,z]=tree.positionXZ;
      const crown=(y:number)=>mesh([[x,y,z],[x+.02,y,z],[x,y,z+.02]]);
      expect(clipPhotomesh(crown(30),mask).index.length).toBe(0);
      expect(clipPhotomesh(crown(northbank.maxHeight+1),mask).index.length).toBe(3);
    }
    const [x,z]=northbank.mappedTrees[0].positionXZ;
    expect(clipPhotomesh(mesh([[x,30,z],[x+.02,30,z],[x,30,z+.02]]),createPhotomeshClearance()).index.length).toBe(0);
  });
  it('covers a modest canopy overhang without widening the northbank mask into the city',()=>{
    const mask=new ClearanceIndex(northbankVegetationVolumes());
    const west=northbank.parcels.flatMap(p=>p.polygonsXZ.flatMap(r=>r[0])).reduce((a,b)=>a[0]<b[0]?a:b);
    const patch=(x:number,z:number)=>mesh([[x,30,z],[x+.02,30,z],[x,30,z+.02]]);
    expect(clipPhotomesh(patch(west[0]-6,west[1]),mask).index.length).toBe(0);
    expect(clipPhotomesh(patch(west[0]-10,west[1]),mask).index.length).toBe(3);
    expect(clipPhotomesh(patch(-750,100),mask).index.length).toBe(3);
    expect(clipPhotomesh(patch(-900,600),mask).index.length).toBe(3);
  });
});
