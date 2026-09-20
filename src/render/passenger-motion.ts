import {STATIONS,positionAt,tangentAt} from '../data/route';
import type {TrainState} from '../game/simulation';
import {trainDoorDistances,CAB_TO_CAR_CENTRE,CAR_SPACING} from './train-layout';

export interface PassengerPlacement {
  station:number;along:number;lateral:number;heading:number;variant:number;
  role:'waiting'|'walking'|'boarding';seed:number;
}
export interface PassengerPose {
  position:{x:number;y:number;z:number};heading:number;visible:boolean;
  walkPhase:number;walkWeight:number;boarding:boolean;
}
export const WALK_STRIDE=1.1;
const tau=Math.PI*2;
const clamp=(x:number)=>Math.max(0,Math.min(1,x));
const smooth=(x:number)=>{const t=clamp(x);return t*t*(3-2*t);};

export function createPassengerPlacements():PassengerPlacement[]{
  return STATIONS.slice(0,-1).flatMap((_,station)=>{
    const people:PassengerPlacement[]=[];
    const queues=Array.from({length:6},(_,i)=>65-CAB_TO_CAR_CENTRE-i*CAR_SPACING-.57);
    // Waiting pockets occupy gaps between the four short walking circuits.
    // Their inland band leaves the whole boarding sweep at x<=3.3 clear,
    // including when an allowed stop offset moves the nearest doorway. The
    // pockets stay in front of benches (x>=4.97) and the SXS stair/lift band.
    const waitingAlong=[-59,-55.6,-50.8,-47.2,-15.1,-11.5,-7.1,-3.4,29.2,33.6,39.1,73.4,78.1,83];
    for(const [i,along] of waitingAlong.entries()){
      people.push({station,along,lateral:4.35+(i%2)*.15,heading:(i%3-1)*.35-Math.PI/2,variant:(i+station)%6,role:'waiting',seed:station*24+i});
    }
    // One potential boarder per car, with generous separation from the others.
    for(let i=0;i<6;i++)people.push({station,along:queues[i],lateral:3.3,heading:-Math.PI/2,variant:(i+station)%6,role:'boarding',seed:station*24+14+i});
    for(let i=0;i<4;i++)people.push({station,along:-87+i*44,lateral:4.37,heading:0,variant:(i+station+2)%6,role:'walking',seed:station*24+20+i});
    return people;
  });
}

/** Same route warp as platform geometry, including the approach behind FSS. */
export function platformPosition(station:number,along:number,lateral:number){
  const s=STATIONS[station].distance-65+along,p=positionAt(s),t=tangentAt(Math.max(0,s));
  if(s<0){p.x+=t.x*s;p.y+=t.y*s;p.z+=t.z*s;}
  const sign=STATIONS[station].code==='FSS'?-1:1,n=Math.hypot(t.x,t.z)||1,x=lateral*sign;
  return {x:p.x+t.z/n*x,y:p.y+1.065,z:p.z-t.x/n*x};
}

function worldHeading(p:PassengerPlacement,along:number,lateralDirection:number,alongDirection:number){
  const t=tangentAt(Math.max(0,STATIONS[p.station].distance-65+along));
  const side=STATIONS[p.station].code==='FSS'?-1:1;
  return Math.atan2(t.x*alongDirection+t.z*lateralDirection*side,t.z*alongDirection-t.x*lateralDirection*side);
}

/** Deterministic visual behaviour: no hidden timers and no changes to saved services. */
export function passengerMotion(p:PassengerPlacement,s:TrainState):PassengerPose {
  // The authored circuit has separate departure/arrival markers at Flinders.
  // Relocate its population only once the distant final approach is selected.
  if(p.station===0&&s.nextStation>=STATIONS.length-1)p={...p,station:STATIONS.length-1};
  let along=p.along,lateral=p.lateral,heading=worldHeading(p,along,Math.sin(p.heading),Math.cos(p.heading));
  let walkDistance=0,walkWeight=0,visible=true,boarding=false;
  if(p.role==='walking'){
    // Four separate short circuits share the clear platform lane. Rounded ends
    // let the feet keep stepping through turns instead of spinning in place.
    const length=24,radius=.27,loop=2*length+tau*radius,speed=.92+(p.seed%5)*.047;
    walkDistance=Math.max(0,s.time)*speed+p.seed*3.71;
    const d=walkDistance%loop;
    let dx=0,dz=1;
    if(d<length){along+=d;lateral+=radius;}
    else if(d<length+Math.PI*radius){const a=(d-length)/radius;along+=length+Math.sin(a)*radius;lateral+=Math.cos(a)*radius;dx=-Math.sin(a);dz=Math.cos(a);}
    else if(d<2*length+Math.PI*radius){along+=2*length+Math.PI*radius-d;lateral-=radius;dz=-1;}
    else{const a=Math.PI+(d-2*length-Math.PI*radius)/radius;along+=Math.sin(a)*radius;lateral+=Math.cos(a)*radius;dx=-Math.sin(a);dz=Math.cos(a);}
    heading=worldHeading(p,along,dx,dz);walkWeight=1;
  }else if(p.role==='boarding'){
    const station=STATIONS[p.station],current=STATIONS[s.nextStation];
    const visiting=current?.code===station.code;
    const served=s.results.some(r=>r.station===station.name&&r.outcome==='served');
    // FSS is visited again at the end of the loop, after its first group left.
    visible=!served||(visiting&&s.nextStation===STATIONS.length-1);
    if(visiting&&s.doors&&Math.abs(s.distance-current.distance)<=8){
      visible=true;boarding=true;
      // Choose a real door centre, including the reversed rear driving car.
      const waiting=current.distance-65+p.along;
      const target=trainDoorDistances(s.distance).reduce((best,d)=>Math.abs(d-waiting)<Math.abs(best-waiting)?d:best);
      const delta=target-waiting,across=p.lateral-.72,total=Math.abs(delta)+across;
      const elapsed=Math.max(0,s.dwell-(.85+(p.seed%6)*.10));
      const travelled=Math.min(total,elapsed*Math.max(1.18,total/6));
      walkDistance=travelled;walkWeight=smooth(elapsed/.25);
      if(travelled<Math.abs(delta)){
        along+=Math.sign(delta)*travelled;heading=worldHeading(p,along,0,Math.sign(delta));
      }else{
        along+=delta;lateral-=travelled-Math.abs(delta);heading=worldHeading(p,along,-1,0);
      }
      // Blend the corner over a short step, avoiding a sideways pose snap.
      if(Math.abs(delta)>.15&&Math.abs(travelled-Math.abs(delta))<.3){
        const blend=smooth((travelled-Math.abs(delta)+.3)/.6);
        heading=worldHeading(p,along,-blend,Math.sign(delta)*(1-blend));
      }
      if(elapsed===0)heading=worldHeading(p,along,Math.sin(p.heading),Math.cos(p.heading));
      visible=lateral>1.03; // fully behind the doorway's exterior face
    }
  }
  return {position:platformPosition(p.station,along,lateral),heading,visible,walkPhase:(walkDistance/WALK_STRIDE)%1,walkWeight,boarding};
}

/** Eight exported stride poses interpolate cyclically, in travelled metres. */
export function walkWeights(phase:number,amount:number){
  const at=((phase%1)+1)%1*8,index=Math.floor(at),fraction=at-index;
  return {first:index,second:(index+1)%8,firstWeight:(1-fraction)*amount,secondWeight:fraction*amount};
}

/** Match Blender's eight sampled gait targets; +Z is the commuter's forward. */
export function footContacts(phase:number,amount:number,variant=0){
  const sample=(at:number,side:number)=>{
    const p=(at+side*.5)%1;
    if(p<.6)return {forward:.33-1.1*p,lift:0};
    const u=(p-.6)/.4;return {forward:-.33+.66*smooth(u),lift:.09*Math.sin(Math.PI*u)};
  };
  const weights=walkWeights(phase,1);
  // Neutral centres measured from each exported shoe sole, including the
  // asymmetrical weight-shift pose. Gait offsets use the same Blender contract.
  const centres=[[.1479,-.1479],[.1235,-.1235],[.1579,-.1579],[.1659,-.1050],[.1454,-.1454],[.1170,-.1170]][((variant%6)+6)%6];
  return [0,1].map(side=>{
    const a=sample(weights.first/8,side),b=sample(weights.second/8,side);
    return {x:centres[side],z:.048+(a.forward*weights.firstWeight+b.forward*weights.secondWeight)*amount,lift:(a.lift*weights.firstWeight+b.lift*weights.secondWeight)*amount};
  });
}
