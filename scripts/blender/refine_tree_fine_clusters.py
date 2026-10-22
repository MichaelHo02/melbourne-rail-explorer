"""Replace large smooth crown lobes with finer authored foliage sprays."""
import bpy,bmesh,json,math,random
from pathlib import Path
from mathutils import Vector
R=Path(bpy.data.filepath).resolve().parents[3];meshes=[]
for variant in range(7):
 name='Authored fine foliage crown '+str(variant);mesh=bpy.data.meshes.get(name)
 if not mesh:
  rng=random.Random(9120+variant);bm=bmesh.new();clusters=[]
  # Fibonacci shell avoids obvious repeated radial rings. Sizes unmeasured.
  for i in range(85):
   z=1-2*(i+.5)/85;angle=i*math.pi*(3-math.sqrt(5))+variant*.35;radius=math.sqrt(1-z*z);direction=Vector((radius*math.cos(angle),radius*math.sin(angle),z));centre=Vector((direction.x*.72,direction.y*.72,direction.z*.62+.08));centre+=Vector((rng.uniform(-.08,.08),rng.uniform(-.08,.08),rng.uniform(-.07,.07)));clusters.append((centre,rng.uniform(.13,.22)))
  for centre,r in clusters:
   result=bmesh.ops.create_icosphere(bm,subdivisions=1,radius=r)
   for v in result['verts']:
    v.co.x*=rng.uniform(.8,1.2);v.co.y*=rng.uniform(.8,1.2);v.co.z*=rng.uniform(.75,1.15);v.co+=centre
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));mesh=bpy.data.meshes.new(name);bm.to_mesh(mesh);bm.free();mesh.materials.append(bpy.data.materials['Authored tree foliage']);mesh.update();mesh['limits']='85 small irregular authored foliage clusters; not measured species, leaf shape, branches, canopy dimensions or condition.'
 meshes.append(mesh)
count=0
for r in json.loads((R/'assets/source/environment/city-trees-expanded.json').read_text())['records']:
 o=bpy.data.objects.get('tree_'+str(r['com_id']))
 if not o or 'palm' in (r.get('common_name') or '').lower():continue
 before=(tuple(o.location),tuple(o.scale));o.data=meshes[int(r['com_id'])%7];o['crown_revision']='authored-fine-clusters-v3';o['shape']='Mapped inventory position and illustrative object scale retained. Fine authored foliage clusters; species-specific geometry, season and condition unverified.';assert before==(tuple(o.location),tuple(o.scale));count+=1
print('VERIFIED finer crowns',count,'shared meshes',len(meshes),'faces each',len(meshes[0].polygons),flush=True)
