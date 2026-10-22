"""Author standing-seam guides on the retained roof footprint, not measured seams."""
import json,math
from pathlib import Path
from shapely.geometry import Polygon,LineString
root=Path(__file__).resolve().parents[1]
roof=json.loads((root/'assets/source/environment/southern-cross-authored-roof.json').read_text())
r=[((p[0]-144.9671)*87939,(p[1]+37.8183)*111320) for p in roof['record']['geo_shape']['geometry']['coordinates'][0]]
p=Polygon(r);cx,cy=p.centroid.coords[0];c=math.cos(.354);s=math.sin(.354)
def xy(u,v):return cx+u*c-v*s,cy+u*s+v*c
def height(x,y):
 u=(x-cx)*c+(y-cy)*s;v=-(x-cx)*s+(y-cy)*c
 return 8.3+9.3*(.5+.5*math.cos(2*math.pi*(u/52+.13*math.sin(v/65))))*(.72+.28*(.5+.5*math.cos(2*math.pi*v/115)))
lines=[]
for i in range(-200,201):
 u=i*1.2;q=p.intersection(LineString([xy(u,-500),xy(u,500)]))
 parts=[q] if q.geom_type=='LineString' else list(q.geoms) if q.geom_type=='MultiLineString' else []
 for line in parts:
  if line.length<.5:continue
  count=math.ceil(line.length/2)
  pts=[]
  for j in range(count+1):
   x,y=line.interpolate(j/count,normalized=True).coords[0];pts.append([x,y,height(x,y)+.045])
  lines.append(pts)
out={'source_id':'3296','source_url':roof['url'],'architect_reference':'https://dda-engineers.co.uk/project/southern-cross-station','limits':'Standing seam roofing informed by project engineer. Seam interval 1.2 m, direction, relief and exact path authored; not construction detail.','lines':lines}
(root/'assets/source/environment/southern-cross-authored-seams.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
print('Prepared',len(lines),'authored standing-seam guides')
