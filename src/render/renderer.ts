import * as T from 'three/webgpu';
import { HDRLoader } from 'three/addons/loaders/HDRLoader.js';
import { World } from './world';
import { TrainVisual } from './train';
import { TimetableTraffic } from './traffic';
import { createNativeRenderer } from './native-renderer';
import { positionAt, tangentAt, project, isUnderground, STATIONS } from '../data/route';
import type { TrainState } from '../game/simulation';

export type View='cab'|'chase';
export class GameRenderer {
  renderer:ReturnType<typeof createNativeRenderer>;scene=new T.Scene();camera=new T.PerspectiveCamera(60,1,.08,12000);
  world:World;train:TrainVisual;view:View='cab';look=0;ready=false;
  private lastCamera=new T.Vector3();private target=new T.Vector3();private contextLost=false;
  private backend='initializing';
  private traffic=new TimetableTraffic();
  private inspectionView=import.meta.env.DEV?new URLSearchParams(location.search).get('view'):null;
  constructor(container:HTMLElement,onFailure:(message:string)=>void){
    this.renderer=createNativeRenderer();
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio,1.65));this.renderer.outputColorSpace=T.SRGBColorSpace;
    this.renderer.toneMapping=T.ACESFilmicToneMapping;this.renderer.toneMappingExposure=1.0;
    this.renderer.shadowMap.enabled=true;this.renderer.shadowMap.type=T.PCFSoftShadowMap;
    container.appendChild(this.renderer.domElement);
    const handleDeviceLost=this.renderer.onDeviceLost.bind(this.renderer);
    this.renderer.onDeviceLost=info=>{
      handleDeviceLost(info);this.contextLost=true;
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
  async startLoop(frame:(now:number)=>void){await this.renderer.setAnimationLoop(frame);}
  render(state:TrainState,dt:number){
    if(this.contextLost||!this.ready)return;
    this.updateScene(state,dt);
    this.renderer.render(this.scene,this.camera);
  }
  private updateScene(state:TrainState,dt:number){
    const p=positionAt(state.distance),t=tangentAt(state.distance),side=new T.Vector3(-t.z,0,t.x);
    const menu=state.phase==='ready',cab=this.view==='cab'&&!menu;
    if(this.inspectionView==='viaduct'){
      const anchor=positionAt(640),t=tangentAt(640),side=new T.Vector3(-t.z,0,t.x);
      this.camera.position.set(anchor.x-side.x*85-t.x*45,19,anchor.z-side.z*85-t.z*45);
      this.target.set(anchor.x+t.x*45,6,anchor.z+t.z*45);
    }
    else if(this.inspectionView==='river'){
      const river=project(144.9667,-37.81965);
      this.camera.position.set(river.x+45,18,river.z+45);this.target.set(river.x-35,-.6,river.z-55);
    }
    else if(this.inspectionView==='platform'){
      const station=STATIONS[state.nextStation]??STATIONS[0],distance=station.distance-65,anchor=positionAt(distance),forward=tangentAt(Math.max(0,distance)),normal=new T.Vector3(-forward.z,0,forward.x),offset=station.code==='FSS'?5.4:-5.4;
      if(distance<0){anchor.x+=forward.x*distance;anchor.y+=forward.y*distance;anchor.z+=forward.z*distance;}
      this.camera.position.set(anchor.x+normal.x*offset,anchor.y+2.65,anchor.z+normal.z*offset);
      this.target.set(anchor.x+forward.x*40+normal.x*offset,anchor.y+2.5,anchor.z+forward.z*40+normal.z*offset);
    }
    else if(menu){this.camera.position.set(p.x+110,p.y+55,p.z+110);this.target.set(p.x-75,p.y+10,p.z-50);}
    else if(cab){
      this.camera.position.set(p.x,p.y+2.85,p.z);
      this.target.set(p.x+t.x*55+side.x*this.look*24,p.y+2.72+t.y*55,p.z+t.z*55+side.z*this.look*24);
    }else{
      this.lastCamera.set(p.x-t.x*45-side.x*18,p.y+12,p.z-t.z*45-side.z*18);
      if(dt===0)this.camera.position.copy(this.lastCamera);else this.camera.position.lerp(this.lastCamera,1-Math.exp(-dt*5));
      this.target.set(p.x+t.x*25,p.y+1,p.z+t.z*25);
    }
    this.camera.lookAt(this.target);this.train.update(state.distance,cab&&!this.inspectionView,state.doors);this.world.update(state.distance,this.camera,state.time);
    this.traffic.update(state.time,this.camera,isUnderground(state.distance));
  }
  metrics(){const i=this.renderer.info;return {drawCalls:i.render.drawCalls,triangles:i.render.triangles,geometries:i.memory.geometries,textures:i.memory.textures,cityReady:this.ready,buildingSections:this.world.buildingCount,trafficTrains:this.traffic.visibleTrains,backend:this.backend};}
}
