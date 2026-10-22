import * as T from 'three/webgpu';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { positionAt, tangentAt } from '../data/route';
import { labelTexture } from './materials';
import { DoorMotion } from './door-motion';
import {CAR_SPACING,CAB_TO_CAR_CENTRE,doorLeafSide} from './train-layout';

/** Blender-authored metre-scale rolling stock. Camera-local cab preserves sightlines. */
export class TrainVisual {
  cars:T.Group[]=[];
  headlamp:T.SpotLight;
  cab=new T.Group();
  readonly ready:Promise<void>;
  private doorNodes:{node:T.Object3D;closed:number;direction:number;side:number}[]=[];
  private doorMotion=new DoorMotion();
  private openSide=1;
  constructor(scene:T.Scene,public camera:T.PerspectiveCamera){
    for(let i=0;i<7;i++){const car=new T.Group();car.name=`commuter-car-${i+1}`;this.cars.push(car);scene.add(car);}
    this.headlamp=new T.SpotLight('#f4eacb',100,160,Math.PI/5,.6,1);this.headlamp.castShadow=false;scene.add(this.headlamp,this.headlamp.target);
    camera.add(this.cab);scene.add(camera);
    this.ready=this.loadAssets();
  }
  private async loadAssets(){
    const loader=new GLTFLoader();
    const [exterior,cab]=await Promise.all([
      loader.loadAsync(`${import.meta.env.BASE_URL}models/melbourne-commuter.glb`),
      loader.loadAsync(`${import.meta.env.BASE_URL}models/driver-cab.glb`),
    ]);
    const displayMaterial=new T.MeshBasicMaterial({map:labelTexture('CITY LOOP','#111d22','#f1bc54',512,64)});
    this.cars.forEach((car,i)=>{
      // All clones share GPU buffers/materials; doors retain independent transforms.
      const body=exterior.scene.clone(true);car.add(body);
      body.traverse(node=>{
        if(node instanceof T.Mesh){node.castShadow=true;node.receiveShadow=true;}
        if((i>0&&i<6)&&node.name.startsWith('nose_'))node.visible=false;
        if(node.name.startsWith('trailer_'))node.visible=i>0&&i<6;
        if(node.name.startsWith('door_')&&node.name.endsWith('_leaf')){
          this.doorNodes.push({node,closed:node.position.z,direction:node.name.includes('_minus_')?-1:1,side:doorLeafSide(node.name,i)});
        }
      });
      const display=new T.Mesh(new T.PlaneGeometry(1.27,.22),displayMaterial);
      display.rotation.set(.65,Math.PI,0);display.position.set(0,3.32,-10.32);display.visible=i===0||i===6;body.add(display);
      // HCMT formation: seven cars, driving cabs only at the two ends.
      if(i===6)body.rotation.y=Math.PI;
    });
    this.cab.add(cab.scene);
    cab.scene.traverse(node=>{if(node instanceof T.Mesh){node.castShadow=false;node.receiveShadow=false;}});
  }
  update(distance:number,cabView:boolean,doors:boolean,seconds:number,complete=false,stationCode='FSS'){
    this.cars.forEach((car,i)=>{
      const s=distance-CAB_TO_CAR_CENTRE-i*CAR_SPACING,p=positionAt(s),t=tangentAt(s);
      if(s<0){p.x+=t.x*s;p.y+=t.y*s;p.z+=t.z*s;}
      car.position.set(p.x,p.y,p.z);car.rotation.y=Math.atan2(-t.x,-t.z);
      car.visible=!(cabView&&i===0);
    });
    const p=positionAt(distance),t=tangentAt(distance);
    this.headlamp.position.set(p.x,p.y+2,p.z);this.headlamp.target.position.set(p.x+t.x*70,p.y+1,p.z+t.z*70);
    this.cab.visible=cabView;
    const amount=this.doorMotion.sample(seconds,distance,doors,complete);
    if(doors)this.openSide=stationCode==='FSS'?1:-1;
    for(const {node,closed,direction,side} of this.doorNodes)node.position.z=closed+direction*(side===this.openSide?amount:0)*.67;
  }
}
