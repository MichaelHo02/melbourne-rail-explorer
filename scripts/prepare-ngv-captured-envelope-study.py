"""Extract NGV upward surfaces from both required2020 tiles; evidence only."""
import array,json,hashlib
from pathlib import Path
import numpy as np,pyproj,shapely
from shapely.geometry import Polygon
ROOT=Path(__file__).resolve().parents[1];b=next(b for b in json.loads((ROOT/'public/data/buildings.json').read_text())['buildings'] if str(b['id'])=='16221');foot=Polygon([(x,-y) for x,y in b['ring']]).buffer(.2);inv=pyproj.Transformer.from_crs(28355,4326,always_xy=True);vertices=[];faces=[];audit=[];centres=[]
for tile in ['C4-29','C4-30']:
 path=Path('/tmp/flinders-photomesh')/(tile+'.obj');raw=array.array('d');ids=[]
 with path.open() as src:
  for line in src:
   if line.startswith('v '):raw.extend(map(float,line.split()[1:4]))
   elif line.startswith('f '):
    ix=[int(s.split('/')[0])-1 for s in line.split()[1:]]
    if len(ix)==3:ids.append(ix)
 a=np.asarray(raw).reshape(-1,3);lon,lat=inv.transform(a[:,0],a[:,1]);local=np.column_stack(((lon-144.9671)*87939,(lat+37.8183)*111320,a[:,2]-4.1));tri=np.asarray(ids,dtype=np.int32);count=0
 for start in range(0,len(tri),50000):
  ix=tri[start:start+50000];p=local[ix];c=p.mean(axis=1);n=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]);length=np.linalg.norm(n,axis=1);valid=(c[:,2]>6)&(c[:,2]<40)&(length>1e-9)&shapely.contains_xy(foot,c[:,0],c[:,1]);kept=ix[valid];centres.extend(c[valid].tolist());count+=len(kept)
  for face in local[kept]:
   k=len(vertices);vertices.extend(face.tolist());faces.append([k,k+1,k+2])
 audit.append({'tile':tile,'source_triangles':len(tri),'retained_envelope_triangles':count});print('CAPTURE_TILE_EXTRACTED',audit[-1],flush=True)
groups={}
for x,y,z in centres:groups.setdefault((int(np.floor(x)),int(np.floor(y))),[]).append((x,y,z))
samples=[np.median(v,axis=0).tolist() for v in groups.values()];assert samples and max(q[0] for q in samples)>275,'Eastern capture missing'
out={'source':'https://discover.data.vic.gov.au/dataset/city-of-melbourne-3d-textured-mesh-photomesh-2020','capture':'May2020','license':'CC BY4.0','tiles':audit,'vertices':vertices,'faces':faces,'samples':samples,'grid_cells':len(samples),'sample_bounds':[[min(q[i] for q in samples) for i in range(3)],[max(q[i] for q in samples) for i in range(3)]],'limits':'Historical geometry-only envelope study, both required tiles.0.2m buffered lower footprint and heights6..40m authored; includes walls, roof and potential plaza/vegetation artefacts. Median cells contain mixed vertical surfaces and are not roof-height evidence. Atrium, plant and scan artefacts may remain. No photographic assets. Evidence only, not installed completed roof.'}
(ROOT/'assets/source/environment/federation-ngv-captured-envelope-study.json').write_text(json.dumps(out)+'\n');print('CAPTURED_ENVELOPE_STUDY',len(faces),len(samples),out['sample_bounds'],flush=True)
