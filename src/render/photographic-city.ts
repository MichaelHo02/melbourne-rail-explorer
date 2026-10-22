import * as T from 'three/webgpu';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import manifest from '../data/photomesh-source.json';
import foreground from '../data/photomesh-foreground.json';
import { conflictsWithStationClearance, insideFootprint } from './photomesh-clearance';
import type { ClippedGeometry, PhotomeshGeometry } from './photomesh-clip';

type Footprint=[number,number][];
interface Tile {footprintHullXZ?:number[][];worldBounds:{min:number[];max:number[]}}
interface Building {id?:string;ring:Footprint;base:number;height:number;kind?:string}
interface FacadeSample {x:number;z:number;minY:number;maxY:number}
type WorkerGeometry=ClippedGeometry&{facades:Float32Array};
const completeForegroundSections=new Set(foreground.structures.flatMap(structure=>structure.objectIds));

/** Actual aerial geometry and photographed colour. Clearance clipping happens
 * in a worker and preserves the JPEG atlas along newly created surface edges. */
export class PhotographicCity {
  group=new T.Group();ready:Promise<void>;
  private tiles:{source:Tile;mesh:T.Mesh}[]=[];
  private facades=new Map<string,FacadeSample[]>();
  private affected=new Map<string,Float32Array[]>();
  private ray=new T.Raycaster(new T.Vector3(),new T.Vector3(0,-1,0),0,1000);
  constructor(){this.group.name='City of Melbourne photographic survey 2020';this.ready=this.load();}
  private async load(){
    const loader=new GLTFLoader(),worker=new Worker(new URL('./photomesh.worker.ts',import.meta.url),{type:'module'});
    let nextId=0,fatalError:Error|undefined;
    const requests=new Map<number,{resolve:(geometry:WorkerGeometry)=>void;reject:(error:Error)=>void}>();
    const fail=(error:Error)=>{fatalError=error;for(const request of requests.values())request.reject(error);requests.clear();};
    worker.onmessage=(event:MessageEvent<{id:number;geometry:WorkerGeometry;error?:string}>)=>{
      const request=requests.get(event.data.id);if(!request)return;requests.delete(event.data.id);
      if(event.data.error)request.reject(new Error(event.data.error));else request.resolve(event.data.geometry);
    };
    worker.onerror=event=>fail(new Error(event.message));
    const clip=(geometry:PhotomeshGeometry)=>new Promise<WorkerGeometry>((resolve,reject)=>{
      if(fatalError){reject(fatalError);return;}
      const id=nextId++;requests.set(id,{resolve,reject});
      worker.postMessage({id,geometry},[geometry.position.buffer,geometry.normal.buffer,geometry.uv.buffer,geometry.index.buffer]);
    });
    try{
      await Promise.all(manifest.assets.map(async asset=>{
        const gltf=await loader.loadAsync(asset.path);gltf.scene.updateMatrixWorld(true);
        const meshes:T.Mesh[]=[];gltf.scene.traverse(node=>{if(node instanceof T.Mesh)meshes.push(node);});
        await Promise.all(meshes.map(async (node,index)=>{
          const source=asset.tiles[index] as Tile,original=node.geometry,p=original.attributes.position,n=original.attributes.normal,uv=original.attributes.uv;
          // The converter's runtime contract is identity scene transform and
          // translation-only tile nodes, preserving source local precision.
          const matrix=node.matrixWorld.elements;
          if(matrix.some((v,i)=>i!==12&&i!==13&&i!==14&&Math.abs(v-(i%5===0?1:0))>1e-6))throw new Error('Photographic tile must retain its translation-only source transform.');
          const offset=[matrix[12],matrix[13],matrix[14]];
          const result=await clip({position:new Float32Array(p.array),normal:new Float32Array(n.array),uv:new Float32Array(uv.array),index:original.index?new Uint32Array(original.index.array):Uint32Array.from({length:p.count},(_,i)=>i),offset});
          const geometry=new T.BufferGeometry();
          geometry.setAttribute('position',new T.BufferAttribute(result.position,3));geometry.setAttribute('normal',new T.BufferAttribute(result.normal,3));geometry.setAttribute('uv',new T.BufferAttribute(result.uv,2));geometry.setIndex(new T.BufferAttribute(result.index,1));
          geometry.computeBoundingSphere();node.geometry=geometry;original.dispose();
          node.userData.clearance={sourceTriangles:result.sourceTriangles,removedTriangles:result.removedTriangles,splitTriangles:result.splitTriangles};
          this.indexFacades(result.facades);
          this.indexAffected(result.affectedBounds);
          for(const material of (Array.isArray(node.material)?node.material:[node.material])){
            material.side=T.FrontSide;material.toneMapped=false;
            if(material instanceof T.MeshBasicMaterial&&material.map)material.map.anisotropy=8;
          }
          node.castShadow=false;node.receiveShadow=false;this.tiles.push({source,mesh:node});
        }));
        this.group.add(gltf.scene);
      }));
      this.group.updateMatrixWorld(true);
    }catch(error){fail(error instanceof Error?error:new Error(String(error)));throw error;}
    finally{worker.terminate();}
  }
  private indexFacades(samples:Float32Array){
    for(let i=0;i<samples.length;i+=4){
      const x=samples[i],z=samples[i+1],minY=samples[i+2],maxY=samples[i+3],key=`${Math.floor(x/25)},${Math.floor(z/25)}`;
      const sample={x,z,minY,maxY},bucket=this.facades.get(key);if(bucket)bucket.push(sample);else this.facades.set(key,[sample]);
    }
  }
  private indexAffected(bounds:Float32Array){
    for(let i=0;i<bounds.length;i+=6){
      const box=bounds.subarray(i,i+6);
      for(let x=Math.floor(box[0]/80);x<=Math.floor(box[3]/80);x++)for(let z=Math.floor(box[2]/80);z<=Math.floor(box[5]/80);z++){
        const key=`${x},${z}`,bucket=this.affected.get(key);if(bucket)bucket.push(box);else this.affected.set(key,[box]);
      }
    }
  }
  /** Explicit geometric conflict, not a claim that a photograph replaces it. */
  conflictsWithClearance(building:Building){return conflictsWithStationClearance(building.ring);}
  replacesBuilding(building:Building){
    // Keep every storey from the same measured structure. The corresponding
    // photographic envelope was removed in the worker, so facades cannot mix.
    if(building.id&&completeForegroundSections.has(String(building.id)))return false;
    if(building.kind&&building.kind!=='Structure')return false;
    const x=building.ring.reduce((sum,p)=>sum+p[0],0)/building.ring.length,z=building.ring.reduce((sum,p)=>sum+p[1],0)/building.ring.length;
    const candidates=this.tiles.filter(({source})=>source.footprintHullXZ&&insideFootprint(x,z,source.footprintHullXZ));
    if(!candidates.length)return false;
    const covered=(x:number,z:number)=>this.tiles.some(({source})=>source.footprintHullXZ&&insideFootprint(x,z,source.footprintHullXZ));
    if(!building.ring.every(([x,z],i)=>{const next=building.ring[(i+1)%building.ring.length];return covered(x,z)&&covered((x+next[0])/2,(z+next[1])/2);}))return false;
    // A roof hit alone used to suppress the complete procedural building even
    // where the station mask had removed its photographed lower storeys.
    const minX=Math.min(...building.ring.map(p=>p[0])),maxX=Math.max(...building.ring.map(p=>p[0])),minZ=Math.min(...building.ring.map(p=>p[1])),maxZ=Math.max(...building.ring.map(p=>p[1]));
    // Retain a procedural section whenever a cut source face intersects its
    // volume. Conservative bounds can preserve an extra section, but a surviving
    // roof/one wall must never erase the support removed on another side.
    for(let gx=Math.floor(minX/80);gx<=Math.floor(maxX/80);gx++)for(let gz=Math.floor(minZ/80);gz<=Math.floor(maxZ/80);gz++){
      if(this.affected.get(`${gx},${gz}`)?.some(b=>b[3]>=minX&&b[0]<=maxX&&b[5]>=minZ&&b[2]<=maxZ&&b[4]>=building.base&&b[1]<=building.base+building.height))return false;
    }
    let support=false;
    const low=building.base+Math.min(1,building.height*.1),high=building.base+Math.max(1.5,Math.min(6,building.height*.2));
    for(let gx=Math.floor(minX/25);gx<=Math.floor(maxX/25)&&!support;gx++)for(let gz=Math.floor(minZ/25);gz<=Math.floor(maxZ/25)&&!support;gz++){
      support=!!this.facades.get(`${gx},${gz}`)?.some(p=>p.minY<=high&&p.maxY>=low&&insideFootprint(p.x,p.z,building.ring));
    }
    if(!support)return false;
    this.ray.ray.origin.set(x,800,z);
    const hits=this.ray.intersectObjects(candidates.map(t=>t.mesh),false);
    return hits.some(hit=>hit.point.y>building.base+Math.min(5,building.height*.35));
  }
  update(camera:T.Camera){
    for(const {source,mesh} of this.tiles){
      const {min,max}=source.worldBounds,x=(min[0]+max[0])/2,z=(min[2]+max[2])/2;
      mesh.visible=Math.hypot(camera.position.x-x,camera.position.z-z)<2500;
    }
  }
}
