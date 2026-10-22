"""Geometry-only historical ground cells from both retained municipal tiles."""
import array,json
from pathlib import Path
import numpy as np,pyproj
r=Path(__file__).resolve().parents[1];inv=pyproj.Transformer.from_crs(28355,4326,always_xy=True);groups={};audit=[]
for tile in ['C4-29','C4-30']:
 raw=array.array('d');ids=[]
 with (Path('/tmp/flinders-photomesh')/(tile+'.obj')).open() as src:
  for line in src:
   if line.startswith('v '):raw.extend(map(float,line.split()[1:4]))
   elif line.startswith('f '):
    ix=[int(v.split('/')[0])-1 for v in line.split()[1:]]
    if len(ix)==3:ids.append(ix)
 a=np.asarray(raw).reshape(-1,3);lon,lat=inv.transform(a[:,0],a[:,1]);local=np.column_stack(((lon-144.9671)*87939,(lat+37.8183)*111320,a[:,2]-4.1));tri=np.asarray(ids,dtype=np.int32);count=0
 for start in range(0,len(tri),50000):
  p=local[tri[start:start+50000]];c=p.mean(axis=1);n=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]);length=np.linalg.norm(n,axis=1);valid=(c[:,0]>185)&(c[:,0]<310)&(c[:,1]>-20)&(c[:,1]<153)&(c[:,2]>1)&(c[:,2]<12.5)&(length>1e-9)&(n[:,2]>.6*length)
  for q in c[valid]:groups.setdefault((int(q[0]//2)*2,int(q[1]//2)*2),[]).append(q.tolist())
  count+=int(valid.sum())
 audit.append({'tile':tile,'kept_triangles':count});print(audit[-1],flush=True)
samples=[np.median(v,axis=0).tolist() for v in groups.values()]
out={'source':'https://discover.data.vic.gov.au/dataset/city-of-melbourne-3d-textured-mesh-photomesh-2020','capture':'May2020','tiles':audit,'samples':samples,'limits':'Own reconstruction filter: upward normals>.6, heights1..12.5m,2m median cells. Historical capture includes terraces/low surfaces; no photographic material.'}
(r/'assets/source/environment/ngv-platform-ground-samples.json').write_text(json.dumps(out)+'\n');print('CELLS',len(samples),flush=True)
