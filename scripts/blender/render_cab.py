import bpy,os,math
from mathutils import Vector
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'../..'))
bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT,'assets/source/melbourne-commuter.blend'))
for o in bpy.data.collections['Exterior'].objects:o.hide_render=True
for o in bpy.data.collections['Driver cab'].objects:o.hide_render=False
bpy.data.objects['Studio ground'].hide_render=True
scene=bpy.context.scene;cam=scene.camera;cam.location=(0,0,0);cam.rotation_euler=(Vector((0,10,-.1))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='PERSP';cam.data.sensor_fit='VERTICAL';cam.data.sensor_height=24;cam.data.lens=20.785
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.32,.41,.51,1)
scene.render.filepath=os.path.join(ROOT,'artifacts/train-cab.png');bpy.ops.render.render(write_still=True)
