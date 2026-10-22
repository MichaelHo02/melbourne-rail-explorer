import schedule from '../data/traffic-schedule.json';
import { project, positionAt, ROUTE_LENGTH, type Vec3 } from '../data/route';

export interface TrafficCall {
  stopId:string;station:string;stationId:string;platform:string;
  arrival:number;departure:number;distance:number;sequence:number;
}
export interface TrafficTrip {
  id:string;tripId:string;routeId:string;routeName:string;headsign:string;directionId:number;
  serviceId:string;shapeId:string;calls:TrafficCall[];
}
export interface TrafficSample {
  id:string;tripId:string;routeId:string;routeName:string;headsign:string;directionId:number;
  position:Vec3;heading:Vec3;speed:number;shapeDistance:number;sourcePlatform:string;
  fromStation:string;toStation:string;stopped:boolean;
}
export const TRAFFIC_METADATA=schedule.metadata;
export const TRAFFIC_TRIPS:readonly TrafficTrip[]=schedule.trips;
const shapes=schedule.shapes as Record<string,number[][]>;
const tripsById=new Map(TRAFFIC_TRIPS.map(trip=>[trip.id,trip]));
const verticalGuide=Array.from({length:Math.ceil(ROUTE_LENGTH/10)+1},(_,i)=>positionAt(Math.min(i*10,ROUTE_LENGTH)));
const prepared=new Map<string,{distance:number;point:Vec3}[]>();

/** Official horizontal shapes with the game's authored vertical alignment.
 * Cached per shape; no wall clock, network request or random state is involved. */
function shapePoints(id:string){
  const cached=prepared.get(id);if(cached)return cached;
  const points=(shapes[id]??[]).map(([lon,lat,distance])=>{
    const point=project(lon,lat);let closest=verticalGuide[0],best=Infinity;
    for(const candidate of verticalGuide){
      const d=(point.x-candidate.x)**2+(point.z-candidate.z)**2;
      if(d<best){closest=candidate;best=d;}
    }
    point.y=closest.y;return {distance,point};
  });
  prepared.set(id,points);return points;
}
function pointOnShape(id:string,distance:number):Vec3|null{
  const points=shapePoints(id);if(points.length<2||distance<points[0].distance||distance>points.at(-1)!.distance)return null;
  let lo=1,hi=points.length-1;
  while(lo<hi){const mid=(lo+hi)>>1;if(points[mid].distance<distance)lo=mid+1;else hi=mid;}
  const a=points[lo-1],b=points[lo],t=b.distance===a.distance?0:(distance-a.distance)/(b.distance-a.distance);
  return {x:a.point.x+(b.point.x-a.point.x)*t,y:a.point.y+(b.point.y-a.point.y)*t,z:a.point.z+(b.point.z-a.point.z)*t};
}

/** Timetable interpolation only: zero speed during the published arrival/departure
 * interval; no invented dwell where the source publishes equal times. */
export function scheduledProgress(calls:readonly TrafficCall[],seconds:number){
  if(!Number.isFinite(seconds)||!calls.length||seconds<calls[0].arrival||seconds>calls.at(-1)!.departure)return null;
  for(let i=0;i<calls.length;i++){
    const call=calls[i];
    if(seconds>=call.arrival&&seconds<=call.departure)return {distance:call.distance,speed:0,from:call,to:call,stopped:true};
    const next=calls[i+1];
    if(next&&seconds>call.departure&&seconds<next.arrival){
      const duration=next.arrival-call.departure,t=(seconds-call.departure)/duration;
      return {distance:call.distance+(next.distance-call.distance)*t,speed:(next.distance-call.distance)/duration,from:call,to:next,stopped:false};
    }
  }
  return null;
}

/** Samples one retained trip section. distanceBehind supports car placement along
 * the same source shape; it does not shift the train's scheduled time or track. */
export function sampleTrafficTrip(id:string,elapsedSeconds:number,distanceBehind=0):TrafficSample|null{
  if(!Number.isFinite(elapsedSeconds)||elapsedSeconds<0||!Number.isFinite(distanceBehind)||distanceBehind<0)return null;
  const trip=tripsById.get(id);if(!trip)return null;
  const progress=scheduledProgress(trip.calls,TRAFFIC_METADATA.startSeconds+elapsedSeconds);if(!progress)return null;
  const distance=progress.distance-distanceBehind,position=pointOnShape(trip.shapeId,distance);if(!position)return null;
  const before=pointOnShape(trip.shapeId,distance-1)??position,after=pointOnShape(trip.shapeId,distance+1)??position;
  const length=Math.hypot(after.x-before.x,after.y-before.y,after.z-before.z);if(length<1e-6)return null;
  return {id:trip.id,tripId:trip.tripId,routeId:trip.routeId,routeName:trip.routeName,headsign:trip.headsign,directionId:trip.directionId,
    position,heading:{x:(after.x-before.x)/length,y:(after.y-before.y)/length,z:(after.z-before.z)/length},
    speed:progress.speed,shapeDistance:distance,sourcePlatform:progress.stopped?progress.from.platform:progress.to.platform,
    fromStation:progress.from.station,toStation:progress.to.station,stopped:progress.stopped};
}

/** Pass Simulation.state.time so pause/resume/save restores the same traffic.
 * Returned trains are timetable replay, never a live vehicle feed. The renderer
 * owns adjacent-track offsets and visual culling, keeping the player isolated. */
export function sampleTraffic(elapsedSeconds:number):TrafficSample[]{
  if(!Number.isFinite(elapsedSeconds)||elapsedSeconds<0)return [];
  const now=TRAFFIC_METADATA.startSeconds+elapsedSeconds;
  return TRAFFIC_TRIPS.filter(trip=>now>=trip.calls[0].arrival&&now<=trip.calls.at(-1)!.departure)
    .map(trip=>sampleTrafficTrip(trip.id,elapsedSeconds)).filter((train):train is TrafficSample=>train!==null);
}
