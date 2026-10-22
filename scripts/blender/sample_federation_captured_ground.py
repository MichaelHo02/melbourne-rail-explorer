"""Geometry-only sample extraction. Requires /tmp/federation-photomesh-2020-trial.obj; run in a disposable background scene, never save imported crop."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];sections=json.loads((root/'assets/source/environment/federation-ground-datum-sections.json').read_text())
for p in sections:
 r=p['ring'];p['bbox']=(min(q[0] for q in r),min(q[1] for q in r),max(q[0] for q in r),max(q[1] for q in r))
def inside(x,y,p):
 a,b,c,d=p['bbox']
 if x<a-.5 or x>c+.5 or y<b-.5 or y>d+.5:return False
 r=p['ring'];v=False
 for i,q in enumerate(r):
  t=r[i-1]
  if (q[1]>y)!=(t[1]>y) and x<(t[0]-q[0])*(y-q[1])/(t[1]-q[1])+q[0]:v=not v
 return v
before=set(bpy.data.objects);bpy.ops.wm.obj_import(filepath='/tmp/federation-photomesh-2020-trial.obj',forward_axis='Y',up_axis='Z');o=next(o for o in bpy.data.objects if o not in before);m=o.data
vs=[v.co.copy() for v in m.vertices];fs=[tuple(p.vertices) for p in m.polygons if p.normal.z>.55 and 0<p.center.z<13]
bvh=BVHTree.FromPolygons(vs,fs,all_triangles=True);samples=[]
for x in range(50,311,2):
 for y in range(-45,116,2):
  if any(inside(x,y,p) for p in sections):continue
  pos,n,index,d=bvh.ray_cast(Vector((x,y,13.1)),Vector((0,0,-1)),14)
  if pos is not None:samples.append([x,y,pos.z])
(root/'assets/source/environment/federation-captured-ground-samples.json').write_text(json.dumps(samples));print('SAMPLES',len(samples),flush=True)
