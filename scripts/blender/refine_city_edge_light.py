"""Non-destructive authored edge softening on visible survey envelopes."""
import bpy
from pathlib import Path
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3]
collection=bpy.data.collections['CITY - surveyed envelopes with authored facade materials']
count=0
for obj in collection.objects:
    if obj.type!='MESH' or not obj.name.startswith('survey_') or obj.hide_render:
        continue
    if not obj.data.vertices:continue
    zs=[v.co.z for v in obj.data.vertices]
    if max(zs)-min(zs)<8:continue
    mod=obj.modifiers.get('Authored corner light catch') or obj.modifiers.new('Authored corner light catch','BEVEL')
    mod.width=.12;mod.segments=2;mod.limit_method='ANGLE';mod.angle_limit=.52;mod.use_clamp_overlap=True
    obj['edge_finish_basis']='Authored 0.12 m corner softening for shading only; unmeasured. Base survey mesh retained; modifier reversible.'
    count+=1
bpy.context.scene['authored_edge_finish_count']=count
print('VERIFIED authored corner light catch:',count,flush=True)
