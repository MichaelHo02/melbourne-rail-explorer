import { tangentAt } from '../data/route';

export interface MotionState {distance:number;speed:number;acceleration:number;controller:number;emergency:boolean}

/** The approachable train model, shared by driving and the training stop guide. */
export function advanceMotion(s:MotionState,dt:number){
  const traction=s.controller>0?s.controller/4*.82*Math.max(.22,1-s.speed/36):0;
  const brake=s.emergency?1.65:Math.max(0,-s.controller)/4*1.12;
  const drag=.015+s.speed*s.speed*.00012;
  const target=traction-brake-drag-9.81*tangentAt(s.distance).y;
  let acceleration=s.acceleration+Math.max(-dt*.9,Math.min(dt*.9,target-s.acceleration));
  if(s.speed===0&&s.controller<=0)acceleration=Math.min(0,acceleration);
  const speed=Math.max(0,s.speed+acceleration*dt);
  return {distance:s.distance+(s.speed+speed)*.5*dt,speed,acceleration};
}

/** Simulation-based estimate, not operational braking data. Includes the current
 * acceleration ramp and upcoming authored gradients rather than v²/2a alone. */
export function stoppingDistance(state:MotionState,controller=-3){
  if(state.speed<.05)return 0;
  let sample={...state,controller,emergency:state.emergency};
  const dt=1/30;
  for(let i=0;i<3600;i++){
    const motion=advanceMotion(sample,dt);sample={...sample,...motion};
    if(sample.speed<.01)return sample.distance-state.distance;
  }
  return Infinity;
}
