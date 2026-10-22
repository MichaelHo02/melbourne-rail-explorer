"""Retain connected raised capture geometry over corrected eastern roof."""
import json,math
from pathlib import Path
import numpy as np
r=Path(__file__).resolve().parents[1];d=json.loads((r/'assets/source/environment/federation-ngv-captured-envelope-study.json').read_text());plane=json.loads((r/'assets/source/environment/ngv-eastern-north-roof-plane.json').read_text())['plane'];vs=[];fs=[];lookup={}
for face in d['faces']:
 p=np.array([d['vertices'][i] for i in face]);c=p.mean(0);dz=p[:,2]-(p[:,0]*plane[0]+p[:,1]*plane[1]+plane[2])
 if not (240<=c[0]<=261 and 105<=c[1]<=136 and .3<float(dz.mean())<4 and float(dz.min())>-.1 and float(dz.max())<4.5):continue
 ids=[]
 for q in p:
  key=tuple(round(float(v),4) for v in q)
  if key not in lookup:lookup[key]=len(vs);vs.append(q.tolist())
  ids.append(lookup[key])
 fs.append(ids)
parent=list(range(len(fs)))
def find(i):
 while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
 return i
owners={}
for i,f in enumerate(fs):
 for v in f:
  if v in owners:parent[find(i)]=find(owners[v])
  else:owners[v]=i
components={}
for i in range(len(fs)):components.setdefault(find(i),[]).append(i)
keep=[];report=[]
for ids in components.values():
 area=sum(float(np.linalg.norm(np.cross(np.subtract(vs[fs[i][1]],vs[fs[i][0]]),np.subtract(vs[fs[i][2]],vs[fs[i][0]])))/2) for i in ids)
 if area<2 or len(ids)<8:continue
 keep.extend(ids);qs=[vs[v] for i in ids for v in fs[i]];report.append({'faces':len(ids),'surface_area_m2':area,'bounds':[[min(q[j] for q in qs) for j in range(3)],[max(q[j] for q in qs) for j in range(3)]]})
used=sorted({v for i in keep for v in fs[i]});mapping={v:i for i,v in enumerate(used)};out={'vertices':[vs[i] for i in used],'faces':[[mapping[v] for v in fs[i]] for i in keep],'components':report,'source':d['source'],'capture':d['capture'],'license':d['license'],'limits':'Original captured raised geometry only, authored centre bounds240..261,105..136m; residual0.3..4m, vertex limits-0.1..4.5m against fitted eastern plane; shared4-decimal vertex coordinates, components>=2m2 and8faces. Features may include skylights, plant or scan artefacts; function/material unverified. Own zinc finish, no photographic textures. Edges may be open; inspect contact before apply.'};assert out['faces'];(r/'assets/source/environment/ngv-eastern-captured-roof-relief.json').write_text(json.dumps(out)+'\n');print('CAPTURED_EASTERN_ROOF_RELIEF',len(used),len(keep),json.dumps(report),flush=True)
