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
    expect(cues.update(sim.state)).toBeNull();expect(cues.text).not.toContain('mind the gap');
  });
});
