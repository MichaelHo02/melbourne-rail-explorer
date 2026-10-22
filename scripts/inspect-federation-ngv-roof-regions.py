"""Plot retained NGV capture after schematic Atrium exclusion; evidence only."""
import json
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon,Point
import zlib,struct
r=Path(__file__).resolve().parents[1]
d=json.loads((r/'assets/source/environment/federation-ngv-roof-evidence.json').read_text())
v=Polygon(json.loads((r/'assets/source/environment/federation-atrium-ownership-reference.json').read_text())['atrium_local_ring'])
p=np.array([q for q in d['samples'] if not v.buffer(.5).covers(Point(q[:2])) and q[2]>24])
# Explicit diagnostic bands, not architectural boundaries or replacement meshes.
bands=[]
for lo,hi in [(0,60),(60,100),(100,150)]:
 a=p[(p[:,1]>=lo)&(p[:,1]<hi)];A=np.c_[a[:,:2],np.ones(len(a))];c=np.linalg.lstsq(A,a[:,2],rcond=None)[0];e=np.abs(A@c-a[:,2]);bands.append({'y_band':[lo,hi],'cells':len(a),'plane':c.tolist(),'median_residual':float(np.median(e)),'p90_residual':float(np.quantile(e,.9)),'z_quantiles':np.quantile(a[:,2],[.1,.5,.9]).tolist()})
# Dependency-free PNG: north up; one pixel group per one-metre captured cell.
w,h=720,1080;rgb=bytearray([245]*(w*h*3))
for x,y,z in p:
 t=max(0,min(1,(z-24)/9));color=bytes((int(35+210*t),int(90+95*t),int(220-175*t)))
 px=int((x-185)*6)+30;py=int((150-y)*6)+30
 for dx in range(5):
  for dy in range(5):
   if 0<=px+dx<w and 0<=py+dy<h:
    i=((py+dy)*w+px+dx)*3;rgb[i:i+3]=color
for a,b in zip(list(v.exterior.coords),list(v.exterior.coords)[1:]):
 for t in np.linspace(0,1,300):
  x,y=np.array(a)*(1-t)+np.array(b)*t;px=int((x-185)*6)+30;py=int((150-y)*6)+30
  if 0<=px<w and 0<=py<h:
   i=(py*w+px)*3;rgb[i:i+3]=bytes((220,25,25))
def chunk(t,d):return struct.pack('!I',len(d))+t+d+struct.pack('!I',zlib.crc32(t+d)&0xffffffff)
raw=b''.join(b'\0'+rgb[y*w*3:(y+1)*w*3] for y in range(h))
(r/'docs/images/federation-ngv-captured-roof-regions.png').write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
audit={'retained_cells':len(p),'diagnostic_bands':bands,'limits':'May2020 geometry only. Atrium visitor-map outline buffered0.5m, minimum24m and northing bands are authored diagnostic filters. Bands are not architectural roof boundaries. No Blender edits or photographic textures.'}
(r/'docs/federation-ngv-roof-regions-audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit,indent=2))
