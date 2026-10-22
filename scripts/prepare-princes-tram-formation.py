"""Use municipal road asset polygons, no width buffer assumption."""
from pathlib import Path
import json,hashlib
from shapely.geometry import shape,Polygon
from shapely.ops import transform
from shapely import constrained_delaunay_triangles
r=Path(__file__).resolve().parents[1];p=r/'assets/source/environment/princes-bridge-road-surface-records.json';d=json.loads(p.read_text());b=next(b for b in json.loads((r/'public/data/buildings.json').read_text())['buildings'] if str(b['id'])=='36402');deck=Polygon([(x,-y) for x,y in b['ring']]);parts=[]
for a in d['records']['results']:
 if a.get('type')!='Road Tram Formation':continue
 geo=a['json_geometry'];g=shape(geo['geometry'] if geo['type']=='Feature' else geo);g=transform(lambda x,y,z=None:((x-144.9671)*87939,(y+37.8183)*111320),g).intersection(deck);vs=[];fs=[]
 for tri in constrained_delaunay_triangles(g).geoms:
  xy=list(tri.exterior.coords)[:3];
  if (xy[1][0]-xy[0][0])*(xy[2][1]-xy[0][1])-(xy[1][1]-xy[0][1])*(xy[2][0]-xy[0][0])<0:xy.reverse()
  k=len(vs);vs.extend([(x,y,9.54) for x,y in xy]);fs.append([k,k+1,k+2])
 if fs:parts.append({'assetid':a['assetid'],'type':a['type'],'surface_material':a.get('surfacematerial'),'area_m2':g.area,'vertices':vs,'faces':fs})
out={'source_url':d['source_url'],'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'parts':parts,'limits':'Municipal road asset polygons clipped to retained2023 survey36402. Tram assets are labelled adjacent Swanston Street but intersect bridge deck. Geometry clipped to survey36402. Authored flat top9.54m and grey concrete shade; current rails, markings, exact heights and southern coverage unverified.'};(r/'assets/source/environment/princes-bridge-tram-formation.json').write_text(json.dumps(out,indent=2)+'\n');print([(p['assetid'],p['type'],round(p['area_m2'],1),len(p['faces'])) for p in parts])
