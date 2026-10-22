"""Reconstruct western narrow Federation roof from retained May2020 samples."""
import json,numpy as np
from shapely.geometry import Polygon
from shapely import make_valid,constrained_delaunay_triangles
from pathlib import Path
root=Path(__file__).resolve().parents[1];r=root/'assets/source/environment'
s=next(p for p in json.loads((r/'federation-ground-datum-sections.json').read_text()) if p['id']=='4607');a=np.array(next(p for p in json.loads((r/'federation-roof-captured-samples.json').read_text()) if p['id']=='4607')['samples']);A=np.c_[a[:,:2],np.ones(len(a))];c=np.linalg.lstsq(A,a[:,2],rcond=None)[0];e=np.abs(A@c-a[:,2]);assert np.median(e)<.05
poly=make_valid(Polygon(s['ring']));vs=[];fs=[]
for t in constrained_delaunay_triangles(poly).geoms:
 f=[]
 for x,y in list(t.exterior.coords)[:3]:f.append(len(vs));vs.append([x,y,float(c[0]*x+c[1]*y+c[2])])
 fs.append(f)
d={'id':'4607','plane':c.tolist(),'vertices':vs,'faces':fs,'ring':s['ring'],'base':s['base']+s['offset'],'old_top':s['base']+s['offset']+s['height'],'samples':len(a),'median_residual':float(np.median(e)),'max_residual':float(e.max()),'limits':'Single sloped roof fitted to May2020 samples; least squares plane and cleaned footprint boundary authored reconstruction. Not current surveyed roof or facade finish.'}
(r/'federation-west-shard-roof-fit.json').write_text(json.dumps(d));print(d['samples'],d['median_residual'],len(fs))
