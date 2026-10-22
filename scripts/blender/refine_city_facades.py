"""Authored fenestration variation on retained structure groups; no photo textures."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3]
name='Authored grouped window bays - varied low rise'
if not bpy.data.objects.get(name):
 data=json.loads((root/'public/data/buildings.json').read_text());groups=json.loads((root/'assets/source/environment/city-facade-groups.json').read_text())['groups'];collection=bpy.data.collections['CITY - surveyed envelopes with authored facade materials'];old=bpy.data.objects['Authored window bays - illustrative spacing'];glass=old.data.materials[0];verts=[];faces=[];trimv=[];trimf=[];count=0;structures=set()
 def quad(v,f,p):
  start=len(v);v.extend(p);f.append(tuple(range(start,start+4)))
 for b in data['buildings']:
  obj=bpy.data.objects.get('survey_'+str(b['id']))
  if not obj or b['kind']!='Structure' or b['height']<8:continue
  group=groups[str(b['id'])];low=group['structure_height']<=45;key=int(group['structure_id']);style=key%3
  if low:
   first=obj.data.materials[0];label='Authored plain masonry - '+first.name;mat=bpy.data.materials.get(label)
   if not mat:
    mat=first.copy();mat.name=label;shader=mat.node_tree.nodes.get('Principled BSDF');links=mat.node_tree.links
    for link in list(links):
     if link.to_node==shader and link.to_socket==shader.inputs['Base Color']:links.remove(link)
    shader.inputs['Base Color'].default_value=first.diffuse_color;shader.inputs['Roughness'].default_value=.8;shader.inputs['Metallic'].default_value=0
   obj.data.materials[0]=mat;obj['fenestration_basis']='Authored low-rise proportions keyed by retained structure ID; exact facade unverified';count+=1;structures.add(group['structure_id'])
  ring=b['ring'][:]
  if ring[0]==ring[-1]:ring.pop()
  n=len(ring);base=b['base'];top=base+b['height'];signed=sum(ring[i-1][0]*(-ring[i][1])-ring[i][0]*(-ring[i-1][1]) for i in range(n))
  step=[3.6,3.9,4.1][style] if low else 3.6;spacing=[3.3,4.1,4.7][style] if low else 3.4
  for i,(x,z) in enumerate(ring):
   bx,bz=ring[(i+1)%n];a=Vector((x,-z,0));v=Vector((bx-x,z-bz,0));length=v.length
   if length<3:continue
   tangent=v/length;normal=Vector((tangent.y,-tangent.x,0))*(1 if signed>0 else -1);bays=min(30,int(length/spacing));floors=min(45,int(b['height']/step))
   for floor in range(floors):
    bottom=base+1+floor*step;high=min(top-.6,bottom+([2.25,2.0,2.4][style] if low else 2.15))
    if high<=bottom:continue
    for bay in range(bays):
     center=(bay+.5)*length/bays;half=min([.72,1.05,1.3][style],length/bays*.29) if low else min(1.25,length/bays*.36)
     left=a+tangent*(center-half)+normal*.05;right=a+tangent*(center+half)+normal*.05
     quad(verts,faces,[(left.x,left.y,bottom),(right.x,right.y,bottom),(right.x,right.y,high),(left.x,left.y,high)])
     if low:
      ll=left-tangent*.12+normal*.025;rr=right+tangent*.12+normal*.025
      for h in [bottom-.12,high]:quad(trimv,trimf,[(ll.x,ll.y,h),(rr.x,rr.y,h),(rr.x,rr.y,h+.1),(ll.x,ll.y,h+.1)])
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.materials.append(glass);mesh.update();obj=bpy.data.objects.new(name,mesh);collection.objects.link(obj);obj['source_url']=data['url'];obj['limits']='Authored window proportions and sill/lintel strips. Structure-group consistency only; no measured individual facade layouts.';obj['lowrise_sections']=count;obj['lowrise_structures']=len(structures)
 assert len(mesh.polygons)>0 and all(p.area>0 for p in mesh.polygons)
 old.hide_render=True;old.hide_set(True);old['replacement']=name
 mat=bpy.data.materials.new('Authored low rise sill stone');mat.use_nodes=True;shader=mat.node_tree.nodes.get('Principled BSDF');shader.inputs['Base Color'].default_value=(.43,.42,.37,1);shader.inputs['Roughness'].default_value=.85
 mesh=bpy.data.meshes.new('Authored low rise sill and lintel bands');mesh.from_pydata(trimv,[],trimf);mesh.materials.append(mat);mesh.update();obj=bpy.data.objects.new(mesh.name,mesh);collection.objects.link(obj);obj['limits']='Illustrative shallow sill and lintel strips; exact detailing not measured'
 print('VERIFIED grouped low-rise facade pass:',count,'sections',len(structures),'structures',len(faces),'window quads')
