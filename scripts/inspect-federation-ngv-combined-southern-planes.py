import json,numpy as np
from pathlib import Path
from shapely.geometry import Polygon,Point
r=Path(__file__).resolve().parents[1]
d=json.loads((r/'assets/source/environment/federation-ngv-combined-roof-evidence.json').read_text());v=Polygon(json.loads((r/'assets/source/environment/federation-atrium-ownership-reference.json').read_text())['atrium_local_ring'])
p=np.array([q for q in d['samples'] if q[1]<95 and q[2]>15 and not v.buffer(.5).covers(Point(q[:2]))]);left=p.copy();out=[];rng=np.random.default_rng(42)
for _ in range(6):
 if len(left)<30:break
 A=np.c_[left[:,:2],np.ones(len(left))];best=None
 for j in range(1500):
  ix=rng.choice(len(left),3,replace=False)
  if abs(np.linalg.det(A[ix]))<.1:continue
  c=np.linalg.solve(A[ix],left[ix,2]);mask=np.abs(A@c-left[:,2])<.18
  if best is None or mask.sum()>best.sum():best=mask
 c=np.linalg.lstsq(A[best],left[best,2],rcond=None)[0];e=np.abs(A[best]@c-left[best,2]);q=left[best]
 out.append({'plane':c.tolist(),'inlier_cells':len(q),'median_residual_m':float(np.median(e)),'bounds_xy':[q[:,:2].min(0).tolist(),q[:,:2].max(0).tolist()],'samples':q.tolist()});left=left[~best]
report={'southern_cells':len(p),'remaining_cells':len(left),'planes':out,'limits':'Diagnostic RANSAC, 0.18m tolerance; disconnected inliers may combine separate surfaces. Historical May2020 evidence, not present-day roof design. No scene edits.'}
(r/'docs/federation-ngv-combined-southern-plane-diagnostic.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({**report,'planes':[{k:v for k,v in x.items() if k!='samples'} for x in out]},indent=2))
