"""Trial coherent finishes following retained NGV nested mega-panel ownership."""
import bpy,json,hashlib
from pathlib import Path
from collections import Counter
r=Path(bpy.data.filepath).resolve().parents[3];source=r/'assets/source/environment/federation-ngv-panels.json';d=json.loads(source.read_text());o=bpy.data.objects['Federation NGV - nested pinwheel panels'];changes=[];groups=[];skipped=[]
assert len(d['faces'])%25==0
for start in range(0,len(d['faces']),25):
 ids=list(range(start,start+25));valid=True
 for i in ids:
  p=o.data.polygons[i];f=d['faces'][i]
  if len(p.vertices)!=len(f) or not all(abs(o.data.vertices[a].co.x-d['vertices'][b][0])<.001 and abs(o.data.vertices[a].co.y-d['vertices'][b][1])<.001 for a,b in zip(p.vertices,f)):valid=False;break
 if not valid:skipped.append(start//25);continue
 assert len(set(d['owners'][i] for i in ids))==1
 seed=int.from_bytes(hashlib.sha256(f'mega:{d["owners"][start]}:{start//25}'.encode()).digest()[:4],'big')%100;mat=0 if seed<68 else 1 if seed<94 else 2
 groups.append({'group':start//25,'faces':ids,'material':mat})
 for i in ids:
  p=o.data.polygons[i]
  if p.material_index!=mat:changes.append({'face':i,'before':p.material_index,'after':mat});p.material_index=mat
limits='One finish per retained25-leaf nested mega-panel,68/26/6 weighted stone/zinc/glass choice authored. Actual material schedule and openings unverified. Groups with changed XY topology skipped, later fragments retained. Geometry and panel seams unchanged; no photographic textures.'
a={'object':o.name,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source':'https://data.melbourne.vic.gov.au/explore/dataset/2023-building-footprints/','reference':'https://fedsquare.com/history-design','groups':groups,'skipped_groups':skipped,'changes':changes,'limits':limits,'counts':dict(Counter(p.material_index for p in o.data.polygons))};(r/'docs/federation-mega-panel-trial-audit.json').write_text(json.dumps(a,indent=2)+'\n');print('MEGA_PANEL_FINISH_TRIAL',len(groups),len(skipped),len(changes),flush=True)
if globals().get('SAVE_MEGA_PASS'):
 backup=o.data.copy();backup.name='NGV panel mesh before coherent mega finishes';backup.use_fake_user=True
 # Backup must preserve original assignments, rather than trial assignments.
 for c in changes:backup.polygons[c['face']].material_index=c['before']
 o['mega_finish_original_mesh']=backup.name;o['mega_finish_limits']=limits;bpy.context.scene['federation_mega_finish_revision']='retained-25-leaf-groups-v1';(r/'docs/federation-mega-panel-audit.json').write_text(json.dumps(a,indent=2)+'\n');bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
else:
 s=(r/'scripts/blender/render_federation_square_detail.py').read_text().replace('bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)','scene.render.engine="CYCLES";scene.cycles.samples=24;scene.cycles.use_denoising=True').replace('observatory-federation-square-detail.png','observatory-federation-mega-panel-trial.png');exec(compile(s,'render','exec'))
