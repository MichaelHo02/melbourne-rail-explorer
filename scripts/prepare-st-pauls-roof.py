import json,math
from pathlib import Path
from shapely.geometry import Polygon,LineString
from shapely.ops import split,triangulate
root=Path(__file__).resolve().parents[1]
b=next(b for b in json.loads((root/'public/data/buildings.json').read_text())['buildings'] if str(b['id'])=='27586');p=Polygon([(x,-y) for x,y in b['ring']]);coords=list(p.minimum_rotated_rectangle.exterior.coords);a,c=max(zip(coords,coords[1:]),key=lambda e:math.dist(*e));dx,dy=c[0]-a[0],c[1]-a[1];l=math.hypot(dx,dy);ux,uy=dx/l,dy/l;nx,ny=-uy,ux;ts=[x*nx+y*ny for x,y in p.exterior.coords];mid=(min(ts)+max(ts))/2;half=(max(ts)-min(ts))/2;center=p.centroid;offset=mid-(center.x*nx+center.y*ny);cx,cy=center.x+nx*offset,center.y+ny*offset
ridge=LineString([(cx-ux*200,cy-uy*200),(cx+ux*200,cy+uy*200)]);pieces=split(p,ridge);faces=[]
for piece in pieces.geoms:
 for t in triangulate(piece):
  if piece.covers(t):faces.append([[x,y,29.6-6.6*abs(x*nx+y*ny-mid)/half] for x,y in list(t.exterior.coords)[:-1]])
(root/'assets/source/environment/st-pauls-authored-roof.json').write_text(json.dumps({'source_section':27586,'faces':faces,'axis_normal':[nx,ny],'mid':mid,'half':half,'limits':'Illustrative longitudinal gable fitted to survey cross-plan; eave 23m and ridge 29.6m authored, not measured roof geometry.'},indent=2)+'\n')
print(len(faces))
