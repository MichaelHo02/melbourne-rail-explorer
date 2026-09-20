import {describe,it,expect,vi} from 'vitest';
import {PerspectiveCamera,Vector3} from 'three/webgpu';
import {CameraLook,CAB_YAW_LIMIT,cabCameraPose,doorCheckCameraPose,gameplayCameraView,developmentInspectionView,inspectionLookTarget} from '../src/render/camera-look';
import {CameraDragInput} from '../src/render/camera-input';
import {positionAt,STATIONS} from '../src/data/route';
import {Simulation,type TrainState} from '../src/game/simulation';
import {platformPosition} from '../src/render/passenger-motion';
import {CAB_TO_CAR_CENTRE} from '../src/render/train-layout';

describe('cab head look',()=>{
  it('keeps head turns within seated limits and recentres without changing simulation state',()=>{
    const sim=new Simulation(),before=sim.snapshot(),look=new CameraLook();look.drag(5,-5);
    expect(look.cab).toEqual({yaw:CAB_YAW_LIMIT,pitch:.55});
    look.reset();expect(look.cab).toEqual({yaw:0,pitch:0});
    look.drag(NaN,1);expect(look.cab).toEqual({yaw:0,pitch:0});expect(sim.snapshot()).toEqual(before);
  });
  it('turns from the same seated eye while preserving route grade and follow position',()=>{
    const distance=3300,straight=cabCameraPose(distance,{yaw:0,pitch:0}),turned=cabCameraPose(distance,{yaw:.7,pitch:.2});
    expect(turned.position).toEqual(straight.position);expect(turned.target).not.toEqual(straight.target);
    const p=positionAt(distance);expect(straight.position).toEqual({x:p.x,y:p.y+2.85,z:p.z});
    const next=cabCameraPose(distance+30,{yaw:.7,pitch:.2});expect(next.position).not.toEqual(turned.position);
    expect(Math.hypot(turned.target.x-turned.position.x,turned.target.y-turned.position.y,turned.target.z-turned.position.z)).toBeCloseTo(35);
  });
});

describe('automatic platform door check',()=>{
  it('follows accepted door, dwell and pause transitions and returns to cab before departure',()=>{
    const sim=new Simulation();sim.loadScenario('platform');
    expect(gameplayCameraView(sim.state)).toBe('cab');
    expect(sim.toggleDoors()).toBe(true);expect(gameplayCameraView(sim.state)).toBe('door-check');
    expect(sim.toggleDoors()).toBe(false);expect(gameplayCameraView(sim.state)).toBe('door-check');
    sim.pause();expect(gameplayCameraView(sim.state)).toBe('door-check');
    sim.step(20);expect(sim.state.dwell).toBe(0);expect(sim.toggleDoors()).toBe(false);
    sim.pause();sim.step(8);expect(gameplayCameraView(sim.state)).toBe('door-check');
    expect(sim.toggleDoors()).toBe(true);expect(sim.state.speed).toBe(0);expect(gameplayCameraView(sim.state)).toBe('cab');
    sim.setController(2);sim.step(.1);expect(sim.state.speed).toBeGreaterThan(0);expect(gameplayCameraView(sim.state)).toBe('cab');
  });
  it('shows the same fixed feed for an open-door paused save and resumed service',()=>{
    const sim=new Simulation();sim.loadScenario('parliament');sim.state.dwell=3;
    const pose=doorCheckCameraPose(sim.state),look=new CameraLook();look.drag(.2,-.1);const head={...look.cab};
    expect(sim.restore(sim.snapshot())).toBe(true);expect(gameplayCameraView(sim.state)).toBe('door-check');
    expect(doorCheckCameraPose(sim.state)).toEqual(pose);
    sim.pause();sim.step(5);expect(doorCheckCameraPose(sim.state)).toEqual(pose);sim.toggleDoors();
    expect(gameplayCameraView(sim.state)).toBe('cab');expect(look.cab).toEqual(head);
  });
  it.each([
    {phase:'ready'},{phase:'complete'},{doors:false},{speed:.001},{speed:.05},{speed:5},
    {distance:STATIONS[0].distance+8.01},{distance:STATIONS[0].distance-8.01},
    {nextStation:STATIONS.length},{nextStation:-1},{dwell:-1},{dwell:9},{dwell:NaN},
  ] as Partial<TrainState>[])('never offers a feed for an ineligible state: %j',change=>{
    const sim=new Simulation();sim.start();Object.assign(sim.state,change);expect(gameplayCameraView(sim.state)).toBe('cab');
  });
  it('opens at the simulation stop threshold after door release normalizes the speed to zero',()=>{
    const sim=new Simulation();sim.loadScenario('platform');sim.state.speed=.05;
    expect(sim.toggleDoors()).toBe(true);expect(sim.state.speed).toBe(0);expect(gameplayCameraView(sim.state)).toBe('door-check');
  });
  it('frames the nearest boarding doorway above the desk on the correct platform side at every stop',()=>{
    for(const [index,station] of STATIONS.entries())for(const offset of [-8,0,8]){
      const sim=new Simulation();Object.assign(sim.state,{phase:'driving',distance:station.distance+offset,nextStation:index,doors:true,dwell:0});
      expect(gameplayCameraView(sim.state)).toBe('door-check');
      const pose=doorCheckCameraPose(sim.state),anchor=platformPosition(index,68+offset,0),edge=platformPosition(index,68+offset,1);
      expect((pose.position.x-anchor.x)*(edge.x-anchor.x)+(pose.position.z-anchor.z)*(edge.z-anchor.z)).toBeCloseTo(4.8);
      const camera=new PerspectiveCamera(60,1280/720,.08,12000);camera.position.copy(pose.position);camera.lookAt(new Vector3().copy(pose.target));camera.updateMatrixWorld();
      // A first-car boarder starts in the platform lane and reaches a real door.
      const doorAlong=65-CAB_TO_CAR_CENTRE-.57+offset;
      for(const lateral of [1.5,3.3])for(const height of [0,1.7]){
        const p=platformPosition(index,doorAlong,lateral),screen=new Vector3(p.x,p.y+height,p.z).project(camera);
        expect(Math.abs(screen.x)).toBeLessThan(.85);expect(screen.y).toBeGreaterThan(-1/3);expect(screen.y).toBeLessThan(.6);expect(screen.z).toBeLessThan(1);
      }
    }
  });
});

describe('development inspection cameras',()=>{
  it('requires a development build, explicit scenario and known fixture',()=>{
    expect(developmentInspectionView('?scene=platform&view=boarding',true)).toBe('boarding');
    expect(developmentInspectionView('?scene=platform&view=boarding',false)).toBeNull();
    expect(developmentInspectionView('?view=boarding',true)).toBeNull();
    expect(developmentInspectionView('?scene=platform&view=outside',true)).toBeNull();
  });
  it('rotates authoring views in place and resets their original sightline',()=>{
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
