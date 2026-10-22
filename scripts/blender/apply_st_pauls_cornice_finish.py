import bpy
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3]
if not bpy.context.scene.get('st_pauls_cornice_finish_revision'):
 SAVE_CORNICE_PASS=True
 exec(compile((r/'scripts/blender/refine_st_pauls_cornice_finish.py').read_text(),'cornice','exec'))
else:print('CATHEDRAL_CORNICE_ALREADY_INSTALLED',flush=True)
