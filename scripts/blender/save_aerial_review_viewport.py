"""Persist coloured CBD framing; no modelling or material changes."""
import bpy
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3]
s=bpy.context.scene
assert s.camera.name=='37 CBD aerial review'
for screen in bpy.data.screens:
 if screen.name!='Layout':continue
 for area in screen.areas:
  if area.type!='VIEW_3D':continue
  v=area.spaces.active;v.shading.type='MATERIAL';v.shading.use_scene_lights=True;v.shading.use_scene_world=True
  v.overlay.show_overlays=False;v.region_3d.view_perspective='CAMERA';v.region_3d.view_camera_zoom=0
s['aerial_review_viewport_revision']='coloured-cbd-layout-v1'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
exec((r/'scripts/blender/audit_city_materials.py').read_text())
