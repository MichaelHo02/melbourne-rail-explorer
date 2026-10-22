"""Audit the loaded saved scene; rendering and live window are separate checks."""
import bpy,json,hashlib,datetime
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene;enabled=set()
def visit(c,allowed=True):
 allowed=allowed and not c.hide_render
 if allowed:enabled.add(c.name)
 for child in c.children:visit(child,allowed)
visit(s.collection)
visible=[o for o in s.objects if o.type=='MESH' and not o.hide_render and any(c.name in enabled for c in o.users_collection)]
missing=[];checked={}
for o in visible:
 key=o.data.as_pointer()
 if key not in checked:checked[key]=not o.data.materials or any(p.material_index>=len(o.data.materials) or o.data.materials[p.material_index] is None for p in o.data.polygons)
 if checked[key]:missing.append(o.name)
image_nodes=[{'material':m.name,'node':n.name} for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE']
world_nodes=[{'world':w.name,'node':n.name} for w in bpy.data.worlds if w.use_nodes for n in w.node_tree.nodes if n.type=='TEX_IMAGE']
layout=[]
for screen in bpy.data.screens:
 if screen.name=='Layout':
  for area in screen.areas:
   if area.type=='VIEW_3D':layout.append({'shading':area.spaces.active.shading.type,'scene_lights':area.spaces.active.shading.use_scene_lights,'scene_world':area.spaces.active.shading.use_scene_world})
out={'audited_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scene_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'saved_camera':s.camera.name if s.camera else None,'render_visible_meshes':len(visible),'missing_material_objects':missing,'material_image_nodes':image_nodes,'world_image_nodes':world_nodes,'layout':layout,'stadium_support_revision':s.get('stadium_panel_support_revision'),'live_window_verified':False,'limits':'Saved datablock audit only. Does not prove architectural accuracy, surface completeness or live viewport refresh.'}
(r/'docs/saved-city-material-audit.json').write_text(json.dumps(out,indent=2)+'\n');assert not missing;assert not image_nodes and not world_nodes;assert out['saved_camera']=='02 Flinders precinct';assert layout and all(v['shading']=='MATERIAL' for v in layout);print('VERIFIED saved scene material coverage',len(visible),'meshes; zero missing materials or photographic texture nodes; saved coloured Layout and Flinders camera',flush=True)
