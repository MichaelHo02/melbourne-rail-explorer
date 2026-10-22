import { STATIONS, ROUTE_LENGTH, speedLimitAt } from '../data/route';
import { advanceMotion } from './motion';

export type Phase='ready'|'driving'|'paused'|'complete';
export interface StopResult { station:string; error:number; outcome:'served'|'missed' }
export interface TrainState {
  version:1; distance:number; speed:number; acceleration:number; controller:number;
  doors:boolean; dwell:number; nextStation:number; time:number; phase:Phase;
  emergency:boolean; results:StopResult[]; overspeedSeconds:number;
}
export const FIXED_STEP=1/60;
export class Simulation {
  state:TrainState=this.initial();
  message='Close the doors, release the brake, and ease into power.';
  private initial():TrainState{return {version:1,distance:STATIONS[0].distance,speed:0,acceleration:0,controller:0,doors:true,dwell:8,nextStation:0,time:0,phase:'ready',emergency:false,results:[],overspeedSeconds:0};}
  reset(){this.state=this.initial();this.message='Close the doors, release the brake, and ease into power.';}
  start(){if(this.state.phase==='ready')this.state.phase='driving';}
  pause(){if(this.state.phase==='driving')this.state.phase='paused';else if(this.state.phase==='paused')this.state.phase='driving';}
  setController(value:number){
    if(this.state.phase!=='driving'||!Number.isFinite(value))return;
    if(this.state.emergency&&this.state.speed>.05)return;
    this.state.emergency=false;
    this.state.controller=Math.round(Math.max(-4,Math.min(4,value)));
    if(this.state.doors&&value>0)this.message='Close the doors before applying power.';
  }
  emergencyBrake(){if(this.state.phase!=='driving')return;this.state.emergency=true;this.state.controller=-4;this.message='Emergency brake applied. Stop, then move the controller to release.';}
  toggleDoors(){
    const s=this.state;
    if(s.phase!=='driving')return false;
    if(s.speed>.05){this.message='Stop the train before opening the doors.';return false;}
    const station=STATIONS[s.nextStation];
    if(!station)return false;
    const error=s.distance-station.distance;
    if(s.doors){
      if(s.dwell<8){this.message=`Boarding passengers · ${Math.ceil(8-s.dwell)} seconds remaining`;return false;}
      s.doors=false;s.dwell=0;
      s.results.push({station:station.name,error,outcome:'served'});
      s.nextStation++;
      if(s.nextStation>=STATIONS.length){s.phase='complete';s.controller=0;this.message='City Loop service complete.';}
      else this.message=`Doors secured. Next stop, ${STATIONS[s.nextStation].name}.`;
      return true;
    }
    if(Math.abs(error)>8){this.message=error<0?'Move forward to the stop marker before opening the doors.':'You passed the stop marker. Continue to the next station or restart the service.';return false;}
    s.doors=true;s.speed=0;s.controller=0;s.dwell=0;s.acceleration=0;
    this.message=`${station.name}. Boarding passengers.`;return true;
  }
  step(dt:number){
    const s=this.state;if(s.phase!=='driving'||!Number.isFinite(dt)||dt<=0)return;
    s.time+=dt;
    if(s.doors){s.speed=0;s.acceleration=0;s.dwell=Math.min(8,s.dwell+dt);return;}
    const motion=advanceMotion(s,dt);
    s.distance=Math.min(ROUTE_LENGTH,motion.distance);s.speed=motion.speed;s.acceleration=motion.acceleration;
    if(s.speed*3.6>speedLimitAt(s.distance)+2)s.overspeedSeconds+=dt;
    const station=STATIONS[s.nextStation];
    if(station&&s.distance>station.distance+24){
      s.results.push({station:station.name,error:s.distance-station.distance,outcome:'missed'});s.nextStation++;
      this.message=`Missed ${station.name}. Continue to the next stop.`;
    }
    if(s.distance>=ROUTE_LENGTH||s.nextStation>=STATIONS.length){s.speed=0;s.acceleration=0;s.controller=0;s.phase='complete';}
  }
  loadScenario(name:'departure'|'tunnel'|'approach'|'platform'|'viaduct'|'flagstaff'|'parliament'|'southern-cross'){
    this.reset();const s=this.state;s.phase='driving';
    if(name==='departure')return;
    if(name==='flagstaff'||name==='parliament'||name==='southern-cross'){s.nextStation=name==='flagstaff'?2:name==='parliament'?4:1;s.distance=STATIONS[s.nextStation].distance;s.doors=true;s.dwell=8;this.message=`${STATIONS[s.nextStation].name}. Platform inspection.`;return;}
    if(name==='viaduct'){s.doors=false;s.dwell=0;s.nextStation=1;s.distance=640;s.speed=0;this.message='Flinders Street viaduct. Continue to Southern Cross.';return;}
    s.doors=false;s.dwell=0;s.nextStation=name==='tunnel'||name==='platform'?3:1;
    s.distance=STATIONS[s.nextStation].distance-(name==='platform'?0:name==='tunnel'?320:150);
    s.speed=name==='platform'?0:name==='tunnel'?10:8;
    this.message=`Approaching ${STATIONS[s.nextStation].name}. Brake to the stop marker.`;
  }
  restore(value:unknown):boolean{
    if(!value||typeof value!=='object')return false;
    const s=value as TrainState;
    if(s.version!==1||!['ready','driving','paused','complete'].includes(s.phase)||
      ![s.distance,s.speed,s.acceleration,s.controller,s.dwell,s.nextStation,s.time,s.overspeedSeconds].every(Number.isFinite)||
      s.distance<0||s.distance>ROUTE_LENGTH||s.speed<0||s.speed>100||s.controller< -4||s.controller>4||!Number.isInteger(s.controller)||
      Math.abs(s.acceleration)>3||s.nextStation<0||s.nextStation>STATIONS.length||!Number.isInteger(s.nextStation)||s.dwell<0||s.dwell>8||s.time<0||s.overspeedSeconds<0||
      typeof s.doors!=='boolean'||typeof s.emergency!=='boolean'||!Array.isArray(s.results)||s.results.length>s.nextStation||
      !s.results.every(r=>r&&STATIONS.some(station=>station.name===r.station)&&Number.isFinite(r.error)&&
        (r.outcome==='served'?Math.abs(r.error)<=8:r.outcome==='missed'&&r.error>24&&r.error<=ROUTE_LENGTH))||
      (s.phase!=='complete'&&s.nextStation===STATIONS.length)||
      (s.phase==='complete'&&(s.speed!==0||s.controller!==0||s.doors))||
      (s.doors&&(s.speed!==0||s.nextStation>=STATIONS.length||Math.abs(s.distance-STATIONS[s.nextStation].distance)>8)))return false;
    this.state=structuredClone(s);this.state.phase=s.phase==='complete'?'complete':'paused';
    this.message=s.emergency?'Emergency brake applied. Stop, then move the controller to release.':s.doors?'Saved service restored. Finish boarding, then close the doors.':'Saved service restored. Check the next station and controller before departing.';return true;
  }
  snapshot(){return structuredClone(this.state);}
}
