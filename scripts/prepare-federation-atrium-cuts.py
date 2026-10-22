"""Clip candidate surfaces against schematic Atrium void; preserve outside fragments."""
import json,numpy as np
from pathlib import Path
from shapely.geometry import Polygon,LineString,box
from shapely import make_valid,constrained_delaunay_triangles
r=Path(__file__).resolve().parents[1];ref=json.loads((r/'assets/source/environment/federation-atrium-ownership-reference.json').read_text());void=Polygon(ref['atrium_local_ring']);data=json.loads((r/'docs/federation-atrium-candidate-faces.json').read_text());patches={}
def polygons(g):
 if g.is_empty:return []
 if g.geom_type=='Polygon':return [g]
 return [p for a in getattr(g,'geoms',[]) for p in polygons(a)]
for name,records in data.items():
 out=[]
 for rec in records:
  a=np.array(rec['vertices']);normal=None
  for i in range(1,len(a)-1):
   n=np.cross(a[i]-a[0],a[i+1]-a[0])
   if np.linalg.norm(n)>1e-7:normal=n/np.linalg.norm(n);break
  if normal is None:continue
  fragments=[]
  if abs(normal[2])>1e-5:
   source=make_valid(Polygon(a[:,:2]));inside=source.intersection(void)
   if inside.area<1e-7:continue
   remain=source.difference(void);c=-normal.dot(a[0]);convert=lambda x,y:[x,y,float(-(normal[0]*x+normal[1]*y+c)/normal[2])]
   fragments=[(p,convert) for p in polygons(remain)]
  else:
   diffs=[q[:2]-a[0,:2] for q in a];u=max(diffs,key=lambda q:np.linalg.norm(q));u=u/np.linalg.norm(u);origin=a[0,:2];uv=np.c_[(a[:,:2]-origin)@u,a[:,2]];low=float(uv[:,0].min());high=float(uv[:,0].max());line=LineString([origin+u*low,origin+u*high]);inside=line.intersection(void)
   if inside.length<1e-5:continue
   remain=line.difference(void);parts=[remain] if remain.geom_type=='LineString' else list(getattr(remain,'geoms',[]));source=make_valid(Polygon(uv));convert=lambda x,y:[float(origin[0]+u[0]*x),float(origin[1]+u[1]*x),y]
   for part in parts:
    if part.geom_type!='LineString' or part.is_empty:continue
    t=[float((np.array(q)-origin)@u) for q in part.coords];g=source.intersection(box(min(t),float(a[:,2].min())-1,max(t),float(a[:,2].max())+1));fragments.extend((p,convert) for p in polygons(g))
  triangles=[]
  for g,convert in fragments:
   for t in constrained_delaunay_triangles(g).geoms:
    if t.area<1e-6:continue
    pts=[convert(x,y) for x,y in list(t.exterior.coords)[:3]]
    if np.dot(np.cross(np.array(pts[1])-pts[0],np.array(pts[2])-pts[0]),normal)<0:pts.reverse()
    triangles.append(pts)
  out.append({'index':rec['index'],'original_vertices':rec['vertices'],'material':rec['material'],'outside_triangles':triangles})
 if out:patches[name]=out
(r/'assets/source/environment/federation-atrium-surface-cuts.json').write_text(json.dumps({'patches':patches,'limits':'Exact surface clipping against schematic visitor-map Atrium polygon. Outside fragments retained; original planes preserved. Cut does not establish actual construction boundary; glass and interior closure reconstruction still required.'}));print('ATRIUM_CUTS',[(k,len(v),sum(len(p['outside_triangles']) for p in v)) for k,v in patches.items()])
