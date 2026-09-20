"""Bake transparent distant-tree silhouettes from the editable tree prototypes.
Blender --background assets/source/environment/urban-trees.blend --python scripts/blender/bake_tree_impostors.py
"""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=24
scene.render.resolution_x=256;scene.render.resolution_y=256;scene.render.resolution_percentage=100
scene.render.film_transparent=True
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
scene.view_settings.view_transform='Standard'
scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.68,.75,.85,1)
scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.8
camera_data=bpy.data.cameras.new('impostor camera');camera=bpy.data.objects.new('impostor camera',camera_data);scene.collection.objects.link(camera);scene.camera=camera
# All prototypes share a sixteen-metre square: horizontal [-8,8], height [-1,15].
camera.location=(0,-30,7);direction=Vector((0,0,7))-camera.location;camera.rotation_euler=direction.to_track_quat('-Z','Y').to_euler();camera_data.type='ORTHO';camera_data.ortho_scale=16
light_data=bpy.data.lights.new('soft canopy illumination','AREA');light_data.energy=900;light_data.shape='DISK';light_data.size=12
light=bpy.data.objects.new('soft canopy illumination',light_data);scene.collection.objects.link(light);light.location=(-8,-10,18);light.rotation_euler=(Vector((0,0,6))-light.location).to_track_quat('-Z','Y').to_euler()
out=ROOT/'public/textures/trees';out.mkdir(parents=True,exist_ok=True)
meshes=[o for o in scene.objects if o.type=='MESH']
for kind in ['plane','gum','elm','palm']:
 for o in meshes:o.hide_render=o.name!=kind
 scene.render.filepath=str(out/(kind+'-impostor.png'));bpy.ops.render.render(write_still=True)
(out/'impostors.json').write_text(json.dumps({'generator':'scripts/blender/bake_tree_impostors.py','source':'assets/source/environment/urban-trees.blend','bounds':{'width':16,'height':16,'centerHeight':7},'resolution':256,'purpose':'Distant canopy silhouettes baked from the same authored botanical prototypes; no new geographic placements.'},indent=2)+'\n')
