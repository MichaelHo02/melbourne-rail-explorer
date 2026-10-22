"""Authored median height skin; only locally supported captured roof grid cells."""
import json,statistics,hashlib
from pathlib import Path
r=Path(__file__).resolve().parents[1];p=r/'assets/source/environment/flinders-concourse-captured-cells.json';d=json.loads(p.read_text());cells={(int(c['xy'][0]-.5),int(c['xy'][1]-.5)):c for c in d['cells'] if 10<c['median_z']<14.5 }
z={}
for (x,y),c in cells.items():
 ns=[cells[(x+i,y+j)]['median_z'] for i in (-1,0,1) for j in (-1,0,1) if (x+i,y+j) in cells]
 if len(ns)>=4:z[(x,y)]=statistics.median(ns)
# Fill isolated missing cells only when seven surrounding captured cells support them.
for x in range(-30,70):
 for y in range(-60,55):
  if (x,y) in z:continue
  ns=[z[(x+i,y+j)] for i in (-1,0,1) for j in (-1,0,1) if (i or j) and (x+i,y+j) in z]
  if len(ns)>=7 and max(ns)-min(ns)<1:z[(x,y)]=statistics.median(ns)
vertices=[];faces=[];indices={};quads=[]
def vid(k):
 if k not in indices:
  indices[k]=len(vertices);vertices.append([k[0]+.5,k[1]+.5,z[k]+.05])
 return indices[k]
for x,y in sorted(z):
 ks=[(x,y),(x+1,y),(x+1,y+1),(x,y+1)]
 if all(k in z for k in ks) and max(z[k] for k in ks)-min(z[k] for k in ks)<2:
  ids=[vid(k) for k in ks];faces.extend([[ids[0],ids[1],ids[2]],[ids[0],ids[2],ids[3]]]);quads.append([x+.5,y+.5])
limits='Authored 3x3 median of one-metre captured roof cells; 50mm offset. Grid boundaries and smoothing approximate. Locally supported quads; isolated gaps filled from seven surrounding cells only; missing cells and >2m jumps excluded. Scan geometry retained for recovery. No measured current roof reconstruction claim.'
out={'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'vertices':vertices,'faces':faces,'quad_origins':quads,'limits':limits};(r/'assets/source/environment/flinders-concourse-continuous-skin.json').write_text(json.dumps(out,separators=(',',':'))+'\n');print(len(quads),'m2 supported grid',len(faces),'triangles')
