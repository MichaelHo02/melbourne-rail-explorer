"""Retain two dominant captured fold supports for review; no invented texture."""
from pathlib import Path
import json,numpy as np
from shapely.geometry import MultiPoint
r=Path(__file__).resolve().parents[1];d=json.loads((r/'assets/source/environment/federation-ngv-complete-captured-roof.json').read_text());a=np.array([q for q in d['samples'] if 232<q[0]<244 and 105<q[1]<137 and q[2]>24]);rng=np.random.default_rng(90);out=[]
for j in range(2):
 A=np.c_[a[:,:2],np.ones(len(a))];best=None
 for _ in range(1500):
  ids=rng.choice(len(a),3,False)
  if abs(np.linalg.det(A[ids]))<.1:continue
  c=np.linalg.solve(A[ids],a[ids,2]);m=abs(A@c-a[:,2])<.12
  if best is None or m.sum()>best.sum():best=m
 c=np.linalg.lstsq(A[best],a[best,2],rcond=None)[0];p=a[best];h=MultiPoint(p[:,:2]).convex_hull;out.append({'plane':c.tolist(),'samples':p.tolist(),'support_hull':list(h.exterior.coords)[:-1],'median_residual_m':float(np.median(abs(A[best]@c-p[:,2])))});a=a[~best]
result={'source':d['source'],'capture':d['capture'],'facets':out,'limits':'Two local RANSAC fits from authored selection bounds; convex support hulls can bridge capture gaps. Diagnostic only, not established roof outlines or current condition.'};(r/'assets/source/environment/ngv-transition-facet-study.json').write_text(json.dumps(result,indent=2)+'\n');print([(len(q['samples']),q['median_residual_m']) for q in out])
