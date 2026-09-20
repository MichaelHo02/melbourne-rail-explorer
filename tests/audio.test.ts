import {afterEach,describe,expect,it,vi} from 'vitest';
import {TrainAudio} from '../src/game/audio';
import {Simulation} from '../src/game/simulation';
import {STATIONS} from '../src/data/route';

class Node {
  gain={value:0,setTargetAtTime:vi.fn(),setValueAtTime:vi.fn(),exponentialRampToValueAtTime:vi.fn()};
  frequency={...this.gain};connect=vi.fn();disconnect=vi.fn();start=vi.fn();stop=vi.fn();
  buffer:unknown;loop=false;onended?:()=>void;
}
class Context {
  static instances:Context[]=[];state='suspended';currentTime=0;sampleRate=4;destination={};sources:Node[]=[];
  constructor(){Context.instances.push(this);}
  resume=vi.fn(async()=>{this.state='running';});suspend=vi.fn(async()=>{this.state='suspended';});close=vi.fn(async()=>{this.state='closed';});
  createGain(){return new Node();}createOscillator(){return new Node();}createBiquadFilter(){return new Node();}
  createBufferSource(){const source=new Node();this.sources.push(source);return source;}
  createBuffer(){return{getChannelData:()=>new Float32Array(8)};}
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
});
