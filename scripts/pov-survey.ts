/** Development-only fixed-camera screenshots, not a service-driving test. */
import {Simulation} from '../src/game/simulation';
import {STATIONS} from '../src/data/route';
import {GameRenderer} from '../src/render/renderer';
const run=new URLSearchParams(location.search).get('run')??'baseline';
const output=document.querySelector('#result')!;
const ranges=[[STATIONS[0].distance,STATIONS[2].distance],[STATIONS[4].distance,STATIONS[5].distance]];
const distances=[...new Set(ranges.flatMap(([a,b])=>[Math.round(a),...Array.from({length:Math.floor(b/200)-Math.ceil(a/200)+1},(_,i)=>(Math.ceil(a/200)+i)*200),Math.round(b)]))].sort((a,b)=>a-b);
const requested=Number(new URLSearchParams(location.search).get('at'));
if(new URLSearchParams(location.search).has('at')&&Number.isInteger(requested)&&requested>=0&&requested<=STATIONS[5].distance){distances.splice(0,distances.length,requested);}
const sim=new Simulation();sim.loadScenario('viaduct');
const renderer=new GameRenderer(document.querySelector('#viewport')!,message=>{throw Error(message);});
renderer.renderer.setPixelRatio(1);renderer.renderer.setSize(1280,720);
await renderer.loadCity(message=>output.textContent=message,sim.state);
let index=0,frames=0,busy=false,previous=0;const times:number[]=[],saved:string[]=[];
await renderer.startLoop(async now=>{
 if(busy||index>=distances.length)return;
 const s=sim.state;s.distance=distances[index];s.speed=0;s.doors=false;s.controller=-4;s.time=120;
 s.nextStation=STATIONS.findIndex(stop=>stop.distance>=s.distance);if(s.nextStation<0)s.nextStation=STATIONS.length-1;
 renderer.render(s,0);
 if(previous&&frames>15)times.push(now-previous);previous=now;
 if(++frames<60)return;
 busy=true;
 try{
  const metrics=renderer.metrics(); // Read before toBlob yields to another animation frame.
  const sorted=[...times].sort((a,b)=>a-b);
  const frameTiming={mean:times.reduce((a,b)=>a+b,0)/times.length,p95:sorted[Math.ceil(sorted.length*.95)-1],p99:sorted[Math.ceil(sorted.length*.99)-1],max:sorted.at(-1),samples:times.length};
  const canvas=document.querySelector('canvas')!;
  const blob=await new Promise<Blob>((resolve,reject)=>canvas.toBlob(b=>b?resolve(b):reject(Error('Empty canvas capture')),'image/png'));
  const bytes=new Uint8Array(await blob.arrayBuffer());let raw='';for(const byte of bytes)raw+=String.fromCharCode(byte);
  const response=await fetch('/__pov_capture',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({run,distance:distances[index],png:btoa(raw),camera:{position:renderer.camera.position.toArray(),quaternion:renderer.camera.quaternion.toArray(),fov:renderer.camera.fov},metrics,frameTiming,probes:[[-.65,.7],[-.4,.7],[-.1,.7],[-.6,.4],[-.4,.4],[0,.3],[.5,.5]].map(([x,y])=>({x,y,hits:renderer.inspectSurface(x,y)})),frameMs:times.reduce((a,b)=>a+b,0)/times.length})});
  if(!response.ok)throw Error(await response.text());saved.push((await response.json()).saved);
  index++;frames=0;previous=0;times.length=0;
  output.textContent=JSON.stringify({run,completed:index,total:distances.length,status:index===distances.length?'complete':'capturing',saved},null,2);busy=false;
 }catch(error){output.textContent=JSON.stringify({run,error:String(error),completed:index,saved});}
});
