import * as T from 'three/webgpu';
import { HDRLoader } from 'three/addons/loaders/HDRLoader.js';
import { World } from './world';
import { TrainVisual } from './train';
import { TimetableTraffic } from './traffic';
import { createNativeRenderer } from './native-renderer';
import { positionAt, tangentAt, project, isUnderground, STATIONS } from '../data/route';
import type { TrainState } from '../game/simulation';
import {platformPosition} from './passenger-motion';
import {CameraLook,cameraConfined,drivingCameraPose,inspectionLookTarget,type CameraView} from './camera-look';
import {CameraDragInput} from './camera-input';

export type View=CameraView;
export class GameRenderer {
  renderer:ReturnType<typeof createNativeRenderer>;scene=new T.Scene();camera=new T.PerspectiveCamera(60,1,.08,12000);
  world:World;train:TrainVisual;view:View='cab';ready=false;
  private target=new T.Vector3();private contextLost=false;
  private lookState=new CameraLook();private inspectionLook={yaw:0,pitch:0};private cameraInput:CameraDragInput;private cameraInputRequested=false;
  private inputPhase:TrainState['phase']='ready';private confined=false;
  private cabHeading=new T.Matrix4();private cabRotation=new T.Quaternion();private cabTarget=new T.Vector3();private up=new T.Vector3(0,1,0);
  private backend='initializing';
  private traffic=new TimetableTraffic();
  private inspectionView=import.meta.env.DEV?new URLSearchParams(location.search).get('view'):null;
  constructor(container:HTMLElement,onFailure:(message:string)=>void){
    this.renderer=createNativeRenderer();
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio,1.65));this.renderer.outputColorSpace=T.SRGBColorSpace;
    this.renderer.toneMapping=T.ACESFilmicToneMapping;this.renderer.toneMappingExposure=1.0;
    this.renderer.shadowMap.enabled=true;this.renderer.shadowMap.type=T.PCFSoftShadowMap;
    container.appendChild(this.renderer.domElement);
    this.cameraInput=new CameraDragInput(this.renderer.domElement,(x,y)=>this.dragLook(x,y),()=>this.resetLook());
    const handleDeviceLost=this.renderer.onDeviceLost.bind(this.renderer);
    this.renderer.onDeviceLost=info=>{
      handleDeviceLost(info);this.contextLost=true;this.cameraInput.setEnabled(false);
      this.renderer.domElement.dataset.rendererStatus='lost';
      onFailure('Graphics were interrupted. Reload to restore the scene; your driving progress has been saved.');
    };
    this.world=new World(this.scene);this.train=new TrainVisual(this.scene,this.camera);this.scene.add(this.traffic.group);
    const resize=()=>{this.camera.aspect=container.clientWidth/container.clientHeight;this.camera.updateProjectionMatrix();this.renderer.setSize(container.clientWidth,container.clientHeight);};
    window.addEventListener('resize',resize);resize();
  }
  async loadCity(onProgress:(s:string)=>void,initialState:TrainState){
    onProgress('Starting graphics…');
    try{await this.renderer.init();}
    catch(error){this.renderer.domElement.dataset.rendererStatus='failed';throw new Error(`WebGPU could not start. Check that your browser and GPU support WebGPU and hardware acceleration is enabled. ${error instanceof Error?error.message:''}`);}
    this.backend='WebGPU';
    this.renderer.domElement.dataset.rendererBackend=this.backend;
    await Promise.all([
      this.world.loadCity(onProgress),
      this.train.ready,
      this.traffic.ready,
      new HDRLoader().loadAsync('/environment/morning-sky.hdr').then(async texture=>{
        texture.mapping=T.EquirectangularReflectionMapping;
        // Generate reflections before compileAsync: nested PMREM renders during
        // compilation in Three r180 can cache an empty environment texture.
        // @types/three r180 omits this method exposed by the WebGPU generator.
        const pmrem=new T.PMREMGenerator(this.renderer) as T.PMREMGenerator & {
          fromEquirectangularAsync(texture:T.Texture):Promise<T.RenderTarget>;
        };
        const environment=await pmrem.fromEquirectangularAsync(texture);
        this.world.exteriorBackground=environment.texture;this.scene.environment=environment.texture;
        pmrem.dispose();texture.dispose();
        this.scene.backgroundBlurriness=.015;this.scene.backgroundIntensity=.7;
        this.scene.environmentIntensity=.45;
      }),
    ]);
    onProgress('Preparing lighting and materials…');
    // Compile both entry views before accepting input, including the cab GLB.
    this.updateScene({...initialState,phase:'driving'},0);
    await this.renderer.compileAsync(this.scene,this.camera);
    this.updateScene(initialState,0);
    await this.renderer.compileAsync(this.scene,this.camera);
    this.ready=true;
    this.renderer.domElement.dataset.rendererStatus='ready';
  }
  /** Explicit view choices leave development inspection fixtures. */
  get displayedView():View|'inspection'{return this.inspectionView?'inspection':this.view;}
  setView(view:View){this.view=view;this.inspectionView=null;this.cameraInput.cancel();this.refreshCameraInput();}
  resetLook(){if(this.inspectionView)this.inspectionLook={yaw:0,pitch:0};else this.lookState.reset(this.view);this.cameraInput.cancel();this.refreshCameraInput();}
  private dragLook(x:number,y:number){
    if(this.inspectionView){const yaw=this.inspectionLook.yaw+x*Math.PI;this.inspectionLook.yaw=Math.atan2(Math.sin(yaw),Math.cos(yaw));this.inspectionLook.pitch=Math.max(-.8,Math.min(.8,this.inspectionLook.pitch-y*Math.PI*.65));}
    else this.lookState.drag(this.view,x,y,this.confined);
  }
  setCameraInputEnabled(enabled:boolean){this.cameraInputRequested=enabled;this.refreshCameraInput();}
  private refreshCameraInput(){this.cameraInput.setEnabled(this.cameraInputRequested&&this.ready&&!this.contextLost&&this.inputPhase==='driving');}
  async startLoop(frame:(now:number)=>void){await this.renderer.setAnimationLoop(frame);}
  render(state:TrainState,dt:number){
    if(this.contextLost||!this.ready)return;
    this.updateScene(state,dt);
    this.renderer.render(this.scene,this.camera);
  }
  private updateScene(state:TrainState,_dt:number){
    const p=positionAt(state.distance),t=tangentAt(state.distance);
    const menu=state.phase==='ready',cab=this.view==='cab'&&!menu;
    this.inputPhase=state.phase;this.confined=cameraConfined(state.distance);this.lookState.constrain(this.view,this.confined);this.refreshCameraInput();
    if(this.inspectionView==='viaduct'){
      const anchor=positionAt(640),t=tangentAt(640),side=new T.Vector3(-t.z,0,t.x);
      this.camera.position.set(anchor.x-side.x*85-t.x*45,19,anchor.z-side.z*85-t.z*45);
      this.target.set(anchor.x+t.x*45,6,anchor.z+t.z*45);
    }
    else if(this.inspectionView==='northbank'){
      this.camera.position.set(-890,6,490);this.target.set(-930,-.8,418);
    }
    else if(this.inspectionView==='river'){
      const river=project(144.9667,-37.81965);
      this.camera.position.set(river.x+45,18,river.z+45);this.target.set(river.x-35,-.6,river.z-55);
    }
    else if(this.inspectionView==='concourse'){
      const index=Math.min(state.nextStation,STATIONS.length-1),p=platformPosition(index,85,4.6),target=platformPosition(index,57,6.8);
      this.camera.position.set(p.x,p.y+1.8,p.z);this.target.set(target.x,target.y+4.2,target.z);
    }
    else if(this.inspectionView==='boarding'){
      const index=Math.min(state.nextStation,STATIONS.length-1),p=platformPosition(index,16,5.9),target=platformPosition(index,31,1.4);
      this.camera.position.set(p.x,p.y+1.8,p.z);this.target.set(target.x,target.y+.8,target.z);
    }
    else if(this.inspectionView==='entrance'){
      const station=STATIONS[state.nextStation]??STATIONS[0];
      const at=(along:number,x:number,y:number)=>{const p=positionAt(station.distance-65+along),t=tangentAt(station.distance-65+along);return new T.Vector3(p.x+t.z*x,p.y+y,p.z-t.x*x);};
      this.camera.position.copy(at(-62,4.8,2.65));this.target.copy(at(-50,10,2.5));
    }
    else if(this.inspectionView==='platform'){
      const station=STATIONS[state.nextStation]??STATIONS[0],distance=station.distance-65,anchor=positionAt(distance),forward=tangentAt(Math.max(0,distance)),normal=new T.Vector3(-forward.z,0,forward.x),offset=station.code==='FSS'?5.4:-5.4;
      if(distance<0){anchor.x+=forward.x*distance;anchor.y+=forward.y*distance;anchor.z+=forward.z*distance;}
      this.camera.position.set(anchor.x+normal.x*offset,anchor.y+2.65,anchor.z+normal.z*offset);
      this.target.set(anchor.x+forward.x*40+normal.x*offset,anchor.y+2.5,anchor.z+forward.z*40+normal.z*offset);
    }
    else if(menu){this.camera.position.set(p.x+110,p.y+55,p.z+110);this.target.set(p.x-75,p.y+10,p.z-50);}
    else{
      const pose=drivingCameraPose(state.distance,this.view,this.lookState.angles(this.view));
      this.camera.position.copy(pose.position);this.target.copy(pose.target);
    }
    if(this.inspectionView)this.target.copy(inspectionLookTarget(this.camera.position,this.target,this.inspectionLook));
    this.camera.lookAt(this.target);
    // The cab is parented to the camera for its seated origin, but its structure
    // must stay aligned with the train when the driver turns their head.
    this.cabTarget.set(p.x+t.x*35,p.y+2.85+t.y*35,p.z+t.z*35);
    this.cabHeading.lookAt(this.camera.position,this.cabTarget,this.up);
    this.train.cab.quaternion.copy(this.camera.quaternion).invert().multiply(this.cabRotation.setFromRotationMatrix(this.cabHeading));
    const angles=this.inspectionView?this.inspectionLook:this.lookState.angles(this.view);
    this.renderer.domElement.dataset.cameraLook=JSON.stringify({view:this.view,yaw:Number(angles.yaw.toFixed(3)),pitch:Number(angles.pitch.toFixed(3)),confined:this.confined,dragging:this.cameraInput.dragging,inspection:this.inspectionView});
    this.train.update(state.distance,cab&&!this.inspectionView,state.doors,state.time,state.phase==='complete',STATIONS[state.nextStation]?.code);this.world.update(state,this.camera);
    this.traffic.update(state.time,this.camera,isUnderground(state.distance));
  }
  metrics(){const i=this.renderer.info;return {drawCalls:i.render.drawCalls,triangles:i.render.triangles,geometries:i.memory.geometries,textures:i.memory.textures,cityReady:this.ready,buildingSections:this.world.buildingCount,passengers:this.world.passengerMetrics(),trafficTrains:this.traffic.visibleTrains,backend:this.backend};}
}
