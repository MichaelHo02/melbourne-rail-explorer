export class TrainAudio{
  private context?:AudioContext;private oscillator?:OscillatorNode;private gain?:GainNode;private noiseGain?:GainNode;
  enabled=false;
  async toggle(){
    if(!this.context){
      this.context=new AudioContext();const ctx=this.context;
      this.gain=ctx.createGain();this.gain.gain.value=0;this.gain.connect(ctx.destination);
      this.oscillator=ctx.createOscillator();this.oscillator.type='sine';this.oscillator.connect(this.gain);this.oscillator.start();
      const buffer=ctx.createBuffer(1,ctx.sampleRate*2,ctx.sampleRate);const data=buffer.getChannelData(0);
      let last=0;for(let i=0;i<data.length;i++){last=(last+Math.random()*.04-.02)/1.02;data[i]=last*3;}
      const noise=ctx.createBufferSource();noise.buffer=buffer;noise.loop=true;this.noiseGain=ctx.createGain();this.noiseGain.gain.value=0;noise.connect(this.noiseGain);this.noiseGain.connect(ctx.destination);noise.start();
    }
    await this.context.resume();this.enabled=!this.enabled;return this.enabled;
  }
  update(speed:number,running:boolean){
    if(!this.context)return;const time=this.context.currentTime;
    this.oscillator!.frequency.setTargetAtTime(40+speed*8,time,.2);
    this.gain!.gain.setTargetAtTime(this.enabled&&running?.012+Math.min(.025,speed*.002):0,time,.15);
    this.noiseGain!.gain.setTargetAtTime(this.enabled&&running?Math.min(.17,speed*.01):0,time,.15);
  }
  horn(){
    if(!this.context||!this.enabled)return;
    for(const f of [311,370]){const osc=this.context.createOscillator(),gain=this.context.createGain();osc.type='triangle';osc.frequency.value=f;gain.gain.value=.045;osc.connect(gain);gain.connect(this.context.destination);osc.start();gain.gain.exponentialRampToValueAtTime(.001,this.context.currentTime+.65);osc.stop(this.context.currentTime+.7);osc.onended=()=>{osc.disconnect();gain.disconnect();};}
  }
}
