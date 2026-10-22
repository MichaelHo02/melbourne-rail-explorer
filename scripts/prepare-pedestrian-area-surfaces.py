"""Tagged ground-level pedestrian-area infill from retained OSM geometry."""
import json,hashlib
from pathlib import Path
from collections import defaultdict
from shapely import Polygon,union_all,box,constrained_delaunay_triangles,set_precision
R=Path(__file__).resolve().parents[1];source=R/'assets/source/environment/city-pedestrian-areas-osm.json';d=json.loads(source.read_text());clip=box(-2000,-800,1250,1750);exclude=[]
for filename in ['city-road-surfaces-expanded.json','city-park-surfaces-expanded.json','city-civic-surfaces.json','southbank-authored-paving.json','federation-authored-plaza.json','city-park-paths-expanded.json']:
 a=json.loads((R/'assets/source/environment'/filename).read_text());parts=a['parts'] if 'parts' in a else [a['asphalt'],a['paving']] if 'asphalt' in a else [a]
 for part in parts:
  v=part['vertices'];exclude.extend(Polygon([v[i][:2] for i in face]) for face in part['faces'])
for b in json.loads((R/'public/data/buildings.json').read_text())['buildings']:
 if b['base']<=.1:exclude.append(Polygon([(x,-y) for x,y in b['ring']]).buffer(0))
a=json.loads((R/'src/data/river-source.json').read_text());exclude.append(Polygon([((x-144.9671)*87939,(y+37.8183)*111320) for x,y in a['geometry']['coordinates'][0]]).buffer(0));obstacles=union_all(exclude);parts=[];used=[]
for w in d['ways']:
 tags=w['tags'];surface=tags.get('surface')
 if surface not in ['paving_stones','paved','asphalt','compacted'] or tags.get('layer','0')!='0' or tags.get('level','0')!='0' or tags.get('covered')=='yes' or not w['closed'] or not w['complete']:continue
 shape=Polygon([((x-144.9671)*87939,(y+37.8183)*111320) for x,y in w['coordinates']]).buffer(0);shape=set_precision(shape.intersection(clip).difference(obstacles),.01)
 if shape.is_empty or shape.area<2:continue
 v=[];f=[]
 for t in constrained_delaunay_triangles(shape).geoms:
  points=list(t.exterior.coords)[:3]
  if sum(points[i][0]*points[(i+1)%3][1]-points[(i+1)%3][0]*points[i][1] for i in range(3))<0:points.reverse()
  start=len(v);v.extend([(x,y,.335) for x,y in points]);f.append([start,start+1,start+2])
 assert abs(sum(Polygon([v[i][:2] for i in face]).area for face in f)-shape.area)<.1
 parts.append({'id':w['id'],'surface':surface,'area_m2':shape.area,'vertices':v,'faces':f});used.append(w)
 # Prevent coplanar duplicate infill when community polygons overlap.
 obstacles=union_all([obstacles,shape])
out={'source':d['source'],'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'license':'ODbL 1.0','attribution':'© OpenStreetMap contributors','source_ways':used,'parts':parts,'limits':'Explicit community surface tags support material family only; exact current finish, colour, joints and flat .335 m level authored. Elevated, covered and unknown-surface polygons skipped. Existing mapped road/paving, park, civic, plaza, paths, ground buildings and river excluded; incomplete coverage remains.'}
(R/'assets/source/environment/city-pedestrian-area-surfaces.json').write_text(json.dumps(out,separators=(',',':'))+'\n');print('VERIFIED pedestrian infill',len(parts),sum(p['area_m2'] for p in parts),[(p['id'],p['surface'],round(p['area_m2'])) for p in parts])
