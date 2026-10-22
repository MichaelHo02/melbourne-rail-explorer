import bpy,json
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];o=bpy.data.objects['Flinders station - municipal 2020 scan, authored colours'];m=bpy.data.meshes[o['concourse_skin_original_mesh']];m.calc_loop_triangles();out={}
for t in m.loop_triangles:
 p=m.polygons[t.polygon_index];c=p.center
 if not (10<c.z<14.5 and p.material_index in (2,4)):continue
 xyz=[tuple(m.vertices[i].co) for i in t.vertices]
 if max(v[0] for v in xyz)<-30 or min(v[0] for v in xyz)>70 or max(v[1] for v in xyz)<-60 or min(v[1] for v in xyz)>55:continue
 out.setdefault(str(t.polygon_index),[]).append(xyz)
(r/'assets/source/environment/flinders-roof-overlap-original.json').write_text(json.dumps(out,separators=(',',':'))+'\n');print('ROOF_OVERLAP_EXPORTED',len(out),flush=True)
