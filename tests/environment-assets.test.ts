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
      const mesh=gltf.meshes[node.mesh];expect(mesh.primitives).toHaveLength(1);
      const primitive=mesh.primitives[0];expect(primitive.attributes.COLOR_0).toBeDefined();
      const position=gltf.accessors[primitive.attributes.POSITION];
      expect(position.min.every(Number.isFinite)&&position.max.every(Number.isFinite)).toBe(true);
      expect(position.min[1]).toBeGreaterThan(-.15);expect(position.max[1]).toBeGreaterThan(6);
      expect(position.max[1]).toBeLessThan(13);
      triangles+=gltf.accessors[primitive.indices].count/3;
    }
    expect(triangles).toBeLessThan(25_000);expect(bytes.byteLength).toBeLessThan(3_000_000);
  });
});
