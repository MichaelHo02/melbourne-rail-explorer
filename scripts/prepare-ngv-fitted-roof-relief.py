"""Clean component hulls and local top fits; perimeter and closures approximate."""
import json,math
from pathlib import Path
import numpy as np
from shapely.geometry import MultiPoint
from shapely import constrained_delaunay_triangles
r=Path(__file__).resolve().parents[1];d=json.loads((r/'assets/source/environment/ngv-eastern-captured-roof-relief.json').read_text());roof=json.loads((r/'assets/source/environment/ngv-eastern-north-roof-plane.json').read_text())['plane'];vertices=[];faces=[];report=[];start=0;rng=np.random.default_rng(38)
for component in d['components']:
 raw=[d['faces'][i] for i in range(start,start+component['faces'])];start+=component['faces'];samples=[];allpts=[]
 for f in raw:
  p=np.array([d['vertices'][i] for i in f]);allpts.extend(p.tolist());n=np.cross(p[1]-p[0],p[2]-p[0]);length=np.linalg.norm(n)
  if length>1e-9 and n[2]>.55*length:samples.append(p.mean(0))
 a=np.array(samples)
 if len(a)<8:continue
 A=np.c_[a[:,:2],np.ones(len(a))];best=None
 for _ in range(400):
  ids=rng.choice(len(a),3,replace=False)
  if abs(np.linalg.det(A[ids]))<.0001:continue
  c=np.linalg.solve(A[ids],a[ids,2]);mask=abs(A@c-a[:,2])<.08
  if best is None or mask.sum()>best.sum():best=mask
 c=np.linalg.lstsq(A[best],a[best,2],rcond=None)[0];err=abs(A[best]@c-a[best,2]);poly=MultiPoint(a[best,:2]).convex_hull
 if poly.area<.5:continue
 ring=list(poly.exterior.coords)[:-1]
 def height(x,y):return c[0]*x+c[1]*y+c[2]
 if min(height(x,y)-(roof[0]*x+roof[1]*y+roof[2]) for x,y in ring)<.05:continue
 for tri in constrained_delaunay_triangles(poly).geoms:
  k=len(vertices);points=list(tri.exterior.coords)[:3]
  if (points[1][0]-points[0][0])*(points[2][1]-points[0][1])-(points[1][1]-points[0][1])*(points[2][0]-points[0][0])<0:points.reverse()
  vertices.extend([(x,y,height(x,y)) for x,y in points]);faces.append((k,k+1,k+2))
 for a,b in zip(ring,ring[1:]+ring[:1]):
  k=len(vertices);vertices.extend([(a[0],a[1],height(*a)),(b[0],b[1],height(*b)),(b[0],b[1],roof[0]*b[0]+roof[1]*b[1]+roof[2]+.003),(a[0],a[1],roof[0]*a[0]+roof[1]*a[1]+roof[2]+.003)]);faces.append((k,k+1,k+2,k+3))
 report.append({'captured_component_bounds':component['bounds'],'top_plane':c.tolist(),'inlier_faces':int(best.sum()),'median_residual_m':float(np.median(err)),'hull_area_m2':poly.area})
assert len(report)>=3
out={'vertices':vertices,'faces':faces,'features':report,'source':d['source'],'capture':d['capture'],'license':d['license'],'limits':'Clean authored roof relief fitted to historical raised capture components. Upward normals>.55,0.08m local RANSAC tolerance; convex inlier support hulls approximate feature perimeters. Hull may bridge small gaps. Vertical zinc-like closures authored down to fitted roof; functions and current appearance unverified. Original capture retained; no photographic textures.'};(r/'assets/source/environment/ngv-eastern-fitted-roof-relief.json').write_text(json.dumps(out,indent=2)+'\n');print('FITTED_CAPTURED_RELIEF',len(report),len(faces),json.dumps(report),flush=True)
