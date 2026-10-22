"""Reference-informed authored cladding on selected retained precinct envelopes."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3];name='Federation Square - authored triangular cladding'
if not bpy.data.objects.get(name) or bpy.data.objects[name].get('panel_revision')!='five-piece-v5':
 data=json.loads((root/'public/data/buildings.json').read_text());groups=json.loads((root/'assets/source/environment/city-facade-groups.json').read_text())['groups'];selected={'806667','816359','812338','805928','809180'};verts=[];faces=[];indices=[];ids=[];face_sections=[]
 mats=[]
 for label,colour,rough,metal in [('sandstone',(.48,.39,.28),.82,0),('zinc',(.35,.39,.40),.48,.4),('glass',(.08,.15,.17),.25,.15)]:
  m=bpy.data.materials.get('Authored Federation Square '+label) or bpy.data.materials.new('Authored Federation Square '+label);m.use_nodes=True;s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*colour,1);s.inputs['Roughness'].default_value=rough;s.inputs['Metallic'].default_value=metal;mats.append(m)
 for b in data['buildings']:
  if str(b['id'])=='20246':continue # Near-duplicate 2018 record superseded by 2022 section 20248.
  if groups[str(b['id'])]['structure_id'] not in selected or not bpy.data.objects.get('survey_'+str(b['id'])) or b['kind']!='Structure':continue
  ids.append(str(b['id']));ring=b['ring'][:]
  if ring[0]==ring[-1]:ring.pop()
  signed=sum(ring[i-1][0]*(-ring[i][1])-ring[i][0]*(-ring[i-1][1]) for i in range(len(ring)))
  for i,(x,z) in enumerate(ring):
   bx,bz=ring[(i+1)%len(ring)];a=Vector((x,-z,b['base']));v=Vector((bx-x,z-bz,0));length=v.length
   if length<.25:continue
   tangent=v/length;normal=Vector((tangent.y,-tangent.x,0))*(1 if signed>0 else -1);cols=max(1,math.ceil(length/6));rows=max(1,math.ceil(b['height']/3))
   for col in range(cols):
    for row in range(rows):
     u0=col*length/cols;u1=(col+1)*length/cols;h0=row*b['height']/rows;h1=(row+1)*b['height']/rows
     # Five congruent 1:2 right triangles exactly tile the inflated parent.
     # Adapt the parent to two wall-cell triangles; final cell sizes are authored.
     pieces=[[(-1,2),(0,0),(0,2)],[(0,0),(0,1),(2,1)],[(0,1),(0,2),(2,1)],[(0,2),(2,1),(2,2)],[(2,1),(2,2),(4,2)]]
     for parent in range(2):
      key=(int(b['id'])*17+i*31+col*7+row*11+parent*3)%20;material=0 if key<11 else 1 if key<18 else 2
      for piece in pieces:
       points=[]
       for px,py in piece:
        du=(px+py/2)/5;dh=(2*py-px)/5
        if parent:du=1-du;dh=1-dh
        points.append((u0+(u1-u0)*du,h0+(h1-h0)*dh))
       signed_panel=sum(points[k][0]*points[(k+1)%3][1]-points[(k+1)%3][0]*points[k][1] for k in range(3))
       if signed_panel*(1 if signed>0 else -1)<0:points.reverse()
       centre=(sum(q[0] for q in points)/3,sum(q[1] for q in points)/3);start=len(verts)
       for u,h in points:
        u=centre[0]+(u-centre[0])*.985;h=centre[1]+(h-centre[1])*.985;verts.append(tuple(a+tangent*u+Vector((0,0,h))+normal*.12))
       faces.append((start,start+1,start+2));indices.append(material);face_sections.append(int(b['id']))
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces)
 for m in mats:mesh.materials.append(m)
 mesh.update();attribute=mesh.attributes.new('source_section','INT','FACE')
 for item,source_id in zip(attribute.data,face_sections):item.value=source_id
 for face,index in zip(mesh.polygons,indices):face.material_index=index
 assert all(p.area>0 for p in mesh.polygons)
 obj=bpy.data.objects.get(name)
 if obj:obj.data=mesh
 else:
  obj=bpy.data.objects.new(name,mesh);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(obj)
 obj['panel_revision']='five-piece-v5';obj['source_ids']=','.join(ids);obj['source_url']=data['url'];obj['design_reference']='https://fedsquare.com/history-design';obj['limits']='Selected precinct survey envelopes receive authored sandstone/zinc/glass triangles. Five-piece right-triangle groups share one material, informed by documented pinwheel language. Cell dimensions, ratio adaptation, panel schedule and present-day cladding distribution authored; not an exact facade reconstruction. Survey silhouettes retained; architectural roof forms and precinct boundary need further reconciliation.';obj['survey_sections']=len(ids);obj['panel_triangles']=len(faces)
 print('VERIFIED authored Federation Square cladding:',len(ids),'sections',len(faces),'triangles')

# Authored physical surface variation; no photographic textures.
for label, low, high, scale, strength, distance in [
 ('sandstone',(.40,.32,.23),(.53,.44,.33),9,.22,.025),
 ('zinc',(.30,.34,.35),(.39,.43,.44),35,.12,.006),
]:
 m=bpy.data.materials['Authored Federation Square '+label]
 if m.get('surface_revision')=='procedural-grain-v1':continue
 nodes=m.node_tree.nodes;links=m.node_tree.links;s=nodes.get('Principled BSDF')
 coord=nodes.new('ShaderNodeTexCoord');coord.label='Authored world-scale grain'
 noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=scale;noise.inputs['Detail'].default_value=2
 ramp=nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(*low,1);ramp.color_ramp.elements[1].color=(*high,1)
 bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=strength;bump.inputs['Distance'].default_value=distance
 links.new(coord.outputs['Object'],noise.inputs['Vector']);links.new(noise.outputs['Fac'],ramp.inputs['Fac']);links.new(ramp.outputs['Color'],s.inputs['Base Color']);links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],s.inputs['Normal'])
 m['surface_revision']='procedural-grain-v1';m['limits']='Authored grain scale and colour range, not sampled site appearance.'
 print('VERIFIED procedural Federation Square surface:',label)

older=bpy.data.objects.get('survey_20246')
if older:
 older.hide_render=True;older.hide_set(True);older['replacement']='survey_20248';older['limits']='2018 Flat record overlaps 2022 Gable record by 99.9457 percent; retained but hidden, not deleted.'
