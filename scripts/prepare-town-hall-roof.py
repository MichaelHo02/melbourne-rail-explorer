"""Triangulate true inset roof bands; no centroid scaling at concave corners."""
from pathlib import Path
import json,hashlib
from shapely.geometry import Polygon,Point
from shapely import constrained_delaunay_triangles
R=Path(__file__).resolve().parents[1];source=R/'assets/source/environment/town-hall-source-reference.json';d=json.loads(source.read_text());r=next(x for x in d['records'] if x['objectid']=='27721')
outline=Polygon([((x-144.9671)*87939,(y+37.8183)*111320) for x,y in r['geo_shape']['geometry']['coordinates'][0]])
assert outline.is_valid
shoulder=outline.buffer(-2,join_style=2);crown=outline.buffer(-4,join_style=2)
assert shoulder.geom_type==crown.geom_type=='Polygon' and not crown.is_empty
bottom=r['footprint_min_elevation']-r['structure_min_elevation'];top=r['footprint_max_elevation']-r['structure_min_elevation'];vertices=[];faces=[];plan=[]
for region,outer,inner,low,high in [(outline.difference(shoulder),outline,shoulder,bottom,top-1.2),(shoulder.difference(crown),shoulder,crown,top-1.2,top),(crown,crown,None,top,top)]:
 for t in constrained_delaunay_triangles(region).geoms:
  assert region.covers(t.representative_point())
  coords=list(t.exterior.coords)[:-1];start=len(vertices)
  for x,y in coords:
   p=Point(x,y);z=low if inner is None or outer.boundary.distance(p)<inner.boundary.distance(p) else high;vertices.append([x,y,z])
  if (coords[1][0]-coords[0][0])*(coords[2][1]-coords[0][1])-(coords[1][1]-coords[0][1])*(coords[2][0]-coords[0][0])<0:coords.reverse();vertices[start:]=list(reversed(vertices[start:]))
  faces.append([start,start+1,start+2]);plan.append(t)
from shapely.ops import unary_union
coverage=unary_union(plan);assert coverage.symmetric_difference(outline).area<.00001
assert abs(sum(t.area for t in plan)-outline.area)<.00001
out={'source_id':'27721','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'reference':d['heritage_reference'],'vertices':vertices,'faces':faces,'plan_area_m2':outline.area,'limits':'Authored true inward offsets2m and4m, shoulder1.2m below retained maximum; source footprint and height bounds preserved. Exact mansard profile, dormers and current condition unverified.'}
(R/'assets/source/environment/town-hall-authored-roof.json').write_text(json.dumps(out,indent=2)+'\n');print('VERIFIED',len(faces),'upward triangles; gap-free plan area',outline.area)
