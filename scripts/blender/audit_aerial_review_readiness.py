"""Current saved material coverage and CBD-scale render; no scene-save mutations."""
import bpy
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3]
exec((r/'scripts/blender/audit_city_materials.py').read_text())
s=bpy.context.scene
assert s.camera.name=='37 CBD aerial review'
s.render.resolution_x=1800;s.render.resolution_y=1300;s.render.resolution_percentage=100
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True
s.render.filepath=str(r/'docs/images/observatory-cbd-final-aerial-review.png')
bpy.ops.render.render(write_still=True)
