import json,math
from pathlib import Path
import numpy as np
from shapely import Polygon,box,union_all,constrained_delaunay_triangles,make_valid
root=Path(__file__).resolve().parents[1];samples=json.loads((root/'assets/source/environment/federation-captured-ground-samples.json').read_text());raw={(x,y):z for x,y,z in samples};clean={};reject=0
for (x,y),z in raw.items():
 near=[raw[(x+dx,y+dy)] for dx in range(-10,11,2) for dy in range(-10,11,2) if (x+dx,y+dy) in raw]
 median=float(np.median(near))
 if z>median+1.2:reject+=1;continue
 clean[(x,y)]=median
# Coverage derives from captured hits; closing/simplification are presentation assumptions.
coverage=union_all([box(x-1,y-1,x+1,y+1) for x,y in clean]).buffer(4).buffer(-4).simplify(2,preserve_topology=True)
# Clip around every retained ground-level building intersecting the crop.

b=json.loads((root/'public/data/buildings.json').read_text())['buildings'];clip=box(50,-45,310,115)
occupied=union_all([make_valid(Polygon([(x,-y) for x,y in q['ring']])).buffer(.2) for q in b if q['base']==0 and Polygon([(x,-y) for x,y in q['ring']]).intersects(clip)])
coverage=coverage.intersection(clip).difference(occupied)
# Infill small capture tears only; retain large unknown holes and building voids.
parts=list(coverage.geoms) if coverage.geom_type=='MultiPolygon' else [coverage];filled=0;new=[]
for p in parts:
 holes=[]
 for ring in p.interiors:
  h=Polygon(ring)
  if h.area<100 and not h.intersects(occupied):filled+=h.area
  else:holes.append(ring.coords)
 new.append(Polygon(p.exterior.coords,holes))
coverage=union_all(new)
xy=np.array(list(clean));zs=np.array(list(clean.values()));verts=[];faces=[];lookup={};interpolated=0

def vertex(x,y):
 global interpolated
 key=(round(x,5),round(y,5))
 if key in lookup:return lookup[key]
 d=((xy-[x,y])**2).sum(axis=1);ids=np.argpartition(d,7)[:8];weights=1/np.maximum(d[ids],.04);z=float((zs[ids]*weights).sum()/weights.sum())+.025
 if min(d)>4:interpolated+=1
 i=len(verts);lookup[key]=i;verts.append([x,y,z]);return i
for x in range(48,312,2):
 for y in range(-46,116,2):
  p=coverage.intersection(box(x,y,x+2,y+2))
  if p.is_empty:continue
  for t in constrained_delaunay_triangles(p).geoms:
   points=list(t.exterior.coords)[:3]
   if Polygon(points).area<1e-5:continue
   if (points[1][0]-points[0][0])*(points[2][1]-points[0][1])-(points[1][1]-points[0][1])*(points[2][0]-points[0][0])<0:points.reverse()
   faces.append([vertex(a,b) for a,b in points])
# One-sided boundary edges receive authored vertical deck closure.
edges={}
for f in faces:
 for a,b in zip(f,f[1:]+f[:1]):
  k=tuple(sorted((a,b)));edges[k]=edges.get(k,0)+1
walls=[];wallverts=[]
for (a,b),n in edges.items():
 if n!=1:continue
 va,vb=verts[a],verts[b];j=len(wallverts);wallverts.extend([va,vb,[vb[0],vb[1],.38],[va[0],va[1],.38]]);walls.append([j,j+1,j+2,j+3])
data={'source':'https://discover.data.vic.gov.au/dataset/city-of-melbourne-3d-textured-mesh-photomesh-2020','capture':'May 2020','license':'CC BY 4.0','remaining':'Street datum and pedestrian access reconciliation, detailed steps, eastern deck boundaries and entrance relationships unresolved.','vertices':verts,'faces':faces,'wall_vertices':wallverts,'wall_faces':walls,'area_m2':coverage.area,'captured_samples':len(samples),'accepted_samples':len(clean),'rejected_outliers':reject,'filled_holes_area_m2':filled,'interpolated_vertices':interpolated,'limits':'Partial authored precinct reconstruction. 2020 captured heights, local AHD minus4.1m datum, 2m sample spacing, 11x11 sample median, inverse-distance interpolation, 4m morphological coverage closing, 2m outline simplification, <100m2 tear fill and .38m wall bases authored. Not surveyed boundaries, entrance levels or structural reconstruction.'}
(root/'assets/source/environment/federation-fitted-deck.json').write_text(json.dumps(data));print({k:v for k,v in data.items() if k not in ['vertices','faces','wall_vertices','wall_faces']});print(len(verts),len(faces),len(walls))
