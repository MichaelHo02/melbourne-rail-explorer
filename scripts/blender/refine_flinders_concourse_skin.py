"""Captured-height concourse skin trial with recoverable scan overlap removal."""
import bpy,json,math
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];d=json.loads((r/'assets/source/environment/flinders-concourse-continuous-skin.json').read_text());o=bpy.data.objects['Flinders station - municipal 2020 scan, authored colours'];covered={(round(x-.5),round(y-.5)) for x,y in d['quad_origins']};old=o.data;backup=old.copy();backup.name='Flinders original before concourse median skin';backup.use_fake_user=True;o['concourse_skin_original_mesh']=backup.name
kept=[];removed=[]
for p in old.polygons:
 c=p.center;k=(math.floor(c.x-.5),math.floor(c.y-.5))
 # Retain masonry/trim, steep surfaces and higher roof features.
 if k in covered and 10<c.z<14.5 and p.material_index in (2,4):removed.append(p.index)
 else:kept.append(p)
m=bpy.data.meshes.new('Flinders retained scan outside concourse skin');m.from_pydata([tuple(v.co) for v in old.vertices],[],[tuple(p.vertices) for p in kept]);m.update()
for mat in old.materials:m.materials.append(mat)
for p,q in zip(m.polygons,kept):p.material_index=q.material_index;p.use_smooth=q.use_smooth
o.data=m
skin=bpy.data.meshes.new('Flinders captured-height authored concourse skin');skin.from_pydata(d['vertices'],[],d['faces']);skin.materials.append(bpy.data.materials['Scan Flinders authored weathered zinc canopy']);skin.update();new=bpy.data.objects.new(skin.name,skin);o.users_collection[0].objects.link(new);new.matrix_world=o.matrix_world.copy();new['limits']=d['limits'];new['source_sha256']=d['source_sha256']
for p in skin.polygons:p.use_smooth=True
bpy.context.scene['flinders_concourse_skin_revision']='captured-median-grid-v1'
a={'supported_area_m2':len(covered),'skin_triangles':len(skin.polygons),'removed_scan_faces':len(removed),'removed_face_indices':removed,'limits':d['limits'],'overlap_limits':'Centroid-based removal of zinc/ground upward faces within supported grid only; boundary scan overlaps remain possible. Masonry retained; zinc/ground steep faces inside height band also removed.'};(r/'docs/flinders-concourse-skin-audit.json').write_text(json.dumps(a,separators=(',',':'))+'\n');print('TRIAL_CONCOURSE_SKIN',len(covered),len(removed),flush=True)

assert len(m.vertices)==len(backup.vertices)
assert all((v.co-w.co).length==0 for v,w in zip(m.vertices,backup.vertices))
assert all(p.area>0 and p.normal.z>0 for p in skin.polygons)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('SAVED_CONCOURSE_SKIN',len(covered),flush=True)
