import * as T from 'three/webgpu';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {passengerIdle} from './passenger-idle';

export interface PassengerPlacement {position:{x:number;y:number;z:number};heading:number;variant:number}
type Batch={variant:number;low:boolean;mesh:T.InstancedMesh;source:T.Matrix4;morph?:T.Mesh;targets?:Record<string,number>};
/** Planted commuters with local head and rib-cage morphs; no root bob or sliding. */
export class Passengers {
  readonly group=new T.Group();
  readonly ready:Promise<void>;
  private batches:Batch[]=[];
  private placements:PassengerPlacement[];
  private matrices:T.Matrix4[];
  private counts={near:0,far:0};
  private point=new T.Vector3();
  private idleWeightSum=0;
  private simulationTime=0;
  private contactShadows:T.InstancedMesh;
  private hidden=new T.Matrix4().makeScale(0,0,0);
  constructor(placements:PassengerPlacement[]){
    this.group.name='anatomical-commuters';this.placements=placements;
    this.matrices=placements.map(p=>new T.Matrix4().compose(new T.Vector3(p.position.x,p.position.y,p.position.z),new T.Quaternion().setFromAxisAngle(new T.Vector3(0,1,0),p.heading),new T.Vector3(1,1,1)));
    this.contactShadows=this.makeContactShadows(placements.length);
    this.group.add(this.contactShadows);this.ready=this.load();
  }
  private makeContactShadows(capacity:number){
    const canvas=document.createElement('canvas');canvas.width=128;canvas.height=96;
    const ctx=canvas.getContext('2d')!;
    // Two small soft footprints anchor the soles, rather than a floating oval
    // under the whole body. These are authored contact cues, not light shadows.
    for(const x of [41,87]){
      ctx.save();ctx.translate(x,50);ctx.scale(.62,1);
      const gradient=ctx.createRadialGradient(0,0,3,0,0,24);
      gradient.addColorStop(0,'rgba(14,19,22,.56)');gradient.addColorStop(.48,'rgba(14,19,22,.28)');gradient.addColorStop(1,'rgba(14,19,22,0)');
      ctx.fillStyle=gradient;ctx.fillRect(-28,-28,56,56);ctx.restore();
    }
    const texture=new T.CanvasTexture(canvas);texture.colorSpace=T.SRGBColorSpace;
    const material=new T.MeshBasicMaterial({map:texture,transparent:true,depthWrite:false,opacity:.68,polygonOffset:true,polygonOffsetFactor:-1,polygonOffsetUnits:-1});
    const geometry=new T.PlaneGeometry(.62,.43);geometry.rotateX(-Math.PI/2);
    const shadows=new T.InstancedMesh(geometry,material,capacity);shadows.name='commuter-foot-contact';shadows.count=0;shadows.frustumCulled=false;shadows.instanceMatrix.setUsage(T.DynamicDrawUsage);shadows.renderOrder=1;return shadows;
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
        const mesh=new T.InstancedMesh(child.geometry,child.material,Math.max(2,capacity));mesh.name=name+'__instances';mesh.instanceMatrix.setUsage(T.DynamicDrawUsage);mesh.count=0;mesh.castShadow=!low;mesh.receiveShadow=true;mesh.frustumCulled=false;
        let morph:T.Mesh|undefined;
        if(!low&&child.geometry.morphAttributes.position?.length){
          morph=new T.Mesh(child.geometry);morph.morphTargetInfluences!.fill(0);
          mesh.morphTargetInfluences=[...morph.morphTargetInfluences!];
          // Allocate at full capacity before visibility changes. WebGPU's MorphNode
          // chooses its instance-texture path when the first visible draw has >1.
          mesh.count=Math.max(2,capacity);mesh.setMorphAt(0,morph);
          for(let i=0;i<mesh.count;i++)mesh.setMatrixAt(i,this.hidden);
          mesh.visible=false;
        }
        this.group.add(mesh);this.batches.push({variant,low,mesh,source:child.matrixWorld.clone(),morph,targets:child.morphTargetDictionary});
      });
    }
  }
  update(camera:T.Camera,seconds:number){
    camera.getWorldPosition(this.point);
    const selected:number[][]=Array.from({length:12},()=>[]);this.counts={near:0,far:0};
    this.placements.forEach((p,i)=>{
      const d=Math.hypot(p.position.x-this.point.x,p.position.y-this.point.y,p.position.z-this.point.z);
      if(d>150)return;
      const low=d>40,variant=((p.variant%6)+6)%6;selected[variant*2+(low?1:0)].push(i);this.counts[low?'far':'near']++;
    });
    const matrix=new T.Matrix4();
    this.simulationTime=seconds;this.idleWeightSum=0;
    const poses=this.placements.map((_,i)=>passengerIdle(seconds,i+1));
    let shadows=0;
    for(const indices of selected)for(const index of indices){
      const p=this.placements[index];
      if(Math.hypot(p.position.x-this.point.x,p.position.y-this.point.y,p.position.z-this.point.z)>75)continue;
      matrix.copy(this.matrices[index]);matrix.elements[13]+=.008;this.contactShadows.setMatrixAt(shadows++,matrix);
    }
    this.contactShadows.count=shadows;this.contactShadows.instanceMatrix.needsUpdate=true;
    for(let variant=0;variant<6;variant++)for(const i of selected[variant*2]){
      const pose=poses[i];this.idleWeightSum+=pose.lookLeft+pose.lookRight+pose.breathe;
    }
    for(const batch of this.batches){
      const indices=selected[batch.variant*2+(batch.low?1:0)];
      batch.mesh.visible=indices.length>0;
      // Keep a second, clipped instance for a single visible commuter so r180's
      // WebGPU morph shader consistently uses the per-instance weight texture.
      batch.mesh.count=batch.morph?Math.max(2,indices.length):indices.length;
      indices.forEach((p,i)=>{
        batch.mesh.setMatrixAt(i,matrix.multiplyMatrices(this.matrices[p],batch.source));
        if(batch.morph&&batch.targets){
          const pose=poses[p],weights=batch.morph.morphTargetInfluences!;
          weights.fill(0);
          weights[batch.targets.look_left]=pose.lookLeft;
          weights[batch.targets.look_right]=pose.lookRight;
          weights[batch.targets.breathe]=pose.breathe;
          batch.mesh.setMorphAt(i,batch.morph);
        }
      });
      if(batch.morph&&indices.length===1)batch.mesh.setMatrixAt(1,this.hidden);
      batch.mesh.instanceMatrix.needsUpdate=true;
      if(batch.mesh.morphTexture)batch.mesh.morphTexture.needsUpdate=true;
    }
  }
  metrics(){return {...this.counts,variants:6,animated:this.counts.near,simulationTime:this.simulationTime,idleWeightSum:Number(this.idleWeightSum.toFixed(6))};}
}
