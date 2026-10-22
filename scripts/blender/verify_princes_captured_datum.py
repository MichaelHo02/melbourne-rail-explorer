import bpy,json,math
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene;assert s.get('princes_bridge_captured_datum_revision')=='historical-capture-flat-deck6.2-v1';p=r/'docs/princes-bridge-captured-datum-audit.json';a=json.loads(p.read_text());checks=[]
for name,d in a['changes'].items():
 o=bpy.data.objects[name]
 if 'translation_z' in d:
  original=o['captured_datum_original_location'];assert abs(o.location.z-original[2]+3.3)<1e-5
 elif 'vertical_scale_above_foundation' in d:
  backup=bpy.data.meshes[o['captured_datum_original_mesh']];assert backup.use_fake_user;assert abs(max(v.co.z for v in o.data.vertices)-5.4)<1e-5
 elif 'curve_vertical_scale' in d:
  backup=bpy.data.curves[o['captured_datum_original_curve']];assert backup.use_fake_user
  for sp,original in zip(o.data.splines,backup.splines):
   for v,q in zip(sp.points,original.points):assert abs(v.co.z-(.05+(q.co.z-.05)*d['curve_vertical_scale']))<1e-5
 elif name=='survey_36402':assert abs(max((o.matrix_world@v.co).z for v in o.data.vertices)-6.19)<1e-5
 elif 'deck_top' in d:
  backup=bpy.data.meshes[o['princes_datum_original_mesh']];assert backup.use_fake_user;changed=0
  for v,q in zip(o.data.vertices,backup.vertices):
   if (v.co-q.co).length>1e-5:assert abs(v.co.z-6.2)<1e-5;assert abs(v.co.x-q.co.x)<1e-6 and abs(v.co.y-q.co.y)<1e-6;changed+=1
  assert changed==d['vertices']
 checks.append(name)
assert s.camera.name=='37 CBD aerial review';assert not any(n.type=='TEX_IMAGE' for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes);a['saved_file_verification']={'checked_objects':checks,'roof_xy_preserved':True,'recovery_meshes_present':True,'image_textures':0};p.write_text(json.dumps(a,indent=2)+'\n');print('SAVED_CAPTURED_DATUM_VERIFIED',len(checks),flush=True)
