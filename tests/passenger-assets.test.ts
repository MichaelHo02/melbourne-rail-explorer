import {readFileSync} from 'node:fs';
import {describe,expect,it} from 'vitest';

const bytes=readFileSync(new URL('../public/models/passengers/commuters.glb',import.meta.url));
const jsonLength=bytes.readUInt32LE(12);
const gltf=JSON.parse(bytes.subarray(20,20+jsonLength).toString());
const binary=bytes.subarray(28+jsonLength);
function vectors(accessorIndex:number):number[][] {
  const a=gltf.accessors[accessorIndex];
  if(a.type!=='VEC3'||a.componentType!==5126)throw new Error('Expected float VEC3');
  const values=Array.from({length:a.count},()=>[0,0,0]);
  if(a.bufferView!==undefined){
    const view=gltf.bufferViews[a.bufferView];
    for(let i=0;i<a.count;i++)for(let c=0;c<3;c++)values[i][c]=binary.readFloatLE((view.byteOffset||0)+(a.byteOffset||0)+i*(view.byteStride||12)+c*4);
  }
  if(a.sparse){
    const {indices,data}= {indices:a.sparse.indices,data:a.sparse.values};
    const iv=gltf.bufferViews[indices.bufferView],dv=gltf.bufferViews[data.bufferView];
    const size=indices.componentType===5125?4:indices.componentType===5123?2:1;
    for(let i=0;i<a.sparse.count;i++){
      const offset=(iv.byteOffset||0)+(indices.byteOffset||0)+i*size;
      const index=size===4?binary.readUInt32LE(offset):size===2?binary.readUInt16LE(offset):binary.readUInt8(offset);
      for(let c=0;c<3;c++)values[index][c]=binary.readFloatLE((dv.byteOffset||0)+(data.byteOffset||0)+i*12+c*4);
    }
  }
  return values;
}

describe('shipped commuter geometry',()=>{
  it('exports six near and six distant roots within the material and payload budget',()=>{
    for(let i=1;i<=6;i++)for(const suffix of ['', '_low'])expect(gltf.nodes.some((n:{name?:string})=>n.name===`commuter_${String(i).padStart(2,'0')}${suffix}`)).toBe(true);
    expect(gltf.materials.length).toBeLessThanOrEqual(5);
    expect(bytes.length).toBeLessThan(12_000_000);
  });
  it('ships actual local morph deltas and keeps lower legs and soles planted',()=>{
    let animatedMeshes=0,movingVertices=0,footVertices=0,maxFootDelta=0,allFinite=true;
    for(const mesh of gltf.meshes){
      if(!mesh.extras?.targetNames)continue;
      expect(mesh.extras.targetNames).toEqual(['look_left','look_right','breathe']);animatedMeshes++;
      for(const primitive of mesh.primitives){
        const positions=vectors(primitive.attributes.POSITION);
        expect(primitive.targets).toHaveLength(3);
        for(const target of primitive.targets){
          const deltas=vectors(target.POSITION);
          for(let i=0;i<positions.length;i++){
            allFinite=allFinite&&deltas[i].every(Number.isFinite);
            if(positions[i][1]<.5){maxFootDelta=Math.max(maxFootDelta,Math.hypot(...deltas[i]));footVertices++;}
            if(Math.hypot(...deltas[i])>.0001)movingVertices++;
          }
        }
      }
    }
    expect(allFinite).toBe(true);
    expect(maxFootDelta).toBeLessThan(1e-7);
    expect(animatedMeshes).toBe(30);
    expect(movingVertices).toBeGreaterThan(1000);
    expect(footVertices).toBeGreaterThan(1000);
  });
});
