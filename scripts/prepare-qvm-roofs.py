import json,math
from pathlib import Path
from shapely.geometry import Polygon,box
from shapely.ops import triangulate
root=Path(__file__).resolve().parents[1];d=json.loads((root/'assets/source/environment/qvm-source-audit.json').read_text());b=d['survey_section'];a=b['ring'][0];origin=(a[0],-a[1]);u=(-162,22.8);l=math.hypot(*u);u=(u[0]/l,u[1]/l);n=(-u[1],u[0])
def local(x,y):return ((x-origin[0])*u[0]+(y-origin[1])*u[1],(x-origin[0])*n[0]+(y-origin[1])*n[1])
def world(x,y,z):return [origin[0]+x*u[0]+y*n[0],origin[1]+x*u[1]+y*n[1],z]
p=Polygon([local(x,-y) for x,y in b['ring']]);faces=[]
for i in range(5):
 start=i*20.65;mid=start+8.2
 for lo,hi in [(start,mid),(mid,start+16.4)]:
  piece=p.intersection(box(-10,lo,200,hi))
  for t in triangulate(piece):
   if piece.covers(t):faces.append([world(x,y,10-3.2*abs(y-mid)/8.2) for x,y in list(t.exterior.coords)[:-1]])
out={'source_section':24605,'origin':origin,'axis':u,'normal':n,'faces':faces,'limits':'Five illustrative gabled A-E ranges fitted to survey outline and historical plan. 20.65 m spacing, 16.4 m coverage including eaves, 6.8 m eave and 10 m ridge authored. Current solar panels and roof pitch unverified; southern sheds retained schematic.'};(root/'assets/source/environment/qvm-authored-roofs.json').write_text(json.dumps(out,indent=2)+'\n');print('roof triangles',len(faces))
