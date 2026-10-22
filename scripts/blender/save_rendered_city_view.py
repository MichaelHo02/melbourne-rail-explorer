"""Persist lit camera view without modifying city geometry or materials."""
import bpy,json
from pathlib import Path
s=bpy.context.scene;assert s.camera.name=='37 CBD aerial review';assert s.get('federation_ngv_eastern_fitted_relief_revision')=='five-local-captured-fits-v1';areas=[]
for screen in bpy.data.screens:
 for a in screen.areas:
  if a.type=='VIEW_3D':
   a.spaces.active.shading.type='RENDERED';a.spaces.active.region_3d.view_perspective='CAMERA';a.spaces.active.region_3d.view_camera_zoom=0;areas.append(screen.name)
assert areas
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
r=Path(bpy.data.filepath).resolve().parents[3];(r/'docs/rendered-city-opening-view-audit.json').write_text(json.dumps({'viewports_set':areas,'camera':s.camera.name,'limits':'Saved Rendered mode and camera view. Native reload must be inspected; GPU lighting compilation can delay preview.'},indent=2)+'\n');print('RENDERED_OPENING_VIEW_SAVED',areas,flush=True)
