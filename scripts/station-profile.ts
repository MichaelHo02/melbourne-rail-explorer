/** Moving render workload profile. Fixed 20 m/s replay, not a driving test. */
import {Simulation} from '../src/game/simulation';
import {STATIONS} from '../src/data/route';
import {GameRenderer} from '../src/render/renderer';
const output=document.querySelector('#result')!;
const renderer=new GameRenderer(document.querySelector('#viewport')!,message=>{throw Error(message);});
renderer.renderer.setPixelRatio(1);renderer.renderer.setSize(1280,720);
const sim=new Simulation();sim.loadScenario('viaduct');
const approaches=[{station:'Southern Cross',start:1180,end:1440},{station:'Flagstaff',start:2320,end:2580},{station:'Flinders Street',start:5260,end:5520}];
const ranges=['first-use','warm'].flatMap(pass=>approaches.map(approach=>({...approach,pass})));
const report:unknown[]=[];let range=0,frames=0,previous=0;
let samples:{distance:number;ms:number;drawCalls:number;triangles:number}[]=[];
await renderer.loadCity(message=>output.textContent=message,sim.state);
await renderer.startLoop(now=>{
 if(range>=ranges.length)return;
 const target=ranges[range];const distance=Math.min(target.end,target.start+Math.max(0,frames-60)/3);
 const s=sim.state;s.distance=distance;s.speed=20;s.doors=false;s.controller=0;s.time=120+Math.max(0,frames-60)/60;
 s.nextStation=STATIONS.findIndex(stop=>stop.distance>=distance);if(s.nextStation<0)s.nextStation=STATIONS.length-1;
 renderer.render(s,1/60);
 const metrics=renderer.metrics();
 if(frames>60)samples.push({distance,ms:now-previous,drawCalls:metrics.drawCalls,triangles:metrics.triangles});
 previous=now;frames++;
 if(distance>=target.end){
  const sorted=samples.map(s=>s.ms).sort((a,b)=>a-b),quantile=(p:number)=>sorted[Math.ceil(sorted.length*p)-1];
  report.push({pass:target.pass,station:target.station,from:target.start,to:target.end,samples:samples.length,meanMs:sorted.reduce((a,b)=>a+b,0)/sorted.length,medianMs:quantile(.5),p95Ms:quantile(.95),p99Ms:quantile(.99),maxMs:sorted.at(-1),over33ms:samples.filter(s=>s.ms>33.34).length,maxDrawCalls:Math.max(...samples.map(s=>s.drawCalls)),maxTriangles:Math.max(...samples.map(s=>s.triangles)),slowest:[...samples].sort((a,b)=>b.ms-a.ms).slice(0,8)});
  range++;frames=0;previous=0;samples=[];
 }
 output.textContent=JSON.stringify({status:range===ranges.length?'complete':'profiling',resolution:[1280,720],backend:metrics.backend,pass:ranges[range]?.pass,currentStation:ranges[range]?.station,distance,report},null,2);
});
