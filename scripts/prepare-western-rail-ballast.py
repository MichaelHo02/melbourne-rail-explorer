"""Authored ground inside public OSM railway land-use polygons."""
import json,hashlib,datetime
from pathlib import Path
from shapely import Polygon,union_all,box,constrained_delaunay_triangles,set_precision
from shapely.geometry import LineString
R=Path(__file__).resolve().parents[1];source=R/'assets/source/environment/city-rails-expanded.json';d=json.loads(source.read_text());clip=box(-2000,300,-1100,1750);shapes=[];ids=[]
for f in d['features']:
 if f['properties']['feature_type_code'] not in ['railway','rail_siding']:continue
 if str(f['properties'].get('structure_type'))=='6':continue
 g=f['geometry'];lines=[g['coordinates']] if g['type']=='LineString' else g['coordinates']
 for line in lines:
  shape=LineString([((x-144.9671)*87939,(y+37.8183)*111320) for x,y in line]).buffer(3.2,cap_style=2,join_style=2).intersection(clip)
  if not shape.is_empty:shapes.append(shape);ids.append(f['properties']['ufi'])
exclude=[]
for filename in ['city-road-surfaces-expanded.json','city-park-surfaces-expanded.json','city-civic-surfaces.json','southbank-authored-paving.json']:
 a=json.loads((R/'assets/source/environment'/filename).read_text());parts=a['parts'] if 'parts' in a else [a['asphalt'],a['paving']] if 'asphalt' in a else [a]
 for part in parts:
  v=part['vertices'];exclude.extend(Polygon([v[i][:2] for i in f]) for f in part['faces'])
for b in json.loads((R/'public/data/buildings.json').read_text())['buildings']:
 if b['base']<=.1:exclude.append(Polygon([(x,-y) for x,y in b['ring']]).buffer(0))
a=json.loads((R/'src/data/river-source.json').read_text());exclude.append(Polygon([((x-144.9671)*87939,(y+37.8183)*111320) for x,y in a['geometry']['coordinates'][0]]).buffer(0))
p=set_precision(union_all(shapes).intersection(clip).difference(union_all(exclude)),.01);v=[];f=[]
for t in constrained_delaunay_triangles(p).geoms:
 points=list(t.exterior.coords)[:3]
 if sum(points[i][0]*points[(i+1)%3][1]-points[(i+1)%3][0]*points[i][1] for i in range(3))<0:points.reverse()
 start=len(v);v.extend([(x,y,.05) for x,y in points]);f.append([start,start+1,start+2])
assert abs(sum(Polygon([v[i][:2] for i in face]).area for face in f)-p.area)<.1
out={'source':d['source'],'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_fetched_at_utc':d['fetchedAt'],'prepared_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'license':d['license'],'attribution':d['attribution'],'source_ufis':sorted(set(ids)),'vertices':v,'faces':f,'area_m2':p.area,'limits':'Authored6.4m-wide ballast margins around retained Vicmap ordinary rail and siding centre lines within western review bounds. Underground and bridge feature classes excluded; structure_type6 additionally excluded. Flat0.05m level and width illustrative, not surveyed yard boundaries or current surface coverage. Roads, parks, civic paving, building footprints and river excluded. No photographic textures.'}
(R/'assets/source/environment/western-rail-ballast-margins.json').write_text(json.dumps(out,separators=(',',':'))+'\n');print('VERIFIED railway ground',p.area,'m2',len(f),'triangles',len(set(ids)),'source alignments')
