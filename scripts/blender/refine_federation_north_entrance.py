import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene
if not s.get('federation_north_entrance_revision'):
 a=Vector((194.1893005923935,132.9081363091356,0));b=Vector((214.23831677004776,138.92288999870829,0));axis=(b-a).normalized();normal=Vector((-axis.y,axis.x,0))
 report={}
 for name in ['Atrium north west and southern glazing','Atrium authored200mm square steel frame']:
  o=bpy.data.objects[name];old=o.data;old.use_fake_user=True;o['north_entrance_original_mesh']=old.name;vs=[v.co[:] for v in old.vertices];keep=[];removed=[]
  for p in old.polygons:
   pts=[Vector(vs[i]) for i in p.vertices]
   end=all(abs((q-a).dot(normal))<.16 and -.2<(q-a).dot(axis)<(b-a).length+.2 for q in pts)
   remove=end and (name.endswith('glazing') or max(q.z for q in pts)<25.5)
   (removed if remove else keep).append(p)
  me=bpy.data.meshes.new(old.name+' open northern entrance');me.from_pydata(vs,[],[list(p.vertices) for p in keep]);me.update()
  for m in old.materials:me.materials.append(m)
  for p,original in zip(me.polygons,keep):p.material_index=original.material_index
  o.data=me;report[name]=len(removed)
 s['federation_north_entrance_revision']='open-prototype-v1'
 limits='Northern opening supported by historical Galvanizers Association account. Exact cut boundary, retained upper framing and present-day entrance dimensions approximate. Existing inferred floor and adjacent levels remain unresolved.'
 (r/'docs/federation-north-entrance-audit.json').write_text(json.dumps({'removed_faces':report,'reference':'https://www.azobuild.com/article.aspx?ArticleID=8004','limits':limits,'original_meshes_retained':True},indent=2)+'\n')
 print('NORTH_ENTRANCE_APPLIED',report,flush=True)
else:print('NORTH_ENTRANCE_ALREADY_APPLIED',flush=True)
