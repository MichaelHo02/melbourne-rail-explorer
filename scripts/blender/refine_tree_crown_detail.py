"""Authored irregular crown clusters; public points do not measure crown geometry."""
import bpy,bmesh,json,math,random
from pathlib import Path
from mathutils import Vector
root=Path(bpy.data.filepath).resolve().parents[3]
meshes=[]
for variant in range(7):
    name=f'Authored irregular crown detail {variant}'
    mesh=bpy.data.meshes.get(name)
    if not mesh:
        rng=random.Random(4200+variant);bm=bmesh.new()
        clusters=[(0,0,-.1,.59)]
        for ring,count,radius,z in [(0,7,.55,.12),(1,5,.34,.53)]:
            for i in range(count):
                angle=i*math.tau/count+rng.uniform(-.24,.24)
                clusters.append((math.cos(angle)*radius,math.sin(angle)*radius,z+rng.uniform(-.12,.12),rng.uniform(.27,.39)))
        for cx,cy,cz,r in clusters:
            result=bmesh.ops.create_icosphere(bm,subdivisions=2,radius=r)
            for v in result['verts']:
                v.co*=1+.07*math.sin(v.co.x*23+v.co.y*19+v.co.z*17+variant)
                v.co+=Vector((cx,cy,cz))
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        mesh=bpy.data.meshes.new(name);bm.to_mesh(mesh);bm.free()
        mesh.materials.append(bpy.data.materials['Authored tree foliage'])
        for p in mesh.polygons:p.use_smooth=True
        mesh['limits']='Thirteen authored clusters; no measured canopy or species geometry.'
        mesh.update()
    meshes.append(mesh)
count=0
for r in json.loads((root/'assets/source/environment/city-trees-expanded.json').read_text())['records']:
    obj=bpy.data.objects.get('tree_'+str(r['com_id']))
    if not obj or 'palm' in (r.get('common_name') or '').lower():continue
    before=(tuple(obj.location),tuple(obj.scale))
    obj.data=meshes[int(r['com_id'])%len(meshes)]
    obj['crown_revision']='authored-irregular-v2'
    obj['shape']='Public inventory location retained; illustrative scale retained. Seven authored irregular silhouettes, not measured branches, species shape, season or condition.'
    assert before==(tuple(obj.location),tuple(obj.scale))
    count+=1
bpy.context.scene['irregular_tree_crown_count']=count
print('VERIFIED irregular crowns',count,'profiles',len(meshes))
