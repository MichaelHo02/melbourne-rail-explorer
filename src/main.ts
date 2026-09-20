import './ui/styles.css';
import { Simulation, FIXED_STEP } from './game/simulation';
import { TrainAudio } from './game/audio';
import { GameRenderer } from './render/renderer';
import { HUD } from './ui/hud';

const app=document.querySelector<HTMLDivElement>('#app')!;
app.innerHTML='<div id="viewport" role="img" aria-label="Three-dimensional Melbourne train driving scene"></div><div id="ui"></div>';
const sim=new Simulation(),audio=new TrainAudio();const SAVE_KEY='melbourne-rail-explorer:service:v2';
let inspectionScenario=import.meta.env.DEV&&new URLSearchParams(location.search).has('scene');
let saved:unknown=null;try{saved=JSON.parse(localStorage.getItem(SAVE_KEY)||'null');}catch{/* Invalid or unavailable storage does not prevent driving. */}
const validator=new Simulation();const hasSave=validator.restore(saved)&&validator.state.phase!=='complete';
let renderer:GameRenderer|undefined;
function save(){if(inspectionScenario)return;try{if(sim.state.phase!=='ready')localStorage.setItem(SAVE_KEY,JSON.stringify(sim.snapshot()));}catch{/* Private browsing can reject persistence. */}}
function pause(){sim.pause();save();}
function changeView(){if(renderer){renderer.view=renderer.view==='cab'?'chase':'cab';renderer.render(sim.state,0);}}
const hud=new HUD(document.querySelector('#ui')!,{
  start:()=>{inspectionScenario=false;sim.start();hud.closePanel();renderer?.render(sim.state,0);},
  resume:()=>{if(sim.restore(saved)){inspectionScenario=false;sim.pause();renderer?.render(sim.state,0);}else hud.error('This saved service could not be restored. Start a new service instead.');},
  restart:()=>{inspectionScenario=false;sim.reset();audio.announcements.reset();sim.start();hud.closePanel();renderer?.render(sim.state,0);save();},
  pause,view:changeView,sound:()=>{void audio.toggle().then(on=>hud.setSound(on)).catch(()=>hud.error('Audio could not start in this browser. Driving is still available.'));},
  doors:()=>sim.toggleDoors(),controller:n=>sim.setController(n),emergency:()=>sim.emergencyBrake(),
},hasSave);
try{renderer=new GameRenderer(document.querySelector('#viewport')!,message=>{if(sim.state.phase==='driving')sim.pause();save();hud.error(message);});}
catch(error){hud.startupError(`The 3D scene could not start. WebGPU is required. ${error instanceof Error?error.message:''}`);}

window.addEventListener('keydown',e=>{
  const element=e.target as HTMLElement;
  if(element.matches('input,textarea,select')&&e.code!=='Escape'){
    // The physical lever keeps native arrow-key adjustment, but must not swallow
    // driving shortcuts (especially emergency braking) after a pointer drag.
    if(element.id!=='controller'||!['KeyW','KeyS','KeyD','KeyH','KeyC','KeyM','Space'].includes(e.code))return;
  }
  if(['Space','ArrowUp','ArrowDown'].includes(e.code))e.preventDefault();
  if(e.code==='Escape'){hud.closePanel();pause();return;}
  if(e.code==='KeyM'){hud.togglePanel('map');return;}
  if(e.code==='KeyC'){changeView();return;}
  if(e.code==='KeyH'){audio.horn();return;}
  if(sim.state.phase!=='driving')return;
  if(e.code==='KeyW'||e.code==='ArrowUp')sim.setController(sim.state.controller+1);
  if(e.code==='KeyS'||e.code==='ArrowDown')sim.setController(sim.state.controller-1);
  if(e.code==='KeyD'&&!e.repeat)sim.toggleDoors();
  if(e.code==='Space')sim.emergencyBrake();
});
window.addEventListener('blur',()=>{if(sim.state.phase==='driving')pause();});
document.addEventListener('visibilitychange',()=>{if(document.hidden&&sim.state.phase==='driving')pause();});
window.addEventListener('pagehide',save);

let previous=performance.now(),accumulator=0,lastUi=0,lastSave=0,lastDiagnostics=0;
const frameTimes:number[]=[];
function frame(now:number){
  const rawFrameMs=now-previous,elapsed=Math.min(.1,rawFrameMs/1000);previous=now;accumulator+=elapsed;
  while(accumulator>=FIXED_STEP){sim.step(FIXED_STEP);accumulator-=FIXED_STEP;}
  renderer?.render(sim.state,elapsed);audio.update(sim.state,renderer?.view==='cab');
  if(now-lastUi>80){hud.update(sim,renderer?.view??'cab');hud.setAnnouncement(audio.announcements.text);lastUi=now;}
  if(now-lastSave>5000){save();lastSave=now;}
  frameTimes.push(rawFrameMs);if(frameTimes.length>180)frameTimes.shift();
  if(import.meta.env.DEV&&now-lastDiagnostics>1000){
    // DOM-readable diagnostics let the in-app browser verify the actual backend.
    const canvas=document.querySelector('canvas');
    if(canvas)canvas.dataset.renderMetrics=JSON.stringify({...renderer?.metrics(),averageFrameMs:frameTimes.reduce((a,b)=>a+b,0)/frameTimes.length});
    lastDiagnostics=now;
  }
}
if(renderer){
  void renderer.loadCity(message=>hud.loading(message),sim.state).then(async()=>{
    if(import.meta.env.DEV){
      const scene=new URLSearchParams(location.search).get('scene');
      if(scene==='tunnel'||scene==='approach'||scene==='departure'||scene==='platform'||scene==='viaduct'||scene==='flagstaff'||scene==='parliament'||scene==='southern-cross'){sim.loadScenario(scene);renderer?.render(sim.state,0);}
    }
    previous=performance.now();
    await renderer!.startLoop(frame);
    hud.ready();
  }).catch(error=>{
    if(import.meta.env.DEV)console.error(error);
    hud.startupError(`The service could not load: ${error.message} Please reload to try again.`);
  });
}

// Named scenarios and serializable state let browser tests inspect the same game
// the player sees, without turning renderer objects into simulation authority.
if(import.meta.env.DEV){
  Object.assign(window,{__RAIL_EXPLORER__:{
    state:()=>sim.snapshot(),
    metrics:()=>({...renderer?.metrics(),averageFrameMs:frameTimes.reduce((a,b)=>a+b,0)/(frameTimes.length||1)}),
    scenario:(name:'departure'|'tunnel'|'approach'|'platform'|'viaduct'|'flagstaff'|'parliament'|'southern-cross')=>{inspectionScenario=true;sim.loadScenario(name);renderer?.render(sim.state,0);},
    restore:(state:unknown)=>sim.restore(state),
  }});
}
