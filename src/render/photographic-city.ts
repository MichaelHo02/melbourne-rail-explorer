import * as T from 'three/webgpu';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import manifest from '../data/photomesh-source.json';
import riverSource from '../data/river-source.json';
import stationClearance from '../data/station-clearance.json';
import { positionAt, project, STATIONS, tangentAt } from '../data/route';

type Footprint=[number,number][];
interface Tile {footprintHullXZ?:number[][];worldBounds:{min:number[];max:number[]}}
interface Building {ring:Footprint;base:number;height:number;kind?:string}
function inside(x:number,z:number,ring:readonly number[][]){
  let hit=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++){
    const a=ring[i],b=ring[j];if((a[1]>z)!==(b[1]>z)&&x<(b[0]-a[0])*(z-a[1])/(b[1]-a[1])+a[0])hit=!hit;
  }return hit;
}
const railway=Array.from({length:176},(_,i)=>positionAt(i*10));
const crossCenter=positionAt(STATIONS[1].distance-65),crossTangent=tangentAt(STATIONS[1].distance-65);
const river=riverSource.geometry.coordinates.map(r=>r.map(([lon,lat])=>{const p=project(lon,lat);return [p.x,p.z];}));
function nearBank(x:number,z:number){
  const ring=river[0];
  for(let i=1;i<ring.length;i++){
    const a=ring[i-1],b=ring[i],dx=b[0]-a[0],dz=b[1]-a[1],length=dx*dx+dz*dz;
    const t=Math.max(0,Math.min(1,((x-a[0])*dx+(z-a[1])*dz)/(length||1)));
    if((x-a[0]-t*dx)**2+(z-a[1]-t*dz)**2<25**2)return true;
  }return false;
}

/** Actual aerial geometry and photographed colour, with only the playable track
 * clearance cut out. The source capture is May 2020, not a live city feed. */
export class PhotographicCity {
  group=new T.Group();ready:Promise<void>;
  private tiles:{source:Tile;mesh:T.Mesh}[]=[];
  private ray=new T.Raycaster(new T.Vector3(),new T.Vector3(0,-1,0),0,1000);
  constructor(){this.group.name='City of Melbourne photographic survey 2020';this.ready=this.load();}
  private async load(){
    const loader=new GLTFLoader();
    await Promise.all(manifest.assets.map(async asset=>{
      const gltf=await loader.loadAsync(asset.path);gltf.scene.updateMatrixWorld(true);
      let index=0;
      gltf.scene.traverse(node=>{
        if(!(node instanceof T.Mesh))return;
        const source=asset.tiles[index++] as Tile;
        const geometry=node.geometry.clone(),p=geometry.attributes.position,indices=geometry.index;
        const count=indices?.count??p.count,kept:number[]=[],center=new T.Vector3();
        for(let i=0;i<count;i+=3){
          const ids=[0,1,2].map(j=>indices?indices.getX(i+j):i+j);
          center.set(0,0,0);for(const id of ids)center.add(new T.Vector3().fromBufferAttribute(p,id));center.multiplyScalar(1/3).applyMatrix4(node.matrixWorld);
          // The CBD tile edge cuts the Flinders dome. Retain the complete
          // authored landmark and remove only the overlapping photographic part.
          const landmark=project(144.96714,-37.81793),dx=center.x-landmark.x,dz=center.z-landmark.z;
          const lx=Math.cos(.22)*dx-Math.sin(.22)*dz,lz=Math.sin(.22)*dx+Math.cos(.22)*dz;
          if(lx>-303&&lx<20&&Math.abs(lz)<18&&center.y>0)continue;
          // Southern Cross's aerial roof includes folded/occluded underside
          // triangles. The playable hall uses a complete authored wave roof.
          const sx=center.x-crossCenter.x,sz=center.z-crossCenter.z;
          const across=sx*crossTangent.z-sz*crossTangent.x,along=sx*crossTangent.x+sz*crossTangent.z;
          if(across>-95&&across<65&&Math.abs(along)<165&&center.y<45)continue;
          if(stationClearance.features.some(feature=>inside(center.x,center.z,feature.ring)))continue;
          // Aerial water and bank/bridge undersides are coarse, folded surfaces.
          // Use the authored structures along the official hydro boundary.
          if(center.y<18&&((inside(center.x,center.z,river[0])&&!river.slice(1).some(r=>inside(center.x,center.z,r)))||nearBank(center.x,center.z)))continue;
          // Baked vehicles/track on the public mesh are not drivable geometry.
          // Keep roofs and buildings above the train's clearance envelope.
          let blocked=false;
          // Clear the complete viaduct structure down to ground, not just the
          // rolling-stock envelope: low aerial geometry otherwise forms a
          // melted embankment through the authored open steel bridge spans.
          if(center.y<18){for(const rail of railway){if((rail.x-center.x)**2+(rail.z-center.z)**2<38**2&&center.y<rail.y+9.5){blocked=true;break;}}}
          if(!blocked)kept.push(...ids);
        }
        geometry.setIndex(kept);geometry.computeBoundingSphere();node.geometry=geometry;
        for(const material of (Array.isArray(node.material)?node.material:[node.material])){
          material.side=T.FrontSide;material.toneMapped=false;
          if(material instanceof T.MeshBasicMaterial&&material.map)material.map.anisotropy=8;
        }
        node.castShadow=false;node.receiveShadow=false;
        this.tiles.push({source,mesh:node});
      });
      this.group.add(gltf.scene);
    }));this.group.updateMatrixWorld(true);
  }
  replacesBuilding(building:Building){
    if(building.kind&&building.kind!=='Structure')return false;
    const x=building.ring.reduce((sum,p)=>sum+p[0],0)/building.ring.length,z=building.ring.reduce((sum,p)=>sum+p[1],0)/building.ring.length;
    const candidates=this.tiles.filter(({source})=>source.footprintHullXZ&&inside(x,z,source.footprintHullXZ));
    if(!candidates.length)return false;
    // Large towers cross tile edges. Check the union of actual footprints,
    // including edge midpoints, rather than requiring one tile to contain them.
    const covered=(x:number,z:number)=>this.tiles.some(({source})=>source.footprintHullXZ&&inside(x,z,source.footprintHullXZ));
    if(!building.ring.every(([x,z],i)=>{const next=building.ring[(i+1)%building.ring.length];return covered(x,z)&&covered((x+next[0])/2,(z+next[1])/2);}))return false;
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
