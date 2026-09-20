import { STATIONS, ROUTE_LENGTH } from '../data/route';
import type { TrainState } from './simulation';
import { AnnouncementCues } from './announcements';

export class TrainAudio{
  private context?:AudioContext;private oscillator?:OscillatorNode;private gain?:GainNode;private noiseGain?:GainNode;
  private master?:GainNode;private loops:{station:number;gain:GainNode;exterior:boolean}[]=[];
  private loading?:Promise<void>;
  private ready=false;private running=false;private clockChange?:Promise<void>;private clockFailed=false;
  private parliament?:AudioBuffer;private parliamentSource?:AudioBufferSourceNode;private parliamentPlayed=false;private previousTime=0;
  private effectNoise?:AudioBuffer;
  private mechanicalState?:TrainState;
  private previousMechanical?:Pick<TrainState,'phase'|'time'|'doors'|'controller'|'speed'|'emergency'>;
  private movedSinceStop=false;
  private mechanicalSources=new Map<AudioBufferSourceNode,()=>void>();
  readonly announcements=new AnnouncementCues();
  enabled=false;
  private async initialise(){
    const ctx=this.context=new AudioContext();
    const master=this.master=ctx.createGain();master.gain.value=0;master.connect(ctx.destination);
    this.gain=ctx.createGain();this.gain.gain.value=0;this.gain.connect(this.master);
    this.oscillator=ctx.createOscillator();this.oscillator.type='sine';this.oscillator.connect(this.gain);this.oscillator.start();
    const buffer=ctx.createBuffer(1,ctx.sampleRate*2,ctx.sampleRate),data=buffer.getChannelData(0);
    let last=0;for(let i=0;i<data.length;i++){last=(last+Math.random()*.04-.02)/1.02;data[i]=last*3;}
    const noise=ctx.createBufferSource();noise.buffer=buffer;noise.loop=true;this.noiseGain=ctx.createGain();this.noiseGain.gain.value=0;noise.connect(this.noiseGain);this.noiseGain.connect(this.master);noise.start();
    // Original broad-band air/mechanical excitation, separate from field recordings.
    this.effectNoise=ctx.createBuffer(1,ctx.sampleRate,ctx.sampleRate);
    const air=this.effectNoise.getChannelData(0);let seed=0x4d5245;
    for(let i=0;i<air.length;i++){seed=(Math.imul(seed,1664525)+1013904223)>>>0;air[i]=seed/0x80000000-1;}
    await Promise.all([
      {file:'southern-cross-ambience.mp3',station:1,exterior:false},
      {file:'flinders-exterior-ambience.mp3',station:0,exterior:true},
    ].map(async entry=>{
      const response=await fetch(`/audio/${entry.file}`);if(!response.ok)throw new Error('Station recording could not be loaded.');
      const sound=await ctx.decodeAudioData(await response.arrayBuffer()),source=ctx.createBufferSource(),gain=ctx.createGain(),filter=ctx.createBiquadFilter();
      if(this.context!==ctx)throw new Error('Audio initialization was superseded.');
      source.buffer=sound;source.loop=true;gain.gain.value=0;
      filter.type='lowpass';filter.frequency.value=entry.exterior?1600:4500;
      source.connect(filter);filter.connect(gain);gain.connect(master);source.start();this.loops.push({station:entry.station,gain,exterior:entry.exterior});
    }));
    const departure=await fetch('/audio/parliament-departure.mp3');if(!departure.ok)throw new Error('Parliament recording could not be loaded.');
    this.parliament=await ctx.decodeAudioData(await departure.arrayBuffer());
    this.ready=true;
  }
  async toggle(){
    this.clockFailed=false;
    if(!this.loading)this.loading=this.initialise().catch(async error=>{
      const ctx=this.context;this.context=undefined;this.ready=false;this.enabled=false;
      this.parliamentSource?.stop();this.parliamentSource=undefined;this.parliament=undefined;this.parliamentPlayed=false;
      this.clearMechanical();this.effectNoise=undefined;
      this.loops=[];this.oscillator=undefined;this.master=undefined;this.gain=undefined;this.noiseGain=undefined;
      this.clockChange=undefined;
      try{if(ctx&&ctx.state!=='closed')await ctx.close();}finally{this.loading=undefined;}
      throw error;
    });
    // Unlock immediately in the user's click gesture while recording fetches run.
    await Promise.all([this.enabled?undefined:this.context?.resume(),this.loading]);this.enabled=!this.enabled;this.syncClock();return this.enabled;
  }
  private syncClock(){
    const ctx=this.context;if(!ctx||!this.ready||this.clockChange||this.clockFailed)return;
    const play=this.enabled&&this.running;
    if((play&&ctx.state==='running')||(!play&&ctx.state==='suspended')||ctx.state==='closed')return;
    // Suspending freezes every source's playback clock, including a partially
    // played Parliament departure. Muting must not consume it in the background.
    this.clockChange=(play?ctx.resume():ctx.suspend()).catch(error=>{
      this.enabled=false;this.clockFailed=true;console.warn('Audio playback could not change state',error);
    }).finally(()=>{this.clockChange=undefined;if(this.context===ctx)this.syncClock();});
  }
  update(state:TrainState,cabView=true){
    const cue=this.announcements.update(state);
    const reset=state.time<this.previousTime||state.phase==='ready';
    if(reset)this.parliamentPlayed=false;
    if(this.parliamentSource&&(reset||Math.abs(state.distance-STATIONS[4].distance)>230)){
      this.parliamentSource.stop();this.parliamentSource=undefined;
    }
    this.previousTime=state.time;
    this.updateMechanical(state,cabView);
    this.running=state.phase==='driving';this.syncClock();
    if(!this.context)return;const time=this.context.currentTime,running=this.running;
    this.master!.gain.setTargetAtTime(this.enabled&&running?1:0,time,.12);
    this.oscillator!.frequency.setTargetAtTime(40+state.speed*8,time,.2);
    this.gain!.gain.setTargetAtTime(.012+Math.min(.025,state.speed*.002),time,.15);
    this.noiseGain!.gain.setTargetAtTime(Math.min(.14,state.speed*.009),time,.15);
    for(const loop of this.loops){
      let distance=Math.abs(state.distance-STATIONS[loop.station].distance);
      if(loop.station===0)distance=Math.min(distance,Math.abs(state.distance-(ROUTE_LENGTH-60)));
      const proximity=Math.max(0,1-distance/230),cabFactor=cabView?(state.doors?.55:.23):1;
      loop.gain.gain.setTargetAtTime(proximity*proximity*cabFactor*(loop.exterior?.4:.7),time,.5);
    }
    // An actual neighbouring Xtrapolis departure at Parliament, played once.
    // It is historic station ambience, never the player's HCMT traction sound.
    if(this.enabled&&running&&this.parliament&&!this.parliamentPlayed&&Math.abs(state.distance-STATIONS[4].distance)<130){
      const source=this.context.createBufferSource(),gain=this.context.createGain();source.buffer=this.parliament;
      gain.gain.value=cabView?.13:.4;source.connect(gain);gain.connect(this.master!);source.start();this.parliamentSource=source;
      source.onended=()=>{source.disconnect();gain.disconnect();if(this.parliamentSource===source)this.parliamentSource=undefined;};this.parliamentPlayed=true;
    }
    if(cue&&this.enabled)this.chime();
  }
  private updateMechanical(state:TrainState,cabView:boolean){
    const previous=this.previousMechanical;
    const baseline=!previous||this.mechanicalState!==state||state.time<previous.time||state.phase==='ready'||state.phase==='complete';
    this.mechanicalState=state;
    this.previousMechanical={phase:state.phase,time:state.time,doors:state.doors,controller:state.controller,speed:state.speed,emergency:state.emergency};
    if(baseline){this.clearMechanical();this.movedSinceStop=state.speed>.5;return;}
    if(state.speed>.5)this.movedSinceStop=true;
    const stopped=this.movedSinceStop&&state.speed<=.05;
    if(stopped)this.movedSinceStop=false;
    // Always consume transitions, including while muted/loading. Enabling sound
    // cannot replay a door/controller change that happened earlier.
    if(!this.enabled||!this.ready||state.phase!=='driving'||previous.phase!=='driving')return;
    const doorChanged=previous.doors!==state.doors;
    if(doorChanged){
      const level=cabView?.036:.068;
      // A short pressure release followed by the mechanical end-stop. Both are
      // original filtered noise, not a recording or reproduction of an HCMT door.
      this.airEffect(state.doors?.52:.62,level,state.doors?1550:900,state.doors?850:1450,.04);
      this.airEffect(.055,level*.62,260,180,.004,state.doors?.43:.56);
    }
    if(previous.controller!==state.controller&&!doorChanged){
      this.airEffect(.032,cabView?.030:.006,2100,1250,.002);
      if(!state.doors&&previous.controller<0&&state.controller>=0&&!state.emergency){
        this.airEffect(.30,cabView?.027:.055,1900,900,.018);
      }
    }
    if(stopped&&!doorChanged&&!state.doors&&(state.controller<0||state.emergency||previous.controller<0||previous.emergency)){
      this.airEffect(.44,cabView?.032:.068,1250,650,.035);
    }
  }
  private airEffect(duration:number,level:number,frequency:number,endFrequency:number,attack:number,delay=0){
    const ctx=this.context;if(!ctx||!this.master||!this.effectNoise)return;
    const source=ctx.createBufferSource(),filter=ctx.createBiquadFilter(),gain=ctx.createGain();
    source.buffer=this.effectNoise;filter.type='bandpass';filter.Q.value=.72;
    const start=ctx.currentTime+delay,end=start+duration;
    filter.frequency.setValueAtTime(frequency,start);filter.frequency.exponentialRampToValueAtTime(endFrequency,end);
    gain.gain.setValueAtTime(.0001,start);gain.gain.exponentialRampToValueAtTime(level,start+attack);gain.gain.exponentialRampToValueAtTime(.0001,end);
    source.connect(filter);filter.connect(gain);gain.connect(this.master);
    const cleanup=()=>{if(!this.mechanicalSources.delete(source))return;source.disconnect();filter.disconnect();gain.disconnect();};
    this.mechanicalSources.set(source,cleanup);source.onended=cleanup;
    // Scheduling is entirely on the AudioContext clock, which syncClock freezes
    // on pause/mute. No wall-clock timers consume a paused effect in the background.
    source.start(start);source.stop(end+.012);
  }
  private clearMechanical(){
    for(const [source,cleanup]of this.mechanicalSources){source.stop();cleanup();}
  }
  private chime(){
    const ctx=this.context;if(!ctx)return;
    // Original two-note cue. This is not sampled Metro announcement branding.
    for(const [index,f] of [660,523.25].entries()){
      const osc=ctx.createOscillator(),gain=ctx.createGain(),start=ctx.currentTime+index*.2;
      osc.frequency.value=f;gain.gain.setValueAtTime(.0001,start);gain.gain.exponentialRampToValueAtTime(.028,start+.025);gain.gain.exponentialRampToValueAtTime(.0001,start+.7);
      osc.connect(gain);gain.connect(this.master!);osc.start(start);osc.stop(start+.72);osc.onended=()=>{osc.disconnect();gain.disconnect();};
    }
  }
  horn(){
    if(!this.context||!this.enabled||!this.running)return;
    for(const f of [311,370]){const osc=this.context.createOscillator(),gain=this.context.createGain();osc.type='triangle';osc.frequency.value=f;gain.gain.value=.045;osc.connect(gain);gain.connect(this.master!);osc.start();gain.gain.exponentialRampToValueAtTime(.001,this.context.currentTime+.65);osc.stop(this.context.currentTime+.7);osc.onended=()=>{osc.disconnect();gain.disconnect();};}
  }
}
