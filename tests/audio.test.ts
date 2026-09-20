import {afterEach,describe,expect,it,vi} from 'vitest';
import {TrainAudio} from '../src/game/audio';
import {Simulation} from '../src/game/simulation';
import {STATIONS} from '../src/data/route';

class Node {
  gain={value:0,setTargetAtTime:vi.fn(),setValueAtTime:vi.fn(),exponentialRampToValueAtTime:vi.fn()};
  frequency={...this.gain};Q={...this.gain};connect=vi.fn();disconnect=vi.fn();start=vi.fn();stop=vi.fn();
  buffer:unknown;loop=false;onended?:()=>void;
}
class Buffer {data:Float32Array;constructor(length:number){this.data=new Float32Array(length);}getChannelData(){return this.data;}}
class Context {
  static instances:Context[]=[];state='suspended';currentTime=0;sampleRate=32;destination={};sources:Node[]=[];filters:Node[]=[];gains:Node[]=[];oscillators:Node[]=[];
  constructor(){Context.instances.push(this);}
  resume=vi.fn(async()=>{this.state='running';});suspend=vi.fn(async()=>{this.state='suspended';});close=vi.fn(async()=>{this.state='closed';});
  createGain(){const node=new Node();this.gains.push(node);return node;}createOscillator(){const node=new Node();this.oscillators.push(node);return node;}createBiquadFilter(){const node=new Node();this.filters.push(node);return node;}
  createBufferSource(){const source=new Node();this.sources.push(source);return source;}
  createBuffer(_channels:number,length:number){return new Buffer(length);}
  advance(seconds:number){if(this.state==='running')this.currentTime+=seconds;}
  async decodeAudioData(){return{};}
}
function setup(){Context.instances=[];vi.stubGlobal('AudioContext',Context);vi.stubGlobal('fetch',vi.fn(async()=>({ok:true,arrayBuffer:async()=>new ArrayBuffer(1)})));}
afterEach(()=>vi.unstubAllGlobals());

describe('audio lifecycle',()=>{
  it('closes failed initialization and permits a later successful Sound retry',async()=>{
    setup();vi.mocked(fetch).mockResolvedValueOnce({ok:false} as Response);
    const audio=new TrainAudio();await expect(audio.toggle()).rejects.toThrow('Station recording');
    expect(Context.instances[0].close).toHaveBeenCalledOnce();expect(audio.enabled).toBe(false);
    await expect(audio.toggle()).resolves.toBe(true);expect(Context.instances).toHaveLength(2);
    const sim=new Simulation();sim.start();audio.update(sim.state);await vi.waitFor(()=>expect(Context.instances[1].state).toBe('running'));
  });
  it('suspends playback on pause and mute without replacing the active Parliament one-shot',async()=>{
    setup();const audio=new TrainAudio(),sim=new Simulation();sim.start();sim.state.distance=STATIONS[4].distance;sim.state.doors=false;
    audio.update(sim.state);await audio.toggle();audio.update(sim.state);
    const ctx=Context.instances[0],departure=ctx.sources.at(-1)!;expect(departure.loop).toBe(false);expect(departure.start).toHaveBeenCalledOnce();
    sim.pause();audio.update(sim.state);await vi.waitFor(()=>expect(ctx.state).toBe('suspended'));
    expect(departure.stop).not.toHaveBeenCalled();
    sim.pause();audio.update(sim.state);await vi.waitFor(()=>expect(ctx.state).toBe('running'));
    expect(departure.start).toHaveBeenCalledOnce();
    await audio.toggle();await vi.waitFor(()=>expect(ctx.state).toBe('suspended'));
    await audio.toggle();audio.update(sim.state);await vi.waitFor(()=>expect(ctx.state).toBe('running'));
    expect(ctx.sources.at(-1)).toBe(departure);
    sim.state.distance=0;audio.update(sim.state);expect(departure.stop).toHaveBeenCalledOnce();
  });
  it('cancels old chime and horn nodes on an equal-time restore without replay',async()=>{
    setup();const sim=new Simulation();sim.start();const {audio,ctx}=await audible(sim);
    sim.toggleDoors();audio.update(sim.state);audio.horn();
    const tones=ctx.oscillators.slice(1);expect(tones).toHaveLength(4);
    expect(sim.restore(sim.snapshot())).toBe(true);audio.update(sim.state);
    for(const tone of tones){expect(tone.stop).toHaveBeenCalledTimes(2);expect(tone.disconnect).toHaveBeenCalledOnce();tone.onended?.();expect(tone.disconnect).toHaveBeenCalledOnce();}
    sim.pause();audio.update(sim.state);expect(ctx.oscillators).toHaveLength(5);
    sim.reset();sim.start();audio.update(sim.state);expect(ctx.oscillators).toHaveLength(5);
  });
  it('does not replay the Parliament recording on restoring within its trigger area',async()=>{
    setup();const sim=new Simulation();sim.loadScenario('parliament');const {audio,ctx}=await audible(sim);
    const departure=ctx.sources.at(-1)!;expect(departure.buffer).not.toBeInstanceOf(Buffer);const count=ctx.sources.length;
    expect(sim.restore(sim.snapshot())).toBe(true);audio.update(sim.state);expect(departure.stop).toHaveBeenCalledOnce();
    sim.pause();audio.update(sim.state);expect(ctx.sources).toHaveLength(count);
  });
  it('cleans active tones at final service completion without a suspended chime',async()=>{
    setup();const sim=new Simulation();sim.start();const {audio,ctx}=await audible(sim);
    for(let index=0;index<STATIONS.length;index++){
      if(index>0){sim.state.distance=STATIONS[index].distance;sim.toggleDoors();audio.update(sim.state);sim.step(8);audio.update(sim.state);}
      if(index===STATIONS.length-1){audio.horn();const tones=ctx.oscillators.length;sim.toggleDoors();audio.update(sim.state);expect(ctx.oscillators).toHaveLength(tones);expect(audio.announcements.text).toContain('terminates');}
      else{sim.toggleDoors();audio.update(sim.state);}
    }
    for(const tone of ctx.oscillators.slice(1))expect(tone.disconnect).toHaveBeenCalledOnce();
    await vi.waitFor(()=>expect(ctx.state).toBe('suspended'));
  });
  it('resumes through the real HUD callback without replaying an equal-time saved platform',async()=>{
    setup();
    const saved=new Simulation();saved.loadScenario('parliament');
    let actions:Record<string,()=>void>,frame:(now:number)=>void;
    const now=vi.spyOn(performance,'now').mockReturnValue(1000);
    const update=vi.spyOn(TrainAudio.prototype,'update');
    const render=vi.fn();
    // Keep the real application callback, simulation and audio lifecycle. Only
    // browser presentation is replaced, so ordering regressions in main.ts fail.
    vi.doMock('../src/ui/hud',()=>({HUD:class{
      constructor(_root:unknown,registered:Record<string,()=>void>){actions=registered;}
      cameraInputAllowed=true;closePanel(){}ready(){}loading(){}update(){}setAnnouncement(){}setSound(){}
    }}));
    vi.doMock('../src/render/renderer',()=>({GameRenderer:class{
      view='cab';render=render;setCameraInputEnabled(){}async loadCity(){}async startLoop(callback:(now:number)=>void){frame=callback;}
    }}));
    vi.stubGlobal('document',{querySelector:()=>({innerHTML:'',dataset:{},style:{setProperty:vi.fn()}}),addEventListener:vi.fn()});
    vi.stubGlobal('window',{addEventListener:vi.fn(),innerWidth:1280,innerHeight:720});vi.stubGlobal('location',{search:''});
    vi.stubGlobal('localStorage',{getItem:()=>JSON.stringify(saved.snapshot()),setItem:vi.fn()});
    try{
      await import('../src/main');await vi.waitFor(()=>expect(frame).toBeTypeOf('function'));
      frame!(1000);
      const audio=update.mock.contexts.at(-1)!;await audio.toggle();
      actions!.start();frame!(1000);actions!.doors();frame!(1000);actions!.horn();
      const ctx=Context.instances.at(-1)!,tones=ctx.oscillators.slice(1),toneCount=ctx.oscillators.length;
      expect(tones.length).toBeGreaterThan(0);
      actions!.resume();frame!(1000);
      expect(render.mock.calls.at(-1)![0].phase).toBe('driving');
      expect(audio.announcements.text).toBe('');expect(ctx.oscillators).toHaveLength(toneCount);
      // The actual Parliament recording is distinct from our Buffer-backed
      // mechanical sounds and must not restart after the restored baseline.
      expect(ctx.sources.filter(source=>!source.loop&&!(source.buffer instanceof Buffer))).toHaveLength(0);
      for(const tone of tones)expect(tone.disconnect).toHaveBeenCalledOnce();
      actions!.doors();frame!(1000);
      expect(audio.announcements.text).toContain('The next station is Flinders Street');
    }finally{
      now.mockRestore();update.mockRestore();vi.doUnmock('../src/ui/hud');vi.doUnmock('../src/render/renderer');
    }
  });
});

const mechanical=(ctx:Context)=>ctx.sources.filter(source=>!source.loop&&source.buffer instanceof Buffer);
async function audible(sim:Simulation){
  const audio=new TrainAudio();audio.update(sim.state);await audio.toggle();audio.update(sim.state);
  const ctx=Context.instances.at(-1)!;await vi.waitFor(()=>expect(ctx.state).toBe('running'));return{audio,ctx};
}
describe('original mechanical cues',()=>{
  it('sounds accepted door/controller changes once, never rejected actions or camera changes',async()=>{
    setup();const sim=new Simulation();sim.start();const {audio,ctx}=await audible(sim);
    expect(mechanical(ctx)).toHaveLength(0);
    expect(sim.toggleDoors()).toBe(true);audio.update(sim.state);
    expect(mechanical(ctx)).toHaveLength(2);
    sim.setController(2);audio.update(sim.state);expect(mechanical(ctx)).toHaveLength(3);
    for(let i=0;i<6;i++)audio.update(sim.state,i%2===0);
    expect(mechanical(ctx)).toHaveLength(3);
    sim.state.speed=2;expect(sim.toggleDoors()).toBe(false);audio.update(sim.state);
    expect(mechanical(ctx)).toHaveLength(3);
    sim.state.distance=STATIONS[1].distance;sim.state.speed=0;sim.setController(-2);audio.update(sim.state);
    const before=mechanical(ctx).length;expect(sim.toggleDoors()).toBe(true);audio.update(sim.state);
    expect(mechanical(ctx)).toHaveLength(before+2);
    for(let i=0;i<6;i++)audio.update(sim.state);
    expect(mechanical(ctx)).toHaveLength(before+2);
  });
  it('baselines initial/restored scenes and consumes muted transitions without replay',async()=>{
    setup();const sim=new Simulation();sim.loadScenario('approach');sim.setController(-2);
    const audio=new TrainAudio();await audio.toggle();audio.update(sim.state);const ctx=Context.instances[0];
    expect(mechanical(ctx)).toHaveLength(0);
    const save=sim.snapshot();save.controller=-4;save.speed=1;save.time=90;
    expect(sim.restore(save)).toBe(true);audio.update(sim.state);sim.pause();audio.update(sim.state);
    expect(mechanical(ctx)).toHaveLength(0);
    await audio.toggle();sim.setController(0);audio.update(sim.state);
    await audio.toggle();audio.update(sim.state);
    expect(mechanical(ctx)).toHaveLength(0);
    sim.setController(1);audio.update(sim.state);expect(mechanical(ctx)).toHaveLength(1);
  });
  it('latches a braking stop and emits one pressure release when the brake is released',async()=>{
    setup();const sim=new Simulation();sim.loadScenario('viaduct');sim.state.speed=.7;sim.setController(-2);
    const {audio,ctx}=await audible(sim);
    for(let i=0;i<300&&sim.state.speed>0;i++){sim.step(1/60);audio.update(sim.state);}
    expect(sim.state.speed).toBe(0);expect(mechanical(ctx)).toHaveLength(1);
    for(let i=0;i<10;i++)audio.update(sim.state);
    expect(mechanical(ctx)).toHaveLength(1);
    sim.setController(0);audio.update(sim.state);expect(mechanical(ctx)).toHaveLength(3);
    sim.setController(1);audio.update(sim.state);expect(mechanical(ctx)).toHaveLength(4);
    audio.update(sim.state);expect(mechanical(ctx)).toHaveLength(4);
  });
  it('schedules on the context clock, freezes active cues on pause/mute and cleans ended/cancelled nodes',async()=>{
    setup();const sim=new Simulation();sim.start();const {audio,ctx}=await audible(sim);ctx.currentTime=12;
    sim.toggleDoors();audio.update(sim.state);const effects=mechanical(ctx);expect(effects).toHaveLength(2);
    expect(effects[0].start).toHaveBeenCalledWith(12);expect(effects[1].start).toHaveBeenCalledWith(12.56);
    const stopAt=effects[0].stop.mock.calls[0][0];expect(stopAt).toBeGreaterThan(12);
    sim.pause();audio.update(sim.state);await vi.waitFor(()=>expect(ctx.state).toBe('suspended'));
    ctx.advance(40);expect(ctx.currentTime).toBe(12);expect(effects[0].stop).toHaveBeenCalledOnce();
    sim.pause();audio.update(sim.state);await vi.waitFor(()=>expect(ctx.state).toBe('running'));
    await audio.toggle();await vi.waitFor(()=>expect(ctx.state).toBe('suspended'));
    ctx.advance(40);expect(ctx.currentTime).toBe(12);
    await audio.toggle();audio.update(sim.state);expect(mechanical(ctx)).toHaveLength(2);
    expect(effects[0].start).toHaveBeenCalledOnce();expect(effects[0].stop).toHaveBeenCalledWith(stopAt);
    const filter=effects[0].connect.mock.calls[0][0] as Node,gain=filter.connect.mock.calls[0][0] as Node;
    effects[0].onended?.();expect(effects[0].disconnect).toHaveBeenCalledOnce();expect(filter.disconnect).toHaveBeenCalledOnce();expect(gain.disconnect).toHaveBeenCalledOnce();
    sim.reset();sim.start();audio.update(sim.state);expect(effects[1].stop).toHaveBeenCalledTimes(2);expect(effects[1].disconnect).toHaveBeenCalledOnce();
    effects[1].onended?.();expect(effects[1].disconnect).toHaveBeenCalledOnce();
    expect(mechanical(ctx)).toHaveLength(2);
  });
});
