from pathlib import Path
import json,numpy as np
from shapely.geometry import Polygon,shape
from shapely.ops import unary_union,transform
from shapely import constrained_delaunay_triangles
r=Path(__file__).resolve().parents[1];raw=json.loads((r/'assets/source/environment/princes-bridge-road-surface-records.json').read_text());b=next(q for q in json.loads((r/'public/data/buildings.json').read_text())['buildings'] if str(q['id'])=='36402');bridge=Polygon([(x,-y) for x,y in b['ring']]);areas=[]
for a in raw['records']['results']:
 if not a['roadsegmentdescription'].startswith('Swanston Street between Princes Bridge'):continue
 geo=a['json_geometry'];g=transform(lambda x,y,z=None:((x-144.9671)*87939,(y+37.8183)*111320),shape(geo.get('geometry',geo))).difference(bridge)
 if not g.is_empty:areas.append(g)
covered=unary_union(areas);source=json.loads((r/'assets/source/environment/swanston-approach-overlap-original.json').read_text());out={}
for name,faces in source.items():
 replacements={}
 for ix,tris in faces.items():
  result=[];changed=False
  for xyz in tris:
   p=Polygon([q[:2] for q in xyz])
   if p.area<1e-8:
    if covered.covers(p.centroid):changed=True
    else:result.append(xyz)
    continue
   if not p.intersects(covered):result.append(xyz);continue
   g=p.difference(covered);changed=True
   plane=np.linalg.solve(np.array([[x,y,1] for x,y,z in xyz]),np.array([z for x,y,z in xyz]));
   for t in constrained_delaunay_triangles(g).geoms:
    xy=list(t.exterior.coords)[:3]
    if (xy[1][0]-xy[0][0])*(xy[2][1]-xy[0][1])-(xy[1][1]-xy[0][1])*(xy[2][0]-xy[0][0])<0:xy.reverse()
    result.append([[x,y,float(plane@[x,y,1])] for x,y in xy])
  if changed:replacements[ix]=result
 out[name]=replacements
(r/'assets/source/environment/swanston-approach-overlap-cuts.json').write_text(json.dumps(out)+'\n');print('APPROACH_CUTS',[(n,len(v)) for n,v in out.items()], 'mapped union',covered.area)
