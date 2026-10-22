"""Extract municipality's 2020 scan geometry; no photographic textures."""
import json,pathlib,array,hashlib,time
import numpy as np
import pyproj,shapely
from shapely.geometry import Polygon
from shapely.ops import unary_union
root=pathlib.Path(__file__).resolve().parents[1]
raw=json.load(open('/Users/holeminhthach/Developer/train-simulator/public/data/buildings-raw.json'))
fwd=pyproj.Transformer.from_crs(4326,28355,always_xy=True)
inv=pyproj.Transformer.from_crs(28355,4326,always_xy=True)
station=[b for b in raw if b['structure_id']=='804817']
clip=unary_union([Polygon([fwd.transform(*p) for p in b['geo_shape']['geometry']['coordinates'][0]]) for b in station]).buffer(1)
verts=[];faces=[];audit=[]
index=json.load(open(root/'assets/source/environment/flinders-photomesh-download-index.json'))['zip_entries']
for tile in sorted(index,key=lambda r: {'C4-34':0,'C4-35':1,'C4-28':2,'C4-29':3}[r['region']]):
 path=pathlib.Path('/tmp/flinders-photomesh')/(tile['region']+'.obj')
 deadline=time.monotonic()+900
 while not path.exists() or path.stat().st_size!=tile['obj']['size']:
  if time.monotonic()>deadline:raise RuntimeError('Incomplete source tile '+tile['region'])
  time.sleep(1)
 xyz=array.array('d');remap=None;count=0;kept=0
 with path.open() as source:
  for line in source:
   if line.startswith('v '):xyz.extend(map(float,line.split()[1:4]))
   elif line.startswith('f '):
    if remap is None:
     a=np.asarray(xyz).reshape(-1,3);valid=shapely.contains_xy(clip,a[:,0],a[:,1]);ids=np.flatnonzero(valid);remap=np.full(len(a),-1,dtype=np.int64);remap[ids]=np.arange(len(ids))+len(verts);lon,lat=inv.transform(a[ids,0],a[ids,1]);local=np.column_stack(((lon-144.9671)*87939,(lat+37.8183)*111320,a[ids,2]-4.1));verts.extend(local.tolist())
    ids=[int(p.split('/')[0])-1 for p in line.split()[1:]];count+=1
    if all(i>=0 and remap[i]>=0 for i in ids):faces.append([int(remap[i]) for i in ids]);kept+=1
 audit.append({'tile':path.stem,'source_faces':count,'retained_faces':kept});print(audit[-1],flush=True)
# Compact away unreferenced vertices; keep source triangles and winding.
used=sorted(set(i for f in faces for i in f));mapping={old:new for new,old in enumerate(used)}
out=root/'assets/source/environment/flinders-photomesh-2020.obj'
with out.open('w') as target:
 target.write('# City of Melbourne May 2020 photomesh; source geometry only, textures omitted\n')
 for i in used:target.write('v '+' '.join(f'{x:.5f}' for x in verts[i])+'\n')
 for f in faces:target.write('f '+' '.join(str(mapping[i]+1) for i in f)+'\n')
report={'source':'https://discover.data.vic.gov.au/dataset/city-of-melbourne-3d-textured-mesh-photomesh-2020','capture':'May 2020','license':'CC BY 4.0','tiles':audit,'vertices':len(used),'faces':len(faces),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'limits':'2020 capture, not present-day survey. Crop uses 2023 station structure804817 footprint plus authored 1m tolerance. MGA55 EPSG28355 transformed to geographic/local scene; authored flat datum offset AHD4.1m. Photographic textures omitted. Scan may contain occlusions, artefacts and captured vehicles/people; inspect before final use.'}
json.dump(report,open(out.with_suffix('.json'),'w'),indent=2);print('WROTE',out,len(used),len(faces),flush=True)
