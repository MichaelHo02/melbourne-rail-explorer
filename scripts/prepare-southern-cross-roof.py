import json,math,hashlib
from pathlib import Path
from shapely.geometry import Polygon,box
from shapely import constrained_delaunay_triangles
root=Path(__file__).resolve().parents[1]
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--raw',type=Path,required=True);raw=parser.parse_args().raw
b=next(b for b in json.loads(raw.read_text()) if str(b['objectid'])=='3296')
r=[((p[0]-144.9671)*87939,(p[1]+37.8183)*111320) for p in b['geo_shape']['geometry']['coordinates'][0]]
p=Polygon(r);a=.354;c=math.cos(a);s=math.sin(a);cx,cy=p.centroid.coords[0]
def h(x,y):
 u=(x-cx)*c+(y-cy)*s;v=-(x-cx)*s+(y-cy)*c
 # Authored continuous moguls: varying transverse phase and longitudinal rise.
 w=(.5+.5*math.cos(2*math.pi*(u/52+.13*math.sin(v/65))))
 return 8.3+9.3*w*(.72+.28*(.5+.5*math.cos(2*math.pi*v/115)))
verts=[];faces=[];area=0
xmin,ymin,xmax,ymax=p.bounds
for x in range(math.floor(xmin/4)*4,math.ceil(xmax/4)*4,4):
 for y in range(math.floor(ymin/4)*4,math.ceil(ymax/4)*4,4):
  q=p.intersection(box(x,y,x+4,y+4))
  if q.area<1e-7:continue
  for t in constrained_delaunay_triangles(q).geoms:
   if t.area<1e-7:continue
   pts=list(t.exterior.coords)[:3]
   if sum(pts[i][0]*pts[(i+1)%3][1]-pts[(i+1)%3][0]*pts[i][1] for i in range(3))<0:pts.reverse()
   start=len(verts);verts.extend([(x,y,h(x,y)) for x,y in pts]);faces.append([start,start+1,start+2]);area+=t.area
assert abs(area-p.area)<.01
out={'source':'City of Melbourne 2023 Building Footprints','url':'https://data.melbourne.vic.gov.au/explore/dataset/2023-building-footprints/','license':'CC BY 4.0','raw_export_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'record':b,'source_id':'3296','architect_reference':'https://grimshaw.global/projects/rail-and-mass-transit/southern-cross-station/','limits':'Survey roof footprint retained; continuous wave profile, bay spacing and zinc finish authored. Not surveyed roof curvature or current condition.','plan_area_m2':area,'vertices':verts,'faces':faces}
(root/'assets/source/environment/southern-cross-authored-roof.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
print('VERIFIED roof footprint area',area,'triangles',len(faces))
