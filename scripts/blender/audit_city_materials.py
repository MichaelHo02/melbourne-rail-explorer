"""Inspect saved scene material coverage and preview state; no scene mutation."""
import bpy,json
from pathlib import Path
root=Path(bpy.data.filepath).resolve().parents[3];visible=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render];missing=[o.name for o in visible if not o.data.materials or any(p.material_index>=len(o.data.materials) or o.data.materials[p.material_index] is None for p in o.data.polygons)];image_nodes=[{'material':m.name,'node':n.name,'image':n.image.name if n.image else None} for m in bpy.data.materials if m.use_nodes and m.node_tree for n in m.node_tree.nodes if n.type=='TEX_IMAGE'];viewports=[]
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   s=area.spaces.active;viewports.append({'screen':screen.name,'shading':s.shading.type,'scene_lights':s.shading.use_scene_lights,'scene_world':s.shading.use_scene_world,'perspective':s.region_3d.view_perspective})
out={'render_engine':bpy.context.scene.render.engine,'saved_camera':bpy.context.scene.camera.name if bpy.context.scene.camera else None,'visible_meshes':len(visible),'missing_material_objects':missing,'image_texture_nodes':image_nodes,'saved_viewports':viewports,'limits':'Material slot coverage does not prove individual real colours, UV accuracy, complete geometry or visual realism. Scene-render visibility differs from live viewport visibility.'};(root/'docs/city-material-coverage-audit.json').write_text(json.dumps(out,indent=2)+'\n');print('VERIFIED material audit',json.dumps(out),flush=True)
