"""Clip authored carriageway widths on retained bridge alignments to survey decks."""
import json
from pathlib import Path
from shapely import Polygon,LineString,union_all,constrained_delaunay_triangles
ROOT=Path(__file__).resolve().parents[1]
s=json.loads((ROOT/'src/data/corridor-source.json').read_text());bs=json.loads((ROOT/'public/data/buildings.json').read_text());lines=[]
for f in s['layers']['roads']['features']:
 if f['properties'].get('feature_type_code')!='bridge':continue
 coords=f['geometry']['coordinates'];parts=[coords] if f['geometry']['type']=='LineString' else coords
 for part in parts:
  line=LineString([((lon-144.9671)*87939,(lat+37.8183)*111320) for lon,lat in part]);lines.append((f['properties']['ufi'],line.buffer(4.5,cap_style='flat')))
results=[]
for b in bs['buildings']:
 if b['kind']!='Bridge':continue
 ring=b['ring'];x=sum(p[0] for p in ring)/len(ring);z=sum(p[1] for p in ring)/len(ring)
 if not (-2000<=x<=1250 and -1750<=z<=800):continue
 deck=Polygon([(x,-z) for x,z in ring]).buffer(0);inset=deck.buffer(-.8)
 hits=[(ufi,shape.intersection(inset)) for ufi,shape in lines if shape.intersection(inset).area>2]
 if not hits:continue
 surface=union_all([shape for _,shape in hits]);v=[];faces=[];area=0;top=max(3,b['base']+b['height'])+.03
 for tri in constrained_delaunay_triangles(surface).geoms:
  coords=list(tri.exterior.coords)[:3];a,c,d=coords
  if (c[0]-a[0])*(d[1]-a[1])-(c[1]-a[1])*(d[0]-a[0])<0:coords.reverse()
  start=len(v);v.extend([(x,y,top) for x,y in coords]);faces.append([start,start+1,start+2]);area+=tri.area
 assert abs(area-surface.area)<max(.01,surface.area*1e-8)
 results.append({'survey_id':b['id'],'source_ufis':sorted(set(ufi for ufi,_ in hits)),'vertices':v,'faces':faces,'area':area})
r={'road_source':s['sources']['roads']['url'],'survey_source':bs['url'],'license':'CC BY 4.0','limits':'Retained Vicmap bridge road alignments clipped to retained survey deck envelopes. Authored 9m carriageway width, 0.8m deck inset and 0.03m surface offset; no surveyed lane allocation, kerb, material or current condition claim.','parts':results}
(ROOT/'assets/source/environment/city-bridge-surfaces.json').write_text(json.dumps(r,separators=(',',':'))+'\n');print('Bridge road surfaces:',len(results),'area:',round(sum(p['area'] for p in results)))
