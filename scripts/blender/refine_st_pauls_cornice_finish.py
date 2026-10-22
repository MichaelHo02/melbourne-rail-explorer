"""Replace generic cornice finish only on faces matched to retained cathedral towers."""
import bpy,json
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];a=json.loads((r/'docs/st-pauls-generic-strip-audit.json').read_text());o=bpy.data.objects['Authored roof edge cornices'];ids=a[o.name]['faces'];assert ids;changes=[{'face':i,'before':o.data.polygons[i].material_index} for i in ids];backup=o.data.copy();backup.name='Cornices before cathedral stone finish';backup.use_fake_user=True;mat=bpy.data.materials['Authored St Pauls warm masonry'];slot=next((i for i,m in enumerate(o.data.materials) if m==mat),None)
if slot is None:slot=len(o.data.materials);o.data.materials.append(mat)
for c in changes:o.data.polygons[c['face']].material_index=slot;c['after']=slot
limits='Generic authored cornice faces within0.5m of existing cathedral tower wall planes receive warm masonry finish. Geometry and dimensions remain illustrative; exact stringcourses not measured. Other cornice faces unchanged; original mesh recoverable.'
a={'object':o.name,'changes':changes,'backup_mesh':backup.name,'limits':limits,'reference':'https://ausmed.arts.uwa.edu.au/items/show/752'};print('CATHEDRAL_CORNICE_FINISH',len(changes),flush=True)
if globals().get('SAVE_CORNICE_PASS'):
 o['cathedral_cornice_original_mesh']=backup.name;bpy.context.scene['st_pauls_cornice_finish_revision']='tower-plane-stone-v1';(r/'docs/st-pauls-cornice-finish-audit.json').write_text(json.dumps(a,indent=2)+'\n');bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
else:
 backup.use_fake_user=False
 (r/'docs/st-pauls-cornice-finish-trial-audit.json').write_text(json.dumps(a,indent=2)+'\n');code=(r/'scripts/blender/render_st_pauls_study.py').read_text().replace('bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)','scene.render.engine="CYCLES";scene.cycles.samples=24;scene.cycles.use_denoising=True').replace('observatory-st-pauls-study.png','observatory-st-pauls-stone-cornice-trial.png');exec(compile(code,'render','exec'))
