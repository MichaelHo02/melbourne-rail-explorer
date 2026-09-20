import {describe,expect,it} from 'vitest';
import {stoppingDistance} from '../src/game/motion';
import {Simulation,FIXED_STEP} from '../src/game/simulation';
import {STATIONS} from '../src/data/route';
import {DoorMotion} from '../src/render/door-motion';

describe('training stop estimate',()=>{
  it('matches an actual stop within one metre on the surface, descent and tunnel',()=>{
    for(const distance of [600,STATIONS[1].distance+125,STATIONS[3].distance-350]){
      const sim=new Simulation();sim.loadScenario('tunnel');
      Object.assign(sim.state,{distance,speed:13,acceleration:.35,controller:3,nextStation:3});
      const estimate=stoppingDistance(sim.state,-3);
      sim.setController(-3);
      for(let i=0;i<60*120&&sim.state.speed>.001;i++)sim.step(FIXED_STEP);
      expect(sim.state.speed).toBeLessThan(.001);
      expect(Math.abs(sim.state.distance-distance-estimate)).toBeLessThan(1);
    }
  });
  it('distinguishes service brake strengths without modifying the player state',()=>{
    const sim=new Simulation();sim.loadScenario('tunnel');const before=sim.snapshot();
    expect(stoppingDistance(before,-4)).toBeLessThan(stoppingDistance(before,-2));
    expect(sim.snapshot()).toEqual(before);
    expect(stoppingDistance({...before,speed:0})).toBe(0);
  });
});

describe('visual door clock',()=>{
  it('closes the final-stop doors when completion freezes the service clock',()=>{
    const sim=new Simulation();sim.start();sim.state.nextStation=STATIONS.length-1;
    sim.state.distance=STATIONS.at(-1)!.distance;sim.state.time=600;
    const doors=new DoorMotion();expect(doors.sample(sim.state.time,sim.state.distance,sim.state.doors)).toBe(1);
    expect(sim.toggleDoors()).toBe(true);expect(sim.state.phase).toBe('complete');
    sim.step(FIXED_STEP);expect(sim.state.time).toBe(600);
    expect(doors.sample(sim.state.time,sim.state.distance,sim.state.doors,sim.state.phase==='complete')).toBe(0);
  });
  it('freezes midway through closing, resumes, and resets for another scenario',()=>{
    const doors=new DoorMotion();expect(doors.sample(0,60,true)).toBe(1);
    const partial=doors.sample(.1,60,false);expect(partial).toBeGreaterThan(0);expect(partial).toBeLessThan(1);
    for(let i=0;i<100;i++)expect(doors.sample(.1,60,false)).toBe(partial);
    expect(doors.sample(.5,60,false)).toBeLessThan(partial);
    expect(doors.sample(0,500,true)).toBe(1);
    expect(doors.sample(0,2000,false)).toBe(0);
  });
});
