"""Clip retained named Southbank parcels to an illustrative upgraded reach."""
import json,hashlib
from pathlib import Path
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
root=Path(__file__).resolve().parents[1];source=root/'assets/source/environment/city-park-surfaces-expanded.json';d=json.loads(source.read_text());parts=[];ids=[]
for p in d['parts']:
 if p['name']!='Southbank Promenade':continue
 pts=p['vertices'];shape=unary_union([Polygon([pts[i][:2] for i in f]) for f in p['faces']]).intersection(box(-170,-340,110,-100))
 if not shape.is_empty:parts.append(shape);ids.append(p['id'])
p=unary_union(parts);v=[];f=[]
for t in constrained_delaunay_triangles(p).geoms:
 pts=list(t.exterior.coords)[:3]
 if sum(pts[i][0]*pts[(i+1)%3][1]-pts[(i+1)%3][0]*pts[i][1] for i in range(3))<0:pts.reverse()
 i=len(v);v.extend([[x,y,.335] for x,y in pts]);f.append([i,i+1,i+2])
out={'vertices':v,'faces':f,'source_ids':ids,'area_m2':p.area,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'reference':'https://participate.melbourne.vic.gov.au/emerging-tech-testbed/southbank-promenade-1/works-between-princes-bridge-and-evan-walker-bridge-are-now-complete','limits':'Retained Southbank Promenade parcels clipped to illustrative east-reach bounds. Authored bluestone palette and paver schedule; exact upgrade boundary, upper/lower levels and current furniture unresolved.'};(root/'assets/source/environment/southbank-authored-paving.json').write_text(json.dumps(out,separators=(',',':'))+'\n');print(len(f),p.area,ids)
