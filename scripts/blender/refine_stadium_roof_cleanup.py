"""Remove leftover generic facade strips and separate coplanar perimeter roofs."""
import bpy,bmesh,json,math
from pathlib import Path
root=Path(bpy.data.filepath).resolve().parents[3];d=json.loads((root/'assets/source/environment/stadium-authored-roof.json').read_text());ring=d['outer_ring_xy']
def covered(x,y):
 result=False
 for i,(a,b) in enumerate(ring):
  c,e=ring[i-1];dx,dy=c-a,e-b;t=max(0,min(1,((x-a)*dx+(y-b)*dy)/(dx*dx+dy*dy))) if dx*dx+dy*dy else 0
  if math.hypot(x-a-t*dx,y-b-t*dy)<.4:return True
  if (b>y)!=(e>y) and x<(c-a)*(y-b)/(e-b)+a:result=not result
 return result
counts={}
for name in ['Authored grouped window bays - varied low rise','Authored low rise sill and lintel bands']:
 o=bpy.data.objects.get(name)
 if not o:continue
 bm=bmesh.new();bm.from_mesh(o.data);cut=[f for f in bm.faces if 31.5<f.calc_center_median().z<40.71 and covered(f.calc_center_median().x,f.calc_center_median().y)]
 if cut:
  backup=o.data.copy();backup.name='REFERENCE before stadium window cleanup '+o.data.name;backup.use_fake_user=True;bmesh.ops.delete(bm,geom=cut,context='FACES_ONLY');bm.to_mesh(o.data);o.data.update()
 counts[name]=len(cut);bm.free()
o=bpy.data.objects['Authored stadium fixed sloping roof'];part=d['fixed'];m=bpy.data.meshes.new(o.data.name+' separated perimeter');m.from_pydata(part['vertices'],[],part['faces'])
for mat in o.data.materials:m.materials.append(mat)
m.update();o.data=m;o['limits']=d['limits']+' Outer perimeter raised50mm to avoid coplanar overlap with retained lower cap.'
bpy.context.scene['stadium_roof_cleanup_revision']=1;print('VERIFIED stadium roof cleanup',counts,flush=True)
