"""Authored macro panels on retained NGV edge geometry, clipped around Atrium."""
import json,math,hashlib
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon,LineString
r=Path(__file__).resolve().parents[1];buildings=json.loads((r/'public/data/buildings.json').read_text())['buildings'];void=Polygon(json.loads((r/'assets/source/environment/federation-atrium-ownership-reference.json').read_text())['atrium_local_ring']);c=json.loads((r/'docs/federation-ngv-north-roof-audit.json').read_text())['plane']
pieces=[[(-1,2),(0,0),(0,2)],[(0,0),(0,1),(2,1)],[(0,1),(0,2),(2,1)],[(0,2),(2,1),(2,2)],[(2,1),(2,2),(4,2)]]
def sub(t):
 a,b,c=map(np.array,t);return [[a+(b-a)*((x+y/2)/5)+(c-a)*((2*y-x)/5) for x,y in piece] for piece in pieces]
def top(sid,x,y,old):
 if sid!=16222:return old
 w=max(0,min(1,(y-95)/10));w=w*w*(3-2*w);return old+(c[0]*x+c[1]*y+c[2]-32.4)*w
vs=[];fs=[];materials=[];owners=[]
for sid in [16221,16222,16223]:
 b=next(b for b in buildings if int(b['id'])==sid);ring=[(x,-y) for x,y in b['ring']];base=b['base']+8.4;old=base+b['height'];sign=1 if Polygon(ring).exterior.is_ccw else -1
 for edge,(a,b) in enumerate(zip(ring,ring[1:])):
  a=np.array(a);b=np.array(b);delta=b-a;length=np.linalg.norm(delta)
  if length<.25:continue
  tangent=delta/length;normal=np.array([tangent[1],-tangent[0],0])*sign;remain=LineString([a,b]).difference(void.buffer(.002));parts=[remain] if remain.geom_type=='LineString' else list(remain.geoms)
  for part in parts:
   if part.is_empty or part.geom_type!='LineString' or part.length<.25:continue
   start=np.array(part.coords[0]);end=np.array(part.coords[-1]);L=np.linalg.norm(end-start);direction=(end-start)/L;cols=max(1,math.ceil(L/12));height=max(top(sid,*start,old),top(sid,*end,old))-base;rows=max(1,math.ceil(height/6))
   for col in range(cols):
    for row in range(rows):
     u0,u1=col/cols,(col+1)/cols;v0,v1=row/rows,(row+1)/rows
     for parent,t in enumerate([[(u0,v0),(u1,v0),(u0,v1)],[(u1,v1),(u0,v1),(u1,v0)]]):
      for panel,triangle in enumerate(sub(t)):
       seed=int.from_bytes(hashlib.sha256(f'{sid}:{edge}:{col}:{row}:{parent}:{panel}'.encode()).digest()[:4],'big')%100;material=0 if seed<68 else 1 if seed<94 else 2
       for leaf in sub(triangle):
        centre=np.mean(leaf,axis=0);points=[]
        for u,v in [centre+(q-centre)*.992 for q in leaf]:
         x,y=start+direction*(u*L);points.append(np.array([x,y,base+v*(top(sid,x,y,old)-base)])+normal*.16)
        if np.dot(np.cross(points[1]-points[0],points[2]-points[0]),normal)<0:points.reverse()
        k=len(vs);vs.extend([q.tolist() for q in points]);fs.append([k,k+1,k+2]);materials.append(material);owners.append(sid)
limits='Nested five-triangle hierarchy;12m by6m target macro groups,68/26/6 stone/zinc/glass proportions and0.8percent seam shrink authored. NGV source edge geometry and fitted northern roof reused. Visitor-map Atrium cut approximated by2mm buffer. Fine architectural folds, openings and actual material schedule unresolved. Historical capture not present-day verification; no photographic textures.'
(r/'assets/source/environment/federation-ngv-panels.json').write_text(json.dumps({'vertices':vs,'faces':fs,'materials':materials,'owners':owners,'limits':limits}));print('NGV_MACRO_PANEL_TRIANGLES',len(fs))
