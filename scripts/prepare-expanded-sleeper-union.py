"""Union authored sleeper footprints to avoid coplanar junction overlap."""
import json,math
from pathlib import Path
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles,set_precision
root=Path(__file__).resolve().parents[1];d=json.loads((root/'assets/source/environment/city-trackbeds-expanded-additions.json').read_text());parts=[]
for line in d['alignments']:
 for a,b in zip(line,line[1:]):
  dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
  if length<.65 or not all(-2000<=p[0]<=1250 and -800<=p[1]<=1750 for p in [a,b]):continue
  tx,ty=dx/length,dy/length;nx,ny=-ty,tx
  for i in range(int(length/.65)):
   x,y=a[0]+tx*(i*.65+.325),a[1]+ty*(i*.65+.325)
   parts.append(Polygon([(x+tx*u+nx*v,y+ty*u+ny*v) for u,v in [(-.12,-1.22),(.12,-1.22),(.12,1.22),(-.12,1.22)]]))
p=set_precision(unary_union(parts),.001);v=[];f=[]
for t in constrained_delaunay_triangles(p).geoms:
 coords=list(t.exterior.coords)[:3]
 if sum(coords[i][0]*coords[(i+1)%3][1]-coords[(i+1)%3][0]*coords[i][1] for i in range(3))<0:coords.reverse()
 start=len(v);v.extend((x,y,.445) for x,y in coords);f.append([start,start+1,start+2])
polygons=list(p.geoms) if p.geom_type=='MultiPolygon' else [p]
for polygon in polygons:
 for ring in [polygon.exterior,*polygon.interiors]:
  coords=list(ring.coords)
  for a,b in zip(coords,coords[1:]):
   start=len(v);v.extend([(a[0],a[1],.405),(b[0],b[1],.405),(b[0],b[1],.445),(a[0],a[1],.445)]);f.append(list(range(start,start+4)))
assert abs(sum(t.area for t in constrained_delaunay_triangles(p).geoms)-p.area)<.01
out={'vertices':v,'faces':f,'original_sleepers':len(parts),'union_area_m2':p.area,'limits':'Unioned illustrative sleeper footprints remove overlap only; no measured switch/turnout geometry or actual sleeper schedule.'};(root/'assets/source/environment/expanded-sleepers-unioned.json').write_text(json.dumps(out,separators=(',',':'))+'\n');print('VERIFIED sleeper union',len(parts),len(f),p.area)
