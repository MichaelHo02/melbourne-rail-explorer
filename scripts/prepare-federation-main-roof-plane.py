"""Fit main roof separately from overlapping higher source section."""
import json,numpy as np
from pathlib import Path
from shapely.geometry import Polygon,Point
r=Path(__file__).resolve().parents[1]/'assets/source/environment';ss=json.loads((r/'federation-ground-datum-sections.json').read_text());upper=Polygon(next(s['ring'] for s in ss if s['id']=='20248')).buffer(.2);s=next(s for s in ss if s['id']=='20247');raw=next(s['samples'] for s in json.loads((r/'federation-roof-captured-samples.json').read_text()) if s['id']=='20247');a=np.array([q for q in raw if not upper.covers(Point(q[:2]))]);A=np.c_[a[:,:2],np.ones(len(a))];mask=np.ones(len(a),bool)
for _ in range(8):
 c=np.linalg.lstsq(A[mask],a[mask,2],rcond=None)[0];e=np.abs(A@c-a[:,2]);mask=e<.6
assert mask.sum()>len(a)*.75 and np.median(e[mask])<.2
old=next(s for s in json.loads((r/'federation-authored-gables.json').read_text())['sections'] if str(s['id'])=='20247');d={'id':'20247','plane':c.tolist(),'vertices':[[x,y,float(c[0]*x+c[1]*y+c[2])] for x,y,z in old['vertices']],'faces':old['faces'],'source_samples':len(raw),'after_upper_footprint_exclusion':len(a),'inliers':int(mask.sum()),'median_residual':float(np.median(e[mask])),'base':20,'old_top':24.4,'limits':'Shallow roof plane fitted to May2020 capture excluding higher section20248 footprint and residuals over0.6m. Original roof boundary retained; small surface relief, plant and edge detail omitted. Authored zinc finish; not verified present-day condition.'};(r/'federation-main-roof-plane.json').write_text(json.dumps(d));print('MAIN_PLANE',len(a),mask.sum(),np.median(e[mask]),c)
