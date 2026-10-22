"""Extract upward ACMI roof samples from retained geometry-only municipal crop.
Requires NumPy/Shapely and /tmp/federation-street-context-2020-trial.obj.
Produces evidence only; does not mutate Blender or infer current construction.
"""
import json
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon, Point
root=Path(__file__).resolve().parents[1]
b=next(b for b in json.loads((root/'public/data/buildings.json').read_text())['buildings'] if str(b['id'])=='17199')
footprint=Polygon([(x,-y) for x,y in b['ring']]).buffer(-.8)
vertices=[];samples=[]
with Path('/tmp/federation-street-context-2020-trial.obj').open() as f:
 for line in f:
  if line.startswith('v '):vertices.append(tuple(map(float,line.split()[1:4])))
  elif line.startswith('f '):
   ids=[int(s.split('/')[0])-1 for s in line.split()[1:]]
   if len(ids)!=3:continue
   raw=[vertices[i] for i in ids];centre=np.mean(raw,axis=0)
   if not (15<centre[2]<40 and footprint.covers(Point(centre[:2]))):continue
   a,c,d=[np.array(v) for v in raw];normal=np.cross(c-a,d-a);length=np.linalg.norm(normal)
   if length<1e-9 or normal[2]/length<.55:continue
   samples.append(centre.tolist())
p=np.array(samples);assert len(p)>100
# Equal-area grid medians reduce dense capture tessellation bias.
groups={}
for x,y,z in p:groups.setdefault((int(np.floor(x)),int(np.floor(y))),[]).append((x,y,z))
grid=np.array([np.median(v,axis=0) for v in groups.values()]);A=np.c_[grid[:,:2],np.ones(len(grid))];c=np.linalg.lstsq(A,grid[:,2],rcond=None)[0];e=np.abs(A@c-grid[:,2])
d={'section':'17199','source':'https://discover.data.vic.gov.au/dataset/city-of-melbourne-3d-textured-mesh-photomesh-2020','license':'CC BY 4.0','capture_date':'May 2020','samples':grid.tolist(),'upward_triangle_centres':len(samples),'grid_cells':len(grid),'single_plane':c.tolist(),'single_plane_median_residual':float(np.median(e)),'single_plane_p90_residual':float(np.quantile(e,.9)),'height_quantiles':np.quantile(grid[:,2],[0,.1,.5,.9,1]).tolist(),'limits':'Evidence only. 0.8m inset source footprint, upward normal threshold0.55 and heights15–40m are authored filters. One-metre grid medians. Surface may include roof plant; single plane is diagnostic, not approved replacement. Historical capture cannot verify present-day condition. No photographic textures.'}
(root/'assets/source/environment/federation-acmi-roof-evidence.json').write_text(json.dumps(d,indent=2)+'\n')
print(json.dumps({k:v for k,v in d.items() if k!='samples'},indent=2))
