"""Contiguous NGV contact apron fitted to retained historical ground."""
import json
from pathlib import Path
import numpy as np
from shapely import Polygon,box,make_valid,constrained_delaunay_triangles
r=Path(__file__).resolve().parents[1];b=next(q for q in json.loads((r/'public/data/buildings.json').read_text())['buildings'] if str(q['id'])=='16221');foot=make_valid(Polygon([(x,-y) for x,y in b['ring']]));atrium=Polygon(json.loads((r/'assets/source/environment/federation-atrium-enclosure.json').read_text())['floor_ring']);samples=np.array(json.loads((r/'assets/source/environment/ngv-platform-ground-samples.json').read_text())['samples']);xy=samples[:,:2];zs=samples[:,2]
# Reject upward terrace/low-building cells inside mapped building footprint.
from shapely import contains_xy
keep=~contains_xy(foot.buffer(.5),xy[:,0],xy[:,1]);xy=xy[keep];zs=zs[keep]
region=foot.buffer(1,join_style='mitre').intersection(box(188,-14,294,150)).difference(atrium.buffer(.12));verts=[];faces=[];lookup={};maxdist=0

def field(x,y):
 global maxdist
 d=((xy-[x,y])**2).sum(axis=1);ix=np.argpartition(d,23)[:24];maxdist=max(maxdist,float(np.sqrt(d[ix].min())));median=float(np.median(zs[ix]));valid=abs(zs[ix]-median)<1.5;ix=ix[valid] if valid.sum()>=6 else ix;weights=1/np.maximum(d[ix],9);z=float((zs[ix]*weights).sum()/weights.sum());return z

def vertex(x,y):
 key=(round(x,5),round(y,5))
 if key not in lookup:
  z=8.33
  lookup[key]=len(verts);verts.append([x,y,z+.015])
 return lookup[key]
for x in range(188,296,2):
 for y in range(-14,150,2):
  cell=region.intersection(box(x,y,x+2,y+2))
  if cell.is_empty:continue
  for t in constrained_delaunay_triangles(cell).geoms:
   q=list(t.exterior.coords)[:3]
   if t.area<1e-5:continue
   if (q[1][0]-q[0][0])*(q[2][1]-q[0][1])-(q[1][1]-q[0][1])*(q[2][0]-q[0][0])<0:q.reverse()
   faces.append([vertex(*p) for p in q])
out={'vertices':verts,'faces':faces,'region_wkt':region.wkt,'boundary_distance':[float(region.boundary.distance(__import__('shapely').Point(v[:2]))) for v in verts],'max_nearest_ground_distance_m':maxdist,'source':'https://discover.data.vic.gov.au/dataset/city-of-melbourne-3d-textured-mesh-photomesh-2020','limits':'Authored1m NGV foundation apron and8.345m flat foundation surface derived from retained8.4m building base. Mapped footprint retained; Atrium excluded. Vertical closure bottoms follow existing source-guided deck/ground/floor. Not surveyed structural podium or exact present-day paving; offset and foundation plane assumed. Historical ground cells retained as diagnostic evidence only.'}
(r/'assets/source/environment/ngv-platform-contact.json').write_text(json.dumps(out)+'\n');print('NGV_PLATFORM_CONTACT',len(verts),len(faces),maxdist)
