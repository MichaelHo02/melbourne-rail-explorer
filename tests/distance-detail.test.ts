import {describe,it,expect} from 'vitest';
import {distanceDetailVisible} from '../src/render/distance-detail';
describe('distance detail hysteresis',()=>{
 it('does not chatter as a stopped camera moves around the entry distance',()=>{
  let visible=false;const states=[350,325,332,329,355,365,335,320].map(distance=>visible=distanceDetailVisible(distance,visible,330,360));
  expect(states).toEqual([false,true,true,true,true,false,false,true]);
 });
 it('drops invalid positions rather than holding stale detail',()=>{
  expect(distanceDetailVisible(NaN,true,330,360)).toBe(false);
 });
});
