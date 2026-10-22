import json,hashlib,math,datetime
from pathlib import Path
from shapely.geometry import Polygon,LineString,Point
from shapely.ops import unary_union
from shapely.strtree import STRtree
from shapely import constrained_delaunay_triangles
root=Path(__file__).resolve().parents[1];raw=Path('/tmp/melbourne-parking-bays.json');rows=json.loads(raw.read_text());s=json.loads((root/'assets/source/environment/city-road-surfaces-expanded.json').read_text())['asphalt'];asphalt=unary_union([Polygon([(s['vertices'][i][0],s['vertices'][i][1]) for i in f]) for f in s['faces']]);roads=json.loads((root/'assets/source/environment/city-roads-expanded.json').read_text());lines=[]
for feat in roads['features']:
 coords=feat['geometry']['coordinates'];parts=[coords] if feat['geometry']['type']=='LineString' else coords
 for part in parts:
  for a,b in zip(part,part[1:]):
   a=((a[0]-144.9671)*87939,(a[1]+37.8183)*111320);b=((b[0]-144.9671)*87939,(b[1]+37.8183)*111320)
   if math.dist(a,b)>.1:lines.append(LineString([a,b]))
tree=STRtree(lines);forest=json.loads((root/'assets/source/environment/city-trees-expanded.json').read_text());tree_points=[Point((r['longitude']-144.9671)*87939,(r['latitude']+37.8183)*111320) for r in forest['records']];tree_index=STRtree(tree_points);out=[];seen=set()
for r in rows:
 x=(r['longitude']-144.9671)*87939;y=(r['latitude']+37.8183)*111320
 if not (-2000<x<1250 and -800<y<1750) or r['kerbsideid'] in seen:continue
 seen.add(r['kerbsideid']);p=Point(x,y);line=lines[int(tree.nearest(p))]
 if line.distance(p)>12:continue
 a,b=list(line.coords);dx,dy=b[0]-a[0],b[1]-a[1];l=math.hypot(dx,dy);u=(dx/l,dy/l);n=(-u[1],u[0]);corners=[(x+sx*2.75*u[0]+sy*1.1*n[0],y+sx*2.75*u[1]+sy*1.1*n[1]) for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
 bay=Polygon(corners)
 if not asphalt.covers(bay):continue
 if any(tree_points[int(i)].distance(bay)<1.5 for i in tree_index.query(bay.buffer(1.5))):continue
 out.append({'kerbsideid':r['kerbsideid'],'road':r['roadsegmentdescription'],'lastupdated':r['lastupdated'],'xy':[x,y],'corners':corners})
paint=unary_union([LineString(r['corners']+[r['corners'][0]]).buffer(.045,cap_style=2,join_style=2) for r in out]);pv=[];pf=[]
for t in constrained_delaunay_triangles(paint).geoms:
 i=len(pv);pv.extend([[x,y] for x,y in list(t.exterior.coords)[:-1]]);pf.append([i,i+1,i+2])
d={'paint_vertices':pv,'paint_faces':pf,'source':'https://data.melbourne.vic.gov.au/api/explore/v2.1/catalog/datasets/on-street-parking-bays/exports/json','source_raw_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'fetched_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':out,'limits':'Current export provides points, not polygons. Illustrative parallel 5.5 x 2.2 m bay boxes oriented to nearest Vicmap road, retained only where whole rectangle fits authored asphalt. Not actual paint inventory, current availability, restriction or vehicle tracking.'};(root/'assets/source/environment/city-parking-markings.json').write_text(json.dumps(d,indent=2)+'\n');print('VERIFIED parking marking candidates',len(out))
