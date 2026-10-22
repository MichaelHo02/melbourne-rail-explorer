"""Connected support hulls for roof fit review; no extrapolated architectural boundaries."""
import json,numpy as np
from pathlib import Path
from shapely.geometry import MultiPoint
r=Path(__file__).resolve().parents[1];d=json.loads((r/'docs/federation-ngv-southern-plane-diagnostic.json').read_text());out=[]
for pi,plane in enumerate(d['planes']):
 a=np.array(plane['samples']);remaining=set(range(len(a)))
 while remaining:
  seed=remaining.pop();ids=[seed];queue=[seed]
  while queue:
   i=queue.pop();near=[j for j in remaining if np.linalg.norm(a[j,:2]-a[i,:2])<1.85]
   remaining.difference_update(near);ids.extend(near);queue.extend(near)
  if len(ids)<12:continue
  p=a[ids];h=MultiPoint(p[:,:2]).convex_hull
  out.append({'plane_index':pi,'cells':len(ids),'support_hull_ring':list(h.exterior.coords),'hull_area_m2':h.area,'plane':plane['plane'],'samples':p.tolist()})
report={'patches':out,'limits':'1.85m connectivity threshold and convex support hull authored. Hull can bridge internal voids; not approved roof edges. Historical2020 geometry. Each local patch must be compared with original triangles before scene replacement.'}
(r/'assets/source/environment/ngv-connected-roof-patches.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps([{k:v for k,v in p.items() if k not in ['samples','support_hull_ring']} for p in out],indent=2))
