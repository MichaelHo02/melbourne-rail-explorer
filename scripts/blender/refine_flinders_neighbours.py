"""Restore survey sections wrongly removed by broad station rectangle."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path(bpy.data.filepath).resolve().parents[3]
d=json.loads((R/'assets/source/environment/flinders-neighbour-restoration.json').read_text());groups=json.loads((R/'assets/source/environment/city-facade-groups.json').read_text())['groups'];col=bpy.data.collections['CITY - surveyed envelopes with authored facade materials']
window_name='Flinders restored neighbour authored windows'
if not bpy.data.objects.get(window_name):
 v=[];f=[];added=[]
 colours=[(.43,.35,.25),(.49,.44,.34),(.37,.24,.16),(.40,.43,.40)]
 for b in d['restored']:
  name='survey_'+b['id'];assert not bpy.data.objects.get(name),name
  ring=b['ring'][:]
  if ring[0]==ring[-1]:ring.pop()
  n=len(ring);base=b['base'];top=base+b['height'];vs=[(x,-y,z) for z in [base,top] for x,y in ring];fs=[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]+[tuple(range(n,n*2)),tuple(reversed(range(n)))]
  mesh=bpy.data.meshes.new(name);mesh.from_pydata(vs,[],fs);bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update();o=bpy.data.objects.new(name,mesh);col.objects.link(o)
  g=groups[b['id']];style=int(g['structure_id'])%4;mn='Authored restored Flinders neighbour masonry '+str(style);m=bpy.data.materials.get(mn) or bpy.data.materials.new(mn);m.use_nodes=True;m.diffuse_color=(*colours[style],1);s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=m.diffuse_color;s.inputs['Roughness'].default_value=.82
  mesh.materials.append(m);mesh.materials.append(bpy.data.materials['Authored pale roof finish'])
  for p in mesh.polygons:
   if p.normal.z>.8:p.material_index=1
  o['source_id']=b['id'];o['source_url']=d['source'];o['limits']=d['limits']+' Own structure-group masonry palette and illustrative windows; finishes not surveyed.';added.append(b['id'])
  if b['kind']!='Structure' or b['height']<8:continue
  signed=sum(ring[i-1][0]*(-ring[i][1])-ring[i][0]*(-ring[i-1][1]) for i in range(n))
  for i,(x,y) in enumerate(ring):
   a=Vector((x,-y,0));xx,yy=ring[(i+1)%n];delta=Vector((xx-x,y-yy,0));length=delta.length
   bays=int(length/[3.3,4.1,4.7,3.4][style])
   if not bays:continue
   t=delta/length;normal=Vector((t.y,-t.x,0))*(1 if signed>0 else -1)
   for floor in range(int(b['height']/3.6)):
    bottom=base+1+floor*3.6;high=min(top-.6,bottom+2.1)
    if high<=bottom:continue
    for bay in range(bays):
     c=a+t*((bay+.5)*length/bays)+normal*.05;half=min(.95,length/bays*.29);k=len(v);v.extend([tuple(c+t*dx+Vector((0,0,z))) for dx,z in [(-half,bottom),(half,bottom),(half,high),(-half,high)]]);f.append((k,k+1,k+2,k+3))
 mesh=bpy.data.meshes.new(window_name);mesh.from_pydata(v,[],f);mesh.materials.append(bpy.data.objects['Authored grouped window bays - varied low rise'].data.materials[0]);mesh.update();o=bpy.data.objects.new(window_name,mesh);col.objects.link(o);o['limits']='Illustrative authored bays on restored source envelopes; no measured facade layouts.'
 assert len(added)==50
 (R/'docs/flinders-neighbour-scene-audit.json').write_text(json.dumps({'restored_source_ids':added,'windows':len(f),'existing_objects_overwritten':0,'limits':d['limits']},indent=2));print('VERIFIED restored',len(added),'source sections',len(f),'window quads',flush=True)
