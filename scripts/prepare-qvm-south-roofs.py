import json
from pathlib import Path
from shapely.geometry import Polygon,box
from shapely.ops import triangulate
root=Path(__file__).resolve().parents[1];d=json.loads((root/'assets/source/environment/qvm-authored-roofs.json').read_text());ox,oy=d['origin'];ux,uy=d['axis'];nx,ny=d['normal'];r=json.loads((root/'assets/source/environment/qvm-source-audit.json').read_text())['survey_section']['ring'];p=Polygon([((x-ox)*ux+(-y-oy)*uy,(x-ox)*nx+(-y-oy)*ny) for x,y in r]);faces=[]
ranges=[('F',103,111,6.8,9),('J',111,130,6.8,9),('KL north secondary',130,141.3,5.2,6.8),('KL main',141.3,158.3,6.8,9),('KL south secondary',158.3,169.6,5.2,6.8)]
for label,lo,hi,eave,ridge in ranges:
 mid=(lo+hi)/2
 for a,b in [(lo,mid),(mid,hi)]:
  part=p.intersection(box(-5,a,170,b))
  for t in triangulate(part):
   if part.covers(t):faces.append([[ox+x*ux+y*nx,oy+x*uy+y*ny,ridge-(ridge-eave)*abs(y-mid)/((hi-lo)/2)] for x,y in list(t.exterior.coords)[:-1]])
out={'faces':faces,'ranges':ranges,'limits':'Historical F/J/K-L roof hierarchy fitted to survey. Boundaries, pitch and heights authored; K-L secondary spans 11.3 m and central 17 m informed by conservation plan. Exact current works, solar arrays and lantern shapes unresolved.'};(root/'assets/source/environment/qvm-south-authored-roofs.json').write_text(json.dumps(out,indent=2)+'\n');print('VERIFIED southern roof triangles',len(faces))
