"""Partition fitted deck with official schematic Square boundary; preserve terrain planes."""
import json,numpy as np
from pathlib import Path
from shapely.geometry import Polygon,shape
from shapely.ops import transform
from shapely import constrained_delaunay_triangles
r=Path(__file__).resolve().parents[1]/'assets/source/environment';ref=json.loads((r/'federation-official-map-reference.json').read_text());square=transform(lambda x,y:((x-144.9671)*87939,(y+37.8183)*111320),shape(ref['layers']['Square'][0]['geometry']));d=json.loads((r/'federation-fitted-deck.json').read_text());verts=[];faces=[];materials=[];areas=[0,0];before=0
for f in d['faces']:
 a=np.array([d['vertices'][j] for j in f]);tri=Polygon(a[:,:2]);before+=tri.area;c=np.linalg.solve(np.c_[a[:,:2],np.ones(3)],a[:,2])
 for region,geom in [(0,tri.intersection(square)),(1,tri.difference(square))]:
  if geom.is_empty or geom.area<1e-8:continue
  for t in constrained_delaunay_triangles(geom).geoms:
   if t.area<1e-8:continue
   new=[]
   for x,y in list(t.exterior.coords)[:3]:new.append(len(verts));verts.append([x,y,float(c[0]*x+c[1]*y+c[2])])
   faces.append(new);materials.append(region);areas[region]+=t.area
assert abs(sum(areas)-before)<.001
(r/'federation-square-paving-regions.json').write_text(json.dumps({'vertices':verts,'faces':faces,'materials':materials,'original_projected_area':before,'region_projected_areas':areas,'official_square_cartographic_area':square.area,'limits':'Official visitor-map Square boundary transformed to local coordinates; schematic, not exact surveyed Main Square limits. Neutral stone outside boundary is an authored finish assumption, not verified paving assignment. Original captured terrain planes preserved.'}));print('PAVING_REGIONS',len(faces),areas,before)
