import {describe,expect,it} from 'vitest';
import {passengerIdle} from '../src/render/passenger-idle';

describe('passenger anatomical idle',()=>{
  it('is an exact function of service time, so paused and replayed poses are identical',()=>{
    const paused=passengerIdle(42.75,17);
    expect(passengerIdle(42.75,17)).toEqual(paused);
    passengerIdle(100,17);
    expect(passengerIdle(42.75,17)).toEqual(paused);
    expect(passengerIdle(0,17)).toEqual(passengerIdle(-1,17));
  });
  it('keeps bounded independent morphs and never combines opposing head rotations',()=>{
    let bounded=true,opposing=false;
    for(let seed=0;seed<24;seed++)for(let t=0;t<120;t+=.13){
      const pose=passengerIdle(t,seed);
      bounded=bounded&&Object.values(pose).every(w=>Number.isFinite(w)&&w>=0&&w<=1);
      opposing=opposing||pose.lookLeft*pose.lookRight!==0;
    }
    expect(bounded).toBe(true);expect(opposing).toBe(false);
  });
  it('gives neighbours independent timing and eases into quiet glances',()=>{
    expect(passengerIdle(3,0)).not.toEqual(passengerIdle(3,1));
    expect(passengerIdle(2,0).lookLeft).toBe(0);
    expect(passengerIdle(2.001,0).lookLeft).toBeLessThan(.00001);
    expect(passengerIdle(8,0).lookLeft).toBe(0);
  });
});
