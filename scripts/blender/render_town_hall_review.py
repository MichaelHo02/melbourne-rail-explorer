"""Render saved Town Hall repair without hiding objects or saving scene changes."""
import bpy
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).resolve().parents[3]
s=bpy.context.scene
camera_data=bpy.data.cameras.new('Town Hall review temporary camera')
camera=bpy.data.objects.new('Town Hall review temporary camera',camera_data)
s.collection.objects.link(camera)
camera.location=(-63,353,32)
camera.rotation_euler=(Vector((-30,365,13))-camera.location).to_track_quat('-Z','Y').to_euler()
camera_data.type='ORTHO'
camera_data.ortho_scale=68
camera_data.clip_end=5000
s.camera=camera
s.render.engine='CYCLES'
s.cycles.samples=24
s.cycles.use_denoising=True
s.render.resolution_x=1500
s.render.resolution_y=1100
s.render.resolution_percentage=100
s.render.filepath=str(r/'docs/images/observatory-town-hall-review-repaired.png')
bpy.ops.render.render(write_still=True)
print('TOWN_HALL_REVIEW_RENDERED_NO_HIDE_NO_SAVE',flush=True)
