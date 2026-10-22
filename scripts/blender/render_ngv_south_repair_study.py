import bpy
from pathlib import Path
from mathutils import Vector
s=bpy.context.scene;d=bpy.data.cameras.new('Southern NGV repair study');o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=(285,-85,95);o.rotation_euler=(Vector((215,35,24))-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=115;d.clip_end=10000;s.camera=o;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.filepath=str(Path(bpy.data.filepath).resolve().parents[3]/'docs/images/observatory-ngv-south-before-repair.png');bpy.ops.render.render(write_still=True);print('NGV_SOUTH_STUDY_RENDERED_NO_SAVE',flush=True)
