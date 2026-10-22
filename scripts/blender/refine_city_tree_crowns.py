"""Shared authored lobed crowns; retained points do not measure canopy form."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3];profiles=[[(0,0,0,.74),(-.43,0,.12,.55),(.42,.1,.05,.57),(0,-.42,.15,.55),(0,.24,.48,.58)],[(0,0,-.05,.72),(-.35,-.22,.15,.56),(.40,-.12,.28,.53),(-.1,.42,.22,.53),(.15,.1,.62,.48)],[(0,0,0,.70),(-.48,-.12,.12,.48),(.32,-.32,.24,.54),(.15,.40,.07,.57),(-.1,.10,.53,.57)]];meshes=[]
for index,lobes in enumerate(profiles):
 label='Authored lobed tree crown '+str(index);mesh=bpy.data.meshes.get(label)
 if not mesh:
  bm=bmesh.new()
  for cx,cy,cz,radius in lobes:
   result=bmesh.ops.create_icosphere(bm,subdivisions=2,radius=radius)
   for v in result['verts']:
    v.co*=1+.025*math.sin(v.co.x*11+v.co.y*7+index);v.co+=Vector((cx,cy,cz))
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));mesh=bpy.data.meshes.new(label);bm.to_mesh(mesh);bm.free();mesh.materials.append(bpy.data.materials['Authored tree foliage']);mesh.update()
  for p in mesh.polygons:p.use_smooth=True
  mesh['authored_detail_version']=1;mesh['limits']='Five overlapping authored crown lobes, not measured branches or species-specific canopy.'
 meshes.append(mesh)
records=json.loads((root/'assets/source/environment/city-trees-expanded.json').read_text())['records'];count=0
for r in records:
 obj=bpy.data.objects.get('tree_'+str(r['com_id']))
 if not obj:continue
 if 'palm' in (r.get('common_name') or '').lower():
  obj.data['authored_detail_version']=1;continue
 key=int(r['com_id']);obj.data=meshes[key%3];obj.rotation_euler.z=(key%37)*math.tau/37;obj['crown_revision']='authored-lobed-v1';obj['shape']='Retained Urban Forest point; three authored lobed crown variants and rotation. Existing illustrative scale retained; individual canopy, height, branches, season and condition unmeasured.';expected=((r['longitude']-144.9671)*87939,(r['latitude']+37.8183)*111320);assert abs(obj.location.x-expected[0])<.01 and abs(obj.location.y-expected[1])<.01;count+=1
bpy.context.scene['authored_lobed_crown_count']=count;print('VERIFIED mapped lobed crowns:',count,'shared profiles:',len(meshes),'faces per profile:',len(meshes[0].polygons))
