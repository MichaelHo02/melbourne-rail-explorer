"""Continuous local-fit northern roof trial, capture supported with authored gap fill."""
import json,numpy as np
from pathlib import Path
from shapely.geometry import Polygon,box,Point,MultiPoint
from shapely import constrained_delaunay_triangles
from shapely import delaunay_triangles
r=Path(__file__).resolve().parents[1];bs=json.loads((r/'public/data/buildings.json').read_text())['buildings'];ring=next(b['ring'] for b in bs if str(b['id'])=='16222');poly=Polygon([(x,-y) for x,y in ring]).intersection(box(-1000,95,1000,145));atrium=json.loads((r/'assets/source/environment/federation-atrium-ownership-reference.json').read_text())['atrium_local_ring'];poly=poly.difference(Polygon(atrium));d=json.loads((r/'assets/source/environment/federation-ngv-complete-captured-roof.json').read_text());samples=np.array([q for q in d['samples'] if q[1]>90 and q[2]>27 and poly.buffer(3).covers(Point(q[:2]))])
def h(x,y):
 ds=np.linalg.norm(samples[:,:2]-[x,y],axis=1);ids=np.argsort(ds)[:30];dist=ds[ids];a=samples[ids];A=np.c_[a[:,0]-x,a[:,1]-y,np.ones(len(a))];w=1/np.maximum(dist,1);mask=np.ones(len(a),bool)
 for _ in range(4):
  c=np.linalg.lstsq(A[mask]*w[mask,None],a[mask,2]*w[mask],rcond=None)[0];err=abs(A@c-a[:,2]);mask=err<max(.15,float(np.quantile(err,.65)))
 return float(c[2])
pts=list(poly.exterior.coords)[:-1]+[q for ring in poly.interiors for q in list(ring.coords)[:-1]];lo=poly.bounds
for x in np.arange(lo[0],lo[2],2):
 for y in np.arange(97,lo[3],2):
  if poly.contains(Point(x,y)):pts.append((float(x),float(y)))
verts=[];faces=[]
for raw in delaunay_triangles(MultiPoint(pts)).geoms:
 t=raw.intersection(poly)
 if t.is_empty:continue
 for tri in constrained_delaunay_triangles(t).geoms:
  xy=list(tri.exterior.coords)[:3];k=len(verts);verts.extend([(x,y,h(x,y)) for x,y in xy]);faces.append([k,k+1,k+2])
out={'source':d['source'],'capture':d['capture'],'vertices':verts,'faces':faces,'samples_used':len(samples),'limits':'Two-metre grid, local robust planes from30 nearest captured cells; authored continuous triangulation fills gaps.95m cut and support filtering approximate. No verified equipment semantics or present-day condition.'};(r/'assets/source/environment/ngv-continuous-north-roof-trial.json').write_text(json.dumps(out,indent=2)+'\n');print('CONTINUOUS_NORTH_TRIAL',len(faces),len(samples))
