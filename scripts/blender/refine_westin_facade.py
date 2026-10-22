"""Historical precast reference informs authored Westin candidate wall and sill relief."""
import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
R=Path(bpy.data.filepath).resolve().parents[3]
source='https://nationalprecast.com.au/wp-content/uploads/2015/09/Precaster-24.pdf'
o=bpy.data.objects['survey_26410'];name='Westin candidate authored sandstone precast';m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(.56,.43,.29,1)
n=m.node_tree.nodes;l=m.node_tree.links;n.clear();out=n.new('ShaderNodeOutputMaterial');s=n.new('ShaderNodeBsdfPrincipled');s.inputs['Roughness'].default_value=.82;l.new(s.outputs['BSDF'],out.inputs['Surface']);tex=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=65;noise.inputs['Detail'].default_value=2;l.new(tex.outputs['Object'],noise.inputs['Vector']);r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=(.50,.38,.25,1);r.color_ramp.elements[1].color=(.58,.45,.31,1);l.new(noise.outputs['Fac'],r.inputs['Fac']);l.new(r.outputs['Color'],s.inputs['Base Color']);bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.001;l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],s.inputs['Normal'])
o['previous_westin_wall_material']=o.get('previous_westin_wall_material',o.data.materials[0].name);o.data.materials[0]=m;o['reference']=source;o['limits']='Location-based Westin structure identification, visually consistent with historical west elevation; main section only. Authored sandstone-look palette and fine grain, not calibrated colour or current-condition survey.'
col=bpy.data.collections.get('Westin authored sill relief')
if col:
 for obj in list(col.objects):bpy.data.objects.remove(obj,do_unlink=True)
else:col=bpy.data.collections.new('Westin authored sill relief');bpy.context.scene.collection.children.link(col)
b=next(b for b in json.loads((R/'public/data/buildings.json').read_text())['buildings'] if str(b['id'])=='26410');ring=b['ring'][:]
if ring[0]==ring[-1]:ring.pop()
# Only the long City Square-facing source edge, not arbitrary detail around every wall.
edges=[(Vector((x,-y,0)),Vector((ring[(i+1)%len(ring)][0],-ring[(i+1)%len(ring)][1],0))) for i,(x,y) in enumerate(ring)];a,end=max(edges,key=lambda pair:(pair[1]-pair[0]).length);delta=end-a;t=delta.normalized();normal=Vector((t.y,-t.x,0));signed=sum(ring[i-1][0]*(-ring[i][1])-ring[i][0]*(-ring[i-1][1]) for i in range(len(ring)))
if signed<0:normal=-normal
v=[];f=[];count=0
for floor in range(min(45,int(b['height']/3.6))):
 z=b['base']+1+floor*3.6
 for bay in range(min(30,int(delta.length/3.4))):
  bays=min(30,int(delta.length/3.4));center=a+t*((bay+.5)*delta.length/bays);k=len(v)
  for zz in [z-.12,z]:
   for dx,dn in [(-1.33,.02),(1.33,.02),(1.33,.25),(-1.33,.25)]:v.append(tuple(center+t*dx+normal*dn+Vector((0,0,zz))))
  f.extend([[k+j for j in q] for q in [[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]]);count+=1
mesh=bpy.data.meshes.new('Westin candidate projecting sill boxes');mesh.from_pydata(v,[],f);mesh.materials.append(m);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();obj=bpy.data.objects.new(mesh.name,mesh);col.objects.link(obj);col['reference']=source;col['limits']='Projecting cast sills documented in September2000 article. Placement follows existing illustrative window spacing, not surveyed original bays; .25m projection and .12m thickness authored. Bay windows, balconies, precast joints, podium and upper facade unfinished.'
print('VERIFIED Westin main wall and',count,'projecting sills',len(f),'faces',flush=True)
