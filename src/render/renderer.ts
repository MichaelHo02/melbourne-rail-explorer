import * as T from 'three';
import { HDRLoader } from 'three/addons/loaders/HDRLoader.js';
import { World } from './world';
import { TrainVisual } from './train';
import { positionAt, tangentAt } from '../data/route';
import type { TrainState } from '../game/simulation';

export type View='cab'|'chase';
export class GameRenderer {
  renderer:T.WebGLRenderer;scene=new T.Scene();camera=new T.PerspectiveCamera(60,1,.08,12000);
  world:World;train:TrainVisual;view:View='cab';look=0;ready=false;
  private lastCamera=new T.Vector3();private target=new T.Vector3();private contextLost=false;
  constructor(container:HTMLElement,onFailure:(message:string)=>void){
    this.renderer=new T.WebGLRenderer({antialias:true,powerPreference:'high-performance'});
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio,1.65));this.renderer.outputColorSpace=T.SRGBColorSpace;
    this.renderer.toneMapping=T.ACESFilmicToneMapping;this.renderer.toneMappingExposure=1.0;
    this.renderer.shadowMap.enabled=true;this.renderer.shadowMap.type=T.PCFSoftShadowMap;
    container.appendChild(this.renderer.domElement);
    this.renderer.domElement.addEventListener('webglcontextlost',e=>{e.preventDefault();this.contextLost=true;onFailure('Graphics were interrupted. Reload to restore the scene; your driving progress has been saved.');});
    this.world=new World(this.scene);this.train=new TrainVisual(this.scene,this.camera);
    const resize=()=>{this.camera.aspect=container.clientWidth/container.clientHeight;this.camera.updateProjectionMatrix();this.renderer.setSize(container.clientWidth,container.clientHeight);};
    window.addEventListener('resize',resize);resize();
  }
  async loadCity(onProgress:(s:string)=>void){
    await Promise.all([
      this.world.loadCity(onProgress),
      this.train.ready,
      new HDRLoader().loadAsync('/environment/morning-sky.hdr').then(texture=>{
        texture.mapping=T.EquirectangularReflectionMapping;
        this.world.exteriorBackground=texture;this.scene.environment=texture;
        this.scene.backgroundBlurriness=.015;this.scene.backgroundIntensity=.7;
        this.scene.environmentIntensity=.45;
      }),
    ]);
    this.ready=true;
  }
  setQuality(high:boolean){this.renderer.setPixelRatio(high?Math.min(devicePixelRatio,1.65):1);this.renderer.shadowMap.enabled=high;}
  render(state:TrainState,dt:number){
    if(this.contextLost)return;
    const p=positionAt(state.distance),t=tangentAt(state.distance),side=new T.Vector3(-t.z,0,t.x);
    const menu=state.phase==='ready',cab=this.view==='cab'&&!menu;
    if(menu){this.camera.position.set(p.x+110,p.y+55,p.z+110);this.target.set(p.x-75,p.y+10,p.z-50);}
    else if(cab){
      this.camera.position.set(p.x,p.y+2.85,p.z);
      this.target.set(p.x+t.x*55+side.x*this.look*24,p.y+2.72+t.y*55,p.z+t.z*55+side.z*this.look*24);
    }else{
      this.lastCamera.set(p.x-t.x*45-side.x*18,p.y+12,p.z-t.z*45-side.z*18);
      if(dt===0)this.camera.position.copy(this.lastCamera);else this.camera.position.lerp(this.lastCamera,1-Math.exp(-dt*5));
      this.target.set(p.x+t.x*25,p.y+1,p.z+t.z*25);
    }
    this.camera.lookAt(this.target);this.train.update(state.distance,cab,state.doors);this.world.update(state.distance,this.camera);
    this.renderer.render(this.scene,this.camera);
  }
  metrics(){const i=this.renderer.info;return {drawCalls:i.render.calls,triangles:i.render.triangles,geometries:i.memory.geometries,textures:i.memory.textures,cityReady:this.ready,buildingSections:this.world.buildingCount,backend:'WebGL2'};}
}
