"""Authored ground inside public OSM railway land-use polygons."""
import json,hashlib,datetime
from pathlib import Path
from shapely import Polygon,union_all,box,constrained_delaunay_triangles,set_precision
R=Path(__file__).resolve().parents[1];source=R/'assets/source/environment/city-rail-land-osm.json';d=json.loads(source.read_text());clip=box(-2000,-800,1250,1750);shapes=[]
for w in d['ways']:
 if w['closed'] and w['complete']:shapes.append(Polygon([((x-144.9671)*87939,(y+37.8183)*111320) for x,y in w['coordinates']]).buffer(0))
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
out={'source':d['source'],'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'fetched_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'license':'ODbL 1.0','attribution':'© OpenStreetMap contributors','source_ways':d['ways'],'vertices':v,'faces':f,'area_m2':p.area,'limits':'Railway land-use boundaries from community mapping, not an official cadastral or surface survey. Authored aggregate finish and flat .05 m level; no claim entire railway land is ballast. Existing road/paving, parks, civic paving, ground-building footprints and river excluded. Exact current surfaces, elevations, platform clearances and data completeness unresolved.'}
(R/'assets/source/environment/city-rail-precinct-ground.json').write_text(json.dumps(out,separators=(',',':'))+'\n');print('VERIFIED railway ground',p.area,'m2',len(f),'triangles',len(d['ways']),'source ways')
