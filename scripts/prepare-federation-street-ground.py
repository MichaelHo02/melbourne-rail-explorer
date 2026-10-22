import json
from pathlib import Path
from shapely import Polygon,box,constrained_delaunay_triangles
root=Path(__file__).resolve().parents[1];source=json.loads((root/'assets/source/environment/federation-street-ground-original.json').read_text());result={};clip=box(-80,-60,260,250)
for name,d in source.items():
 verts=[];faces=[];mats=[]
 def add(poly,z,mat):
  for tri in constrained_delaunay_triangles(poly).geoms:
   if tri.area<1e-7:continue
   points=list(tri.exterior.coords)[:3]
   if (points[1][0]-points[0][0])*(points[2][1]-points[0][1])-(points[1][1]-points[0][1])*(points[2][0]-points[0][0])<0:points.reverse()
   j=len(verts);verts.extend([[x,y,z] for x,y in points]);faces.append([j,j+1,j+2]);mats.append(mat)
 for ids,mi in zip(d['faces'],d['materials']):
  coords=[d['vertices'][i] for i in ids];z=sum(p[2] for p in coords)/len(coords);assert max(p[2] for p in coords)-min(p[2] for p in coords)<.001;poly=Polygon([p[:2] for p in coords]);add(poly.difference(clip),z,mi)
  inner=poly.intersection(clip)
  for x in range(-80,260,8):
   for y in range(-60,250,8):
    q=inner.intersection(box(x,y,min(x+8,260),min(y+8,250)))
    if not q.is_empty:add(q,z,mi)
 result[name]={'vertices':verts,'faces':faces,'materials':mats};print('GROUND_PATCH',name,len(verts),len(faces))
(root/'assets/source/environment/federation-street-ground-patch.json').write_text(json.dumps(result))
