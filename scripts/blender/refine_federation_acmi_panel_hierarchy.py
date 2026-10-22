"""Two-level pinwheel trial on ACMI envelopes; authored layout, retained geometry recoverable."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).resolve().parents[3];name='Federation ACMI - nested pinwheel panels';old=bpy.data.objects['Federation ACMI and Beer Deluxe - authored triangular cladding'];vs=[];fs=[];mi=[];owned=[];panels=[]
pieces=[[(-1,2),(0,0),(0,2)],[(0,0),(0,1),(2,1)],[(0,1),(0,2),(2,1)],[(0,2),(2,1),(2,2)],[(2,1),(2,2),(4,2)]]
def subdivide(t):
 a,b,c=t
 return [[(a[0]+(b[0]-a[0])*((x+y/2)/5)+(c[0]-a[0])*((2*y-x)/5),a[1]+(b[1]-a[1])*((x+y/2)/5)+(c[1]-a[1])*((2*y-x)/5)) for x,y in piece] for piece in pieces]
for sid in [17198,17199]:
 o=bpy.data.objects['survey_'+str(sid)];coords=[o.matrix_world@v.co for v in o.data.vertices];base=min(v.z for v in coords);ring=[v for v in coords if abs(v.z-base)<.001];top=coords[len(ring):];assert len(top)==len(ring)
 signed=sum(a.x*b.y-b.x*a.y for a,b in zip(ring,ring[1:]+ring[:1]));direction=1 if signed>0 else -1
 for edge,(a,b) in enumerate(zip(ring,ring[1:]+ring[:1])):
  length=(b-a).length
  if length<.25:continue
  tangent=(b-a)/length;normal=Vector((tangent.y,-tangent.x,0))*direction;hleft=top[edge].z-base;hright=top[(edge+1)%len(top)].z-base;height=max(hleft,hright);cols=max(1,math.ceil(length/12));rows=max(1,math.ceil(height/6))
  for col in range(cols):
   for row in range(rows):
    u0=col/cols;u1=(col+1)/cols;v0=row/rows;v1=(row+1)/rows
    for parent,t in enumerate([[(u0,v0),(u1,v0),(u0,v1)],[(u1,v1),(u0,v1),(u1,v0)]]):
     for panel,triangle in enumerate(subdivide(t)):
      seed=int.from_bytes(hashlib.sha256(f'{sid}:{edge}:{col}:{row}:{parent}:{panel}'.encode()).digest()[:4],'big')%100;material=0 if seed<68 else 1 if seed<94 else 2;pid=len(panels);panels.append({'section':sid,'edge':edge,'column':col,'row':row,'parent':parent,'panel':panel,'material':material})
      for leaf in subdivide(triangle):
       centre=(sum(q[0] for q in leaf)/3,sum(q[1] for q in leaf)/3);points=[]
       for u,v in leaf:
        u=centre[0]+(u-centre[0])*.992;v=centre[1]+(v-centre[1])*.992;points.append(a+tangent*(u*length)+Vector((0,0,v*(hleft+(hright-hleft)*u)))+normal*.14)
       if (points[1]-points[0]).cross(points[2]-points[0]).dot(normal)<0:points.reverse()
       k=len(vs);vs.extend([tuple(q) for q in points]);fs.append((k,k+1,k+2));mi.append(material);owned.append(sid)
mesh=bpy.data.meshes.new(name);mesh.from_pydata(vs,[],fs)
for label in ['sandstone','zinc','glass']:mesh.materials.append(bpy.data.materials['Authored Federation Square '+label])
mesh.update();assert all(p.area>0 for p in mesh.polygons);a=mesh.attributes.new('source_section','INT','FACE')
for p,i,sid in zip(mesh.polygons,mi,owned):p.material_index=i;a.data[p.index].value=sid
obj=bpy.data.objects.get(name)
if obj:obj.data=mesh
else:obj=bpy.data.objects.new(name,mesh);old.users_collection[0].objects.link(obj)
old.hide_render=True;old.hide_set(True);old['replacement']=name;obj['reference']='https://fedsquare.com/history-design';obj['limits']='Two nested five-triangle subdivisions implement documented panel hierarchy.12m x6m target macro cells,68/26/6 material weighting and distribution authored; not real panel schedule. Source envelopes and captured upper roof slope retained; no photographic textures.';bpy.context.scene['federation_acmi_panel_revision']='nested-five-v1';(r/'docs/federation-acmi-panel-audit.json').write_text(json.dumps({'triangles':len(fs),'panels':len(panels),'status':'trial unless saved scene marker verified','limits':obj['limits']},indent=2)+'\n');print('ACMI_NESTED_PANELS',len(fs),len(panels),flush=True)
