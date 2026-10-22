"""Retain original roof triangles near one connected local slope; evidence only."""
import json,numpy as np
from pathlib import Path
from shapely.geometry import Polygon,Point
r=Path(__file__).resolve().parents[1];patch=next(p for p in json.loads((r/'assets/source/environment/ngv-connected-roof-patches.json').read_text())['patches'] if p['plane_index']==1);poly=Polygon(patch['support_hull_ring']);lo,ly,hi,hy=poly.bounds;c=patch['plane'];vs=[];faces=[]
with Path('/tmp/federation-street-context-2020-trial.obj').open() as f:
 for line in f:
  if line.startswith('v '):vs.append(tuple(map(float,line.split()[1:4])))
  elif line.startswith('f '):
   ids=[int(s.split('/')[0])-1 for s in line.split()[1:]]
   if len(ids)!=3:continue
   p=[vs[i] for i in ids];x=sum(q[0] for q in p)/3;y=sum(q[1] for q in p)/3;z=sum(q[2] for q in p)/3
   if not (lo<=x<=hi and ly<=y<=hy and abs(z-(c[0]*x+c[1]*y+c[2]))<.3):continue
   if not poly.covers(Point(x,y)):continue
   n=np.cross(np.subtract(p[1],p[0]),np.subtract(p[2],p[0]));l=np.linalg.norm(n)
   if l>.00001 and n[2]/l>.55:faces.append(ids)
indices=sorted({i for f in faces for i in f});mapping={v:i for i,v in enumerate(indices)};out={'vertices':[vs[i] for i in indices],'faces':[[mapping[i] for i in f] for f in faces],'source':'https://discover.data.vic.gov.au/dataset/city-of-melbourne-3d-textured-mesh-photomesh-2020','capture_date':'May2020','license':'CC BY4.0','limits':'Original geometry only, within authored support hull and0.3m fitted-plane tolerance. Boundary faces may cross hull. Not approved complete roof replacement; no photographic textures.'};assert faces
(r/'assets/source/environment/ngv-local-captured-roof.json').write_text(json.dumps(out)+'\n');print('LOCAL_CAPTURED_ROOF',len(indices),len(faces),flush=True)
