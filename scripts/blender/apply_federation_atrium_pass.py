"""Apply bounded reversible Atrium pass; compare retained source geometry before/after."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene
names=list(json.loads((r/'assets/source/environment/federation-atrium-surface-cuts.json').read_text())['patches'])
def geometry(o):
 h=hashlib.sha256()
 for v in o.data.vertices:h.update(str(tuple(v.co)).encode())
 for p in o.data.polygons:h.update(str(tuple(p.vertices)).encode())
 return h.hexdigest()
before={n:geometry(bpy.data.objects[n]) for n in names}
for name in ['refine_federation_atrium_void.py','refine_federation_atrium_enclosure.py']:exec(compile((r/'scripts/blender'/name).read_text(),name,'exec'),{})
assert all(geometry(bpy.data.objects[n])==v for n,v in before.items())
name='36 Federation Atrium inspection';c=bpy.data.objects.get(name)
if not c:
 cd=bpy.data.cameras.new(name);cd.type='ORTHO';cd.ortho_scale=135;c=bpy.data.objects.new(name,cd);s.collection.objects.link(c);c.location=(130,185,135);c.rotation_euler=(Vector((218,92,16))-c.location).to_track_quat('-Z','Y').to_euler()
s.camera=c
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
(r/'docs/federation-atrium-enclosure-audit.json').write_text(json.dumps({'original_geometry_hashes':before,'original_geometry_unchanged':True,'revision':s.get('federation_atrium_enclosure_revision'),'limits':json.loads((r/'assets/source/environment/federation-atrium-enclosure.json').read_text())['limits']},indent=2))
print('ATRIUM_PASS_VERIFIED',flush=True)
