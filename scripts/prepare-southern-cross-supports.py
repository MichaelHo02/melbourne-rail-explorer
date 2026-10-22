"""Illustrative Y supports constrained by roof boundary and retained rail clearance."""
import json,math
from pathlib import Path
from shapely.geometry import Polygon,LineString,Point
from shapely.ops import unary_union
root=Path(__file__).resolve().parents[1]
roof=json.loads((root/'assets/source/environment/southern-cross-authored-roof.json').read_text());corridor=json.loads((root/'src/data/corridor-source.json').read_text())
def project(p):return ((p[0]-144.9671)*87939,(p[1]+37.8183)*111320)
p=Polygon([project(q) for q in roof['record']['geo_shape']['geometry']['coordinates'][0]]);cx,cy=p.centroid.coords[0];c=math.cos(.354);s=math.sin(.354)
rails=[];ids=[]
for f in corridor['layers']['rails']['features']:
 if f['properties']['feature_type_code']!='railway':continue
 g=f['geometry'];parts=[g['coordinates']] if g['type']=='LineString' else g['coordinates']
 for r in parts:
  line=LineString([project(q) for q in r])
  if line.intersects(p):rails.append(line);ids.append(f['properties']['ufi'])
assert rails
rail=unary_union(rails);supports=[]
for u in [-52,0,52]:
 for v in range(-120,121,40):
  # Seek a nearby clear strip rather than planting a column in mapped rails.
  for shift in [0,-3,3,-6,6]:
   x=cx+(u+shift)*c-v*s;y=cy+(u+shift)*s+v*c
   if p.buffer(-5).contains(Point(x,y)) and rail.distance(Point(x,y))>2.5:
    supports.append({'base':[x,y,.3],'forks':[[x-3*c,y-3*s],[x+3*c,y+3*s]],'rail_clearance_m':rail.distance(Point(x,y))});break
out={'supports':supports,'source_id':'3296','rail_ufis':sorted(set(ids)),'rail_source':corridor['sources']['rails']['url'],'architect_reference':'https://dda-engineers.co.uk/project/southern-cross-station','limits':'Y-column form and approximate 40 m longitudinal rhythm informed by project engineer; support positions, sizes and branches authored, not surveyed. Bases offset from retained mapped railway centrelines by at least 2.5 m; not an engineering or operational clearance certification.'}
(root/'assets/source/environment/southern-cross-authored-supports.json').write_text(json.dumps(out,separators=(',',':'))+'\n');print('Prepared',len(supports),'supports; minimum mapped clearance',min(q['rail_clearance_m'] for q in supports))
