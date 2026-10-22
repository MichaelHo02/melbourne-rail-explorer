"""Bake original full scan smoothing before any roof boundary clipping."""
import bpy,json
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];o=bpy.data.objects['Flinders station - municipal 2020 scan, authored colours'];original=bpy.data.meshes[o['concourse_skin_original_mesh']];temp=o.copy();temp.name='Temporary original scan smoothing bake';temp.data=original;bpy.context.scene.collection.objects.link(temp);temp.hide_viewport=False;temp.hide_render=False;bpy.context.view_layer.update();ev=temp.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();assert len(m.vertices)==len(original.vertices) and len(m.polygons)==len(original.polygons);m.calc_loop_triangles();out={}
for t in m.loop_triangles:
 p=m.polygons[t.polygon_index];c=p.center
 if not (10<c.z<14.5 and p.material_index in (2,4)):continue
 xyz=[tuple(m.vertices[i].co) for i in t.vertices]
 if max(v[0] for v in xyz)<-30 or min(v[0] for v in xyz)>70 or max(v[1] for v in xyz)<-60 or min(v[1] for v in xyz)>55:continue
 out.setdefault(str(t.polygon_index),[]).append(xyz)
(r/'assets/source/environment/flinders-roof-baked-overlap-original.json').write_text(json.dumps(out,separators=(',',':'))+'\n');(r/'assets/source/environment/flinders-original-smoothed-vertices.json').write_text(json.dumps([list(v.co) for v in m.vertices],separators=(',',':'))+'\n');ev.to_mesh_clear();bpy.data.objects.remove(temp,do_unlink=True);print('BAKED_ROOF_OVERLAP',len(out),flush=True)
