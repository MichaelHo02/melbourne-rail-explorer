"""Bounded sample triangulation for roof study; does not infer architectural edges."""
import json,math
from pathlib import Path
from shapely.geometry import MultiPoint
from shapely import delaunay_triangles
r=Path(__file__).resolve().parents[1];d=json.loads((r/'assets/source/environment/federation-ngv-complete-captured-roof.json').read_text());vs=d['samples'];lookup={(q[0],q[1]):i for i,q in enumerate(vs)};faces=[];rejected={'long_span':0,'height_jump':0}
for tri in delaunay_triangles(MultiPoint([q[:2] for q in vs])).geoms:
 ids=[lookup[tuple(q)] for q in list(tri.exterior.coords)[:3]];p=[vs[i] for i in ids]
 if max(math.dist(a[:2],b[:2]) for a,b in zip(p,p[1:]+p[:1]))>2.5:rejected['long_span']+=1;continue
 if max(q[2] for q in p)-min(q[2] for q in p)>1.5:rejected['height_jump']+=1;continue
 if (p[1][0]-p[0][0])*(p[2][1]-p[0][1])-(p[1][1]-p[0][1])*(p[2][0]-p[0][0])<0:ids.reverse()
 faces.append(ids)
assert len(faces)>10000
out={'vertices':vs,'faces':faces,'source':d['source'],'capture':d['capture'],'license':d['license'],'triangles':len(faces),'rejected':rejected,'limits':'Study skin from historical one-metre grid medians; maximum triangle edge2.5m and vertex height range1.5m authored. Can bridge small capture holes and discard real sharp folds/steps. No inferred architectural perimeter, skylight schedule or complete closure. Original captured triangles retained separately. Own zinc finish; no photographic textures. Not installed in city.'};(r/'assets/source/environment/ngv-captured-roof-skin-study.json').write_text(json.dumps(out)+'\n');print('ROOF_SKIN_STUDY',len(vs),len(faces),rejected,flush=True)
