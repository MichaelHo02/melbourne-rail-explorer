"""Authored outward mansard shell around a retained upper survey footprint."""
import json
from pathlib import Path
from shapely.geometry import Polygon,Point
from shapely import constrained_delaunay_triangles
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];data=json.loads((R/'public/data/buildings.json').read_text());b=next(b for b in data['buildings'] if str(b['id'])=='26404');outline=Polygon([(x,-y) for x,y in b['ring']]);outer=outline.buffer(2,join_style=2);band=outer.difference(outline);low=b['base'];high=low+b['height'];v=[];f=[];tri=[]
for region,cap in [(band,False),(outline,True)]:
 for t in constrained_delaunay_triangles(region).geoms:
  assert region.covers(t.representative_point());coords=list(t.exterior.coords)[:-1]
  if (coords[1][0]-coords[0][0])*(coords[2][1]-coords[0][1])-(coords[1][1]-coords[0][1])*(coords[2][0]-coords[0][0])<0:coords.reverse()
  k=len(v)
  for x,y in coords:
   p=Point(x,y);z=high if cap or outline.boundary.distance(p)<outer.boundary.distance(p) else low;v.append([x,y,z])
  f.append([k,k+1,k+2]);tri.append(t)
assert unary_union(tri).symmetric_difference(outer).area<1e-5
assert abs(sum(t.area for t in tri)-outer.area)<1e-5
out={'source_id':'26404','vertices':v,'faces':f,'ring':list(outline.exterior.coords),'base':low,'top':high,'plan_area_m2':outer.area,'reference':'https://whatson.melbourne.vic.gov.au/places-to-stay/the-westin-melbourne','limits':'Authored2m outward roof eave projection from upper source footprint at34m, tapering to original footprint at49m. Upper height preserved; extent and profile not measured. Retained original source body behind shell; source ground footprint unchanged. Window arrangement authored, photograph capture date unknown.'}
(R/'assets/source/environment/westin-authored-mansard.json').write_text(json.dumps(out,indent=2)+'\n');print('VERIFIED mansard shell',len(f),'upward triangles',outer.area,'m2 gap-free plan')
