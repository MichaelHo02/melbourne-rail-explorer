"""Authored wider ballast margins on retained ordinary Flinders railway lines."""
import json,hashlib
from pathlib import Path
from shapely.geometry import Polygon,LineString,box
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles,set_precision
root=Path(__file__).resolve().parents[1];source=root/'src/data/corridor-source.json';d=json.loads(source.read_text());clip=box(-550,-170,-15,25);parts=[];ids=[]
for f in d['layers']['rails']['features']:
 if f['properties']['feature_type_code']!='railway':continue
 g=f['geometry'];lines=[g['coordinates']] if g['type']=='LineString' else g['coordinates']
 for line in lines:
  p=LineString([((v[0]-144.9671)*87939,(v[1]+37.8183)*111320) for v in line]).buffer(3.2,cap_style=2,join_style=2).intersection(clip)
  if not p.is_empty:parts.append(p);ids.append(f['properties']['ufi'])
roads=json.loads((root/'assets/source/environment/city-road-surfaces-expanded.json').read_text())['asphalt'];rv=roads['vertices'];obstacles=[Polygon([rv[i][:2] for i in f]) for f in roads['faces']]
for b in json.loads((root/'public/data/buildings.json').read_text())['buildings']:
 if b['base']<=.1:
  p=Polygon([(x,-y) for x,y in b['ring']])
  if p.is_valid and p.intersects(clip):obstacles.append(p)
p=set_precision(unary_union(parts).difference(unary_union(obstacles)),.01);tris=list(constrained_delaunay_triangles(p).geoms);v=[];f=[]
for t in tris:
 pts=list(t.exterior.coords)[:3]
 if sum(pts[i][0]*pts[(i+1)%3][1]-pts[(i+1)%3][0]*pts[i][1] for i in range(3))<0:pts.reverse()
 start=len(v);v.extend([[x,y,.395] for x,y in pts]);f.append([start,start+1,start+2])
assert abs(sum(t.area for t in tris)-p.area)<.01
out={'vertices':v,'faces':f,'area_m2':p.area,'source_ufis':sorted(set(ids)),'source_url':d['sources']['rails']['url'],'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'limits':'Authored 6.4m ballast margins on explicit ordinary railway features clipped to Flinders study bounds, excluding retained road and ground building footprints. Width, level and yard extents illustrative; not a surveyed yard surface.'};(root/'assets/source/environment/flinders-authored-ballast.json').write_text(json.dumps(out,separators=(',',':'))+'\n');print('VERIFIED Flinders ballast:',len(out['source_ufis']),p.area,len(f))
