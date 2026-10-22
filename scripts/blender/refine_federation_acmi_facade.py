"""Incremental ACMI/Beer Deluxe cladding; current surveyed levels, reversible generic detail masks."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3];name='Federation ACMI and Beer Deluxe - authored triangular cladding'
if not bpy.data.objects.get(name) or bpy.data.objects[name].get('panel_revision')!='five-piece-v5':
 data=json.loads((root/'public/data/buildings.json').read_text());groups=json.loads((root/'assets/source/environment/city-facade-groups.json').read_text())['groups'];selected={'805929'};verts=[];faces=[];indices=[];ids=[];face_sections=[]
 mats=[]
 mats=[bpy.data.materials['Authored Federation Square '+label] for label in ['sandstone','zinc','glass']]
 for b in data['buildings']:
  if str(b['id'])=='20246':continue # Near-duplicate 2018 record superseded by 2022 section 20248.
  if groups[str(b['id'])]['structure_id'] not in selected or not bpy.data.objects.get('survey_'+str(b['id'])) or b['kind']!='Structure':continue
  b=dict(b);o=bpy.data.objects['survey_'+str(b['id'])];points=[o.matrix_world@v.co for v in o.data.vertices];b['base']=min(v.z for v in points);b['height']=max(v.z for v in points)-b['base']
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


# Mask only faces with explicit section ownership. Original assignments retained.
mask=bpy.data.materials.get('Federation ACMI generic detail mask')
if not mask:
 mask=bpy.data.materials.new('Federation ACMI generic detail mask');mask.use_nodes=True;nodes=mask.node_tree.nodes;nodes.clear();t=nodes.new('ShaderNodeBsdfTransparent');out=nodes.new('ShaderNodeOutputMaterial');mask.node_tree.links.new(t.outputs[0],out.inputs['Surface'])
report={}
for label in ['Authored grouped window bays - varied low rise','Authored low rise sill and lintel bands','Authored short low-rise window bays']:
 o=bpy.data.objects.get(label)
 if not o:continue
 attr=o.data.attributes.get('source_section')
 if not attr:
  report[label]={'masked':0,'reason':'No explicit source ownership; preserved'};continue
 if o.get('acmi_mask_recovery'):continue
 selected=[p for p in o.data.polygons if attr.data[p.index].value in {17198,17199}]
 if not selected:continue
 text=bpy.data.texts.new(label+' ACMI original assignments.json');text.write(json.dumps({str(p.index):p.material_index for p in selected}));o['acmi_mask_recovery']=text.name;slot=len(o.data.materials);o.data.materials.append(mask)
 for p in selected:p.material_index=slot
 report[label]={'masked':len(selected)}
bpy.context.scene['federation_acmi_facade_revision']='incremental-v1'
(root/'docs/federation-acmi-facade-audit.json').write_text(json.dumps({'masked_details':report,'limits':'Official visitor-map overlaps identify these source sections with ACMI and Beer Deluxe. Existing survey silhouettes and current heights retained. Panel cells and stone/zinc/glass distribution approximate; no exact facade reconstruction or photographic textures.'},indent=2)+'\n')
print('FEDERATION_ACMI_FACADE_UPDATED',report,flush=True)
