import bpy,json
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];out={}
for name in ['Continuous Vicmap road surface','Continuous authored pavement bands','Authored kerbs - retained road edges','Authored CBD junction crossings - illustrative','Authored CBD midblock lane guides - illustrative','Authored illustrative lane dashes']:
 o=bpy.data.objects.get(name)
 if not o or o.hide_render:continue
 assert all(abs(o.matrix_world[i][j]-(1 if i==j else 0))<1e-6 for i in range(4) for j in range(4));m=o.data;m.calc_loop_triangles();faces={}
 for t in m.loop_triangles:
  xyz=[tuple(m.vertices[i].co) for i in t.vertices]
  if max(q[0] for q in xyz)<-10 or min(q[0] for q in xyz)>105 or max(q[1] for q in xyz)<-65 or min(q[1] for q in xyz)>110:continue
  faces.setdefault(str(t.polygon_index),[]).append(xyz)
 chosen=set(faces);faces={str(i):[] for i in chosen}
 for t in m.loop_triangles:
  if str(t.polygon_index) in chosen:faces[str(t.polygon_index)].append([tuple(m.vertices[i].co) for i in t.vertices])
 out[name]=faces
(r/'assets/source/environment/swanston-approach-overlap-original.json').write_text(json.dumps(out)+'\n');print('APPROACH_OVERLAP_EXPORT',[(k,len(v)) for k,v in out.items()],flush=True)
