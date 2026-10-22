import json,numpy as np
from shapely.geometry import Polygon,LineString
from shapely.ops import unary_union
from pathlib import Path
r=Path(__file__).resolve().parents[1];d=json.loads((r/'assets/source/environment/federation-atrium-enclosure.json').read_text());cand=json.loads((r/'docs/federation-atrium-candidate-faces.json').read_text());masses=[]
from shapely.ops import polygonize
source=json.loads((r/'assets/source/environment/federation-atrium-source-boundaries.json').read_text())
for item in source.values():
 footprint=unary_union(list(polygonize(unary_union([LineString(line) for line in item['lines']]))));masses.append((footprint,item['low'],item['high']))
closures=[]
for side in d['sides']:
 for footprint,low,high in masses:
  a,b,c,e=side['points'];line=LineString([a[:2],b[:2]]);g=line.intersection(footprint.buffer(-.001));parts=[g] if g.geom_type=='LineString' else list(getattr(g,'geoms',[]))
  for part in parts:
   if part.is_empty or part.geom_type!='LineString':continue
   xy=[part.coords[0],part.coords[-1]];dist=np.linalg.norm(np.array(b[:2])-a[:2]);t=[np.linalg.norm(np.array(p)-a[:2])/dist for p in xy];tops=[e[2]+(c[2]-e[2])*u for u in t];floors=[a[2]+(b[2]-a[2])*u for u in t]
   for lows,highs in [([low,low],[min(high,v) for v in floors]),([max(low,v) for v in tops],[high,high])]:
    if min(highs[i]-lows[i] for i in range(2))>.02:closures.append([[*xy[0],lows[0]],[*xy[1],lows[1]],[*xy[1],highs[1]],[*xy[0],highs[0]]])
d['boundary_closures']=closures;(r/'assets/source/environment/federation-atrium-enclosure.json').write_text(json.dumps(d));print('CLOSURES',len(closures))
