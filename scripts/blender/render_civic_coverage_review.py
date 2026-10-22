"""Inspect remaining authored civic parcels without changing their geometry."""
import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path(bpy.data.filepath).resolve().parents[3];parts=json.loads((root/'assets/source/environment/city-civic-surfaces.json').read_text())['parts'];scene=bpy.context.scene;views=[]
for name,ids,image_name in [('27 Docklands civic coverage',{'M021968','M012907','M021969'},'observatory-docklands-civic-study.png'),('28 Harbour civic coverage',{'P378294'},'observatory-harbour-civic-study.png')]:
 selected=[p for p in parts if p['source_id'] in ids];verts=[v for p in selected for v in p['vertices']];lo=[min(v[i] for v in verts) for i in range(2)];hi=[max(v[i] for v in verts) for i in range(2)];x,y=[(lo[i]+hi[i])/2 for i in range(2)];scale=max(hi[0]-lo[0],hi[1]-lo[1])*1.35+35
 c=bpy.data.objects.get(name)
 if not c:c=bpy.data.objects.new(name,bpy.data.cameras.new(name));bpy.data.collections['PREVIEW - lighting and aerial camera'].objects.link(c)
 c.location=(x,y,1200);target=Vector((x,y,0));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=scale;c.data.clip_end=10000;c['source_ids']=','.join(sorted(ids));c['limits']='Retained clipped inventory parcels with illustrative paving; current surface and capture date unverified.';views.append((c,image_name))
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
for c,name in views:
 scene.camera=c;scene.render.resolution_x=1400;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.filepath=str(root/'docs/images'/name);bpy.ops.render.render(write_still=True);print('VERIFIED civic coverage render',c.name,flush=True)
