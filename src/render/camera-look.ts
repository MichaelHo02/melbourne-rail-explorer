import {positionAt,tangentAt,type Vec3} from '../data/route';

export type CameraView='cab'|'chase';
export interface LookAngles {yaw:number;pitch:number}
const clamp=(n:number,min:number,max:number)=>Math.max(min,Math.min(max,n));
const wrap=(angle:number)=>Math.atan2(Math.sin(angle),Math.cos(angle));
export const CAB_YAW_LIMIT=105*Math.PI/180;
export const DEFAULT_ORBIT={yaw:-.55,pitch:.24};

/** View-only state, deliberately excluded from the saved driving simulation. */
export class CameraLook {
  readonly cab:LookAngles={yaw:0,pitch:0};
  readonly chase:LookAngles={...DEFAULT_ORBIT};
  angles(view:CameraView){return view==='cab'?this.cab:this.chase;}
  reset(view:CameraView){Object.assign(this.angles(view),view==='cab'?{yaw:0,pitch:0}:DEFAULT_ORBIT);}
  constrain(view:CameraView,confined:boolean){
    const angles=this.angles(view);
    angles.yaw=view==='cab'?clamp(angles.yaw,-CAB_YAW_LIMIT,CAB_YAW_LIMIT):confined?clamp(angles.yaw,-1.25,1.25):wrap(angles.yaw);
    angles.pitch=view==='cab'?clamp(angles.pitch,-.6,.55):clamp(angles.pitch,confined?-.12:.16,confined?.48:1.1);
  }
  drag(view:CameraView,xFraction:number,yFraction:number,confined:boolean){
    if(!Number.isFinite(xFraction)||!Number.isFinite(yFraction))return;
    const angles=this.angles(view);
    angles.yaw+=xFraction*Math.PI;angles.pitch-=yFraction*Math.PI*.65;
    this.constrain(view,confined);
  }
}

// The authored running bore begins at -5.6m. Enter its conservative envelope
// before the full-size exterior orbit could cross the portal (and leave later).
export function cameraConfined(distance:number){
  return [-48,0,48].some(offset=>positionAt(distance+offset).y< -5.2);
}
const ahead=(distance:number):Vec3=>{
  const p=positionAt(distance);
  // The first train can stand with its body before route distance zero.
  if(distance<0){const t=tangentAt(0);p.x+=t.x*distance;p.y+=t.y*distance;p.z+=t.z*distance;}
  return p;
};
const frame=(distance:number)=>{
  const t=tangentAt(distance),length=Math.hypot(t.x,t.z)||1;
  return {forward:{x:t.x/length,z:t.z/length},side:{x:-t.z/length,z:t.x/length},grade:Math.atan2(t.y,length)};
};
export interface CameraPose {position:Vec3;target:Vec3;confined:boolean}
export function drivingCameraPose(distance:number,view:CameraView,look:LookAngles):CameraPose {
  const p=ahead(distance),f=frame(distance),confined=cameraConfined(distance);
  if(view==='cab'){
    const pitch=clamp(look.pitch,-.6,.55)+f.grade,yaw=clamp(look.yaw,-CAB_YAW_LIMIT,CAB_YAW_LIMIT);
    const direction={x:(f.forward.x*Math.cos(yaw)+f.side.x*Math.sin(yaw))*Math.cos(pitch),y:Math.sin(pitch),z:(f.forward.z*Math.cos(yaw)+f.side.z*Math.sin(yaw))*Math.cos(pitch)};
    const position={x:p.x,y:p.y+2.85,z:p.z};
    return {position,target:{x:position.x+direction.x*35,y:position.y+direction.y*35,z:position.z+direction.z*35},confined};
  }
  if(confined){
    // There is no room for a camera to orbit behind/through a full-width train.
    // Stay ahead of its nose, follow the curved track and orbit within the bore.
    const yaw=clamp(look.yaw,-1.25,1.25),pitch=clamp(look.pitch,-.12,.48);
    const distanceAhead=3.3+6*Math.cos(yaw),anchor=ahead(distance+distanceAhead),local=frame(distance+distanceAhead);
    const height=2.5+Math.sin(pitch)*2;
    const boreHalfWidth=3.4*Math.sqrt(Math.max(0,1-((height-.9)/3.9)**2));
    const across=clamp(Math.sin(yaw)*2.55,-boreHalfWidth+.4,boreHalfWidth-.4);
    const target=ahead(distance-.5);
    return {position:{x:anchor.x+local.side.x*across,y:anchor.y+height,z:anchor.z+local.side.z*across},target:{x:target.x,y:target.y+2.55,z:target.z},confined};
  }
  const pitch=clamp(look.pitch,.16,1.1),radius=42,horizontal=radius*Math.cos(pitch),target=ahead(distance-8);
  return {position:{x:p.x+horizontal*(f.forward.x*Math.cos(look.yaw)+f.side.x*Math.sin(look.yaw)),y:p.y+2+radius*Math.sin(pitch),z:p.z+horizontal*(f.forward.z*Math.cos(look.yaw)+f.side.z*Math.sin(look.yaw))},target:{x:target.x,y:target.y+2.2,z:target.z},confined};
}

/** Rotate a fixed inspection viewpoint about its original sightline. */
export function inspectionLookTarget(origin:Vec3,target:Vec3,look:LookAngles):Vec3 {
  const dx=target.x-origin.x,dy=target.y-origin.y,dz=target.z-origin.z;
  const horizontal=Math.hypot(dx,dz)||1,length=Math.hypot(dx,dy,dz)||1;
  const pitch=clamp(Math.atan2(dy,horizontal)+look.pitch,-1.3,1.3),fx=dx/horizontal,fz=dz/horizontal;
  return {x:origin.x+(fx*Math.cos(look.yaw)-fz*Math.sin(look.yaw))*Math.cos(pitch)*length,y:origin.y+Math.sin(pitch)*length,z:origin.z+(fz*Math.cos(look.yaw)+fx*Math.sin(look.yaw))*Math.cos(pitch)*length};
}
