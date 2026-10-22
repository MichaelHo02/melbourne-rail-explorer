"""Approximate glass enclosure from schematic footprint and local captured roof heights."""
import json,numpy as np
from pathlib import Path
from shapely.geometry import Polygon,LineString,box
from shapely import constrained_delaunay_triangles
r=Path(__file__).resolve().parents[1];ref=json.loads((r/'assets/source/environment/federation-atrium-ownership-reference.json').read_text());ring=ref['atrium_local_ring'][:-1];poly=Polygon(ring);samples=np.array(ref['captured_roof_samples']);vertices=[];faces=[]
def roofz(x,y):
 d=np.sum((samples[:,:2]-[x,y])**2,axis=1);local=samples[np.argsort(d)[:15],2];return float(np.median(local))
def floorz(y):return 10.7+1.5*np.clip((139-y)/90,0,1)
# Northern gallery roof: capture guides shallow folds; regular stationing is authored.
for lo,hi in [(y,min(y+8,139)) for y in range(59,139,8)]+[(42,59)]:
 g=poly.intersection(box(180,lo,240,hi))
 for tri in constrained_delaunay_triangles(g).geoms:
  pts=list(tri.exterior.coords)[:3];k=len(vertices);vertices.extend([[x,y,roofz(x,y)] for x,y in pts]);faces.append([k,k+1,k+2])
# North and western gallery glazing, southern irregular return. East long edge belongs to NGV closure.
sides=[]
for i,a in enumerate(ring):
 b=ring[(i+1)%len(ring)];n=max(1,int(np.ceil(np.linalg.norm(np.array(b)-a)/8)))
 for j in range(n):
  p=np.array(a)+(np.array(b)-a)*j/n;q=np.array(a)+(np.array(b)-a)*(j+1)/n
  sides.append({'edge':i,'points':[[*p,float(floorz(p[1]))],[*q,float(floorz(q[1]))],[*q,roofz(*q)],[*p,roofz(*p)]]})
out={'roof_vertices':vertices,'roof_faces':faces,'sides':sides,'floor_ring':[[x,y,float(floorz(y))] for x,y in ring],'limits':'Schematic footprint; locally median-filtered May2020 roof samples, not exact folds. Frame bay spacing and node positions authored. Floor graded10.7m north to12.2m south from North Atrium height inference and adjacent deck contact, not surveyed interior. East closure approximate; do not claim as-built.', 'sources':['https://fedsquare.com/map','https://fedsquare.com/plan-your-event/atrium','https://www.researchgate.net/publication/254782878_VISION-BASED_MULTI-EPOCH_DEFORMATION_MONITORING_OF_THE_ATRIUM_OF_FEDERATION_SQUARE']}
(r/'assets/source/environment/federation-atrium-enclosure.json').write_text(json.dumps(out));print('ENCLOSURE',len(faces),len(sides))
