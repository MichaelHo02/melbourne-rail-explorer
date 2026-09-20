import {describe,it,expect,vi} from 'vitest';
import {CameraLook,CAB_YAW_LIMIT,DEFAULT_ORBIT,cameraConfined,drivingCameraPose,inspectionLookTarget} from '../src/render/camera-look';
import {CameraDragInput} from '../src/render/camera-input';
import {positionAt,tangentAt,ROUTE_LENGTH} from '../src/data/route';

describe('train camera look',()=>{
  it('keeps cab head turns within seated limits and restores each view independently',()=>{
    const look=new CameraLook();look.drag('cab',5,-5,false);
    expect(look.cab).toEqual({yaw:CAB_YAW_LIMIT,pitch:.55});
    look.drag('chase',.4,-.2,false);const exterior={...look.chase};
    look.reset('cab');expect(look.cab).toEqual({yaw:0,pitch:0});expect(look.chase).toEqual(exterior);
    look.reset('chase');expect(look.chase).toEqual(DEFAULT_ORBIT);
    look.drag('cab',NaN,1,false);expect(look.cab).toEqual({yaw:0,pitch:0});
  });
  it('turns from the same seated eye while preserving the route grade and follow position',()=>{
    const distance=3300,straight=drivingCameraPose(distance,'cab',{yaw:0,pitch:0}),turned=drivingCameraPose(distance,'cab',{yaw:.7,pitch:.2});
    expect(turned.position).toEqual(straight.position);expect(turned.target).not.toEqual(straight.target);
    const p=positionAt(distance);expect(straight.position).toEqual({x:p.x,y:p.y+2.85,z:p.z});
    const next=drivingCameraPose(distance+30,'cab',{yaw:.7,pitch:.2});expect(next.position).not.toEqual(turned.position);
    expect(Math.hypot(turned.target.x-turned.position.x,turned.target.y-turned.position.y,turned.target.z-turned.position.z)).toBeCloseTo(35);
  });
  it('allows a complete surface orbit while keeping the camera above the train',()=>{
    expect(cameraConfined(60)).toBe(false);
    const a=drivingCameraPose(60,'chase',{yaw:0,pitch:-1}),b=drivingCameraPose(60,'chase',{yaw:Math.PI,pitch:-1}),p=positionAt(60),t=tangentAt(60);
    expect((a.position.x-p.x)*t.x+(a.position.z-p.z)*t.z).toBeGreaterThan(35);
    expect((b.position.x-p.x)*t.x+(b.position.z-p.z)*t.z).toBeLessThan(-35);
    expect(a.position.y-p.y).toBeGreaterThan(8);
  });
  it('constrains underground orbit poses inside the authored bore and ahead of the nose',()=>{
    let poses=0;
    for(let distance=0;distance<ROUTE_LENGTH;distance+=150){
      if(!cameraConfined(distance))continue;
      for(const yaw of [-Math.PI,-1.25,0,1.25,Math.PI])for(const pitch of [-10,-.12,.24,.48,10]){
        const pose=drivingCameraPose(distance,'chase',{yaw,pitch}),bounded=Math.max(-1.25,Math.min(1.25,yaw));
        const cameraDistance=distance+3.3+6*Math.cos(bounded),anchor=positionAt(cameraDistance),t=tangentAt(cameraDistance),length=Math.hypot(t.x,t.z);
        const across=(pose.position.x-anchor.x)*(-t.z/length)+(pose.position.z-anchor.z)*(t.x/length),height=pose.position.y-anchor.y;
        expect((across/3.4)**2+((height-.9)/3.9)**2).toBeLessThan(.93);
        expect(cameraDistance-distance).toBeGreaterThan(5);expect(height).toBeGreaterThan(2.2);expect(height).toBeLessThan(3.5);poses++;
      }
    }
    expect(poses).toBeGreaterThan(300);
  });
  it('rotates fixed inspection views in place and resets their original sightline',()=>{
    const origin={x:12,y:3,z:5},target={x:12,y:3,z:-15};
    expect(inspectionLookTarget(origin,target,{yaw:0,pitch:0})).toEqual(target);
    const right=inspectionLookTarget(origin,target,{yaw:Math.PI/2,pitch:0});
    expect(right.x).toBeCloseTo(32);expect(right.y).toBe(3);expect(right.z).toBeCloseTo(5);
    const up=inspectionLookTarget(origin,target,{yaw:0,pitch:.4});expect(up.y).toBeGreaterThan(3);
  });
});

class CanvasStub extends EventTarget {
  style={cursor:'',touchAction:''};dataset:Record<string,string>={};captured=new Set<number>();
  width=800;height=450;
  getBoundingClientRect(){return {width:this.width,height:this.height};}
  setPointerCapture(id:number){this.captured.add(id);}hasPointerCapture(id:number){return this.captured.has(id);}releasePointerCapture(id:number){this.captured.delete(id);}
  pointer(type:string,props:Record<string,number|boolean|string>={}){
    const event=Object.assign(new Event(type,{cancelable:true}),{button:0,buttons:1,isPrimary:true,pointerId:1,pointerType:'mouse',clientX:0,clientY:0,...props});this.dispatchEvent(event);return event;
  }
}
const input=()=>{const canvas=new CanvasStub(),drag=vi.fn(),reset=vi.fn(),controller=new CameraDragInput(canvas as unknown as HTMLCanvasElement,drag,reset);return {canvas,drag,reset,controller};};
describe('scene-only camera drag input',()=>{
  it('normalizes scaled canvas pointer deltas and releases capture at the end',()=>{
    const {canvas,drag,controller}=input();controller.setEnabled(true);
    canvas.pointer('pointerdown',{clientX:100,clientY:50});canvas.pointer('pointermove',{clientX:180,clientY:95});
    expect(drag).toHaveBeenLastCalledWith(.1,.1);expect(canvas.captured.has(1)).toBe(true);
    canvas.pointer('pointerup');expect(controller.dragging).toBe(false);expect(canvas.captured.size).toBe(0);
    canvas.width=400;canvas.height=225;canvas.pointer('pointerdown',{clientX:50,clientY:25});canvas.pointer('pointermove',{clientX:90,clientY:47.5});
    expect(drag).toHaveBeenLastCalledWith(.1,.1);
  });
  it('rejects disabled, secondary and concurrent pointers and cancels when an overlay opens',()=>{
    const {canvas,drag,controller}=input();canvas.pointer('pointerdown');canvas.pointer('pointermove',{clientX:50});expect(drag).not.toHaveBeenCalled();
    controller.setEnabled(true);canvas.pointer('pointerdown',{button:2});canvas.pointer('pointerdown',{isPrimary:false});expect(controller.dragging).toBe(false);
    canvas.pointer('pointerdown');canvas.pointer('pointerdown',{pointerId:2});canvas.pointer('pointermove',{pointerId:2,clientX:100});expect(drag).not.toHaveBeenCalled();
    controller.setEnabled(false);expect(controller.dragging).toBe(false);expect(canvas.captured.size).toBe(0);
    controller.setEnabled(true);canvas.pointer('pointermove',{clientX:100});expect(drag).not.toHaveBeenCalled();
  });
  it('ends lost/cancelled drags and limits double-click reset to the enabled canvas',()=>{
    const {canvas,drag,reset,controller}=input();controller.setEnabled(true);canvas.pointer('pointerdown');canvas.pointer('pointercancel');canvas.pointer('pointermove',{clientX:100});expect(drag).not.toHaveBeenCalled();
    canvas.pointer('pointerdown');canvas.pointer('lostpointercapture');expect(controller.dragging).toBe(false);
    canvas.pointer('dblclick');expect(reset).toHaveBeenCalledTimes(1);controller.setEnabled(false);canvas.pointer('dblclick');expect(reset).toHaveBeenCalledTimes(1);
    controller.setEnabled(true);controller.dispose();canvas.pointer('pointerdown');canvas.pointer('pointermove',{clientX:100});canvas.pointer('dblclick');expect(drag).not.toHaveBeenCalled();expect(reset).toHaveBeenCalledTimes(1);
  });
});
