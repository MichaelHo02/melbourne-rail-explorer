"""Conservative authored interior asphalt patch; not a surveyed carpark boundary."""
import json,math
from pathlib import Path
from shapely import Polygon,union_all,constrained_delaunay_triangles
R=Path(__file__).resolve().parents[1];roof=json.loads((R/'assets/source/environment/qvm-authored-roofs.json').read_text());origin=roof['origin'];u=roof['axis'];n=roof['normal']
def world(x,y):return (origin[0]+u[0]*x+n[0]*y,origin[1]+u[1]*x+n[1]*y)
p=Polygon([world(x,y) for x,y in [(8,170),(154,170),(154,265),(8,265)]])
exclude=[]
for b in json.loads((R/'public/data/buildings.json').read_text())['buildings']:
 if b['base']<=.1:exclude.append(Polygon([(x,-y) for x,y in b['ring']]).buffer(0))
roads=json.loads((R/'assets/source/environment/city-road-surfaces-expanded.json').read_text())
for part in [roads['asphalt'],roads['paving']]:
 v=part['vertices'];exclude.extend(Polygon([v[i][:2] for i in f]) for f in part['faces'])
p=p.difference(union_all(exclude));v=[];f=[]
for t in constrained_delaunay_triangles(p).geoms:
 pts=list(t.exterior.coords)[:3]
 if sum(pts[i][0]*pts[(i+1)%3][1]-pts[(i+1)%3][0]*pts[i][1] for i in range(3))<0:pts.reverse()
 start=len(v);v.extend([(x,y,.24) for x,y in pts]);f.append([start,start+1,start+2])
out={'vertices':v,'faces':f,'area_m2':p.area,'source':'https://qvm.com.au/parking/','status_reference':'https://qvm.com.au/gurrowa-place-update/','plan_reference':'https://mvga-prod-files.s3.ap-southeast-4.amazonaws.com/public/2024-07/qvm-conservation-management-plan.pdf','limits':'Conservative authored interior patch located south of shed ranges from historical 2002 plan. Exact footprint, present surface, bay layout and construction staging unverified. Road paving and ground-building footprints excluded. Asphalt finish and flat level authored; no occupancy inference.'}
(R/'assets/source/environment/qvm-authored-carpark-surface.json').write_text(json.dumps(out,separators=(',',':'))+'\n');print(p.area,len(f))
