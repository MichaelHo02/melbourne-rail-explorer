"""Authored ground margins around retained ordinary Flinders rail centre lines."""
import json,hashlib
from pathlib import Path
from shapely.geometry import Polygon,LineString,box
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles,set_precision
R=Path(__file__).resolve().parents[1];source=R/'src/data/corridor-source.json';d=json.loads(source.read_text());clip=box(-550,-170,-15,25);parts=[];ids=[]
for f in d['layers']['rails']['features']:
 if f['properties']['feature_type_code']!='railway':continue
 g=f['geometry'];lines=[g['coordinates']] if g['type']=='LineString' else g['coordinates']
 for line in lines:
  p=LineString([((x-144.9671)*87939,(y+37.8183)*111320) for x,y in line]).buffer(8,cap_style=2,join_style=2).intersection(clip)
  if not p.is_empty:parts.append(p);ids.append(f['properties']['ufi'])
obstacles=[]
for file in ['city-road-surfaces-expanded.json','city-park-surfaces-expanded.json','city-civic-surfaces.json','southbank-authored-paving.json','city-rail-precinct-ground.json','flinders-authored-ballast.json']:
 a=json.loads((R/'assets/source/environment'/file).read_text());ps=a['parts'] if 'parts' in a else [a['asphalt'],a['paving']] if 'asphalt' in a else [a]
 for part in ps:
  v=part['vertices'];obstacles.extend(Polygon([v[i][:2] for i in f]) for f in part['faces'])
for b in json.loads((R/'public/data/buildings.json').read_text())['buildings']:
 if b['base']<=.1:obstacles.append(Polygon([(x,-y) for x,y in b['ring']]).buffer(0))
a=json.loads((R/'src/data/river-source.json').read_text());obstacles.append(Polygon([((x-144.9671)*87939,(y+37.8183)*111320) for x,y in a['geometry']['coordinates'][0]]).buffer(0))
p=set_precision(unary_union(parts).difference(unary_union(obstacles)),.01);v=[];f=[];tri=[]
for t in constrained_delaunay_triangles(p).geoms:
 assert p.covers(t.representative_point());pts=list(t.exterior.coords)[:3]
 if sum(pts[i][0]*pts[(i+1)%3][1]-pts[(i+1)%3][0]*pts[i][1] for i in range(3))<0:pts.reverse()
 k=len(v);v.extend([[x,y,.04] for x,y in pts]);f.append([k,k+1,k+2]);tri.append(t)
assert abs(sum(t.area for t in tri)-p.area)<.01
out={'source_url':d['sources']['rails']['url'],'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_ufis':sorted(set(ids)),'vertices':v,'faces':f,'area_m2':p.area,'license':'CC BY 4.0','attribution':'State of Victoria, Vicmap Transport','limits':'Authored8m half-width ground margins around retained ordinary railway centre lines, clipped to Flinders study bounds. Not rail land-use boundary or actual yard/surface survey. Flat .04m aggregate finish, width and extent approximate. Roads/pavements, parks, civic surfaces, existing railway ground/ballast, ground buildings and river excluded.'}
(R/'assets/source/environment/flinders-authored-ground-margins.json').write_text(json.dumps(out,separators=(',',':'))+'\n');print('VERIFIED rail margins',p.area,'m2',len(f),'triangles',len(out['source_ufis']),'retained lines')
