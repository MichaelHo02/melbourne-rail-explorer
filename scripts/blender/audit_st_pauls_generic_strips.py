import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).resolve().parents[3];source=bpy.data.objects['St Pauls Cathedral - authored three spires'];walls=[]
for p in source.data.polygons:
 if abs(p.normal.z)>.05 or p.material_index!=0:continue
 cs=[source.matrix_world@source.data.vertices[i].co for i in p.vertices];bottom=min(q.z for q in cs);top=max(q.z for q in cs);low=[q for q in cs if abs(q.z-bottom)<.001]
 if len(low)!=2:continue
 a,b=low;walls.append((a,b,(source.matrix_world.to_3x3()@p.normal).normalized(),bottom,top))
records={}
for name in ['Authored roof edge cornices','Authored low rise sill and lintel bands','Authored grouped window bays - varied low rise']:
 o=bpy.data.objects.get(name)
 if not o:continue
 ids=[]
 for p in o.data.polygons:
  cs=[o.matrix_world@o.data.vertices[i].co for i in p.vertices]
  for a,b,n,bottom,top in walls:
   d=b-a;L=d.length;t=d/L
   if all(0<q.z<top+.2 and abs((q-a).dot(n))<.5 and -.3<(q-a).dot(t)<L+.3 for q in cs):ids.append(p.index);break
 if ids:records[name]={'faces':ids,'materials':sorted(set(o.data.polygons[i].material_index for i in ids)),'material_names':[m.name if m else None for m in o.data.materials]}
(r/'docs/st-pauls-generic-strip-audit.json').write_text(json.dumps(records,indent=2)+'\n');print('CATHEDRAL_STRIP_AUDIT',json.dumps({k:len(v['faces']) for k,v in records.items()}),flush=True)
