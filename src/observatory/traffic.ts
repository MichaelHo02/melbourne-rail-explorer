import roads from '../data/observatory-roads.json';
import {project} from '../data/route';
import {signalGreen,trafficDemand,type ParkingBay,freshBay} from './data';
export interface Lane {id:string;name:string;points:{x:number;z:number}[];lengths:number[];length:number;end:string;axis:'east-west'|'north-south';seed:number}
export interface Car {lane:Lane;s:number;speed:number;seed:number}
const lanes:Lane[]=[];
const key=(p:{x:number;z:number})=>`${Math.round(p.x/4)},${Math.round(p.z/4)}`;
for(const feature of roads.features){
  const props=feature.properties;
  if(String(props.vehicular_access)!=='1'||Number(props.class_code)>5)continue;
  const paths=feature.geometry.type==='LineString'?[feature.geometry.coordinates]:feature.geometry.coordinates;
  for(const path of paths){
    if(!Array.isArray(path[0]))continue;
    const points=(path as number[][]).map(p=>project(p[0],p[1]));
    const directions=props.direction_code==='B'?[points,points.slice().reverse()]:props.direction_code==='R'?[points.slice().reverse()]:[points];
    for(const line of directions){
      const lengths=[0];for(let i=1;i<line.length;i++)lengths.push(lengths[i-1]+Math.hypot(line[i].x-line[i-1].x,line[i].z-line[i-1].z));
      const length=lengths.at(-1)!;if(length<12)continue;
      const a=line[0],b=line.at(-1)!,seed=Number(props.ufi)||lanes.length;
      lanes.push({id:`${props.ufi}:${lanes.length}`,name:props.ezi_road_name??'Unnamed road',points:line,lengths,length,end:key(b),axis:Math.abs(b.x-a.x)>Math.abs(b.z-a.z)?'east-west':'north-south',seed});
    }
  }
}
export function lanePose(lane:Lane,s:number){
  s=Math.max(0,Math.min(s,lane.length));let i=1;while(i<lane.lengths.length-1&&lane.lengths[i]<s)i++;
  const a=lane.points[i-1],b=lane.points[i],length=lane.lengths[i]-lane.lengths[i-1],t=length?(s-lane.lengths[i-1])/length:0;
  const dx=b.x-a.x,dz=b.z-a.z,mag=Math.hypot(dx,dz)||1;
  // Left-hand lane offset and width are authored, not surveyed lane markings.
  return {x:a.x+dx*t+dz/mag*2,z:a.z+dz*t-dx/mag*2,angle:Math.atan2(dx,dz)};
}
export class RoadTraffic {
  cars:Car[]=[];demand=.4;parkingInfluence=0;
  private exits=new Map<string,Lane[]>();
  private pressure=new Map<string,number>();
  constructor(){
    for(const lane of lanes){const k=key(lane.points[0]),list=this.exits.get(k)??[];list.push(lane);this.exits.set(k,list);}
    // Stable sampling avoids flickering vehicles when observations refresh.
    for(const lane of lanes)if(lane.length>50&&this.cars.length<650){
      const count=Math.min(5,Math.floor(lane.length/45));
      for(let i=0;i<count&&this.cars.length<650;i++)this.cars.push({lane,s:lane.length*(i+.5)/count,speed:0,seed:lane.seed+i*31});
    }
  }
  observations(bays:ParkingBay[],now=Date.now()){
    this.pressure.clear();const counts=new Map<string,{n:number;occupied:number}>();
    for(const bay of bays){if(!freshBay(bay,now))continue;const p=project(bay.lon,bay.lat);let closest:Lane|undefined,best=60**2;
      for(const lane of lanes){const a=lane.points[0],b=lane.points.at(-1)!,dx=b.x-a.x,dz=b.z-a.z,t=Math.max(0,Math.min(1,((p.x-a.x)*dx+(p.z-a.z)*dz)/(dx*dx+dz*dz||1))),d=(p.x-a.x-dx*t)**2+(p.z-a.z-dz*t)**2;if(d<best){closest=lane;best=d;}}
      if(closest){const value=counts.get(closest.name)??{n:0,occupied:0};value.n++;value.occupied+=Number(bay.occupied);counts.set(closest.name,value);}
    }
    for(const [name,value] of counts)if(value.n>=3)this.pressure.set(name,value.occupied/value.n);
    this.parkingInfluence=this.pressure.size;
  }
  step(dt:number,time:number,hour:number,weekday:boolean){
    dt=Math.min(.05,dt);const total=this.pressure.size?[...this.pressure.values()].reduce((a,b)=>a+b,0)/this.pressure.size:null;
    this.demand=trafficDemand(total,hour,weekday);
    const queues=new Map<string,Car[]>();for(const car of this.cars){const q=queues.get(car.lane.id)??[];q.push(car);queues.set(car.lane.id,q);}
    for(const queue of queues.values()){
      queue.sort((a,b)=>b.s-a.s);let leader=Infinity;
      for(const car of queue){
        const local=this.pressure.get(car.lane.name)??.5,target=7.5+(1-this.demand)*4-local*1.2;
        const red=!signalGreen(time,car.lane.seed,car.lane.axis);
        const limit=Math.min(leader-7,red?car.lane.length-6:Infinity);
        const gap=limit-car.s;
        const desired=Math.min(target,Math.sqrt(Math.max(0,2*2.5*gap)));
        car.speed=Math.max(0,Math.min(desired,car.speed+dt*1.5));car.s=Math.min(car.s+car.speed*dt,Math.max(car.s,limit));leader=car.s;
        if(car.s>=car.lane.length){
          const options=(this.exits.get(car.lane.end)??[]).filter(l=>key(l.points.at(-1)!)!==key(car.lane.points[0]));
          const next=options[car.seed%Math.max(1,options.length)]??lanes[car.seed%lanes.length];
          if(this.cars.some(other=>other!==car&&other.lane===next&&other.s<10)){car.s=car.lane.length-.1;car.speed=0;}else{car.lane=next;car.s=0;}
        }
      }
    }
  }
}
