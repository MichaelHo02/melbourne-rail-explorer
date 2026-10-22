import * as T from 'three/webgpu';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { sampleTraffic, sampleTrafficTrip, type TrafficSample } from '../game/traffic';
import { positionAt, tangentAt, type Vec3 } from '../data/route';

const guide=Array.from({length:171},(_,i)=>({s:i*10,p:positionAt(i*10)}));
/** Source shapes drive progress. Render them on the authored adjacent tracks:
 * GTFS does not supply individual track geometry or rolling-stock assignments. */
function railPosition(point:Vec3,heading:Vec3){
  let closest=guide[0],error=Infinity;
  for(const sample of guide){const d=(sample.p.x-point.x)**2+(sample.p.z-point.z)**2;if(d<error){closest=sample;error=d;}}
  if(error>85*85||closest.s>1650)return null;
  const local=tangentAt(closest.s),along=(point.x-closest.p.x)*local.x+(point.z-closest.p.z)*local.z;
  const s=T.MathUtils.clamp(closest.s+along,0,1650),p=positionAt(s),t=tangentAt(s);
  const direction=heading.x*t.x+heading.z*t.z>=0?1:-1;
  const lane=direction===1?4.2:8.4;
  const start=direction===1?12:17,end=direction===1?14:28;
  const offset=s<162?T.MathUtils.lerp(start,lane,T.MathUtils.smoothstep(s,95,162)):s>1154?T.MathUtils.lerp(lane,end,T.MathUtils.smoothstep(s,1154,1360)):lane;
  return {s,direction,p:new T.Vector3(p.x-t.z*offset,p.y,p.z+t.x*offset),angle:Math.atan2(-t.x*direction,-t.z*direction)};
}

/** A visual subset, not a change to the official timetable: the two authored
 * adjacent lanes cannot display every simultaneous source platform movement. */
export function selectAdjacentTraffic(trains:TrafficSample[],camera:Vec3,limit=8):TrafficSample[]{
  const candidates=trains.flatMap(train=>{
    const distance=(train.position.x-camera.x)**2+(train.position.z-camera.z)**2;
    const placed=distance<1150**2?railPosition(train.position,train.heading):null;
    if(!placed)return [];
    // Seven cars occupy about 160m. Include a small buffer for curve projection
    // and the front/rear overhang instead of allowing source trains to overlap.
    const rear=placed.s-placed.direction*170;
    return [{train,distance,lane:placed.direction,start:Math.min(rear,placed.s)-10,end:Math.max(rear,placed.s)+10}];
  }).sort((a,b)=>a.distance-b.distance||a.train.id.localeCompare(b.train.id));
  const selected:typeof candidates=[];
  for(const candidate of candidates){
    if(selected.some(other=>other.lane===candidate.lane&&candidate.start<other.end&&candidate.end>other.start))continue;
    selected.push(candidate);if(selected.length>=limit)break;
  }
  return selected.map(candidate=>candidate.train);
}

export class TimetableTraffic {
  group=new T.Group();ready:Promise<void>;visibleTrains=0;
  private batches:{mesh:T.InstancedMesh;kind:'cab'|'trailer'}[]=[];
  constructor(){this.group.name='Official timetable traffic';this.ready=this.load();}
  private async load(){
    const asset=await new GLTFLoader().loadAsync('/models/traffic-commuter.glb');asset.scene.updateMatrixWorld(true);
    for(const kind of ['cab','trailer'] as const){
      const materials=new Map<T.Material,T.BufferGeometry[]>();
      asset.scene.traverse(node=>{
        if(!(node instanceof T.Mesh)||Array.isArray(node.material))return;
        if(kind==='trailer'&&node.name.startsWith('nose_')||kind==='cab'&&node.name.startsWith('trailer_'))return;
        const geometry=node.geometry.clone().applyMatrix4(node.matrixWorld);
        const list=materials.get(node.material)??[];list.push(geometry);materials.set(node.material,list);
      });
      for(const [material,geometries] of materials){
        const merged=mergeGeometries(geometries);if(!merged)throw new Error('Traffic train geometry could not be prepared.');
        geometries.forEach(g=>g.dispose());const mesh=new T.InstancedMesh(merged,material,kind==='cab'?16:40);
        mesh.instanceMatrix.setUsage(T.DynamicDrawUsage);mesh.count=0;mesh.castShadow=true;mesh.receiveShadow=true;mesh.frustumCulled=true;
        this.batches.push({mesh,kind});this.group.add(mesh);
      }
    }
  }
  update(seconds:number,camera:T.Camera,underground:boolean){
    this.group.visible=!underground;this.visibleTrains=0;if(underground)return;
    const matrices:{cab:T.Matrix4[];trailer:T.Matrix4[]}={cab:[],trailer:[]};
    const trains=selectAdjacentTraffic(sampleTraffic(seconds),camera.position);
    for(const train of trains){
      let visible=false;
      for(let car=0;car<7;car++){
        const sample=sampleTrafficTrip(train.id,seconds,11.2+car*22.85);if(!sample)continue;
        const placed=railPosition(sample.position,sample.heading);if(!placed)continue;
        const kind=car===0||car===6?'cab':'trailer';
        const rotation=new T.Quaternion().setFromAxisAngle(new T.Vector3(0,1,0),placed.angle+(car===6?Math.PI:0));
        matrices[kind].push(new T.Matrix4().compose(placed.p,rotation,new T.Vector3(1,1,1)));visible=true;
      }
      if(visible)this.visibleTrains++;
    }
    for(const {mesh,kind} of this.batches){mesh.count=matrices[kind].length;matrices[kind].forEach((m,i)=>mesh.setMatrixAt(i,m));mesh.instanceMatrix.needsUpdate=true;if(mesh.count)mesh.computeBoundingSphere();}
  }
}
