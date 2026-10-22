"""Authored parapet relief on conservative single-section flat low-rise footprints."""
import json,hashlib
from pathlib import Path
from collections import Counter
from shapely import Polygon,constrained_delaunay_triangles
R=Path(__file__).resolve().parents[1];rawpath=Path('/Users/holeminhthach/Developer/train-simulator/public/data/buildings-raw.json');raw=json.loads(rawpath.read_text());lookup={str(b['objectid']):b for b in raw};counts=Counter(str(b['structure_id']) for b in raw);parts=[]
for b in json.loads((R/'public/data/buildings.json').read_text())['buildings']:
 a=lookup.get(str(b['id']))
 if not a or a['roof_type']!='Flat' or counts[str(a['structure_id'])]!=1 or b['kind']!='Structure' or b['base']!=0 or not 6<=b['height']<=25:continue
 p=Polygon([(x,-y) for x,y in b['ring']]).buffer(0)
 if p.geom_type!='Polygon' or not 60<=p.area<=1200 or not (-1800<p.centroid.x<800 and 0<p.centroid.y<1600) or p.area/p.minimum_rotated_rectangle.area<.95:continue
 inner=p.buffer(-.22,join_style='mitre')
 if inner.is_empty or inner.geom_type!='Polygon':continue
 border=p.difference(inner);v=[];f=[];z=b['height']+.025;top=z+.40
 for t in constrained_delaunay_triangles(border).geoms:
  pts=list(t.exterior.coords)[:3]
  if sum(pts[i][0]*pts[(i+1)%3][1]-pts[(i+1)%3][0]*pts[i][1] for i in range(3))<0:pts.reverse()
  start=len(v);v.extend([(x,y,top) for x,y in pts]);f.append([start,start+1,start+2])
 for ring in [p.exterior,inner.exterior]:
  coords=list(ring.coords)
  for x,y in zip(coords,coords[1:]):
   start=len(v);v.extend([(x[0],x[1],z),(y[0],y[1],z),(y[0],y[1],top),(x[0],x[1],top)]);f.append([start,start+1,start+2,start+3])
 parts.append({'id':b['id'],'structure_id':a['structure_id'],'date_captured':a['date_captured'],'vertices':v,'faces':f})
assert parts
out={'source':'https://data.melbourne.vic.gov.au/explore/dataset/2023-building-footprints/','raw_sha256':hashlib.sha256(rawpath.read_bytes()).hexdigest(),'parts':parts,'limits':'Flat classification and footprint are source-derived. Parapet presence, width .22 m, height .40 m and pale finish authored, not measured. Added maximum .425 m above retained envelope; source envelope retained. Conservative single-section rectangular low-rise selection only; current condition and true roofprint unverified.'}
(R/'assets/source/environment/city-authored-flat-parapets.json').write_text(json.dumps(out,separators=(',',':'))+'\n');print(len(parts),'selected flat roofs')
