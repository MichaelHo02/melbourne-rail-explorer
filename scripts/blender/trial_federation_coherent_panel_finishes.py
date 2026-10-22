"""Unsaved NGV material grouping trial; geometry and existing panel seams retained."""
import bpy,json,math,hashlib
from pathlib import Path
from collections import Counter
r=Path(bpy.data.filepath).resolve().parents[3];o=bpy.data.objects['Federation NGV - nested pinwheel panels'];a=o.data.attributes['source_section'];changes=[]
for p,sid in zip(o.data.polygons,a.data):
 n=p.normal;c=p.center
 if abs(n.z)>.5:continue
 # Stable projected facade coordinates; contiguous authored zones reduce random contrast.
 axis=0 if abs(n.x)>abs(n.y) else 1;u=c.y if axis==0 else c.x
 col=math.floor(u/12);row=math.floor(c.z/6);parent=int(u/12-col+c.z/6-row>1)
 seed=int.from_bytes(hashlib.sha256(f'{sid.value}:{axis}:{round(n[axis])}:{col}:{row}:{parent}'.encode()).digest()[:4],'big')%100
 mat=0 if seed<68 else 1 if seed<94 else 2
 if mat!=p.material_index:changes.append({'face':p.index,'before':p.material_index,'after':mat});p.material_index=mat
limits='Authored contiguous finish zones projected on12m by6m facade cells, split diagonally;68/26/6 stone/zinc/glass weighting. Retains existing nested panel geometry. Zone boundaries do not establish actual mega-panel or glazing schedule. Geometry unchanged; no photographic textures.'
(r/'docs/federation-coherent-panel-trial-audit.json').write_text(json.dumps({'object':o.name,'changes':changes,'limits':limits,'reference':'https://fedsquare.com/history-design','counts':dict(Counter(p.material_index for p in o.data.polygons))},indent=2)+'\n')
print('FEDERATION_COHERENT_FINISH_TRIAL',len(changes),flush=True)
s=(r/'scripts/blender/render_federation_square_detail.py').read_text().replace('bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)','scene.render.engine="CYCLES";scene.cycles.samples=24;scene.cycles.use_denoising=True').replace('observatory-federation-square-detail.png','observatory-federation-coherent-panel-trial.png');exec(compile(s,'render','exec'))
