"""Union illustrative ballast beds on explicitly ordinary railway features."""
import json,hashlib
from pathlib import Path
from shapely.geometry import LineString,box
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles,set_precision
root=Path(__file__).resolve().parents[1];source=root/'assets/source/environment/city-rails-expanded.json';data=json.loads(source.read_text());parts=[];ids=[];alignments=[]
old=json.loads((root/'src/data/corridor-source.json').read_text());existing={f['properties']['ufi'] for f in old['layers']['rails']['features']}
for f in data['features']:
 if f['properties']['feature_type_code']!='railway' or f['properties']['ufi'] in existing:continue
 g=f['geometry'];lines=[g['coordinates']] if g['type']=='LineString' else g['coordinates']
 for line in lines:
  alignments.append([((p[0]-144.9671)*87939,(p[1]+37.8183)*111320) for p in line])
  parts.append(LineString([((p[0]-144.9671)*87939,(p[1]+37.8183)*111320) for p in line]).buffer(1.8,cap_style=2,join_style=2))
 ids.append(f['properties']['ufi'])
p=set_precision(unary_union(parts).intersection(box(-2000,-800,1250,1750)),.01);verts=[];faces=[]
triangles=list(constrained_delaunay_triangles(p).geoms)
for t in triangles:
 pts=list(t.exterior.coords)[:3]
 if sum(pts[i][0]*pts[(i+1)%3][1]-pts[(i+1)%3][0]*pts[i][1] for i in range(3))<0:pts.reverse()
 start=len(verts);verts.extend([[x,y,.4] for x,y in pts]);faces.append([start,start+1,start+2])
assert abs(sum(t.area for t in triangles)-p.area)<.01
out={'alignments':alignments,'vertices':verts,'faces':faces,'area_m2':p.area,'source_ufis':ids,'source_url':data['source'],'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'limits':'Additional union of authored 3.6 m ballast beds on ordinary railway features only. Bridges, underground rail and tramways excluded by explicit feature type. Flat datum and width illustrative; not complete station tracks or surveyed yard boundary.'}
(root/'assets/source/environment/city-trackbeds-expanded-additions.json').write_text(json.dumps(out,separators=(',',':'))+'\n');print('VERIFIED trackbed union:',len(ids),'features;',p.area,'m2;',len(faces),'triangles')
