import * as T from 'three/webgpu';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {passengerIdle} from './passenger-idle';
import {passengerMotion,walkWeights,footContacts,type PassengerPlacement} from './passenger-motion';
import type {TrainState} from '../game/simulation';

type Batch={variant:number;low:boolean;mesh:T.InstancedMesh;source:T.Matrix4;morph?:T.Mesh;targets?:Record<string,number>};
/** Shared Blender geometry with per-instance idle and distance-driven gait poses. */
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
  private walking=0;
  private boarding=0;
  private walkPhaseSum=0;
  private contactShadows:T.InstancedMesh;
  private hidden=new T.Matrix4().makeScale(0,0,0);
  constructor(placements:PassengerPlacement[]){
    this.group.name='anatomical-commuters';this.placements=placements;
    this.matrices=placements.map(()=>new T.Matrix4());
    this.contactShadows=this.makeContactShadows(placements.length*2);
    this.group.add(this.contactShadows);this.ready=this.load();
  }
  private makeContactShadows(capacity:number){
    const canvas=document.createElement('canvas');canvas.width=128;canvas.height=96;
    const ctx=canvas.getContext('2d')!;
    // Individual sole contacts can follow stance/swing independently.
    {
      ctx.save();ctx.translate(64,48);ctx.scale(.75,1);
      const gradient=ctx.createRadialGradient(0,0,3,0,0,42);
      gradient.addColorStop(0,'rgba(14,19,22,.56)');gradient.addColorStop(.48,'rgba(14,19,22,.28)');gradient.addColorStop(1,'rgba(14,19,22,0)');
      ctx.fillStyle=gradient;ctx.fillRect(-48,-48,96,96);ctx.restore();
    }
    const texture=new T.CanvasTexture(canvas);texture.colorSpace=T.SRGBColorSpace;
    const material=new T.MeshBasicMaterial({map:texture,transparent:true,depthWrite:false,opacity:.68,polygonOffset:true,polygonOffsetFactor:-1,polygonOffsetUnits:-1});
    const geometry=new T.PlaneGeometry(.25,.38);geometry.rotateX(-Math.PI/2);
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
        if(child.geometry.morphAttributes.position?.length){
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
  update(camera:T.Camera,state:TrainState){
    camera.getWorldPosition(this.point);
    const selected:number[][]=Array.from({length:12},()=>[]);this.counts={near:0,far:0};
    const motion=this.placements.map(p=>passengerMotion(p,state));
    const position=new T.Vector3(),rotation=new T.Quaternion(),up=new T.Vector3(0,1,0),scale=new T.Vector3(1,1,1);
    this.walking=0;this.boarding=0;this.walkPhaseSum=0;
    this.placements.forEach((p,i)=>{
      const pose=motion[i];if(!pose.visible)return;
      const d=Math.hypot(pose.position.x-this.point.x,pose.position.y-this.point.y,pose.position.z-this.point.z);
      if(d>150)return;
      this.matrices[i].compose(position.copy(pose.position),rotation.setFromAxisAngle(up,pose.heading),scale);
      if(pose.walkWeight>0){this.walking++;this.walkPhaseSum+=pose.walkPhase;}if(pose.boarding)this.boarding++;
      const low=d>40,variant=((p.variant%6)+6)%6;selected[variant*2+(low?1:0)].push(i);this.counts[low?'far':'near']++;
    });
    const matrix=new T.Matrix4();
    this.simulationTime=state.time;this.idleWeightSum=0;
    const poses=this.placements.map((_,i)=>passengerIdle(state.time,i+1));
    let shadows=0;
    for(const indices of selected)for(const index of indices){
      const p=motion[index];
      if(Math.hypot(p.position.x-this.point.x,p.position.y-this.point.y,p.position.z-this.point.z)>75)continue;
      for(const foot of footContacts(p.walkPhase,p.walkWeight,this.placements[index].variant)){
        if(foot.lift>.035)continue;
        matrix.makeTranslation(foot.x,.008,foot.z);matrix.premultiply(this.matrices[index]);
        this.contactShadows.setMatrixAt(shadows++,matrix);
      }
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
          const movement=motion[p];
          for(const [name,weight] of [['look_left',pose.lookLeft],['look_right',pose.lookRight],['breathe',pose.breathe]] as const)
            if(batch.targets[name]!==undefined)weights[batch.targets[name]]=weight*(1-movement.walkWeight);
          const gait=walkWeights(movement.walkPhase,movement.walkWeight);
          for(const [index,weight] of [[gait.first,gait.firstWeight],[gait.second,gait.secondWeight]])
            if(batch.targets[`walk_${index}`]!==undefined)weights[batch.targets[`walk_${index}`]]=weight;
          batch.mesh.setMorphAt(i,batch.morph);
        }
      });
      if(batch.morph&&indices.length===1)batch.mesh.setMatrixAt(1,this.hidden);
      batch.mesh.instanceMatrix.needsUpdate=true;
      if(batch.mesh.morphTexture)batch.mesh.morphTexture.needsUpdate=true;
    }
  }
  metrics(){return {...this.counts,variants:6,animated:this.counts.near,walking:this.walking,boarding:this.boarding,simulationTime:this.simulationTime,idleWeightSum:Number(this.idleWeightSum.toFixed(6)),walkPhaseSum:Number(this.walkPhaseSum.toFixed(6))};}
}
