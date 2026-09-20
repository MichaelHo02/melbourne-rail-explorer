import { describe,it,expect } from 'vitest';
import { Simulation, FIXED_STEP } from '../src/game/simulation';
import routeSource from '../src/data/route-source.json';
import { STATIONS, ROUTE_LENGTH, positionAt, tangentAt, project } from '../src/data/route';
const advance=(sim:Simulation,seconds:number)=>{for(let i=0;i<Math.round(seconds/FIXED_STEP);i++)sim.step(FIXED_STEP);};

describe('platform extension beyond route endpoints',()=>{
  it('preserves the endpoint bearing and carriage spacing behind Flinders Street',()=>{
    const bearing=tangentAt(-100),endpoint=tangentAt(0);
    expect(bearing).toEqual(endpoint);
    expect(Math.hypot(bearing.x,bearing.y,bearing.z)).toBeCloseTo(1,8);
    expect(tangentAt(ROUTE_LENGTH+100)).toEqual(tangentAt(ROUTE_LENGTH));
    const car=(distance:number)=>{const p=positionAt(distance),t=tangentAt(distance);return{x:p.x+t.x*distance,y:p.y+t.y*distance,z:p.z+t.z*distance};};
    const a=car(-50),b=car(-72.85);
    expect(Math.hypot(a.x-b.x,a.y-b.y,a.z-b.z)).toBeCloseTo(22.85,6);
  });
});

describe('driver controls',()=>{
  it('interlocks traction while doors are open, then accelerates after closing',()=>{
    const sim=new Simulation();sim.start();sim.setController(4);advance(sim,3);expect(sim.state.speed).toBe(0);
    expect(sim.toggleDoors()).toBe(true);advance(sim,5);expect(sim.state.speed).toBeGreaterThan(1);expect(sim.state.nextStation).toBe(1);
  });
  it('rejects opening doors while moving or outside a platform stop zone',()=>{
    const sim=new Simulation();sim.loadScenario('approach');expect(sim.toggleDoors()).toBe(false);
    sim.state.speed=0;expect(sim.toggleDoors()).toBe(false);expect(sim.state.doors).toBe(false);
  });
  it('requires full boarding time and records stop accuracy before advancing',()=>{
    const sim=new Simulation();sim.loadScenario('approach');sim.state.distance=STATIONS[1].distance-3;sim.state.speed=0;
    expect(sim.toggleDoors()).toBe(true);expect(sim.toggleDoors()).toBe(false);advance(sim,8.1);
    expect(sim.toggleDoors()).toBe(true);expect(sim.state.nextStation).toBe(2);expect(sim.state.results[0].error).toBe(-3);
  });
  it('brakes to a standstill without reversing and locks an emergency brake until stopped',()=>{
    const sim=new Simulation();sim.loadScenario('approach');sim.emergencyBrake();sim.setController(4);expect(sim.state.controller).toBe(-4);
    advance(sim,12);expect(sim.state.speed).toBe(0);const distance=sim.state.distance;advance(sim,3);expect(sim.state.distance).toBe(distance);
    sim.setController(0);expect(sim.state.emergency).toBe(false);
  });
  it('freezes simulation during pause and restores a valid save paused',()=>{
    const sim=new Simulation();sim.loadScenario('tunnel');sim.pause();const before=sim.snapshot();advance(sim,10);expect(sim.snapshot()).toEqual(before);
    const other=new Simulation();expect(other.restore(before)).toBe(true);expect(other.state.phase).toBe('paused');expect(other.state.distance).toBe(before.distance);
    expect(other.restore({...before,speed:NaN})).toBe(false);expect(other.restore({...before,distance:ROUTE_LENGTH+10})).toBe(false);
    expect(other.restore({...before,doors:true,speed:5})).toBe(false);
  });
  it('records an overrun once and terminates at route end',()=>{
    const sim=new Simulation();sim.loadScenario('approach');sim.state.distance=STATIONS[1].distance+25;sim.step(FIXED_STEP);
    expect(sim.state.results).toHaveLength(1);expect(sim.state.results[0].outcome).toBe('missed');expect(sim.state.nextStation).toBe(2);
    sim.state.distance=ROUTE_LENGTH;sim.state.nextStation=5;sim.step(FIXED_STEP);expect(sim.state.phase).toBe('complete');expect(sim.state.speed).toBe(0);
  });
  it('settles the train immediately when doors open at walking-stop tolerance',()=>{
    const sim=new Simulation();sim.loadScenario('platform');sim.state.speed=.04;
    expect(sim.toggleDoors()).toBe(true);expect(sim.state.speed).toBe(0);
    const restored=new Simulation();expect(restored.restore(sim.snapshot())).toBe(true);
    const distance=sim.state.distance;advance(sim,3);expect(sim.state.distance).toBe(distance);
  });
  it('ignores invalid timing and controller inputs without corrupting the service',()=>{
    const sim=new Simulation();sim.loadScenario('tunnel');const before=sim.snapshot();
    for(const value of [NaN,Infinity,-Infinity])sim.setController(value);
    for(const value of [NaN,Infinity,-1,0])sim.step(value);
    expect(sim.snapshot()).toEqual(before);
  });
  it('rejects corrupt saves atomically while accepting stopped and completed services',()=>{
    const sim=new Simulation();sim.loadScenario('platform');const valid=sim.snapshot();
    const corrupt=[
      {...valid,doors:true,distance:valid.distance-50},
      {...valid,nextStation:STATIONS.length},
      {...valid,acceleration:100},
      {...valid,phase:'complete',speed:1},
      {...valid,results:[{station:'Unknown station',error:0,outcome:'served'}]},
      {...valid,results:[{station:'Flagstaff',error:50,outcome:'served'}]},
      {...valid,results:[{station:'Flagstaff',error:-50,outcome:'missed'}]},
    ];
    for(const save of corrupt){expect(sim.restore(save)).toBe(false);expect(sim.snapshot()).toEqual(valid);}
    expect(sim.restore(valid)).toBe(true);
    const fresh=new Simulation();expect(fresh.restore(new Simulation().snapshot())).toBe(true);
    const complete={...valid,phase:'complete',nextStation:STATIONS.length,speed:0,controller:0,doors:false};
    expect(sim.restore(complete)).toBe(true);expect(sim.state.phase).toBe('complete');
  });
  it('freezes boarding and rejects every driving input while paused',()=>{
    const sim=new Simulation();sim.loadScenario('platform');sim.toggleDoors();advance(sim,2);sim.pause();
    const before=sim.snapshot();sim.setController(4);sim.emergencyBrake();expect(sim.toggleDoors()).toBe(false);advance(sim,10);
    expect(sim.snapshot()).toEqual(before);sim.pause();advance(sim,6.1);expect(sim.toggleDoors()).toBe(true);
  });
  it('can run the complete circuit, serve every station and finish',()=>{
    const sim=new Simulation();sim.start();
    for(let frame=0;frame<60*60*30&&sim.state.phase!=='complete';frame++){
      const s=sim.state,stop=STATIONS[s.nextStation];
      if(!stop)break;
      if(s.doors){if(s.dwell>=8)sim.toggleDoors();}
      else{
        const remaining=stop.distance-s.distance;
        if(Math.abs(remaining)<7&&s.speed<.05){sim.toggleDoors();}
        else if(frame%12===0){
          const desired=Math.min(12,Math.sqrt(Math.max(0,2*.55*(remaining-3))));
          if(remaining<6)sim.setController(-4);
          else if(s.speed>desired+.2)sim.setController(-3);
          else if(s.speed<desired-.5)sim.setController(3);
          else sim.setController(0);
        }
      }
      sim.step(FIXED_STEP);
    }
    expect(sim.state.phase,JSON.stringify(sim.state)).toBe('complete');
    expect(sim.state.results).toHaveLength(STATIONS.length);
    expect(sim.state.results.every(r=>r.outcome==='served')).toBe(true);
  });
});
describe('continuous route',()=>{
  it('places intermediate stops on official platform coordinates and closes without a heading kink',()=>{
    for(let i=1;i<routeSource.sourceStops.length;i++){
      const [lon,lat]=routeSource.sourceStops[i].geometry.coordinates;
      const official=project(lon,lat),actual=positionAt(STATIONS[i].distance);
      expect(Math.hypot(actual.x-official.x,actual.z-official.z)).toBeLessThan(20);
      expect(actual.y).toBe(i===1?3:-23);
    }
    expect(positionAt(STATIONS[0].distance).y).toBe(7);
    expect(positionAt(STATIONS.at(-1)!.distance).y).toBe(7);
    const start=tangentAt(0),end=tangentAt(ROUTE_LENGTH);
    expect(start.x*end.x+start.y*end.y+start.z*end.z).toBeGreaterThan(.999);
  });
  it('keeps authored grades drivable and joins the loop at the same elevation',()=>{
    let maxGrade=0;
    for(let distance=0;distance<ROUTE_LENGTH;distance+=2)maxGrade=Math.max(maxGrade,Math.abs(tangentAt(distance).y));
    // Bound the fictional alignment so gravity never exceeds usable full traction.
    expect(maxGrade).toBeLessThan(.055);
    expect(positionAt(0)).toEqual(positionAt(ROUTE_LENGTH));
    for(const stop of STATIONS)expect(stop.distance).toBeGreaterThanOrEqual(0);
    expect(STATIONS.at(-1)!.distance).toBeLessThan(ROUTE_LENGTH);
  });
  it('orders station markers and samples positions in metres without jumps',()=>{
    for(let i=1;i<STATIONS.length;i++)expect(STATIONS[i].distance).toBeGreaterThan(STATIONS[i-1].distance);
    for(let s=0;s<ROUTE_LENGTH-1;s+=7){const a=positionAt(s),b=positionAt(s+1);expect(Math.hypot(a.x-b.x,a.y-b.y,a.z-b.z)).toBeLessThan(1.01);const t=tangentAt(s);expect(Math.hypot(t.x,t.y,t.z)).toBeCloseTo(1,6);}
  });
});
