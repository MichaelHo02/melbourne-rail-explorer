import bpy
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3]
if not bpy.context.scene.get('federation_mega_finish_revision'):
 SAVE_MEGA_PASS=True
 exec(compile((r/'scripts/blender/trial_federation_mega_panel_finishes.py').read_text(),'mega_finish','exec'))
else:print('MEGA_FINISH_ALREADY_INSTALLED',flush=True)
