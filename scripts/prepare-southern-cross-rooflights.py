"""Split the authored roof mesh for illustrative diffusing rooflight bands."""
import json,math
from pathlib import Path
from shapely.geometry import Polygon,LineString
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
root=Path(__file__).resolve().parents[1];roof=json.loads((root/'assets/source/environment/southern-cross-authored-roof.json').read_text())
r=[((p[0]-144.9671)*87939,(p[1]+37.8183)*111320) for p in roof['record']['geo_shape']['geometry']['coordinates'][0]];boundary=Polygon(r);cx,cy=boundary.centroid.coords[0];c=math.cos(.354);s=math.sin(.354)
bands=[]
for offset in [-78,-26,26,78]:
 pts=[]
 for v in range(-250,251,2):
  u=offset-52*.13*math.sin(v/65);pts.append((cx+u*c-v*s,cy+u*s+v*c))
 bands.append(LineString(pts).buffer(1.4,cap_style=2))
band=unary_union(bands).intersection(boundary);verts=[];faces=[];materials=[];area=[0.,0.]
for face in roof['faces']:
 a,b,d=[roof['vertices'][i] for i in face];tri=Polygon([a[:2],b[:2],d[:2]])
 def height(x,y):
  den=(b[1]-d[1])*(a[0]-d[0])+(d[0]-b[0])*(a[1]-d[1]);w1=((b[1]-d[1])*(x-d[0])+(d[0]-b[0])*(y-d[1]))/den;w2=((d[1]-a[1])*(x-d[0])+(a[0]-d[0])*(y-d[1]))/den
  return w1*a[2]+w2*b[2]+(1-w1-w2)*d[2]
 for material,part in [(0,tri.difference(band)),(1,tri.intersection(band))]:
  if part.area<1e-7:continue
  for t in constrained_delaunay_triangles(part).geoms:
   if t.area<1e-7:continue
   pts=list(t.exterior.coords)[:3]
   if sum(pts[i][0]*pts[(i+1)%3][1]-pts[(i+1)%3][0]*pts[i][1] for i in range(3))<0:pts.reverse()
   start=len(verts);verts.extend([[x,y,height(x,y)] for x,y in pts]);faces.append([start,start+1,start+2]);materials.append(material);area[material]+=t.area
assert abs(sum(area)-roof['plan_area_m2'])<.01
out={'vertices':verts,'faces':faces,'materials':materials,'rooflight_plan_area_m2':area[1],'source_id':'3296','source_url':roof['url'],'reference':'https://grimshaw.global/journal/sculpted-by-the-wind/','limits':'Diffusing ETFE skylight language informed by architect journal. Four bands, 2.8 m width, curves and placement authored on the approximate dune profile; not measured platform or skylight layout.'}
(root/'assets/source/environment/southern-cross-authored-rooflights.json').write_text(json.dumps(out,separators=(',',':'))+'\n');print('VERIFIED roof area preserved; rooflights',area[1],'m2;',len(faces),'triangles')
