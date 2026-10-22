"""Retain official signal sites and derive illustrative Hoddle-grid corner hardware."""
import csv,json,math,hashlib,datetime
from pathlib import Path
from shapely.geometry import Polygon,Point
from shapely.strtree import STRtree
R=Path(__file__).resolve().parents[1];raw=Path('/tmp/victorian-traffic-signals.csv');rows=list(csv.DictReader(raw.read_text(encoding='utf-8-sig').splitlines()));records=[];placements=[]
buildings=json.loads(Path('/Users/holeminhthach/Developer/train-simulator/public/data/buildings-raw.json').read_text());source_records=buildings.get('results',buildings.get('records',[])) if isinstance(buildings,dict) else buildings
polygons=[]
for r in source_records:
 r=r.get('fields',r)
 try:
  if float(r['footprint_min_elevation'])-float(r['structure_min_elevation'])>.15:continue
  g=r['geo_shape'];g=g.get('geometry',g);p=Polygon([((x-144.9671)*87939,(y+37.8183)*111320) for x,y in g['coordinates'][0]])
  if p.is_valid:polygons.append(p)
 except (KeyError,TypeError,ValueError):continue
assert polygons,'No source building obstacles loaded'
tree=STRtree(polygons);rotation=.354;ux,uy=math.cos(rotation),math.sin(rotation);nx,ny=-uy,ux;excluded=0
for r in rows:
 if not r['LONGITUDE'] or not r['LATITUDE']:continue
 lon=float(r['LONGITUDE']);lat=float(r['LATITUDE']);x=(lon-144.9671)*87939;y=(lat+37.8183)*111320
 if r['TYPE']!='INT' or not (-1250<x<350 and 0<y<1150):continue
 records.append(r)
 for a,b in [(-1,-1),(-1,1),(1,-1),(1,1)]:
  px=x+12*(a*ux+b*nx);py=y+12*(a*uy+b*ny);point=Point(px,py)
  if any(polygons[int(i)].distance(point)<.6 for i in tree.query(point.buffer(.6))):excluded+=1;continue
  placements.append({'site_no':r['SITE_NO'],'x':px,'y':py,'rotation':rotation+(math.pi if a<0 else 0)})
d={'source':'https://opendata.transport.vic.gov.au/dataset/923af458-363d-469f-bc5e-84746a80b9a2/resource/1036a318-8867-4dc6-bd84-fc3bcd6cbdb9/download/victorian_traffic_signals.csv','license':'CC BY4.0','source_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':records,'placements':placements,'excluded_building_collisions':excluded,'limits':'Official intersection site points only. Pole locations inferred at four12m offsets along authored grid axes; actual pole inventory, road width, light state and timings unknown. Building footprints used only to exclude collisions. Heads unlit, not realtime.'};(R/'assets/source/environment/cbd-authored-traffic-signals.json').write_text(json.dumps(d,indent=2)+'\n');print('VERIFIED official sites',len(records),'authored poles',len(placements),'building exclusions',excluded)
