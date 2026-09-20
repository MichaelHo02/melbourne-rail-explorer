import {readFileSync} from 'node:fs';
import {describe,it,expect} from 'vitest';
import extension from '../src/data/loop-landscape-source.json';

describe('official City Loop landscape extension',()=>{
  it('retains official provenance and covers the previously missing parks',()=>{
    expect(extension.sources.every(s=>s.license==='CC BY 4.0')).toBe(true);
    const names=extension.layers.openSpaces.features.map(f=>f.properties.name);
    for(const name of ['Flagstaff Gardens','Treasury Gardens','Parliament Gardens','Birrarung Marr'])expect(names).toContain(name);
    expect(extension.layers.roads.features.length).toBeGreaterThan(1000);
  });
  it('keeps every mapped tree in its queried region with a resolvable species',()=>{
    const ids=new Set<string>();
    for(const tree of extension.layers.trees.features){
      const [lon,lat]=tree.geometry.coordinates;
      expect(Number.isFinite(lon)&&Number.isFinite(lat)).toBe(true);
      expect(extension.bounds.some(([west,south,east,north])=>lon>=west&&lon<=east&&lat>=south&&lat<=north)).toBe(true);
      expect(extension.treeSpecies[tree.properties.species]).toBeDefined();
      expect(ids.has(String(tree.properties.com_id))).toBe(false);ids.add(String(tree.properties.com_id));
    }
  });
});

describe('Blender vegetation export contract',()=>{
  const bytes=readFileSync(new URL('../public/models/environment/urban-trees.glb',import.meta.url));
  const gltf=JSON.parse(bytes.subarray(20,20+bytes.readUInt32LE(12)).toString());
  it('exports four upright, grounded species prototypes with vertex colours and bounded geometry',()=>{
    let triangles=0;
    for(const name of ['plane','gum','elm','palm']){
      const node=gltf.nodes.find((n:{name:string})=>n.name===name);expect(node).toBeDefined();
      const mesh=gltf.meshes[node.mesh];expect(mesh.primitives.length).toBeLessThanOrEqual(2);
      for(const primitive of mesh.primitives){expect(primitive.attributes.COLOR_0).toBeDefined();
      const position=gltf.accessors[primitive.attributes.POSITION];
      expect(position.min.every(Number.isFinite)&&position.max.every(Number.isFinite)).toBe(true);
      expect(position.min[1]).toBeGreaterThan(-.15);expect(position.max[1]).toBeGreaterThan(6);
      expect(position.max[1]).toBeLessThan(13);
      triangles+=gltf.accessors[primitive.indices].count/3;
      }
    }
    expect(triangles).toBeLessThan(25_000);expect(bytes.byteLength).toBeLessThan(3_000_000);
  });
});

describe('Swann House survey replacement',()=>{
  const bytes=readFileSync(new URL('../public/models/environment/swann-house.glb',import.meta.url));
  const model=JSON.parse(bytes.subarray(20,20+bytes.readUInt32LE(12)).toString());
  const source=JSON.parse(readFileSync(new URL('../public/data/buildings.json',import.meta.url),'utf8'));
  const manifest=JSON.parse(readFileSync(new URL('../public/models/environment/swann-house.json',import.meta.url),'utf8'));
  it('preserves every retained section and exact survey envelope extents',()=>{
    const node=model.nodes.find((n:{name:string})=>n.name==='structure_801838_clean_envelope');
    expect(node).toBeDefined();expect(node.extras.source_object_ids.split(',').sort()).toEqual([...manifest.objectIds].sort());
    const sections=source.buildings.filter((b:{id:string})=>manifest.objectIds.includes(b.id));
    expect(sections).toHaveLength(manifest.objectIds.length);
    const positions=model.meshes[node.mesh].primitives.map((p:{attributes:{POSITION:number}})=>model.accessors[p.attributes.POSITION]);
    const bounds=[Math.min(...positions.map((p:{min:number[]})=>p.min[0])),Math.min(...positions.map((p:{min:number[]})=>p.min[2])),Math.max(...positions.map((p:{max:number[]})=>p.max[0])),Math.max(...positions.map((p:{max:number[]})=>p.max[2]))];
    const rings:number[][]=sections.flatMap((b:{ring:number[][]})=>b.ring);
    const actual=[Math.min(...rings.map(p=>p[0])),Math.min(...rings.map(p=>p[1])),Math.max(...rings.map(p=>p[0])),Math.max(...rings.map(p=>p[1]))];
    bounds.forEach((v,i)=>expect(v).toBeCloseTo(actual[i],2));
    expect(Math.max(...positions.map((p:{max:number[]})=>p.max[1]))).toBeCloseTo(Math.max(...sections.map((b:{base:number;height:number})=>b.base+b.height)),2);
    expect(model.nodes.some((n:{name:string})=>n.name==='swann_stone_details')).toBe(true);
  });
});
