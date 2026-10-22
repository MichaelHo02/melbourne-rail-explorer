"""Smooth authored foliage cluster normals without changing mapped trees."""
import bpy
meshes=[m for m in bpy.data.meshes if m.name.startswith('Authored fine foliage crown ')]
assert len(meshes)==7
for mesh in meshes:
 for p in mesh.polygons:p.use_smooth=True
 mesh['shading_limits']='Smooth cluster normals are an authored visual choice. Tree dimensions, species morphology and condition remain unverified.'
 mesh.update()
print('VERIFIED smooth foliage cluster shading',len(meshes),'shared meshes',flush=True)
