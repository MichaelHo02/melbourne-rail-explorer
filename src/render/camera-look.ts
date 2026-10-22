import {positionAt,tangentAt,STATIONS,type Vec3} from '../data/route';
import type {TrainState} from '../game/simulation';
import {platformPosition} from './passenger-motion';

export type CameraView='cab'|'door-check';
export type InspectionView='viaduct'|'northbank'|'river'|'concourse'|'boarding'|'entrance'|'platform';
export interface LookAngles {yaw:number;pitch:number}
const clamp=(n:number,min:number,max:number)=>Math.max(min,Math.min(max,n));
export const DOOR_CHECK_YAW_LIMIT=78*Math.PI/180;
export const DOOR_CHECK_PITCH_LIMIT=.42;

/** Keep late WebGPU compilation/HMR frames safe if a view-state object is absent. */
export function safeLookAngles(look:LookAngles|undefined|null):LookAngles {
  return look&&Number.isFinite(look.yaw)&&Number.isFinite(look.pitch)?look:{yaw:0,pitch:0};
}

/** A platform feed is available only during an actual stationary station call.
 * Pausing keeps the same view; closing the doors restores the cab immediately. */
export function gameplayCameraView(state:TrainState):CameraView {
  const station=STATIONS[state.nextStation];
  return (state.phase==='driving'||state.phase==='paused')&&state.doors&&state.speed===0&&
    station&&Math.abs(state.distance-station.distance)<=8&&state.dwell>=0&&state.dwell<=8?'door-check':'cab';
}

/** Authoring viewpoints require an explicit development scenario and known name. */
export function developmentInspectionView(search:string,development:boolean):InspectionView|null {
  if(!development)return null;
  const params=new URLSearchParams(search),view=params.get('view');
  return params.has('scene')&&['viaduct','northbank','river','concourse','boarding','entrance','platform'].includes(view??'')?view as InspectionView:null;
}

/** The seated driver faces forward; only the automatic platform camera can look around. */
export class CameraLook {
  doorCheck:LookAngles={yaw:0,pitch:0};
  private view:CameraView='cab';
  setView(view:CameraView){if(view===this.view)return false;this.reset();this.view=view;return true;}
  private currentLook(){if(!this.doorCheck||!Number.isFinite(this.doorCheck.yaw)||!Number.isFinite(this.doorCheck.pitch))this.doorCheck={yaw:0,pitch:0};return this.doorCheck;}
  reset(){Object.assign(this.currentLook(),{yaw:0,pitch:0});}
  constrain(){const look=this.currentLook();look.yaw=clamp(look.yaw,-DOOR_CHECK_YAW_LIMIT,DOOR_CHECK_YAW_LIMIT);look.pitch=clamp(look.pitch,-DOOR_CHECK_PITCH_LIMIT,DOOR_CHECK_PITCH_LIMIT);}
  drag(view:CameraView,xFraction:number,yFraction:number){
    if(view!=='door-check'||this.view!=='door-check')return;
    if(!Number.isFinite(xFraction)||!Number.isFinite(yFraction))return;
    const look=this.currentLook();look.yaw+=xFraction*Math.PI;look.pitch-=yFraction*Math.PI*.65;this.constrain();
  }
}

export function cameraDragAllowed(view:CameraView,phase:TrainState['phase']){
  return view==='door-check'&&phase==='driving';
}

export interface CameraPose {position:Vec3;target:Vec3}
export function cabCameraPose(distance:number):CameraPose {
  const p=positionAt(distance),t=tangentAt(distance),length=Math.hypot(t.x,t.z)||1;
  const forward={x:t.x/length,z:t.z/length},side={x:-t.z/length,z:t.x/length};
  const pitch=Math.atan2(t.y,length),yaw=0;
  const direction={x:(forward.x*Math.cos(yaw)+side.x*Math.sin(yaw))*Math.cos(pitch),y:Math.sin(pitch),z:(forward.z*Math.cos(yaw)+side.z*Math.sin(yaw))*Math.cos(pitch)};
  const position={x:p.x,y:p.y+2.85,z:p.z};
  return {position,target:{x:position.x+direction.x*35,y:position.y+direction.y*35,z:position.z+direction.z*35}};
}

/** Authored fixed platform camera, looking back along the open-door side.
 * The shared platform warp handles FSS's opposite side and the route curves.
 * Its elevated sightline includes the first boarding queue and following doors;
 * bounded look changes the sightline only, never the fixed camera position. */
export function doorCheckCameraPose(state:TrainState,look:LookAngles={yaw:0,pitch:0}):CameraPose {
  const offset=state.distance-STATIONS[state.nextStation].distance;
  const p=platformPosition(state.nextStation,68+offset,4.8),target=platformPosition(state.nextStation,34+offset,1.8);
  const position={x:p.x,y:p.y+2.6,z:p.z},sightline={x:target.x,y:target.y+.95,z:target.z};
  return {position,target:boundedLookTarget(position,sightline,look,DOOR_CHECK_YAW_LIMIT,DOOR_CHECK_PITCH_LIMIT)};
}

function boundedLookTarget(origin:Vec3,target:Vec3,look:LookAngles,yawLimit:number,pitchLimit:number):Vec3 {
  const dx=target.x-origin.x,dy=target.y-origin.y,dz=target.z-origin.z;
  const horizontal=Math.hypot(dx,dz)||1,length=Math.hypot(dx,dy,dz)||1;
  const yaw=clamp(look.yaw,-yawLimit,yawLimit),pitch=clamp(Math.atan2(dy,horizontal)+look.pitch,-pitchLimit,pitchLimit);
  const fx=dx/horizontal,fz=dz/horizontal;
  return {x:origin.x+(fx*Math.cos(yaw)-fz*Math.sin(yaw))*Math.cos(pitch)*length,y:origin.y+Math.sin(pitch)*length,z:origin.z+(fz*Math.cos(yaw)+fx*Math.sin(yaw))*Math.cos(pitch)*length};
}

/** Rotate a fixed inspection viewpoint about its original sightline. */
export function inspectionLookTarget(origin:Vec3,target:Vec3,look:LookAngles):Vec3 {
  const dx=target.x-origin.x,dy=target.y-origin.y,dz=target.z-origin.z;
  const horizontal=Math.hypot(dx,dz)||1,length=Math.hypot(dx,dy,dz)||1;
  const pitch=clamp(Math.atan2(dy,horizontal)+look.pitch,-1.3,1.3),fx=dx/horizontal,fz=dz/horizontal;
  return {x:origin.x+(fx*Math.cos(look.yaw)-fz*Math.sin(look.yaw))*Math.cos(pitch)*length,y:origin.y+Math.sin(pitch)*length,z:origin.z+(fz*Math.cos(look.yaw)+fx*Math.sin(look.yaw))*Math.cos(pitch)*length};
}
