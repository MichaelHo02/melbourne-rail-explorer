import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene
a=Vector((194.1893005923935,132.9081363091356,0));b=Vector((214.23831677004776,138.92288999870829,0));axis=(b-a).normalized();normal=Vector((-axis.y,axis.x,0))
report={}
for name in ['Atrium north west and southern glazing','Atrium authored200mm square steel frame']:
 o=bpy.data.objects[name];old=o.data;vs=[v.co[:] for v in old.vertices];keep=[];removed=[]
 for p in old.polygons:
  pts=[Vector(vs[i]) for i in p.vertices]
  end=all(abs((q-a).dot(normal))<.16 and -.2<(q-a).dot(axis)<(b-a).length+.2 for q in pts)
  remove=end and (name.endswith('glazing') or max(q.z for q in pts)<25.5)
  (removed if remove else keep).append(p)
 me=bpy.data.meshes.new(old.name+' open north trial');me.from_pydata(vs,[],[list(p.vertices) for p in keep]);me.update()
 for m in old.materials:me.materials.append(m)
 for p,original in zip(me.polygons,keep):p.material_index=original.material_index
 o.data=me;report[name]=len(removed)
o=bpy.data.objects['Federation Square - authored triangular cladding'];old=o.data;vs=[v.co[:] for v in old.vertices];keep=[];removed=[]
for p in old.polygons:
 q=p.center;end=abs((q-a).dot(normal))<1.5 and 0<(q-a).dot(axis)<(b-a).length and q.z<26
 (removed if end else keep).append(p)
me=bpy.data.meshes.new(old.name+' open north trial');me.from_pydata(vs,[],[list(p.vertices) for p in keep]);me.update()
for m in old.materials:me.materials.append(m)
for p,original in zip(me.polygons,keep):p.material_index=original.material_index
o.data=me;report[o.name]=len(removed)
print('OPEN_NORTH_TRIAL',report,flush=True)
s.camera=bpy.data.objects['36 Federation Atrium inspection'];s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.filepath='/tmp/atrium-open-north-uncovered-trial.png';bpy.ops.render.render(write_still=True)
