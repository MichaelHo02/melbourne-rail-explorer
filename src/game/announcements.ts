import { STATIONS } from '../data/route';
import type { TrainState } from './simulation';

/** Player-service captions. Field-recorded PA remains location ambience and is
 * never represented as a live announcement for this fictional training train. */
export class AnnouncementCues {
  text='';until=0;
  private previousTime=-1;private previousDoors=false;private previousStation=-1;
  private approached=new Set<number>();private arrived=new Set<number>();
  reset(){this.text='';this.until=0;this.previousTime=-1;this.previousDoors=false;this.previousStation=-1;this.approached.clear();this.arrived.clear();}
  update(s:TrainState):string|null{
    if(s.time<this.previousTime)this.reset();
    if(s.phase==='ready'){this.reset();return null;}
    if(s.phase!=='driving')return null;
    const station=STATIONS[s.nextStation];let cue:string|null=null;
    if(station&&s.doors&&!this.arrived.has(s.nextStation)){
      cue=`${station.name}. Please mind the gap between the train and the platform.`;this.arrived.add(s.nextStation);
    }else if(this.previousDoors&&!s.doors&&s.nextStation>this.previousStation){
      cue=station?`Doors closing. The next station is ${station.name}.`:'This service terminates at Flinders Street.';
    }else if(station&&!s.doors&&station.distance-s.distance>8&&station.distance-s.distance<260&&!this.approached.has(s.nextStation)){
      cue=`Now approaching ${station.name}.`;this.approached.add(s.nextStation);
    }
    if(cue){this.text=cue;this.until=s.time+7;}
    this.previousDoors=s.doors;this.previousStation=s.nextStation;this.previousTime=s.time;
    if(s.time>this.until)this.text='';return cue;
  }
}
