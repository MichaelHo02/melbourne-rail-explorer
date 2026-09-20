import * as T from 'three/webgpu';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';

export interface PassengerPlacement {position:{x:number;y:number;z:number};heading:number;variant:number}
type Batch={variant:number;low:boolean;mesh:T.InstancedMesh;source:T.Matrix4};
/** Static, planted commuter poses. No capsule geometry or flat image cards. */
export class Passengers {
  readonly group=new T.Group();
  readonly ready:Promise<void>;
  private batches:Batch[]=[];
  private placements:PassengerPlacement[];
  private matrices:T.Matrix4[];
  private counts={near:0,far:0};
  private point=new T.Vector3();
  constructor(placements:PassengerPlacement[]){
    this.group.name='anatomical-commuters';this.placements=placements;
    this.matrices=placements.map(p=>new T.Matrix4().compose(new T.Vector3(p.position.x,p.position.y,p.position.z),new T.Quaternion().setFromAxisAngle(new T.Vector3(0,1,0),p.heading),new T.Vector3(1,1,1)));
    this.ready=this.load();
  }
  private async load(){
    const {scene}=await new GLTFLoader().loadAsync(`${import.meta.env.BASE_URL}models/passengers/commuters.glb`);
    scene.updateMatrixWorld(true);
    for(let variant=0;variant<6;variant++)for(const low of [false,true]){
      const name=`commuter_${String(variant+1).padStart(2,'0')}${low?'_low':''}`;
      const root=scene.getObjectByName(name);if(!root)throw new Error(`Passenger asset missing ${name}`);
      const capacity=this.placements.filter(p=>((p.variant%6)+6)%6===variant).length;
      if(!capacity)continue;
      root.traverse(child=>{
        if(!(child instanceof T.Mesh))return;
        const materials=Array.isArray(child.material)?child.material:[child.material];
        for(const material of materials)if(material instanceof T.MeshStandardMaterial){if(material.map)material.map.anisotropy=8;if(material.normalMap)material.normalMap.anisotropy=8;}
        const mesh=new T.InstancedMesh(child.geometry,child.material,capacity);mesh.name=name+'__instances';mesh.instanceMatrix.setUsage(T.DynamicDrawUsage);mesh.count=0;mesh.castShadow=!low;mesh.receiveShadow=true;mesh.frustumCulled=false;
        this.group.add(mesh);this.batches.push({variant,low,mesh,source:child.matrixWorld.clone()});
      });
    }
  }
  update(camera:T.Camera,_seconds:number){
    camera.getWorldPosition(this.point);
    const selected:number[][]=Array.from({length:12},()=>[]);this.counts={near:0,far:0};
    this.placements.forEach((p,i)=>{
      const d=Math.hypot(p.position.x-this.point.x,p.position.y-this.point.y,p.position.z-this.point.z);
      if(d>150)return;
      const low=d>40,variant=((p.variant%6)+6)%6;selected[variant*2+(low?1:0)].push(i);this.counts[low?'far':'near']++;
    });
    const matrix=new T.Matrix4();
    for(const batch of this.batches){
      const indices=selected[batch.variant*2+(batch.low?1:0)];batch.mesh.count=indices.length;
      indices.forEach((p,i)=>batch.mesh.setMatrixAt(i,matrix.multiplyMatrices(this.matrices[p],batch.source)));
      batch.mesh.instanceMatrix.needsUpdate=true;
    }
  }
  metrics(){return {...this.counts,variants:6};}
}
