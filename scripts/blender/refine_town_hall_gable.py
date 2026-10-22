"""Replace source-classified gable envelope with authored pitched surfaces."""
import bpy,json,bmesh
from pathlib import Path
R=Path(bpy.data.filepath).resolve().parents[3];d=json.loads((R/'assets/source/environment/town-hall-authored-gable.json').read_text());name='Town Hall source-classified authored gable'
if not bpy.data.objects.get(name):
 m=bpy.data.materials.get('Town Hall authored main hall roof') or bpy.data.materials.new('Town Hall authored main hall roof');m.use_nodes=True;m.diffuse_color=(.16,.21,.23,1);s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=m.diffuse_color;s.inputs['Roughness'].default_value=.75;s.inputs['Metallic'].default_value=.15
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(d['vertices'],[],d['faces']);mesh.materials.append(m);mesh.materials.append(bpy.data.materials['Town Hall authored freestone']);mesh.update()
 for p,i in zip(mesh.polygons,d['materials']):p.material_index=i
 assert all(p.normal.z>0 for p in mesh.polygons if p.material_index==0)
 o=bpy.data.objects.new(name,mesh);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(o);o['source_id']=d['source_id'];o['limits']=d['limits'];original=bpy.data.objects['survey_27720'];original.hide_render=True;original.hide_viewport=True
 points=d['outline'][:-1]
 def inside(x,y):
  hit=False
  for i,a in enumerate(points):
   b=points[(i+1)%len(points)]
   if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
  return hit
 cap=bpy.data.objects['Continuous surveyed roofs - authored finishes'];indices=[p.index for p in cap.data.polygons if abs(p.center.z-d['top'])<.02 and inside(p.center.x,p.center.y)];bm=bmesh.new();bm.from_mesh(cap.data);bm.faces.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.faces[i] for i in indices],context='FACES_ONLY');bm.to_mesh(cap.data);bm.free();cap.data.update();print('VERIFIED Town Hall gable faces',len(mesh.polygons),'generic cap removed',len(indices),flush=True)
