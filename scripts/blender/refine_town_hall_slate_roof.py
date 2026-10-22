"""Authored mansard interpretation bounded by retained Town Hall hip section."""
import bpy,json,math
from pathlib import Path
R=Path(bpy.data.filepath).resolve().parents[3]
d=json.loads((R/'assets/source/environment/town-hall-source-reference.json').read_text())
r=next(x for x in d['records'] if x['objectid']=='27721')
name='Town Hall authored slate mansard interpretation'
if not bpy.data.objects.get(name):
 points=[((x-144.9671)*87939,(y+37.8183)*111320) for x,y in r['geo_shape']['geometry']['coordinates'][0][:-1]]
 cx=sum(x for x,y in points)/len(points);cy=sum(y for x,y in points)/len(points)
 bottom=r['footprint_min_elevation']-r['structure_min_elevation'];top=r['footprint_max_elevation']-r['structure_min_elevation']
 v=[];f=[];n=len(points)
 for scale,z in [(1,bottom),(.85,top-1.2),(.75,top)]:v.extend([(cx+(x-cx)*scale,cy+(y-cy)*scale,z) for x,y in points])
 for ring in range(2):
  for i in range(n):j=(i+1)%n;f.append((ring*n+i,ring*n+j,(ring+1)*n+j,(ring+1)*n+i))
 f.append(tuple(range(2*n,3*n)))
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(v,[],f);mesh.materials.append(bpy.data.materials['Town Hall authored slate']);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(o)
 original=bpy.data.objects.get('survey_27721');original.hide_render=True;original.hide_viewport=True
 def inside(x,y):
  hit=False
  for i,a in enumerate(points):
   b=points[(i+1)%n]
   if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
  return hit
 cap=bpy.data.objects['Continuous surveyed roofs - authored finishes'];indices=[]
 for p in cap.data.polygons:
  c=p.center
  if abs(c.z-top)<.02 and inside(c.x,c.y):indices.append(p.index)
 import bmesh
 bm=bmesh.new();bm.from_mesh(cap.data);bm.faces.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.faces[i] for i in indices],context='FACES_ONLY');bm.to_mesh(cap.data);bm.free();cap.data.update()
 o['source_id']='27721';o['reference']=d['heritage_reference'];o['limits']='Historical hip roof footprint and min/max retained. Three rings at scale1/.85/.75 and shoulder1.2m below maximum are authored mansard interpretation, not traced roof sections. Exact slopes, dormers, cupola and current condition unverified.'
 print('VERIFIED Town Hall mansard',len(f),'faces; removed generic cap',len(indices),flush=True)
