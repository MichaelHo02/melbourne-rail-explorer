"""Historical geometry-only bridge elevation evidence; no Blender mutation."""
from pathlib import Path
import array,json,hashlib,sys
import numpy as np,pyproj,shapely
from shapely.geometry import Polygon
ROOT=Path(__file__).resolve().parents[1]
buildings=json.loads((ROOT/'public/data/buildings.json').read_text())['buildings']
ids=['24181','39116','39117','22347']
foot={sid:Polygon([(x,-y) for x,y in next(b for b in buildings if b['id']==sid)['ring']]).buffer(-1) for sid in ids}
foot['princes_south']=Polygon([(65,-289),(250,-289),(250,-179),(65,-179)])
ids.append('princes_south')
inverse=pyproj.Transformer.from_crs(28355,4326,always_xy=True)
groups={sid:{} for sid in ids}; tiles=[]
for tile in (sys.argv[1:] or ['C4-31','C4-32','C4-33','C4-35']):
    path=Path('/tmp/flinders-photomesh')/(tile+'.obj');raw=array.array('d');faces=array.array('i')
    with path.open() as src:
        for line in src:
            if line.startswith('v '):raw.extend(map(float,line.split()[1:4]))
            elif line.startswith('f '):
                ix=[int(s.split('/')[0])-1 for s in line.split()[1:]]
                if len(ix)==3:faces.extend(ix)
    a=np.asarray(raw).reshape(-1,3);lon,lat=inverse.transform(a[:,0],a[:,1])
    local=np.column_stack(((lon-144.9671)*87939,(lat+37.8183)*111320,a[:,2]-4.1));tri=np.asarray(faces,dtype=np.int32).reshape(-1,3)
    counts={sid:0 for sid in ids}
    for start in range(0,len(tri),50000):
        p=local[tri[start:start+50000]];c=p.mean(axis=1);n=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]);length=np.linalg.norm(n,axis=1)
        # Bridge evidence excludes low river/water artefacts; south terrain may be lower.
        valid=(c[:,2]>1)&(c[:,2]<18)&(n[:,2]>.8*length)&(length>1e-9)
        for sid,poly in foot.items():
            kept=c[valid&(True if sid=='princes_south' else c[:,2]>3)&shapely.contains_xy(poly,c[:,0],c[:,1])];counts[sid]+=len(kept)
            for x,y,z in kept:groups[sid].setdefault((int(np.floor(x)),int(np.floor(y))),[]).append(float(z))
    tiles.append({'tile':tile,'triangles':len(tri),'kept':counts});print(tiles[-1],flush=True)
out={'source':'https://discover.data.vic.gov.au/dataset/city-of-melbourne-3d-textured-mesh-photomesh-2020','capture':'May2020','license':'CC BY4.0','tiles':tiles,'bridges':{},'limits':'Historical upward-normal>.8 triangle centres inside retained footprint inset1m,z1..18m. One-metre median cells can retain cars, railings and artefacts. Elevation evidence, not present-day surveyed engineering dimensions; no textures.'}
for sid,g in groups.items():
    samples=[[x+.5,y+.5,float(np.median(z))] for (x,y),z in g.items()]
    heights=np.array([s[2] for s in samples]);out['bridges'][sid]={'samples':samples,'count':len(samples),'quantiles':np.quantile(heights,[.1,.25,.5,.75,.9]).tolist() if len(heights) else []}
    print(sid,out['bridges'][sid]['count'],out['bridges'][sid]['quantiles'],flush=True)
(ROOT/'assets/source/environment/yarra-bridge-captured-levels.json').write_text(json.dumps(out)+'\n')
