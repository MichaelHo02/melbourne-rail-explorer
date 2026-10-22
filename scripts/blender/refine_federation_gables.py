"""Apply authored roof profiles while preserving survey footprint bounds."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import intersect_point_tri_2d,tessellate_polygon
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3];name='Federation Square - authored gable roof profiles'
if not bpy.data.objects.get(name):
 d=json.loads((root/'assets/source/environment/federation-authored-gables.json').read_text());old=bpy.data.objects['Continuous surveyed roofs - authored finishes'];r=d['flat_roofs'];mesh=bpy.data.meshes.new('Survey flat roofs with gable cutouts');mesh.from_pydata(r['vertices'],[],r['faces'])
 for m in old.data.materials:mesh.materials.append(m)
 for p,i in zip(mesh.polygons,r['materials']):p.material_index=i
 mesh.update();old.data=mesh
 verts=[];faces=[]
 for section in d['sections']:
  start=len(verts);verts.extend(section['vertices']);faces.extend([tuple(start+i for i in f) for f in section['faces']]);ring=[Vector((x,y,0)) for x,y in section['ring'][:-1]];tris=[[ring[q] if isinstance(q,int) else q for q in tri] for tri in tessellate_polygon([ring])];n=section['normal'];mid=section['mid'];half=section['half_width'];base=section['base'];height=section['height']
  def inside(x,y):
   point=Vector((x,y))
   if any(intersect_point_tri_2d(point,*[Vector((q.x,q.y)) for q in tri]) for tri in tris):return True
   for i,a in enumerate(ring):
    av=Vector((a.x,a.y));b=ring[(i+1)%len(ring)];edge=Vector((b.x-a.x,b.y-a.y));t=max(0,min(1,(point-av).dot(edge)/max(edge.length_squared,1e-12)))
    if (point-av-edge*t).length<.2:return True
   return False
  # Conform source roof-section walls and their authored cladding to roof planes.
  for obj in [bpy.data.objects.get('survey_'+str(section['id']))]:
   if not obj:continue
   for v in obj.data.vertices:
    x,y,z=v.co
    if base-.01<=z<=base+height+.01 and inside(x,y):
     factor=max(0,1-abs((x*n[0]+y*n[1]-mid)/half));v.co.z=base+(z-base)*factor
   obj.data.update()
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.materials.append(bpy.data.materials['Authored Federation Square zinc']);mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(obj);obj['limits']=d['limits'];obj['source_ids']='20247,20248';obj['source_url']='https://data.melbourne.vic.gov.au/explore/dataset/2023-building-footprints/'
 assert all(p.area>0 and p.normal.z>0 for p in mesh.polygons)
 print('VERIFIED authored gable roof profiles:',len(mesh.polygons))

# Fit only panels belonging to each roof section, rather than neighbouring walls.
cladding=bpy.data.objects['Federation Square - authored triangular cladding']
if cladding.get('gable_fit_revision')!='section-owned-v2':
 d=json.loads((root/'assets/source/environment/federation-authored-gables.json').read_text());attribute=cladding.data.attributes['source_section']
 for section in d['sections']:
  indices={i for p,a in zip(cladding.data.polygons,attribute.data) if a.value==int(section['id']) for i in p.vertices}
  assert indices, 'Missing source-owned roof panels'
  n=section['normal'];base=section['base'];height=section['height']
  for i in indices:
   v=cladding.data.vertices[i];x,y,z=v.co;factor=max(0,1-abs((x*n[0]+y*n[1]-section['mid'])/section['half_width']));v.co.z=base+(z-base)*factor
 cladding.data.update();cladding['gable_fit_revision']='section-owned-v2';print('VERIFIED section-owned gable cladding fit')
