"""Render current city review cameras without changing the saved Blender file."""
import bpy
from pathlib import Path
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
original=(scene.camera,scene.render.filepath,scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage)
views=[('Aerial overview','observatory-blender-preview.png',1600,1000),('02 Flinders precinct','observatory-flinders-detail.png',1400,1000),('03 Hoddle grid streets','observatory-street-detail.png',1400,1000)]
try:
 for name,path,width,height in views:
  camera=bpy.data.objects[name];camera.data.clip_end=10000;scene.camera=camera;scene.render.resolution_x=width;scene.render.resolution_y=height;scene.render.resolution_percentage=100;scene.render.filepath=str(root/'docs/images'/path);bpy.ops.render.render(write_still=True);print('VERIFIED current review render:',name,flush=True)
finally:
 scene.camera,scene.render.filepath,scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage=original
