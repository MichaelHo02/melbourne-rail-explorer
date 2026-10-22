"""Infer authored street-parallel seat orientation from public road geometry."""
import json,math
from pathlib import Path
from shapely.geometry import LineString,Point
root=Path(__file__).resolve().parents[1];p=root/'assets/source/environment/city-authored-steel-seats.json';d=json.loads(p.read_text());roads=json.loads((root/'assets/source/environment/city-roads-expanded.json').read_text());segments=[]
for f in roads['features']:
 lines=[f['geometry']['coordinates']] if f['geometry']['type']=='LineString' else f['geometry']['coordinates']
 for line in lines:
  xy=[((v[0]-144.9671)*87939,(v[1]+37.8183)*111320) for v in line]
  segments.extend((LineString([a,b]),a,b,f['properties']['ufi']) for a,b in zip(xy,xy[1:]) if math.dist(a,b)>.01)
for r in d['records']:
 seg,a,b,ufi=min(segments,key=lambda s:s[0].distance(Point(r['preview_xy'])));r['authored_rotation_z']=math.atan2(b[1]-a[1],b[0]-a[0]);r['orientation_road_ufi']=ufi
p.write_text(json.dumps(d,indent=2)+'\n');print('VERIFIED street-parallel authored seat rotations',len(d['records']))
