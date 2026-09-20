"""Blender visual check of the converted official photomesh sample GLBs."""
import bpy,pathlib,json
from mathutils import Vector
ROOT=pathlib.Path(__file__).resolve().parents[1]
REVIEWS=ROOT/'artifacts/photomesh-review'
REVIEWS.mkdir(parents=True,exist_ok=True)
for name in ['flinders-street-context','viaduct-context','southbank-context','southern-cross-context','southern-cross-north']:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.gltf(filepath=str(ROOT/'public/models/photomesh'/f'{name}.glb'))
 points=[obj.matrix_world@Vector(corner) for obj in bpy.context.scene.objects if obj.type=='MESH' for corner in obj.bound_box]
 low=Vector([min(p[i] for p in points) for i in range(3)]);high=Vector([max(p[i] for p in points) for i in range(3)]);center=(low+high)/2;extent=max(high.x-low.x,high.y-low.y)
 bpy.ops.object.camera_add(location=center+Vector((extent*.35,-extent*.60,extent*.60)));camera=bpy.context.object;camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=extent*1.22
 scene=bpy.context.scene;scene.camera=camera;scene.render.engine='CYCLES';scene.cycles.samples=16;scene.world.color=(.12,.12,.12);scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.render.resolution_x=1500;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.filepath=str(REVIEWS/f'{name}-review.png');bpy.ops.render.render(write_still=True)
 print(name,'bounds',tuple(low),tuple(high))
