#!/usr/bin/env python3
"""Derive a reproducible City Loop timetable replay from official Metro GTFS.
Usage: python3 scripts/prepare-traffic.py /tmp/gtfs-metro.zip --date 2026-09-19
Input is the 2/google_transit.zip member of the public statewide GTFS ZIP.
"""
import argparse, csv, datetime, hashlib, io, json, pathlib, zipfile

PARENTS={'vic:rail:FSS','vic:rail:SSS','vic:rail:FGS','vic:rail:MCE','vic:rail:PAR'}
URL='https://opendata.transport.vic.gov.au/dataset/3f4e292e-7f8a-4ffe-831f-1953be0fe448/resource/fb152201-859f-4882-9206-b768060b50ad/download/gtfs.zip'
def seconds(value):
    h,m,s=map(int,value.split(':'))
    assert h>=0 and 0<=m<60 and 0<=s<60
    return h*3600+m*60+s

def main():
    parser=argparse.ArgumentParser();parser.add_argument('archive');parser.add_argument('--date',default='2026-09-19');args=parser.parse_args()
    date=datetime.date.fromisoformat(args.date);stamp=date.strftime('%Y%m%d');day=date.strftime('%A').lower()
    z=zipfile.ZipFile(args.archive)
    def rows(name):return csv.DictReader(io.TextIOWrapper(z.open(name),encoding='utf-8-sig'))
    calendars=list(rows('calendar.txt'));exceptions=list(rows('calendar_dates.txt'))
    active={r['service_id'] for r in calendars if r['start_date']<=stamp<=r['end_date'] and r[day]=='1'}
    for r in exceptions:
        if r['date']==stamp:
            if r['exception_type']=='1':active.add(r['service_id'])
            else:active.discard(r['service_id'])
    stops={r['stop_id']:r for r in rows('stops.txt')}
    city={i for i,r in stops.items() if r.get('parent_station') in PARENTS and r.get('location_type') in ('','0') and r.get('platform_code')!='Replacement bus'}
    routes={r['route_id']:r for r in rows('routes.txt')}
    trips={r['trip_id']:r for r in rows('trips.txt') if r['service_id'] in active and routes[r['route_id']]['route_type'] in ('2','400') and routes[r['route_id']]['route_short_name']!='Replacement Bus'}
    calls={}
    for r in rows('stop_times.txt'):
        if r['trip_id'] in trips:calls.setdefault(r['trip_id'],[]).append(r)
    output=[];shape_ranges={};used_stops=set()
    for trip_id,rr in calls.items():
        rr.sort(key=lambda r:int(r['stop_sequence']));groups=[];group=[]
        for r in rr:
            if r['stop_id'] in city:group.append(r)
            else:
                if len(group)>1:groups.append(group)
                group=[]
        if len(group)>1:groups.append(group)
        for group_index,group in enumerate(groups):
            trip=trips[trip_id];route=routes[trip['route_id']];clean=[]
            for r in group:
                stop=stops[r['stop_id']];distance=float(r['shape_dist_traveled'])
                call={'stopId':r['stop_id'],'station':stop['stop_name'].removesuffix(' Station'),'stationId':stop['parent_station'],'platform':stop.get('platform_code',''),'arrival':seconds(r['arrival_time']),'departure':seconds(r['departure_time']),'distance':distance,'sequence':int(r['stop_sequence'])}
                assert call['arrival']<=call['departure']
                if clean:assert clean[-1]['departure']<=call['arrival'] and clean[-1]['distance']<distance
                clean.append(call);used_stops.add(r['stop_id'])
            output.append({'id':trip_id+':'+str(group_index),'tripId':trip_id,'routeId':trip['route_id'],'routeName':route['route_long_name'],'headsign':trip['trip_headsign'],'directionId':int(trip['direction_id']),'serviceId':trip['service_id'],'shapeId':trip['shape_id'],'calls':clean})
            lo,hi=shape_ranges.get(trip['shape_id'],(float('inf'),-float('inf')))
            shape_ranges[trip['shape_id']]=(min(lo,clean[0]['distance']-250),max(hi,clean[-1]['distance']+250))
    shapes={sid:[] for sid in shape_ranges}
    for r in rows('shapes.txt'):
        sid=r['shape_id']
        if sid in shapes:shapes[sid].append((int(r['shape_pt_sequence']),[float(r['shape_pt_lon']),float(r['shape_pt_lat']),float(r['shape_dist_traveled'])]))
    for sid,points in shapes.items():
        points=[p for _,p in sorted(points)];lo,hi=shape_ranges[sid]
        first=next((i for i,p in enumerate(points) if p[2]>=lo),len(points)-1);last=next((i for i,p in enumerate(points) if p[2]>=hi),len(points)-1)
        shapes[sid]=points[max(0,first-1):last+1]
        assert len(shapes[sid])>1
    output.sort(key=lambda r:(r['calls'][0]['arrival'],r['id']))
    used_services={t['serviceId'] for t in output}
    result={'metadata':{'source':'Transport Victoria GTFS Schedule, metropolitan train archive 2/google_transit.zip','url':URL,'license':'CC BY 4.0','attribution':'State of Victoria (Department of Transport and Planning / Transport Victoria)','archiveSha256':hashlib.sha256(pathlib.Path(args.archive).read_bytes()).hexdigest(),'serviceDate':args.date,'timezone':'Australia/Melbourne','startTime':'06:42:00','startSeconds':seconds('06:42:00'),'mode':'timetable-replay','scope':'Consecutive calls among Flinders Street, Southern Cross, Flagstaff, Melbourne Central and Parliament; other route sections omitted.','calendar':[r for r in calendars if r['service_id'] in used_services],'calendarExceptions':[r for r in exceptions if r['service_id'] in used_services],'caveats':['Positions between calls interpolate scheduled shape distance; not observed live vehicles.','Vertical alignment and renderer track offsets are authored approximations; source does not establish track occupancy or fleet type.','The fixed service date is replayed; this archive is not a current-day journey planner.']},'trips':output,'shapes':shapes}
    path=pathlib.Path('src/data/traffic-schedule.json');path.write_text(json.dumps(result,separators=(',',':'))+'\n')
    print(f'Prepared {len(output)} trip sections, {len(shapes)} shapes, {path.stat().st_size} bytes for {args.date}')
if __name__=='__main__':main()
