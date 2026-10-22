"""Add authored paving on retained civic-class parcels, subtracting existing surfaces."""
import json,hashlib
from pathlib import Path
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles,set_precision
root=Path(__file__).resolve().parents[1];source=root/'assets/source/environment/city-parks-expanded.json';d=json.loads(source.read_text());clip=box(-2000,-800,1250,1750);exclude=[]
for filename in ['city-park-surfaces-expanded.json','city-road-surfaces-expanded.json','southbank-authored-paving.json']:
 data=json.loads((root/'assets/source/environment'/filename).read_text());parts=data['parts'] if 'parts' in data else [data['asphalt'],data['paving']] if 'asphalt' in data else [data]
 for part in parts:
  v=part['vertices'];exclude.extend(Polygon([v[i][:2] for i in f]) for f in part['faces'])
for b in json.loads((root/'public/data/buildings.json').read_text())['buildings']:
 if b['base']<=.1:
  p=Polygon([(x,-y) for x,y in b['ring']]).buffer(0)
  if p.intersects(clip):exclude.append(p)
obstacles=unary_union(exclude);parts=[]
for f in d['layers']['openSpaces']['features']:
 prop=f['properties']
 if prop['os_group']!='Civic square and promenade' or prop['veac_id']=='Q002052':continue
 ringsets=f['geometry']['coordinates'] if f['geometry']['type']=='MultiPolygon' else [f['geometry']['coordinates']]
 shapes=[]
 for rings in ringsets:
  r=[[( (x-144.9671)*87939,(y+37.8183)*111320) for x,y in ring] for ring in rings]
  shapes.append(Polygon(r[0],r[1:]).buffer(0))
 p=set_precision(unary_union(shapes).intersection(clip).difference(obstacles),.01)
 if p.is_empty:continue
 v=[];faces=[];tris=list(constrained_delaunay_triangles(p).geoms)
 for t in tris:
  pts=list(t.exterior.coords)[:3]
  if sum(pts[i][0]*pts[(i+1)%3][1]-pts[(i+1)%3][0]*pts[i][1] for i in range(3))<0:pts.reverse()
  start=len(v);v.extend([[x,y,.325] for x,y in pts]);faces.append([start,start+1,start+2])
 assert abs(sum(t.area for t in tris)-p.area)<.01
 parts.append({'source_id':prop['veac_id'],'name':prop['name'],'source_properties':prop,'vertices':v,'faces':faces,'area_m2':p.area,'centroid_xy':list(p.centroid.coords)[0]})
out={'source':d['sources']['openSpaces'],'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'parts':parts,'limits':'Retained civic classification only; authored generic paving, not measured surface coverage. Flat datum. Existing park/road/pavement and ground-building geometry excluded. Inventory age and present-day condition unresolved.'}
(root/'assets/source/environment/city-civic-surfaces.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
print('VERIFIED civic surfaces',[(p['source_id'],round(p['area_m2'],1),p['centroid_xy']) for p in parts])
