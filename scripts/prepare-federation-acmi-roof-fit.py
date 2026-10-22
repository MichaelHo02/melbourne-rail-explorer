"""Robust historical roof plane; outliers excluded, original section outline retained."""
import json
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import triangulate
r=Path(__file__).resolve().parents[1];d=json.loads((r/'assets/source/environment/federation-acmi-roof-evidence.json').read_text());p=np.array(d['samples']);A=np.c_[p[:,:2],np.ones(len(p))];mask=p[:,2]>25
for _ in range(8):
 c=np.linalg.lstsq(A[mask],p[mask,2],rcond=None)[0];e=np.abs(A@c-p[:,2]);mask=e<.4
assert mask.mean()>.85 and np.median(e[mask])<.15
b=next(b for b in json.loads((r/'public/data/buildings.json').read_text())['buildings'] if str(b['id'])=='17199');polygon=Polygon([(x,-y) for x,y in b['ring']]);vs=[];fs=[]
for t in triangulate(polygon):
 if not polygon.covers(t):continue
 k=len(vs);vs.extend([[x,y,float(c[0]*x+c[1]*y+c[2])] for x,y in list(t.exterior.coords)[:3]]);fs.append([k,k+1,k+2])
assert abs(sum(Polygon([(vs[i][0],vs[i][1]) for i in f]).area for f in fs)-polygon.area)<1e-6
out={'section':'17199','plane':c.tolist(),'vertices':vs,'faces':fs,'inliers':int(mask.sum()),'samples':len(p),'median_residual':float(np.median(e[mask])),'p90_residual':float(np.quantile(e[mask],.9)),'limits':'Plane fitted to May2020 captured geometry with authored0.4m residual rejection. Source section outline retained. Fine relief, plant and edge construction unresolved. Zinc-like finish authored; not measured present-day appearance.'};(r/'assets/source/environment/federation-acmi-roof-fit.json').write_text(json.dumps(out,indent=2)+'\n');print({k:v for k,v in out.items() if k not in ['vertices','faces']})
