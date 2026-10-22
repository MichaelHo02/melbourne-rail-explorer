import bpy
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3]
if not bpy.context.scene.get('st_pauls_belfry_relief_revision'):
 SAVE_BELFRY_PASS=True
 exec(compile((r/'scripts/blender/refine_st_pauls_belfry_relief.py').read_text(),'belfry','exec'))
else:print('BELFRY_ALREADY_INSTALLED',flush=True)
