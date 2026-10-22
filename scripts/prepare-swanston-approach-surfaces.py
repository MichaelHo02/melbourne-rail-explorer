"""Municipal approach planforms with historical captured-height interpolation."""
from pathlib import Path
import json,hashlib
import numpy as np
from shapely.geometry import shape,Polygon
from shapely.ops import transform
from shapely import constrained_delaunay_triangles
r=Path(__file__).resolve().parents[1];raw=r/'assets/source/environment/princes-bridge-road-surface-records.json';d=json.loads(raw.read_text());model=r/'assets/source/environment/federation-street-level-model.json';samples=np.array(json.loads(model.read_text())['samples']);b=next(q for q in json.loads((r/'public/data/buildings.json').read_text())['buildings'] if str(q['id'])=='36402');bridge=Polygon([(x,-y) for x,y in b['ring']]);parts=[]
def height(x,y):
 ds=((samples[:,:2]-[x,y])**2).sum(1);ix=np.argsort(ds)[:8];w=1/np.maximum(ds[ix],1);h=float((samples[ix,2]*w).sum()/w.sum());t=max(0,min(1,(y+52)/22));t=t*t*(3-2*t);return 6.2*(1-t)+h*t
for a in d['records']['results']:
 if not a['roadsegmentdescription'].startswith('Swanston Street between Princes Bridge'):continue
 geo=a['json_geometry'];g=shape(geo.get('geometry',geo));g=transform(lambda x,y,z=None:((x-144.9671)*87939,(y+37.8183)*111320),g).difference(bridge);vs=[];fs=[]
 if g.is_empty:continue
 offset=.035 if a['type'] in ['Road Carriageway','Road Tram Formation','Road Channel'] else .15
 def add(xy):
  lengths=[np.linalg.norm(np.array(xy[(i+1)%3])-xy[i]) for i in range(3)];i=int(np.argmax(lengths))
  if lengths[i]>6:
   j=(i+1)%3;k=(i+2)%3;mid=tuple((np.array(xy[i])+xy[j])/2);add([xy[i],mid,xy[k]]);add([mid,xy[j],xy[k]]);return
  if (xy[1][0]-xy[0][0])*(xy[2][1]-xy[0][1])-(xy[1][1]-xy[0][1])*(xy[2][0]-xy[0][0])<0:xy.reverse()
  k=len(vs);vs.extend([(x,y,height(x,y)+offset) for x,y in xy]);fs.append([k,k+1,k+2])
 for tri in constrained_delaunay_triangles(g).geoms:add(list(tri.exterior.coords)[:3])
 if fs:parts.append({'assetid':a['assetid'],'type':a['type'],'surface_material':a['surfacematerial'],'area_m2':g.area,'vertices':vs,'faces':fs})
out={'source_url':d['source_url'],'source_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'height_source_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'parts':parts,'limits':'Municipal mapped planforms outside bridge footprint. Historical2020 eight-nearest inverse-distance ground interpolation; authored22m blend to6.2m bridge deck,6m triangle subdivision, surface offsets35/150mm. Current heights, pavement material colours and unknown material classes approximate. No photographic textures.'};(r/'assets/source/environment/swanston-approach-authored-surfaces.json').write_text(json.dumps(out)+'\n');print('APPROACH_POLYGONS',len(parts),sum(p['area_m2'] for p in parts),sum(len(p['faces']) for p in parts))
