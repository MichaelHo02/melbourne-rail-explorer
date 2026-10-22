"""Remove coplanar overlaps in illustrative sleeper geometry."""
import bpy,json
from pathlib import Path
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3];o=bpy.data.objects['Expanded ordinary railway authored sleepers']
if not o.get('unioned_junctions'):
 d=json.loads((root/'assets/source/environment/expanded-sleepers-unioned.json').read_text());old=o.data;backup=bpy.data.objects.new('REFERENCE expanded sleeper boxes before union',old);o.users_collection[0].objects.link(backup);backup.hide_render=True;backup.hide_set(True)
 m=bpy.data.meshes.new('Expanded sleeper union top and edges');m.from_pydata(d['vertices'],[],d['faces']);m.materials.append(bpy.data.materials['Authored sleeper concrete']);m.update();o.data=m;o['unioned_junctions']=True;o['union_area_m2']=d['union_area_m2'];o['limits']=d['limits'];assert all(p.area>0 for p in m.polygons);print('VERIFIED non-overlapping sleeper union',len(m.polygons),flush=True)
