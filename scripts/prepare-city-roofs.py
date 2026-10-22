"""Merge coplanar surveyed roof sections without changing surveyed heights.
Requires Shapely 2.1+. Roof colour remains authored, not individual evidence.
"""
import json
from collections import defaultdict
from pathlib import Path
from shapely import Polygon, union_all, constrained_delaunay_triangles
ROOT=Path(__file__).resolve().parents[1]
source=json.loads((ROOT/'public/data/buildings.json').read_text())
front=json.loads((ROOT/'public/models/environment/viaduct-frontage.json').read_text())
excluded={i for s in front['structures'].values() for i in s['objectIds']}
groups=defaultdict(list);ids=[]
for item in source['buildings']:
    ring=item['ring'][:]
    if ring[0]==ring[-1]:ring.pop()
    if len(ring)<3 or item['id'] in excluded:continue
    x=sum(p[0] for p in ring)/len(ring);z=sum(p[1] for p in ring)/len(ring)
    if not (-2000<=x<=1250 and -1750<=z<=800):continue
    top=item['base']+item['height']
    if item['kind'] in ('Bridge','Jetty'):top=max(3,top)
    shape=Polygon([(x,-z) for x,z in ring]).buffer(0)
    if shape.is_empty:continue
    groups[round(top,4)].append(shape);ids.append(item['id'])
vertices=[];faces=[];materials=[];area=0
for height,shapes in sorted(groups.items()):
    roof=union_all(shapes);triangles=constrained_delaunay_triangles(roof);total=0
    for triangle in triangles.geoms:
        points=list(triangle.exterior.coords)[:3];start=len(vertices)
        a,b,c=points
        if (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])<0:points.reverse()
        vertices.extend([(x,y,height) for x,y in points]);faces.append([start,start+1,start+2]);materials.append(int(height*10)%3);total+=triangle.area
    assert abs(total-roof.area)<max(.01,roof.area*1e-8),(height,total,roof.area)
    area+=total
result={'source':source['url'],'license':source['license'],'limits':'Survey roof sections unioned at their retained heights; finishes authored; no new height or roof equipment evidence','source_ids':ids,'vertices':vertices,'faces':faces,'materials':materials,'area':area}
(ROOT/'assets/source/environment/city-roof-surfaces.json').write_text(json.dumps(result,separators=(',',':'))+'\n')
print('Merged roof sections:',len(ids),'height groups:',len(groups),'triangles:',len(faces))
