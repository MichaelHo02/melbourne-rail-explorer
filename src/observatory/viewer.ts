import * as T from 'three/webgpu';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {HDRLoader} from 'three/addons/loaders/HDRLoader.js';
import {World} from '../render/world';
import {createNativeRenderer} from '../render/native-renderer';
import {Simulation} from '../game/simulation';
import {TimetableTraffic} from '../render/traffic';
import {project} from '../data/route';
import {RoadTraffic,lanePose} from './traffic';
import {freshBay,type ParkingBay} from './data';
import roads from '../data/observatory-roads.json';
export class CityViewer {
  renderer=createNativeRenderer();scene=new T.Scene();camera=new T.PerspectiveCamera(48,1,1,14000);world:World;controls:OrbitControls;
  model=new RoadTraffic();parking=new T.Group();transit=new TimetableTraffic();paused=false;seconds=0;ready=false;
  private state=new Simulation().state;
  private carMesh:T.InstancedMesh;private cabinMesh:T.InstancedMesh;private dummy=new T.Object3D();private bays:ParkingBay[]=[];
  private roads=new T.Group();private freshParking:boolean[]=[];
  private transitEnabled=true;
  constructor(container:HTMLElement){
    this.renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));this.renderer.toneMapping=T.ACESFilmicToneMapping;this.renderer.outputColorSpace=T.SRGBColorSpace;
    this.renderer.shadowMap.enabled=true;this.renderer.shadowMap.type=T.PCFSoftShadowMap;
    container.append(this.renderer.domElement);this.world=new World(this.scene);
    this.controls=new OrbitControls(this.camera,this.renderer.domElement);this.controls.enableDamping=true;this.controls.dampingFactor=.08;this.controls.minDistance=120;this.controls.maxDistance=4500;this.controls.maxPolarAngle=Math.PI*.46;
    this.focus('overview');
    this.carMesh=new T.InstancedMesh(new T.BoxGeometry(1.8,1.1,4.2),new T.MeshStandardMaterial({roughness:.45}),650);
    this.cabinMesh=new T.InstancedMesh(new T.BoxGeometry(1.5,.65,2),new T.MeshStandardMaterial({color:'#263e4b',roughness:.2}),650);
    this.carMesh.instanceMatrix.setUsage(T.DynamicDrawUsage);this.cabinMesh.instanceMatrix.setUsage(T.DynamicDrawUsage);
    this.scene.add(this.carMesh,this.cabinMesh,this.parking,this.transit.group,this.roads);
    const resize=()=>{this.camera.aspect=container.clientWidth/container.clientHeight;this.camera.updateProjectionMatrix();this.renderer.setSize(container.clientWidth,container.clientHeight);};window.addEventListener('resize',resize);resize();
    const material=new T.MeshStandardMaterial({color:'#777a78',roughness:1});
    // Road surfaces follow official centrelines. Widths and ground level are authored.
    const verts:number[]=[];
    for(const feature of roads.features){if(String(feature.properties.vehicular_access)!=='1')continue;
      const lines=feature.geometry.type==='LineString'?[feature.geometry.coordinates]:feature.geometry.coordinates;
      for(const line of lines){if(!Array.isArray(line[0]))continue;const points=(line as number[][]).map(p=>project(p[0],p[1]));
        for(let i=1;i<points.length;i++){const a=points[i-1],b=points[i],dx=b.x-a.x,dz=b.z-a.z,length=Math.hypot(dx,dz);if(!length)continue;const w=Number(feature.properties.class_code)<4?6:3.2,nx=dz/length*w,nz=-dx/length*w;
          const quad=[[a.x+nx,.14,a.z+nz],[a.x-nx,.14,a.z-nz],[b.x-nx,.14,b.z-nz],[b.x+nx,.14,b.z+nz]];for(const j of [0,2,1,0,3,2])verts.push(...quad[j]);}
      }
    }
    const geometry=new T.BufferGeometry();geometry.setAttribute('position',new T.Float32BufferAttribute(verts,3));geometry.computeVertexNormals();material.side=T.DoubleSide;const mesh=new T.Mesh(geometry,material);mesh.receiveShadow=true;this.roads.add(mesh);
    this.renderer.onDeviceLost=()=>{this.paused=true;document.querySelector('#status')!.textContent='Graphics interrupted. Reload to restore the city.';};
  }
  async load(progress:(s:string)=>void){
    await this.renderer.init();this.renderer.domElement.dataset.rendererBackend='WebGPU';
    await Promise.all([this.world.loadCity(progress),this.transit.ready,new HDRLoader().loadAsync('/environment/morning-sky.hdr').then(async texture=>{
      texture.mapping=T.EquirectangularReflectionMapping;
      const generator=new T.PMREMGenerator(this.renderer) as T.PMREMGenerator&{fromEquirectangularAsync:(t:T.Texture)=>Promise<T.RenderTarget>};
      const env=await generator.fromEquirectangularAsync(texture);this.world.exteriorBackground=env.texture;this.scene.environment=env.texture;this.scene.environmentIntensity=.55;generator.dispose();texture.dispose();
    })]);
    this.update(0);await this.renderer.compileAsync(this.scene,this.camera);this.ready=true;this.renderer.domElement.dataset.rendererStatus='ready';
    let previous=performance.now();await this.renderer.setAnimationLoop((now:number)=>{const dt=Math.min(.1,(now-previous)/1000);previous=now;this.update(dt);this.renderer.render(this.scene,this.camera);});
  }
  focus(name:string){
    const views:Record<string,number[]>={overview:[-600,0,-580,1600,1400,1850],flinders:[-130,0,25,480,430,580],southern:[-1330,0,-150,520,530,650],river:[-700,0,220,1000,650,820]};
    const [x,y,z,dx,dy,dz]=views[name]??views.overview;this.controls.target.set(x,y,z);this.camera.position.set(x+dx,y+dy,z+dz);this.controls.update();
  }
  layer(name:string,enabled:boolean){
    if(name==='traffic'){this.carMesh.visible=enabled;this.cabinMesh.visible=enabled;}
    if(name==='parking')this.parking.visible=enabled;
    if(name==='transit'){this.transitEnabled=enabled;this.transit.group.visible=enabled;}
  }
  setParking(bays:ParkingBay[],observed:boolean){
    for(const child of this.parking.children){if(child instanceof T.Mesh){child.geometry.dispose();(child.material as T.Material).dispose();}}this.parking.clear();this.bays=bays;this.freshParking=[];
    const mesh=new T.InstancedMesh(new T.CylinderGeometry(3.5,3.5,.8,8),new T.MeshBasicMaterial({depthTest:false,transparent:true,opacity:.85}),bays.length);mesh.renderOrder=5;
    bays.forEach((bay,i)=>{const p=project(bay.lon,bay.lat);this.dummy.position.set(p.x,1,p.z);this.dummy.rotation.set(0,0,0);this.dummy.updateMatrix();mesh.setMatrixAt(i,this.dummy.matrix);const fresh=observed&&freshBay(bay);this.freshParking[i]=fresh;mesh.setColorAt(i,new T.Color(fresh?(bay.occupied?'#f47b67':'#0daaa3'):'#98a3ad'));});
    mesh.userData.parking=true;mesh.computeBoundingSphere();this.parking.add(mesh);this.model.observations(observed?bays:[]);
  }
  pick(event:PointerEvent){const rect=this.renderer.domElement.getBoundingClientRect(),ray=new T.Raycaster();ray.setFromCamera(new T.Vector2((event.clientX-rect.left)/rect.width*2-1,-(event.clientY-rect.top)/rect.height*2+1),this.camera);const hit=this.parking.visible?ray.intersectObjects(this.parking.children)[0]:undefined;return hit?.instanceId!==undefined?{bay:this.bays[hit.instanceId],fresh:this.freshParking[hit.instanceId]}:null;}
  private update(dt:number){
    if(!document.hidden&&!this.paused){this.seconds+=dt;const now=new Date(),parts=new Intl.DateTimeFormat('en-AU',{timeZone:'Australia/Melbourne',hour:'numeric',hourCycle:'h23',weekday:'short'}).formatToParts(now),hour=Number(parts.find(p=>p.type==='hour')!.value),weekday=!['Sat','Sun'].includes(parts.find(p=>p.type==='weekday')!.value);this.model.step(dt,this.seconds,hour,weekday);}
    this.controls.update();this.state.time=this.seconds;this.world.update(this.state,this.camera);
    // City observation has no player train or underground cab state.
    this.world.stations.children.forEach(st=>st.visible=!st.userData.underground);
    for(const chunk of this.world.cityChunks)chunk.visible=true;
    const fraction=this.model.demand,count=Math.floor(this.model.cars.length*fraction);this.carMesh.count=this.cabinMesh.count=count;
    for(let i=0;i<count;i++){const car=this.model.cars[i],p=lanePose(car.lane,car.s);this.dummy.position.set(p.x,.85,p.z);this.dummy.rotation.set(0,p.angle,0);this.dummy.updateMatrix();this.carMesh.setMatrixAt(i,this.dummy.matrix);this.carMesh.setColorAt(i,new T.Color(['#ddd9cf','#566978','#b3705e','#303f48','#b9c1bc'][car.seed%5]));this.dummy.position.y=1.7;this.dummy.updateMatrix();this.cabinMesh.setMatrixAt(i,this.dummy.matrix);}
    this.carMesh.instanceMatrix.needsUpdate=true;this.cabinMesh.instanceMatrix.needsUpdate=true;if(this.carMesh.instanceColor)this.carMesh.instanceColor.needsUpdate=true;this.carMesh.computeBoundingSphere();this.cabinMesh.computeBoundingSphere();
    this.transit.update(this.seconds,this.camera,false);this.transit.group.visible=this.transitEnabled;
  }
}
