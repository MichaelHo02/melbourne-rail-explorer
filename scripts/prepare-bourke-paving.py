"""Authored local side paving on retained Bourke street segment."""
import json
from pathlib import Path
from shapely.geometry import LineString,Polygon
from shapely.ops import substring,unary_union
from shapely import constrained_delaunay_triangles
root=Path(__file__).resolve().parents[1];d=json.loads((root/'assets/source/environment/city-roads-expanded.json').read_text());r=next(f for f in d['features'] if f['properties']['ufi']==76347243);coords=r['geometry']['coordinates'];line=LineString([((v[0]-144.9671)*87939,(v[1]+37.8183)*111320) for v in coords]);line=substring(line,20,line.length-20);p=line.buffer(9,cap_style=2,join_style=2).difference(line.buffer(6,cap_style=2,join_style=2));obstacles=[]
for b in json.loads((root/'public/data/buildings.json').read_text())['buildings']:
 if b['base']>.1:continue
 q=Polygon([(x,-y) for x,y in b['ring']])
 if q.is_valid and q.intersects(p):obstacles.append(q)
p=p.difference(unary_union(obstacles));v=[];f=[]
for t in constrained_delaunay_triangles(p).geoms:
 points=list(t.exterior.coords)[:3];i=len(v);v.extend((x,y,.30) for x,y in points);f.append([i,i+1,i+2])
out={'vertices':v,'faces':f,'area_m2':p.area,'source_ufi':76347243,'limits':'Local authored side paving between 6 and9m from Vicmap street centreline, ends trimmed20m; flat .30m level and bluestone appearance illustrative. Inventory furniture points support need to reconcile crude asphalt width, not actual kerb outline or present-day surface.'};(root/'assets/source/environment/bourke-authored-side-paving.json').write_text(json.dumps(out,indent=2)+'\n');print('VERIFIED Bourke side paving',p.area,len(f))
