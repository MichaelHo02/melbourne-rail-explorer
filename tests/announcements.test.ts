import { describe,it,expect } from 'vitest';
import { AnnouncementCues } from '../src/game/announcements';
import { Simulation } from '../src/game/simulation';
import { STATIONS } from '../src/data/route';

describe('service information cues',()=>{
  it('announces a stop once and only closes doors after the interlock accepts departure',()=>{
    const sim=new Simulation(),cues=new AnnouncementCues();sim.start();
    expect(cues.update(sim.state)).toContain('Flinders Street');
    expect(cues.update(sim.state)).toBeNull();
    sim.toggleDoors();expect(cues.update(sim.state)).toContain('next station is Southern Cross');
    expect(cues.update(sim.state)).toBeNull();
    sim.state.distance=STATIONS[1].distance;sim.toggleDoors();expect(cues.update(sim.state)).toContain('Southern Cross');
    sim.toggleDoors();expect(cues.update(sim.state)).toBeNull();
    expect(sim.state.doors).toBe(true);
  });
  it('pauses cue expiry with service time and allows cues after restart',()=>{
    const sim=new Simulation(),cues=new AnnouncementCues();sim.start();cues.update(sim.state);sim.pause();
    for(let i=0;i<20;i++){sim.step(1);cues.update(sim.state);}
    expect(cues.text).toContain('Flinders Street');sim.pause();sim.step(8);cues.update(sim.state);expect(cues.text).toBe('');
    sim.reset();sim.start();expect(cues.update(sim.state)).toContain('Flinders Street');
  });
  it('emits a single approach cue and does not issue arrival for a missed stop',()=>{
    const sim=new Simulation(),cues=new AnnouncementCues();sim.start();sim.toggleDoors();cues.update(sim.state);
    sim.state.distance=STATIONS[1].distance-200;expect(cues.update(sim.state)).toBe('Now approaching Southern Cross.');
    expect(cues.update(sim.state)).toBeNull();sim.state.distance=STATIONS[1].distance+25;sim.step(.02);
    expect(cues.update(sim.state)).toBeNull();expect(cues.text).toBe('');
  });
  it('announces the accepted final stop once and expires despite frozen completion time',()=>{
    const sim=new Simulation(),cues=new AnnouncementCues();sim.start();cues.update(sim.state,0);
    for(let index=0;index<STATIONS.length;index++){
      if(index>0){sim.state.distance=STATIONS[index].distance;expect(sim.toggleDoors()).toBe(true);cues.update(sim.state,index*10);sim.step(8);cues.update(sim.state,index*10+8);}
      expect(sim.toggleDoors()).toBe(true);
      const cue=cues.update(sim.state,index*10+9);
      expect(cue).toContain(index===STATIONS.length-1?'terminates at Flinders Street':'The next station');
    }
    const stoppedTime=sim.state.time;expect(sim.state.phase).toBe('complete');
    expect(cues.update(sim.state,60)).toBeNull();expect(cues.text).toContain('terminates');
    sim.step(20);expect(sim.state.time).toBe(stoppedTime);
    expect(cues.update(sim.state,67)).toBeNull();expect(cues.text).toBe('');
  });
  it('never announces a served termination when the final stop is missed',()=>{
    const sim=new Simulation(),cues=new AnnouncementCues();sim.start();sim.toggleDoors();
    sim.state.nextStation=STATIONS.length-1;sim.state.distance=STATIONS.at(-1)!.distance-100;
    cues.update(sim.state,1);expect(cues.text).toContain('approaching');
    sim.state.distance=STATIONS.at(-1)!.distance+25;sim.step(.02);
    expect(sim.state.phase).toBe('complete');expect(cues.update(sim.state,2)).toBeNull();expect(cues.text).toBe('');
  });
  it('baselines equal-time restored arrivals and approaches without replay, but announces a new service',()=>{
    const sim=new Simulation(),cues=new AnnouncementCues();sim.start();cues.update(sim.state);
    expect(sim.restore(sim.snapshot())).toBe(true);expect(cues.update(sim.state)).toBeNull();expect(cues.text).toBe('');
    sim.pause();expect(cues.update(sim.state)).toBeNull();
    sim.toggleDoors();expect(cues.update(sim.state)).toContain('Southern Cross');
    sim.state.distance=STATIONS[1].distance-200;cues.update(sim.state);
    expect(sim.restore(sim.snapshot())).toBe(true);cues.update(sim.state);sim.pause();
    expect(cues.update(sim.state)).toBeNull();expect(cues.text).toBe('');
    sim.reset();sim.start();expect(cues.update(sim.state)).toContain('Flinders Street');
    sim.reset();sim.start();expect(cues.update(sim.state)).toContain('Flinders Street');
  });
});
