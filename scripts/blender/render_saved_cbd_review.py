import bpy
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene;assert s.camera.name=='37 CBD aerial review';assert abs(s.camera.data.ortho_scale-1900)<.01;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.filepath=str(r/'docs/images/observatory-cbd-focused.png');bpy.ops.render.render(write_still=True);print('SAVED_CBD_CAMERA_VERIFIED',flush=True)
