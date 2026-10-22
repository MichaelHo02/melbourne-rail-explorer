"""Reversible NGV foundation/contact repair; no scene save."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parents[2];s=bpy.context.scene;key='ngv_platform_contact_revision'
if not s.get(key):
 d=json.loads((r/'assets/source/environment/ngv-platform-contact.json').read_text());ring=[];report={}
 protected=['Federation NGV - nested pinwheel panels','Atrium capture guided glazed roof','NGV eastern captured-fit roof relief']
 def signature(name):
  o=bpy.data.objects[name];return hashlib.sha256(str(([tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons],[p.material_index for p in o.data.polygons])).encode()).hexdigest()
 before={name:signature(name) for name in protected}
 def inside(x,y):
  yes=False
  for i,a in enumerate(ring):
   b=ring[i-1]
   if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:yes=not yes
  return yes
 def copy(o):
  old=o.data;old.use_fake_user=True;o['ngv_platform_original_mesh']=old.name;o.data=old.copy();return o.data
 clipped=json.loads((r/'assets/source/environment/ngv-platform-clipped-ground.json').read_text())
 def trim(name):
  o=bpy.data.objects[name];old=o.data;old.use_fake_user=True;o['ngv_platform_original_mesh']=old.name;data=clipped[name]
  assert len(old.vertices)==data['audit']['original_vertex_count'],(name,'source topology drift')
  assert all(max(abs(v.co[j]-data['vertices'][v.index][j]) for j in range(3))<1e-5 for v in old.vertices),(name,'source coordinates drift')
  me=bpy.data.meshes.new(old.name+' exact outside NGV contact');me.from_pydata(data['vertices'],[],data['faces']);me.update()
  for mat in old.materials:me.materials.append(mat)
  for p,material in zip(me.polygons,data['materials']):p.material_index=material
  o.data=me;report[name]=dict(data['audit'],backup=old.name)
 # Keep a clean horizontal source-base plinth; closures meet existing support vertically.
 supports=[BVHTree.FromObject(bpy.data.objects[n],bpy.context.evaluated_depsgraph_get()) for n in ['Federation fitted captured-height deck','Authored ground with City Square portal','Atrium assumed graded concrete floor']]
 for name in ['Federation fitted captured-height deck','Federation approximate deck closure walls','Federation approximate building base closures']:trim(name)
 me=bpy.data.meshes.new('NGV continuous captured-ground contact');me.from_pydata(d['vertices'],[],d['faces']);me.update();mat=bpy.data.materials.new('Authored NGV landscape neutral paving');mat.use_nodes=True;p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.22,.23,.225,1);p.inputs['Roughness'].default_value=.83;me.materials.append(mat);o=bpy.data.objects.new(me.name,me);s.collection.objects.link(o);o['limits']=d['limits'];o['source']=d['source'];bpy.context.view_layer.update();bvh=BVHTree.FromObject(o,bpy.context.evaluated_depsgraph_get())
 edges={}
 for f in d['faces']:
  for a,b in zip(f,f[1:]+f[:1]):
   k=tuple(sorted((a,b)));edges[k]=edges.get(k,0)+1
 wallvs=[];wallfs=[]
 for (a,b),count in edges.items():
  if count!=1:continue
  va,vb=d['vertices'][a],d['vertices'][b];bottom=[]
  for v in [va,vb]:
   hits=[t.ray_cast(Vector((v[0],v[1],50)),Vector((0,0,-1)),100)[0] for t in supports];heights=[q.z for q in hits if q is not None];bottom.append(min(v[2],max(heights))-.03 if heights else .38)
  if max(va[2]-bottom[0],vb[2]-bottom[1])<.05:continue
  k=len(wallvs);wallvs.extend([va,vb,[vb[0],vb[1],bottom[1]],[va[0],va[1],bottom[0]]]);wallfs.append([k,k+1,k+2,k+3])
 wallme=bpy.data.meshes.new('NGV continuous foundation retaining closures');wallme.from_pydata(wallvs,[],wallfs);wallme.update();wallme.materials.append(mat);wallobj=bpy.data.objects.new(wallme.name,wallme);s.collection.objects.link(wallobj);wallobj['limits']='Authored narrow1m plinth boundary and vertical closures to existing visible ground; not surveyed structural podium.';report['clean_foundation_boundary_walls']=len(wallfs)
 # Repair only lower authored Atrium wall seams, not roof or surveyed skin.
 north=6.7701292
 def floor(y):return north+(12.2-north)*max(0,min(1,(139-y)/90))
 for name in ['Atrium adjacent upper and lower cut closures','NGV east Atrium exposed envelope closure']:
  o=bpy.data.objects[name];me=copy(o);n=0
  for v in me.vertices:
   if v.co.z<12.21:v.co.z=floor(v.co.y);n+=1
  me.update();report[name]={'lower_vertices_fitted':n}
 assert all(signature(name)==before[name] for name in protected),'Protected NGV facade/roof changed'
 report['protected_ngv_mesh_hashes']=before
 s[key]='historical-ground-contiguous-contact-v1';s['ngv_platform_limits']=d['limits'];(r/'docs/ngv-platform-contact-audit.json').write_text(json.dumps({'revision':s[key],'objects':report,'contact_vertices':len(d['vertices']),'contact_faces':len(d['faces']),'limits':d['limits']},indent=2)+'\n');print('NGV_PLATFORM_CONTACT_APPLIED',report,flush=True)
else:print('NGV_PLATFORM_CONTACT_ALREADY_APPLIED',flush=True)
