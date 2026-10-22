"""Extract historical entrance ground evidence from retained untextured capture; no Blender mutation."""
import json, math, statistics
from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=Path('/tmp/federation-street-context-2020-trial.obj');vertices=[];groups={};count=0
with source.open() as f:
 for line in f:
  if line.startswith('v '):vertices.append(tuple(map(float,line.split()[1:4])))
  elif line.startswith('f '):
   ids=[int(x.split('/')[0])-1 for x in line.split()[1:]]
   if len(ids)!=3:continue
   a,b,c=[vertices[i] for i in ids];x=(a[0]+b[0]+c[0])/3;y=(a[1]+b[1]+c[1])/3;z=(a[2]+b[2]+c[2])/3
   if not(185<x<235 and 125<y<160 and 0<z<13):continue
   u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)];n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];length=math.sqrt(sum(t*t for t in n))
   if length<1e-9 or n[2]/length<.55:continue
   groups.setdefault((math.floor(x),math.floor(y)),[]).append((x,y,z));count+=1
samples=[[statistics.median(v[i] for v in rows) for i in range(3)] for rows in groups.values()]
out={'source':'https://discover.data.vic.gov.au/dataset/city-of-melbourne-3d-textured-mesh-photomesh-2020','capture':'May 2020','license':'CC BY 4.0','upward_triangle_centres':count,'samples':samples,'limits':'Geometry-only historical capture. Authored bbox185..235,125..160; heights0..13; upward normals>.55; 1m median cells. Can include steps, furniture or lower roof surfaces. Not an interior floor survey or present-day verification.'}
assert samples
(root/'assets/source/environment/federation-entrance-ground-evidence.json').write_text(json.dumps(out,indent=2)+'\n')
print('ENTRANCE_GROUND',count,len(samples),'range',min(p[2] for p in samples),max(p[2] for p in samples),flush=True)
