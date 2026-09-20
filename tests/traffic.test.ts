import { describe,expect,it } from 'vitest';
import {selectAdjacentTraffic} from '../src/render/traffic';
import {positionAt,tangentAt} from '../src/data/route';
import schedule from '../src/data/traffic-schedule.json';
import { scheduledProgress,sampleTraffic,sampleTrafficTrip,TRAFFIC_METADATA,TRAFFIC_TRIPS,type TrafficCall } from '../src/game/traffic';

const call=(arrival:number,departure:number,distance:number):TrafficCall=>({arrival,departure,distance,stopId:'test',station:'Test',stationId:'test',platform:'1',sequence:1});

describe('official timetable replay',()=>{
  it('uses the fixed Melbourne service date and only services active under its calendar',()=>{
    expect(TRAFFIC_METADATA.serviceDate).toBe('2026-09-19');
    expect(TRAFFIC_METADATA.timezone).toBe('Australia/Melbourne');
    expect(TRAFFIC_METADATA.startSeconds).toBe(6*3600+42*60);
    expect(TRAFFIC_METADATA.mode).toBe('timetable-replay');
    expect(TRAFFIC_METADATA.archiveSha256).toMatch(/^[a-f0-9]{64}$/);
    const date=TRAFFIC_METADATA.serviceDate.replaceAll('-','');
    for(const trip of TRAFFIC_TRIPS){
      const calendar=TRAFFIC_METADATA.calendar.find(c=>c.service_id===trip.serviceId);
      const exception=TRAFFIC_METADATA.calendarExceptions.find(c=>c.service_id===trip.serviceId&&c.date===date);
      expect(exception?.exception_type==='1'||(exception?.exception_type!=='2'&&calendar?.saturday==='1'&&calendar.start_date<=date&&calendar.end_date>=date)).toBe(true);
    }
  });

  it('honours published dwell and interpolates only between departure and next arrival, including after midnight',()=>{
    const calls=[call(86390,86410,100),call(86510,86530,1100)];
    expect(scheduledProgress(calls,86389)).toBeNull();
    expect(scheduledProgress(calls,86400)).toMatchObject({distance:100,speed:0,stopped:true});
    expect(scheduledProgress(calls,86460)).toMatchObject({distance:600,speed:10,stopped:false});
    expect(scheduledProgress(calls,86520)).toMatchObject({distance:1100,speed:0,stopped:true});
    expect(scheduledProgress(calls,86531)).toBeNull();
    expect(scheduledProgress(calls,NaN)).toBeNull();
  });

  it('retains real source calls and valid monotonic shape intervals, without crossing omitted suburban calls',()=>{
    const shapes=schedule.shapes as Record<string,number[][]>;
    const trip=TRAFFIC_TRIPS.find(t=>t.tripId==='02-CGB--67-T2-5201');
    expect(trip?.calls.map(c=>[c.stopId,c.platform,c.departure])).toEqual([['11216','5',20100],['22190','11',20340]]);
    expect(trip?.calls.at(-1)?.distance).toBe(1515.33);
    expect(TRAFFIC_TRIPS.length).toBeGreaterThan(100);
    expect(new Set(TRAFFIC_TRIPS.map(t=>t.id)).size).toBe(TRAFFIC_TRIPS.length);
    for(const t of TRAFFIC_TRIPS){
      const points=shapes[t.shapeId];expect(points.length).toBeGreaterThan(1);
      expect(points[0][2]).toBeLessThanOrEqual(t.calls[0].distance);
      expect(points.at(-1)![2]).toBeGreaterThanOrEqual(t.calls.at(-1)!.distance);
      for(let i=1;i<t.calls.length;i++){
        expect(t.calls[i].sequence).toBeGreaterThan(t.calls[i-1].sequence);
        expect(t.calls[i].arrival).toBeGreaterThanOrEqual(t.calls[i-1].departure);
        expect(t.calls[i].distance).toBeGreaterThan(t.calls[i-1].distance);
      }
    }
  });

  it('replays deterministically with finite geographic positions and allows cars to follow the source shape',()=>{
    const samples=sampleTraffic(0);expect(samples.length).toBeGreaterThan(0);
    expect(sampleTraffic(0)).toEqual(samples);
    for(const train of samples){
      expect(Object.values(train.position).every(Number.isFinite)).toBe(true);
      expect(Math.hypot(train.heading.x,train.heading.y,train.heading.z)).toBeCloseTo(1,6);
      expect(train.position.x).toBeGreaterThan(-2200);expect(train.position.x).toBeLessThan(1800);
      expect(train.position.z).toBeGreaterThan(-2500);expect(train.position.z).toBeLessThan(1200);
      const rear=sampleTrafficTrip(train.id,0,24);
      if(rear){expect(rear.shapeDistance).toBeCloseTo(train.shapeDistance-24,6);expect(Math.hypot(rear.position.x-train.position.x,rear.position.z-train.position.z)).toBeLessThan(30);}
    }
    expect(sampleTraffic(-1)).toEqual([]);expect(sampleTraffic(NaN)).toEqual([]);
    expect(sampleTraffic(3*86400)).toEqual([]); // Never loop the snapshot into another day.
  });
});


describe('adjacent traffic presentation',()=>{
  it('suppresses the real Lilydale/Upfield overlap without changing official replay samples',()=>{
    const all=sampleTraffic(270),ids=['02-LIL--67-T2-3603','02-UFD--67-T2-5009'];
    expect(all.filter(t=>ids.includes(t.tripId))).toHaveLength(2);
    const visible=selectAdjacentTraffic(all,positionAt(250));
    expect(visible.filter(t=>ids.includes(t.tripId))).toHaveLength(1);
    expect(sampleTraffic(270)).toEqual(all);
  });
  it('keeps opposing trains on separate lanes and excludes distant invalid shapes before capping',()=>{
    const template=sampleTraffic(0)[0],p=positionAt(600),heading=tangentAt(600);
    const a={...template,id:'a',position:p,heading};
    const b={...a,id:'b',heading:{x:-heading.x,y:-heading.y,z:-heading.z}};
    const hidden={...a,id:'hidden',position:{x:90000,y:0,z:90000}};
    expect(selectAdjacentTraffic([hidden,a,b],p,2).map(t=>t.id)).toEqual(['a','b']);
  });
});
