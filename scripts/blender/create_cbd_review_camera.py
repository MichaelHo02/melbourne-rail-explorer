"""Focused CBD review camera; full-city audit camera retained."""
import bpy
from mathutils import Vector
name='37 CBD aerial review';o=bpy.data.objects.get(name)
if not o:
 d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);bpy.context.scene.collection.objects.link(o)
o.location=(900,-950,2100);target=Vector((-100,600,40));o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler();o.data.type='ORTHO';o.data.ortho_scale=1900;o.data.clip_end=12000;o['limits']='Authored review composition; does not conceal outstanding whole-city audit requirements.'
