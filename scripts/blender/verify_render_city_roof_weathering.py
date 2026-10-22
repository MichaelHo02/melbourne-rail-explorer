import bpy,json
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];assert bpy.context.scene.get('generic_roof_weathering_revision')=='quarter-contrast-neutral-zinc-v1';p=r/'docs/city-roof-weathering-audit.json';d=json.loads(p.read_text())
for name,rec in d['materials'].items():
 m=bpy.data.materials[name];n=next(n for n in m.node_tree.nodes if n.type=='VALTORGB');assert bpy.data.materials.get(rec['backup']);assert all(abs(a-b)<1e-6 for e,c in zip(n.color_ramp.elements,rec['after']) for a,b in zip(e.color,c))
assert not any(n.type=='TEX_IMAGE' for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes);d['saved_file_verification']={'ramps_match':True,'backups_present':True,'no_image_texture_nodes':True};p.write_text(json.dumps(d,indent=2)+'\n');print('SAVED_ROOF_WEATHERING_VERIFIED',flush=True)
import bpy
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene;assert s.camera.name=='37 CBD aerial review';assert abs(s.camera.data.ortho_scale-1900)<.01;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.filepath=str(r/'docs/images/observatory-cbd-roof-weathering.png');bpy.ops.render.render(write_still=True);print('SAVED_CBD_CAMERA_VERIFIED',flush=True)
