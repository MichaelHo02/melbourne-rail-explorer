import { STATIONS } from '../data/route';
import type { TrainState } from './simulation';

/** Player-service captions. Field-recorded PA remains location ambience and is
 * never represented as a live announcement for this fictional training train. */
export class AnnouncementCues {
  text='';until=0;
  private previousTime=-1;private previousDoors=false;private previousStation=-1;
  private service?:TrainState;private previousPhase?:TrainState['phase'];
  private completionUntil=0;private kind:'arrival'|'departure'|'approach'|'termination'|null=null;
  private approached=new Set<number>();private arrived=new Set<number>();
  reset(){this.text='';this.until=0;this.previousTime=-1;this.previousDoors=false;this.previousStation=-1;this.previousPhase=undefined;this.service=undefined;this.completionUntil=0;this.kind=null;this.approached.clear();this.arrived.clear();}
  update(s:TrainState,displaySeconds=performance.now()/1000):string|null{
    const replaced=!!this.service&&this.service!==s;
    if(replaced||s.time<this.previousTime)this.reset();
    if(s.phase==='ready'){this.reset();this.service=s;return null;}
    const first=!this.service;this.service=s;
    // restore() replaces state and starts paused, even for an equal-time save.
    // Establish its current events silently instead of replaying old PA cues.
    if(first&&s.phase==='paused'){
      if(s.doors)this.arrived.add(s.nextStation);
      const stop=STATIONS[s.nextStation];
      if(stop&&stop.distance-s.distance<260)this.approached.add(s.nextStation);
      this.remember(s);return null;
    }
    if(s.phase==='paused'){this.previousPhase=s.phase;return null;}
    if(s.phase==='complete'){
      const servedFinal=this.previousPhase!=='complete'&&this.previousDoors&&!s.doors&&this.previousStation===STATIONS.length-1&&s.nextStation===STATIONS.length&&s.results.at(-1)?.outcome==='served';
      if(servedFinal){
        this.text='This service terminates at Flinders Street.';this.kind='termination';this.completionUntil=displaySeconds+7;
      }else if(this.kind!=='termination'||displaySeconds>=this.completionUntil){this.text='';this.kind=null;}
      this.remember(s);return servedFinal?this.text:null;
    }
    const station=STATIONS[s.nextStation];let cue:string|null=null;
    if(s.nextStation!==this.previousStation||(!s.doors&&this.kind==='approach'&&station&&s.distance>station.distance+8)){this.text='';this.kind=null;}
    if(station&&s.doors&&!this.arrived.has(s.nextStation)){
      cue=`${station.name}. Please mind the gap between the train and the platform.`;this.kind='arrival';this.arrived.add(s.nextStation);
    }else if(this.previousDoors&&!s.doors&&s.nextStation>this.previousStation){
      cue=station?`Doors closing. The next station is ${station.name}.`:null;this.kind='departure';
    }else if(station&&!s.doors&&station.distance-s.distance>8&&station.distance-s.distance<260&&!this.approached.has(s.nextStation)){
      cue=`Now approaching ${station.name}.`;this.kind='approach';this.approached.add(s.nextStation);
    }
    if(cue){this.text=cue;this.until=s.time+7;}
    this.remember(s);
    if(s.time>this.until){this.text='';this.kind=null;}return cue;
  }
  private remember(s:TrainState){this.previousDoors=s.doors;this.previousStation=s.nextStation;this.previousTime=s.time;this.previousPhase=s.phase;}
}
