"""Exact XY contact-region subtraction, preserving untouched outside source faces."""
import json
from pathlib import Path
import numpy as np
from shapely import Polygon,LineString,constrained_delaunay_triangles,make_valid
r=Path(__file__).resolve().parents[1];contact=json.loads((r/'assets/source/environment/ngv-platform-contact.json').read_text());region=__import__('shapely').from_wkt(contact['region_wkt']);original=json.loads(Path('/tmp/ngv-platform-original-meshes.json').read_text());out={}
for name,d in original.items():
 vs=d['vertices'][:];fs=[];mi=[];removed=0;partial=0;unchanged=0
 for face,material in zip(d['faces'],d['materials']):
  pts=np.array([d['vertices'][i] for i in face]);poly=make_valid(Polygon(pts[:,:2]));area=poly.area
  if area>1e-7:
   cut=poly.intersection(region)
   if cut.area<1e-8:fs.append(face);mi.append(material);unchanged+=1;continue
   remain=poly.difference(region);removed+=1
   if remain.is_empty:continue
   partial+=1
   plane=np.linalg.lstsq(np.column_stack((pts[:,0],pts[:,1],np.ones(len(pts)))),pts[:,2],rcond=None)[0]
   for t in constrained_delaunay_triangles(remain).geoms:
    if t.area<1e-8:continue
    q=list(t.exterior.coords)[:3];ids=[]
    for x,y in q:ids.append(len(vs));vs.append([x,y,float(plane@[x,y,1])])
    fs.append(ids);mi.append(material)
  else:
   dist=((pts[:,None,:2]-pts[None,:,:2])**2).sum(axis=2);a,b=np.unravel_index(dist.argmax(),dist.shape);pa,pb=pts[a,:2],pts[b,:2];line=LineString([pa,pb])
   if line.length<1e-8:fs.append(face);mi.append(material);unchanged+=1;continue
   remaining=line.difference(region)
   if abs(remaining.length-line.length)<1e-7:fs.append(face);mi.append(material);unchanged+=1;continue
   removed+=1
   if remaining.is_empty:continue
   partial+=1;parts=list(remaining.geoms) if remaining.geom_type=='MultiLineString' else [remaining]
   t=((pts[:,:2]-pa)@(pb-pa))/((pb-pa)@(pb-pa));za=[pts[t<.5,2].min(),pts[t<.5,2].max()];zb=[pts[t>=.5,2].min(),pts[t>=.5,2].max()]
   for p in parts:
    qa,qb=list(p.coords)[0],list(p.coords)[-1];u=line.project(__import__('shapely').Point(qa))/line.length;v=line.project(__import__('shapely').Point(qb))/line.length;lo=lambda w:za[0]*(1-w)+zb[0]*w;hi=lambda w:za[1]*(1-w)+zb[1]*w;k=len(vs);vs.extend([[*qa,lo(u)],[*qb,lo(v)],[*qb,hi(v)],[*qa,hi(u)]]);fs.append([k,k+1,k+2,k+3]);mi.append(material)
 out[name]={'vertices':vs,'faces':fs,'materials':mi,'audit':{'intersecting_original_faces':removed,'partially_clipped_faces':partial,'untouched_original_faces':unchanged,'original_vertex_count':len(d['vertices'])}}
 print(name,out[name]['audit'],flush=True)
(r/'assets/source/environment/ngv-platform-clipped-ground.json').write_text(json.dumps(out)+'\n')
