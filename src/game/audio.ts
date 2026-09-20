import { STATIONS, ROUTE_LENGTH } from '../data/route';
import type { TrainState } from './simulation';
import { AnnouncementCues } from './announcements';

export class TrainAudio{
  private context?:AudioContext;private oscillator?:OscillatorNode;private gain?:GainNode;private noiseGain?:GainNode;
  private master?:GainNode;private loops:{station:number;gain:GainNode;exterior:boolean}[]=[];
  private loading?:Promise<void>;
  private ready=false;private running=false;private clockChange?:Promise<void>;private clockFailed=false;
  private parliament?:AudioBuffer;private parliamentSource?:AudioBufferSourceNode;private parliamentPlayed=false;private previousTime=0;
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
