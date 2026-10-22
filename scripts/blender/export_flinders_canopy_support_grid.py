"""Export captured roof support grid for the offline planar fit.
Run headlessly against city-observatory.blend. Rebuilds authored support surfaces
in memory only, exports /tmp JSON, and never saves the Blender scene.
"""
import bpy,json,runpy
from pathlib import Path
root=Path(bpy.data.filepath).resolve().parents[3]
runpy.run_path(str(root/'scripts/blender/refine_flinders_canopy_surfaces.py'))
mesh=bpy.data.objects['Flinders captured canopy fitted metal skins'].data
out=Path('/tmp/flinders-canopy-surface-grid.json')
out.write_text(json.dumps({'vertices':[list(v.co) for v in mesh.vertices],'triangles':[list(p.vertices) for p in mesh.polygons]}))
print('CANOPY_SUPPORT_GRID',str(out),len(mesh.vertices),len(mesh.polygons),flush=True)
