export const CBD=[144.949,-37.825,144.981,-37.805] as const;
export const PARKING_SOURCE='https://data.melbourne.vic.gov.au/explore/dataset/on-street-parking-bay-sensors/information/';
export interface ParkingBay {id:string;lon:number;lat:number;occupied:boolean|null;updated:number;statusChanged:number}
export function normalizeParking(records:unknown):ParkingBay[]{
  if(!Array.isArray(records))throw new Error('Parking feed is not an array');
  const unique=new Map<string,ParkingBay>();
  for(const record of records){
    if(!record||typeof record!=='object')continue;
    const r=record as Record<string,any>,lon=Number(r.location?.lon),lat=Number(r.location?.lat);
    if(!Number.isFinite(lon)||!Number.isFinite(lat)||lon<CBD[0]||lon>CBD[2]||lat<CBD[1]||lat>CBD[3]||r.kerbsideid==null)continue;
    const status=String(r.status_description).toLowerCase();
    const bay={id:String(r.kerbsideid),lon,lat,occupied:status==='present'?true:status==='unoccupied'?false:null,updated:Date.parse(r.lastupdated),statusChanged:Date.parse(r.status_timestamp)};
    if(!unique.has(bay.id)||bay.updated>unique.get(bay.id)!.updated)unique.set(bay.id,bay);
  }
  return [...unique.values()];
}
export function freshBay(bay:ParkingBay,now=Date.now()){return Number.isFinite(bay.updated)&&bay.updated<=now+60000&&now-bay.updated<15*60*1000&&bay.occupied!==null;}
export function parkingSummary(bays:ParkingBay[],now=Date.now()){
  const fresh=bays.filter(b=>freshBay(b,now)),occupied=fresh.filter(b=>b.occupied).length;
  return {fresh:fresh.length,occupied,vacant:fresh.length-occupied,stale:bays.length-fresh.length,ratio:fresh.length?occupied/fresh.length:null};
}
/** A prior, not a measured flow: parking pressure weakly increases circulation.
 * Melbourne weekday peaks are authored, not calibrated telemetry predictions. */
export function trafficDemand(occupancy:number|null,melbourneHour:number,weekday:boolean){
  const peak=weekday&&(melbourneHour>=7&&melbourneHour<9||melbourneHour>=16&&melbourneHour<19);
  return Math.max(.15,Math.min(1,.34+(peak?.2:0)+(occupancy===null?0:(occupancy-.5)*.25)));
}
export function signalGreen(time:number,node:number,axis:'east-west'|'north-south'){
  const phase=((time+node%23)%80+80)%80;
  return axis==='east-west'?phase<34:phase>=40&&phase<74;
}
