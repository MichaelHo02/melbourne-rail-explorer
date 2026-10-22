import bpy,json
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];out={}
for name in ['survey_16221','survey_16222','survey_16223']:
 o=bpy.data.objects[name];vs=[list(o.matrix_world@v.co) for v in o.data.vertices];base=min(v[2] for v in vs);lines=[]
 for p in o.data.polygons:
  for i,j in zip(p.vertices,list(p.vertices)[1:]+list(p.vertices)[:1]):
   a,b=vs[i],vs[j]
   if abs(a[2]-base)<.001 and abs(b[2]-base)<.001:lines.append([a[:2],b[:2]])
 out[name]={'lines':lines,'low':base,'high':max(v[2] for v in vs)}
(r/'assets/source/environment/federation-atrium-source-boundaries.json').write_text(json.dumps(out))
