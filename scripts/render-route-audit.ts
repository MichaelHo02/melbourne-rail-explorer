/** Development harness: open /scripts/render-route-audit.html under Vite.
 * Advances the normal fixed-step simulation 30 ticks per rendered frame.
 * This exercises a complete service, not wall-clock driving performance. */
import {Simulation,FIXED_STEP} from '../src/game/simulation';
import {STATIONS} from '../src/data/route';
import {GameRenderer} from '../src/render/renderer';
const output=document.querySelector('#result')!;
const sim=new Simulation();
const errors:string[]=[];
window.addEventListener('error',event=>errors.push(event.message));
window.addEventListener('unhandledrejection',event=>errors.push(String(event.reason)));
const renderer=new GameRenderer(document.querySelector('#viewport')!,message=>errors.push(message));
let ticks=0,frames=0,previousDistance=sim.state.distance,maxGap=0;
const visited=new Set<number>(),views=new Set<string>();
await renderer.loadCity(message=>output.textContent=message,sim.state);
sim.start();
await renderer.startLoop(()=>{
 if(errors.length||sim.state.phase==='complete'||ticks>=60*60*30)return;
 try{
  for(let batch=0;batch<30&&sim.state.phase!=='complete';batch++,ticks++){
   const s=sim.state,stop=STATIONS[s.nextStation];if(!stop)break;
   if(s.doors){if(s.dwell>=8)sim.toggleDoors();}
   else{
    const remaining=stop.distance-s.distance;
    if(Math.abs(remaining)<7&&s.speed<.05)sim.toggleDoors();
    else if(ticks%12===0){
     const desired=Math.min(12,Math.sqrt(Math.max(0,2*.55*(remaining-3))));
     sim.setController(remaining<6?-4:s.speed>desired+.2?-3:s.speed<desired-.5?3:0);
    }
   }
   sim.step(FIXED_STEP);
  }
  renderer.render(sim.state,.5);frames++;
  maxGap=Math.max(maxGap,sim.state.distance-previousDistance);previousDistance=sim.state.distance;
  visited.add(Math.floor(sim.state.distance/100));views.add(renderer.displayedView);
  const report={phase:sim.state.phase,ticks,frames,simulationSeconds:sim.state.time,distance:sim.state.distance,maxRenderedDistanceGap:maxGap,visited100mCells:visited.size,views:[...views],results:sim.state.results,errors,metrics:renderer.metrics()};
  output.textContent=JSON.stringify(report,null,2);
  if(sim.state.phase==='complete')document.title=errors.length||sim.state.results.length!==STATIONS.length||sim.state.results.some(stop=>stop.outcome!=='served')?'Audit completed with errors':'City Loop audit passed';
 }catch(error){errors.push(String(error));output.textContent=JSON.stringify({errors,ticks,frames});sim.pause();}
});
