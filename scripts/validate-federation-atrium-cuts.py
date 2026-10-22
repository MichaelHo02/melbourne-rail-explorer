import json,numpy as np
from pathlib import Path
from shapely.geometry import Polygon,LineString
r=Path(__file__).resolve().parents[1];d=json.loads((r/'assets/source/environment/federation-atrium-surface-cuts.json').read_text());void=Polygon(json.loads((r/'assets/source/environment/federation-atrium-ownership-reference.json').read_text())['atrium_local_ring']);count=0;maxplane=0.;maxoverlap=0.
for name,recs in d['patches'].items():
 for rec in recs:
  a=np.array(rec['original_vertices']);n=None
  for i in range(1,len(a)-1):
   z=np.cross(a[i]-a[0],a[i+1]-a[0])
   if np.linalg.norm(z)>1e-7:n=z/np.linalg.norm(z);break
  for tri in rec['outside_triangles']:
   t=np.array(tri);dist=float(np.max(np.abs((t-a[0])@n)));maxplane=max(maxplane,dist);assert dist<1e-4,(name,rec['index'],dist)
   assert np.dot(np.cross(t[1]-t[0],t[2]-t[0]),n)>0
   if abs(n[2])>1e-5:
    overlap=Polygon(t[:,:2]).intersection(void).area;maxoverlap=max(maxoverlap,overlap);assert overlap<1e-6
   else:
    # A vertical triangle has a line footprint. Its centroid must be outside the void.
    from shapely.geometry import Point
    assert not void.buffer(-1e-5).contains(Point(t[:,:2].mean(axis=0)))
   count+=1
result={'outside_triangles_checked':count,'max_plane_distance_m':maxplane,'max_projected_void_overlap_m2':maxoverlap,'status':'pass','limits':'Checks original planes, winding and outside ownership; not architectural completeness or closure.'}
(r/'docs/federation-atrium-cut-validation.json').write_text(json.dumps(result,indent=2));print(result)
