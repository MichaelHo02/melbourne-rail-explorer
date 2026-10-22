"""Fit one robust plane to retained Federation May2020 roof samples.
NumPy required. Excludes larger compound roof after unsuccessful IDW trial.
"""
import json
from pathlib import Path
import numpy as np
root=Path(__file__).resolve().parents[1]
samples=json.loads((root/'assets/source/environment/federation-roof-captured-samples.json').read_text());gables=json.loads((root/'assets/source/environment/federation-authored-gables.json').read_text())['sections'];s=next(x for x in gables if str(x['id'])=='20248');p=next(x for x in samples if x['id']=='20248');a=np.array(p['samples']);A=np.column_stack([a[:,0],a[:,1],np.ones(len(a))]);mask=np.ones(len(a),bool)
for _ in range(6):
 c=np.linalg.lstsq(A[mask],a[mask,2],rcond=None)[0];err=np.abs(A@c-a[:,2]);mask=err<max(.4,np.median(err)*2.5)
assert mask.sum()>=30 and np.median(err[mask])<.1
section={'id':'20248','vertices':[[x,y,float(c[0]*x+c[1]*y+c[2])] for x,y,z in s['vertices']],'faces':s['faces'],'plane':c.tolist(),'inliers':int(mask.sum()),'samples':p['samples'],'median_inlier_residual':float(np.median(err[mask]))}
(root/'assets/source/environment/federation-captured-roof-fit.json').write_text(json.dumps({'sections':[section],'retained_sections':[x for x in gables if str(x['id'])!='20248'],'limits':'One robust plane fitted to May2020 captured samples. Outliers excluded at authored 0.4m floor; source geometry, not exact architectural detail. Larger roof kept unchanged after jagged IDW trial rejected.'}))
print('ROOF_PLANE',mask.sum(),float(np.median(err[mask])))
