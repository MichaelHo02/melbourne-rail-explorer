"""Dominant eastern northern capture fit; filters are authored, not roof edges."""
from pathlib import Path
import json,numpy as np
r=Path(__file__).resolve().parents[1];d=json.loads((r/'assets/source/environment/federation-ngv-complete-captured-roof.json').read_text());a=np.array([q for q in d['samples'] if q[0]>235 and q[1]>95 and q[2]>24]);A=np.c_[a[:,:2],np.ones(len(a))];rng=np.random.default_rng(37);best=None
for _ in range(2500):
 ids=rng.choice(len(a),3,replace=False)
 if abs(np.linalg.det(A[ids]))<.1:continue
 c=np.linalg.solve(A[ids],a[ids,2]);mask=abs(A@c-a[:,2])<.18
 if best is None or mask.sum()>best.sum():best=mask
c=np.linalg.lstsq(A[best],a[best,2],rcond=None)[0];err=abs(A[best]@c-a[best,2]);p=a[best];out={'plane':c.tolist(),'candidate_cells':len(a),'inlier_cells':len(p),'median_residual_m':float(np.median(err)),'p90_residual_m':float(np.quantile(err,.9)),'inlier_bounds_xy':[p[:,:2].min(0).tolist(),p[:,:2].max(0).tolist()],'inlier_samples':p.tolist(),'limits':'Historical2020 grid medians. Authored east235m/north95m/minimum24m filters and0.18m RANSAC tolerance. Dominant plane does not establish exact roof edges, plant, skylights or present-day conditions.'};(r/'assets/source/environment/ngv-eastern-north-roof-plane.json').write_text(json.dumps(out,indent=2)+'\n');print('EASTERN_NORTH_ROOF_PLANE',len(p),float(np.median(err)),flush=True)
