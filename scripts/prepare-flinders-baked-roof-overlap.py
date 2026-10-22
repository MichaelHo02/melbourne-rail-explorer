import json,numpy as np
from pathlib import Path
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
r=Path(__file__).resolve().parents[1];d=json.loads((r/'assets/source/environment/flinders-concourse-continuous-skin.json').read_text());covered=unary_union([box(x,y,x+1,y+1) for x,y in d['quad_origins']]);source=json.loads((r/'assets/source/environment/flinders-roof-baked-overlap-original.json').read_text());out={};restored_area=0;old_removed=set(json.loads((r/'docs/flinders-concourse-skin-audit.json').read_text())['removed_face_indices'])
for ix,tris in source.items():
 changed=False;result=[]
 for xyz in tris:
  p=Polygon([q[:2] for q in xyz])
  if p.area<1e-9:
   if covered.covers(p.centroid):changed=True
   else:result.append(xyz)
   continue
  if not p.intersects(covered):result.append(xyz);continue
  g=p.difference(covered);changed=True
  if int(ix) in old_removed:restored_area+=g.area
  if g.is_empty:continue
  plane=np.linalg.solve(np.array([[x,y,1] for x,y,z in xyz]),np.array([z for x,y,z in xyz]));sign=(xyz[1][0]-xyz[0][0])*(xyz[2][1]-xyz[0][1])-(xyz[1][1]-xyz[0][1])*(xyz[2][0]-xyz[0][0])
  for t in constrained_delaunay_triangles(g).geoms:
   xy=list(t.exterior.coords)[:3];ts=(xy[1][0]-xy[0][0])*(xy[2][1]-xy[0][1])-(xy[1][1]-xy[0][1])*(xy[2][0]-xy[0][0])
   if ts*sign<0:xy.reverse()
   result.append([[x,y,float(plane@[x,y,1])] for x,y in xy])
 if changed:out[ix]=result
(r/'assets/source/environment/flinders-roof-baked-overlap-cuts.json').write_text(json.dumps(out,separators=(',',':'))+'\n');(r/'docs/flinders-roof-baked-boundary-audit.json').write_text(json.dumps({'covered_area_m2':covered.area,'cut_original_faces':len(out),'outside_xy_area_restored_from_centroid_cut_m2':restored_area,'limits':'Exact XY subtraction of authored grid coverage; height/material selection approximate. Original roof surface interpolation retained outside repaired coverage. Vertical faces use covered centroid rule.'},indent=2)+'\n');print(len(out),'cut faces;',restored_area,'m2 outside repair previously removed')
