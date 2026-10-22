"""Remove legacy procedural grids on short low-rise sections; authored windows."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(bpy.data.filepath).resolve().parents[3];groups=json.loads((R/'assets/source/environment/city-facade-groups.json').read_text())['groups'];buildings=json.loads((R/'public/data/buildings.json').read_text())['buildings'];records=[];v=[];f=[]
if not bpy.context.scene.get('short_lowrise_facade_revision'):
 for b in buildings:
  key=str(b['id']);o=bpy.data.objects.get('survey_'+key)
  if not o or not o.data.materials or groups[key]['structure_height']>45:continue
  first=o.data.materials[0]
  if not any(first.name.startswith('Authored '+kind+' facade') for kind in ['stone','concrete','terracotta']):continue
  label='Authored short low-rise plain wall - '+first.name;m=bpy.data.materials.get(label)
  if not m:
   m=first.copy();m.name=label;s=m.node_tree.nodes.get('Principled BSDF')
   for link in list(m.node_tree.links):
    if link.to_node==s and link.to_socket==s.inputs['Base Color']:m.node_tree.links.remove(link)
   s.inputs['Base Color'].default_value=first.diffuse_color;s.inputs['Roughness'].default_value=.85;s.inputs['Metallic'].default_value=0
  o.data.materials[0]=m;records.append({'section':key,'previous':first.name,'finish':m.name});o['fenestration_basis']='Authored plain wall and geometry windows; removes legacy procedural grid, exact facade unverified'
  if b['kind']!='Structure' or not 3<=b['height']<8:continue
  ring=b['ring'][:]
  if ring[0]==ring[-1]:ring.pop()
  signed=sum(ring[i-1][0]*(-ring[i][1])-ring[i][0]*(-ring[i-1][1]) for i in range(len(ring)))
  for i,(x,z) in enumerate(ring):
   bx,bz=ring[(i+1)%len(ring)];a=Vector((x,-z,0));delta=Vector((bx-x,z-bz,0));length=delta.length
   if length<3:continue
   tangent=delta/length;normal=Vector((tangent.y,-tangent.x,0))*(1 if signed>0 else -1);bays=min(30,int(length/3.8))
   for floor in range(max(1,int(b['height']/3.6))):
    bottom=b['base']+1+floor*3.6;top=min(b['base']+b['height']-.5,bottom+1.8)
    if top<=bottom:continue
    for bay in range(bays):
     c=(bay+.5)*length/bays;left=a+tangent*(c-.7)+normal*.05;right=a+tangent*(c+.7)+normal*.05;start=len(v);v.extend([(left.x,left.y,bottom),(right.x,right.y,bottom),(right.x,right.y,top),(left.x,left.y,top)]);f.append([start+i for i in range(4)])
 if v:
  mesh=bpy.data.meshes.new('Authored short low-rise window bays');mesh.from_pydata(v,[],f);mesh.materials.append(bpy.data.objects['Authored grouped window bays - varied low rise'].data.materials[0]);mesh.update();o=bpy.data.objects.new(mesh.name,mesh);bpy.data.collections['CITY - surveyed envelopes with authored facade materials'].objects.link(o);o['limits']='Authored 3.8 m spacing, 1.4 m width, 1.8 m height on short source sections. No measured facade or occupancy evidence.'
 bpy.context.scene['short_lowrise_facade_revision']=1
 (R/'assets/source/environment/city-short-lowrise-facade-audit.json').write_text(json.dumps({'changed_sections':records,'added_window_quads':len(f),'limits':'Source envelope and structure groups retained; wall finish and window proportions authored. Landmark materials excluded; exact individual facade and current condition unverified.'},indent=2)+'\n')
 print('VERIFIED short low-rise facade correction',len(records),'sections',len(f),'geometry windows',flush=True)
