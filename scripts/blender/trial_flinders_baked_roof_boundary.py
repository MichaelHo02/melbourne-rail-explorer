import bpy,json
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];o=bpy.data.objects['Flinders station - municipal 2020 scan, authored colours'];b=bpy.data.meshes[o['concourse_skin_original_mesh']];cuts=json.loads((r/'assets/source/environment/flinders-roof-baked-overlap-cuts.json').read_text());v=json.loads((r/'assets/source/environment/flinders-original-smoothed-vertices.json').read_text());f=[];mats=[];smooth=[]
for p in b.polygons:
 replacement=cuts.get(str(p.index))
 if replacement is None:f.append(tuple(p.vertices));mats.append(p.material_index);smooth.append(p.use_smooth)
 else:
  for tri in replacement:
   k=len(v);v.extend(tri);f.append((k,k+1,k+2));mats.append(p.material_index);smooth.append(p.use_smooth)
m=bpy.data.meshes.new('Flinders scan exact concourse boundary');m.from_pydata(v,[],f);m.update()
for mat in b.materials:m.materials.append(mat)
for p,mat,sm in zip(m.polygons,mats,smooth):p.material_index=mat;p.use_smooth=sm
o.data=m;
for modifier in o.modifiers:
 if modifier.type=='SMOOTH':modifier.show_viewport=False;modifier.show_render=False
bpy.context.scene['flinders_concourse_boundary_revision']='exact-xy-subtraction-trial-v1';print('EXACT_ROOF_BOUNDARY_TRIAL',len(cuts),len(f),flush=True)
exec(compile((r/'scripts/blender/render_swanston_approach_detail.py').read_text().replace('observatory-swanston-approach-detail.png','observatory-flinders-baked-roof-boundary-trial.png'),'render','exec'))
