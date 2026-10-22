"""Retained Vicmap trail alignments clipped to named park parcels."""
import json
import argparse
from pathlib import Path
from shapely import Polygon,LineString,union_all,constrained_delaunay_triangles,set_precision
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--roads-source',default='src/data/corridor-source.json');parser.add_argument('--parks-source',default='assets/source/environment/city-park-surfaces.json');parser.add_argument('--output',default='assets/source/environment/city-park-paths.json');args=parser.parse_args()
s=json.loads((ROOT/args.roads_source).read_text());parks=json.loads((ROOT/args.parks_source).read_text())
park=union_all([Polygon([(p['vertices'][i][0],p['vertices'][i][1]) for i in face]) for p in parks['parts'] if p['finish']==0 for face in p['faces']]);paths=[];ids=[]
for f in (s['features'] if 'features' in s else s['layers']['roads']['features']):
 if f['properties'].get('feature_type_code')!='trail':continue
 coords=f['geometry']['coordinates'];lines=[coords] if f['geometry']['type']=='LineString' else coords
 pieces=[]
 for line in lines:
  shape=LineString([((lon-144.9671)*87939,(lat+37.8183)*111320) for lon,lat in line]).buffer(1.2,cap_style='round',join_style='round').intersection(park)
  if shape.area>.1:pieces.append(shape)
 if pieces:paths.extend(pieces);ids.append(f['properties']['ufi'])
shape=set_precision(union_all(paths),.01);v=[];faces=[];area=0
for tri in constrained_delaunay_triangles(shape).geoms:
 coords=list(tri.exterior.coords)[:3];a,b,c=coords
 if (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])<0:coords.reverse()
 start=len(v);v.extend([(x,y,.345) for x,y in coords]);faces.append([start,start+1,start+2]);area+=tri.area
assert abs(area-shape.area)<max(.01,shape.area*1e-8)
result={'revision':s.get('sourceSha256','retained-corridor')+'-'+parks.get('revision','retained-corridor'),'source':s.get('source') or s['sources']['roads']['url'],'park_source':parks['source'],'license':'CC BY 4.0','source_ufis':ids,'vertices':v,'faces':faces,'area':area,'limits':'Retained Vicmap trails clipped to retained named park parcels, preserving parcel holes. Authored 2.4m width, pale path surface and flat datum; generated surface snapped to a 1cm grid to avoid float-precision sliver triangles; actual path widths, materials and present-day condition unverified.'}
(ROOT/args.output).write_text(json.dumps(result,separators=(',',':'))+'\n');print('Retained park trail features:',len(ids),'path area:',round(area),'triangles:',len(faces))
