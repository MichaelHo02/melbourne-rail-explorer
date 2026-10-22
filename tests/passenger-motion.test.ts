import {describe,expect,it} from 'vitest';
import {Simulation} from '../src/game/simulation';
import {STATIONS} from '../src/data/route';
import {createPassengerPlacements,passengerMotion,platformPosition,walkWeights,footContacts} from '../src/render/passenger-motion';
import {trainDoorDistances,doorLeafSide} from '../src/render/train-layout';

const people=createPassengerPlacements();
describe('platform passenger behaviour',()=>{
  it('populates every physical station and keeps walking in a separate furniture-free lane',()=>{
    for(let station=0;station<5;station++){
      const local=people.filter(p=>p.station===station);
      expect(local).toHaveLength(24);
      expect(local.filter(p=>p.role==='walking')).toHaveLength(4);
      const stationary=local.filter(p=>p.role!=='walking');
      for(const a of stationary)for(const b of stationary)if(a!==b)expect(Math.hypot(a.along-b.along,a.lateral-b.lateral)).toBeGreaterThan(.7);
      const sim=new Simulation();sim.start();sim.state.doors=false;
      for(const p of local.filter(p=>p.role==='walking'))for(let time=0;time<120;time+=.7){
        const pose=passengerMotion(p,{...sim.state,time});
        // The rounded walk lane remains at least 1.8m from the platform edge.
        const start=platformPosition(station,p.along,4.37);
        expect(Math.hypot(pose.position.x-start.x,pose.position.z-start.z)).toBeLessThan(25);
        expect(pose.walkWeight).toBe(1);expect(pose.visible).toBe(true);
      }
    }
  });
  it('pauses and restores walking/boarding exactly from the saved service state',()=>{
    const sim=new Simulation();sim.loadScenario('platform');sim.toggleDoors();sim.step(2.75);
    for(const p of people){
      const moving=passengerMotion(p,sim.state);
      const restored=new Simulation();expect(restored.restore(sim.snapshot())).toBe(true);
      expect(passengerMotion(p,restored.state)).toEqual(moving);
      expect(passengerMotion(p,{...sim.state,phase:'paused'})).toEqual(moving);
    }
  });
  it('keeps boarding paths clear of waiting passengers throughout allowed stop offsets',()=>{
    const sim=new Simulation();sim.start();let minimum=Infinity;
    for(let station=0;station<STATIONS.length;station++){
      Object.assign(sim.state,{nextStation:station,distance:STATIONS[station].distance,doors:true,dwell:0});
      const local=people.filter(p=>p.station===(station===STATIONS.length-1?0:station));
      const waiting=local.filter(p=>p.role==='waiting').map(p=>passengerMotion(p,sim.state).position);
      const boarders=local.filter(p=>p.role==='boarding');
      // Quarter-metre stop offsets include doorway-selection boundaries; 50ms
      // steps cover the approach along the queue and the turn into the train.
      for(let error=-8;error<=8;error+=.25)for(let dwell=0;dwell<=8;dwell+=.05){
        const state={...sim.state,distance:STATIONS[station].distance+error,dwell};
        for(const p of boarders){
          const pose=passengerMotion(p,state);if(!pose.visible)continue;
          for(const q of waiting)minimum=Math.min(minimum,Math.hypot(pose.position.x-q.x,pose.position.z-q.z));
        }
      }
    }
    // This is a visual body clearance, not just distinct placement origins.
    expect(minimum).toBeGreaterThan(.7);
  },10_000);
  it('keeps waiting pockets outside walking circuits and the furniture band',()=>{
    const sim=new Simulation();sim.start();sim.state.doors=false;let minimum=Infinity;
    for(let station=0;station<STATIONS.length;station++){
      sim.state.nextStation=station;sim.state.distance=STATIONS[station].distance-120;
      const local=people.filter(p=>p.station===(station===STATIONS.length-1?0:station));
      const waiting=local.filter(p=>p.role==='waiting');
      const positions=waiting.map(p=>passengerMotion(p,sim.state).position);
      // All current low furniture starts at the bench front x4.97; the SXS
      // stairs/lift begin farther inland at5.675. Keep a body-sized margin.
      for(const p of waiting)expect(p.lateral+.4).toBeLessThan(4.97);
      for(let time=0;time<180;time+=.25)for(const p of local.filter(p=>p.role==='walking')){
        const pose=passengerMotion(p,{...sim.state,time});
        for(const q of positions)minimum=Math.min(minimum,Math.hypot(pose.position.x-q.x,pose.position.z-q.z));
      }
    }
    expect(minimum).toBeGreaterThan(.7);
  });
  it('boards through actual door centres for every allowed stop offset before dwell ends',()=>{
    const sim=new Simulation();sim.start();
    for(let station=0;station<STATIONS.length;station++)for(const error of [-8,-4,0,4,8]){
      Object.assign(sim.state,{nextStation:station,distance:STATIONS[station].distance+error,doors:true,dwell:0});
      const boarders=people.filter(p=>p.station===(station===5?0:station)&&p.role==='boarding');
      for(const p of boarders){
        expect(passengerMotion(p,sim.state).visible).toBe(true);
        let crossed=false;
        for(let dwell=0;dwell<=8;dwell+=.025){
          const pose=passengerMotion(p,{...sim.state,dwell});
          if(!pose.visible){crossed=true;break;}
          // A traveller remains on the platform until aligned with a doorway.
          const nominal=STATIONS[station].distance-65+p.along;
          const target=trainDoorDistances(sim.state.distance).reduce((best,d)=>Math.abs(d-nominal)<Math.abs(best-nominal)?d:best);
          const doorAlong=65+target-STATIONS[station].distance;
          const reference=platformPosition(station,doorAlong,1.05);
          if(Math.hypot(pose.position.x-reference.x,pose.position.z-reference.z)<.6){
            const far=platformPosition(station,doorAlong,3.3);
            const vx=far.x-reference.x,vz=far.z-reference.z;
            const cross=(pose.position.x-reference.x)*vz-(pose.position.z-reference.z)*vx;
            expect(Math.abs(cross)).toBeLessThan(.08);
          }
        }
        expect(crossed).toBe(true);
      }
    }
  });
  it('retains missed-station queues and hides served boarders until the final Flinders visit',()=>{
    const sim=new Simulation();sim.start();sim.state.doors=false;sim.state.nextStation=2;
    const p=people.find(p=>p.station===1&&p.role==='boarding')!;
    sim.state.results=[{station:STATIONS[1].name,error:25,outcome:'missed'}];expect(passengerMotion(p,sim.state).visible).toBe(true);
    sim.state.results=[{station:STATIONS[1].name,error:0,outcome:'served'}];expect(passengerMotion(p,sim.state).visible).toBe(false);
    const first=people.find(p=>p.station===0&&p.role==='boarding')!;
    sim.state.results=[{station:STATIONS[0].name,error:0,outcome:'served'}];expect(passengerMotion(first,sim.state).visible).toBe(false);
    sim.state.nextStation=5;sim.state.distance=STATIONS[5].distance;expect(passengerMotion(first,sim.state).visible).toBe(true);
    sim.state.nextStation=6;sim.state.phase='complete';expect(passengerMotion(first,sim.state).visible).toBe(false);
  });
  it('interpolates gait continuously and keeps stance contacts fixed as the root advances',()=>{
    const a=walkWeights(.9999,1),b=walkWeights(1,1);expect(a.second).toBe(b.first);
    for(let phase=0;phase<1;phase+=.01){const w=walkWeights(phase,.7);expect(w.firstWeight+w.secondWeight).toBeCloseTo(.7);}
    const at=footContacts(.125,1)[0],later=footContacts(.25,1)[0];
    expect(at.lift).toBe(0);expect(later.lift).toBe(0);
    expect(later.z-at.z+1.1*.125).toBeCloseTo(0);
    expect(footContacts(.75,1)[0].lift).toBeGreaterThan(.05);
  });
  it('accounts for the reversed rear cab when selecting platform-side doors',()=>{
    expect(doorLeafSide('door_L_0_minus_leaf',0)).toBe(-1);
    expect(doorLeafSide('door_L_0_minus_leaf',6)).toBe(1);
    expect(doorLeafSide('door_R_0_minus_leaf',6)).toBe(-1);
    const distances=trainDoorDistances(500);expect(distances).toHaveLength(21);
    expect(distances[18]).toBeCloseTo(500-11.2-6*22.85-5.62);
  });
});
