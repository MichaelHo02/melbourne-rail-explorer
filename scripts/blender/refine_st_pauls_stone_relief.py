"""Incremental authored cathedral stone shaders and illustrative lancet surrounds.
Keeps survey vertices, fitted datum and existing roof/spire silhouette intact.
"""
import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path(bpy.data.filepath).resolve().parents[3]
scene=bpy.context.scene
revision='authored-stone-relief-v1'
if scene.get('st_pauls_stone_relief_revision')!=revision:
 assert scene.get('federation_street_levels_revision')=='captured-streets-v1'
 limits='Authored colour values, procedural stone grain, lancet surrounds and slate response. No photographic textures. Material family supported by cathedral guide; exact finishes and dimensions unmeasured.'
 def stone(name,low,high):
  m=bpy.data.materials[name];m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;n.clear()
  out=n.new('ShaderNodeOutputMaterial');bs=n.new('ShaderNodeBsdfPrincipled');l.new(bs.outputs['BSDF'],out.inputs['Surface']);bs.inputs['Roughness'].default_value=.84
  tex=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=2.4;noise.inputs['Detail'].default_value=3;l.new(tex.outputs['Object'],noise.inputs['Vector'])
  ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(*low,1);ramp.color_ramp.elements[1].color=(*high,1);l.new(noise.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs['Color'],bs.inputs['Base Color'])
  grain=n.new('ShaderNodeTexNoise');grain.inputs['Scale'].default_value=35;grain.inputs['Detail'].default_value=2;l.new(tex.outputs['Object'],grain.inputs['Vector'])
  bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.08;bump.inputs['Distance'].default_value=.012;l.new(grain.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],bs.inputs['Normal'])
  m.diffuse_color=(*[(a+b)/2 for a,b in zip(low,high)],1);m['limits']=limits
 stone('Authored St Pauls warm masonry',(.28,.17,.075),(.36,.235,.12))
 stone('Authored St Pauls spire stone',(.22,.13,.055),(.30,.19,.085))
 roof=bpy.data.materials['Authored cathedral slate roof'];bs=roof.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.035,.047,.052,1);bs.inputs['Roughness'].default_value=.73;roof.diffuse_color=(.035,.047,.052,1);roof['limits']=limits
 # Rings follow existing authored pointed openings, without claiming measured tracery.
 panes=bpy.data.objects['St Pauls Cathedral - authored lancet bays'];verts=[];faces=[]
 for p in panes.data.polygons:
  points=[panes.matrix_world@panes.data.vertices[i].co for i in p.vertices];centre=sum(points,Vector())/len(points);normal=(panes.matrix_world.to_3x3()@p.normal).normalized();normal.z=0;normal.normalize()
  inner=[q+normal*.045 for q in points];outer=[]
  for q in points:
   d=q-centre;horizontal=Vector((d.x,d.y,0));horizontal.normalize();outer.append(q+horizontal*.16+Vector((0,0,.16 if d.z>0 else -.16))+normal*.17)
  k=len(verts);verts.extend(inner+outer);count=len(points)
  for i in range(count):j=(i+1)%count;faces.append((k+i,k+j,k+count+j,k+count+i))
 name='St Pauls Cathedral - authored stone lancet surrounds';mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.materials.append(bpy.data.materials['Authored St Pauls warm masonry']);mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(obj);obj['limits']=limits
 assert all(p.area>1e-7 for p in mesh.polygons)
 scene['st_pauls_stone_relief_revision']=revision
 audit={'revision':revision,'surround_faces':len(faces),'openings':len(panes.data.polygons),'source':'https://cathedral.org.au/wp-content/uploads/2022/11/2022-English-Guide-Sheet-Final.pdf','limits':limits,'survey_geometry_changed':False,'datum_changed':False}
 (root/'docs/st-pauls-stone-relief-audit.json').write_text(json.dumps(audit,indent=2))
 print('CATHEDRAL_STONE_RELIEF',len(faces))
else:print('CATHEDRAL_STONE_RELIEF_ALREADY_APPLIED')
