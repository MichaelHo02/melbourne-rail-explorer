"""Union retained Vicmap road ribbons into non-overlapping preview surfaces.
Requires Shapely 2.1+. Dimensions remain authored; no new geographic evidence.
"""
import json
import argparse
from pathlib import Path
from shapely import LineString, union_all, constrained_delaunay_triangles, box
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--source',default='src/data/observatory-roads.json');parser.add_argument('--output',default='assets/source/environment/city-road-surfaces.json');parser.add_argument('--clip-bounds',nargs=4,type=float);args=parser.parse_args()
source=json.loads((ROOT/args.source).read_text())
major={'FLINDERS STREET','COLLINS STREET','BOURKE STREET','LONSDALE STREET','LA TROBE STREET','SWANSTON STREET','ELIZABETH STREET','QUEEN STREET','WILLIAM STREET','KING STREET','SPENCER STREET','RUSSELL STREET','EXHIBITION STREET','SPRING STREET'}
roads=[];pavements=[]
for feature in source['features']:
    p=feature['properties']
    if str(p.get('vehicular_access'))!='1':continue
    width=9 if str(p.get('ezi_road_name','')).upper() in major else (6 if int(p.get('class_code',5))<4 else 3.2)
    lines=[feature['geometry']['coordinates']] if feature['geometry']['type']=='LineString' else feature['geometry']['coordinates']
    for line in lines:
        points=[((p[0]-144.9671)*87939,(p[1]+37.8183)*111320) for p in line]
        shape=LineString(points)
        if shape.length<.1:continue
        roads.append(shape.buffer(width,cap_style='flat',join_style='mitre'))
        pavements.append(shape.buffer(width+2,cap_style='flat',join_style='mitre'))
asphalt=union_all(roads);paving=union_all(pavements).difference(asphalt)
if args.clip_bounds:
    clip=box(*args.clip_bounds);asphalt=asphalt.intersection(clip);paving=paving.intersection(clip)
def triangulated(shape):
    vertices=[];faces=[];indices={};total=0
    for triangle in constrained_delaunay_triangles(shape).geoms:
        face=[]
        for point in list(triangle.exterior.coords)[:3]:
            key=tuple(round(c,6) for c in point)
            if key not in indices:indices[key]=len(vertices);vertices.append(key)
            face.append(indices[key])
        a,b,c=[vertices[i] for i in face]
        if (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])<0:face.reverse()
        faces.append(face);total+=triangle.area
    assert abs(total-shape.area)<max(.01,shape.area*1e-8),(total,shape.area)
    return {'vertices':vertices,'faces':faces,'area':shape.area}
result={'source':source['source'],'license':source['license'],'feature_count':len(source['features']),'bounds':source.get('bounds'),'preview_clip_bounds':args.clip_bounds,'limits':'Official horizontal road centrelines; authored preview widths and level, current kerbs unverified','asphalt':triangulated(asphalt),'paving':triangulated(paving)}
(ROOT/args.output).write_text(json.dumps(result,separators=(',',':'))+'\n')
print({k:len(result[k]['faces']) for k in ('asphalt','paving')})
