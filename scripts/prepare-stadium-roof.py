"""Authored closed-panel roof constrained by retained footprint and historical dimensions."""
import json,math
from pathlib import Path
from shapely.geometry import Polygon,box
from shapely import constrained_delaunay_triangles,segmentize
root=Path(__file__).resolve().parents[1];d=json.loads((root/'assets/source/environment/stadium-roof-reference.json').read_text());cx,cy=d['roof_centroid_xy'];vx,vy=d['authored_long_axis_from_minimum_rectangle'];ux,uy=vy,-vx
ring=[(x,-y) for x,y in d['roof_section']['ring']];local=[((x-cx)*ux+(y-cy)*uy,(x-cx)*vx+(y-cy)*vy) for x,y in ring];outer=Polygon(local).buffer(0);panel=box(-52,-84,52,84);assert outer.contains(panel)
fixed=segmentize(outer.difference(panel),2);verts=[];faces=[]
def world(u,v,z):return [cx+u*ux+v*vx,cy+u*uy+v*vy,z]
def height(u,v):
 nearest_u=max(-52,min(52,u));nearest_v=max(-84,min(84,v));inner_z=28.7
 a=math.dist((u,v),(nearest_u,nearest_v));b=outer.boundary.distance(__import__('shapely').geometry.Point(u,v));t=a/(a+b) if a+b>1e-8 else 0
 return inner_z*(1-t)+31.35*t
tris=list(constrained_delaunay_triangles(fixed).geoms)
for tri in tris:
 pts=list(tri.exterior.coords)[:3]
 if sum(pts[i][0]*pts[(i+1)%3][1]-pts[(i+1)%3][0]*pts[i][1] for i in range(3))<0:pts.reverse()
 start=len(verts);verts.extend(world(u,v,height(u,v)) for u,v in pts);faces.append([start,start+1,start+2])
assert abs(sum(t.area for t in tris)-fixed.area)<.01
panels=[]
for side in [-1,1]:
 pv=[];pf=[]
 for row in range(43):
  v=-84+row*4
  for col in range(27):
   u=(col*2 if side==1 else -52+col*2);pv.append(world(u,v,28.7))
 for row in range(42):
  for col in range(26):
   i=row*27+col;pf.append([i,i+1,i+28,i+27])
 panels.append({'vertices':pv,'faces':pf,'side':side})
b925=next(b for b in json.loads((root/'public/data/buildings.json').read_text())['buildings'] if b['id']=='925')
p925=Polygon([(x,-y) for x,y in b925['ring']]).buffer(0);p934=Polygon(ring).buffer(0);flange=p925.difference(p934);fv=[];ff=[]
for t in constrained_delaunay_triangles(flange).geoms:
 pts=list(t.exterior.coords)[:3]
 if sum(pts[i][0]*pts[(i+1)%3][1]-pts[(i+1)%3][0]*pts[i][1] for i in range(3))<0:pts.reverse()
 start=len(fv);fv.extend([[x,y,31.36] for x,y in pts]);ff.append([start,start+1,start+2])
out={'perimeter_flange':{'vertices':fv,'faces':ff,'area_m2':flange.area},'fixed':{'vertices':verts,'faces':faces,'area_m2':fixed.area},'panels':panels,'source_reference':'stadium-roof-reference.json','outer_ring_xy':ring,'centroid_xy':[cx,cy],'long_axis':[vx,vy],'across_axis':[ux,uy],'limits':'Closed illustrative state. Two168x52m panels follow historical engineer dimensions. Fixed-roof slope, cladding and panel datum28.7m authored; panel-support rise12m reaches retained relative40.7m upper height approximately. Not exact truss model or live roof state.'};(root/'assets/source/environment/stadium-authored-roof.json').write_text(json.dumps(out,separators=(',',':'))+'\n');print('VERIFIED stadium roof prepared',len(faces),'fixed triangles',len(panels[0]['faces'])*2,'panel faces')
