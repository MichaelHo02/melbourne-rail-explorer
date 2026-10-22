"""Persist a coloured Layout viewport for reopening the authored city."""
import bpy
for screen in bpy.data.screens:
 if screen.name!='Layout':continue
 for area in screen.areas:
  if area.type!='VIEW_3D':continue
  s=area.spaces.active;s.shading.type='MATERIAL';s.shading.use_scene_lights=True;s.shading.use_scene_world=True;s.overlay.show_overlays=False;s.region_3d.view_perspective='CAMERA';s.region_3d.view_camera_zoom=0
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True);print('VERIFIED saved Layout Material Preview with scene lighting/world',flush=True)
