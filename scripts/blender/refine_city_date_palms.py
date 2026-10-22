"""Authored pinnate palm geometry on retained Canary Island date-palm points."""
import bpy,json,math
from pathlib import Path
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3];revision='authored-pinnate-v2';mesh=bpy.data.meshes.get('Authored Canary Island palm - layered crown v2')
if not mesh:
 verts=[];faces=[];indices=[]
 def face(points,material):
  start=len(verts);verts.extend(points);faces.append(tuple(range(start,start+len(points))));indices.append(material)
 for i in range(12):
  a=i*math.tau/12;b=(i+1)*math.tau/12;face([(.42*math.cos(a),.42*math.sin(a),0),(.42*math.cos(b),.42*math.sin(b),0),(.32*math.cos(b),.32*math.sin(b),8),(.32*math.cos(a),.32*math.sin(a),8)],0)
 for layer in range(3):
  for frond in range(16):
   angle=frond*math.tau/16+layer*.17;dx,dy=math.cos(angle),math.sin(angle);nx,ny=-dy,dx;length=4.2-layer*.8
   def centre(t):return (dx*length*t,dy*length*t,8+(1.4*math.sin(math.pi*t)+2*t-.6*t*t if layer==2 else .9*math.sin(math.pi*t)+layer*.6*t-1.8*t*t))
   for i in range(12):
    a=centre(i/12);b=centre((i+1)/12);w=.055*(1-i/14);face([(a[0]-nx*w,a[1]-ny*w,a[2]),(b[0]-nx*w,b[1]-ny*w,b[2]),(b[0]+nx*w,b[1]+ny*w,b[2]),(a[0]+nx*w,a[1]+ny*w,a[2])],1+frond%2)
   for i in range(1,18):
    t=i/19;a=centre(t);spread=.65*math.sin(math.pi*t)**.6
    for sign in (-1,1):
     tip=(a[0]+nx*spread*sign+dx*.22,a[1]+ny*spread*sign+dy*.22,a[2]-.10);face([(a[0]-dx*.06,a[1]-dy*.06,a[2]),tip,(a[0]+dx*.06,a[1]+dy*.06,a[2]+.015)],1+(frond+i)%2)
 mesh=bpy.data.meshes.new('Authored Canary Island palm - layered crown v2');mesh.from_pydata(verts,[],faces)
 for label,color,rough in [('Authored date palm trunk',(.18,.13,.085),.9),('Authored date palm fronds dark',(.065,.17,.065),.8),('Authored date palm fronds light',(.13,.25,.075),.8)]:
  m=bpy.data.materials.get(label) or bpy.data.materials.new(label);m.use_nodes=True;s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*color,1);s.inputs['Roughness'].default_value=rough;mesh.materials.append(m)
 for p,i in zip(mesh.polygons,indices):p.material_index=i
 mesh.update();assert all(p.area>0 for p in mesh.polygons)
records=json.loads((root/'assets/source/environment/city-trees-expanded.json').read_text())['records'];count=0
for r in records:
 if r.get('common_name')!='Canary Island Date Palm':continue
 obj=bpy.data.objects.get('tree_'+str(r['com_id']))
 if not obj:continue
 obj.data=mesh;size=.85+(int(r['com_id'])%7)*.05;obj.scale=(size,size,size);obj.location.z=.32;obj.rotation_euler.z=(int(r['com_id'])%31)*math.tau/31;obj['palm_revision']=revision;obj['shape']='Mapped Canary Island Date Palm; authored 8 m stem, spreading pinnate leaves, variation and palette. Individual tree height/crown and present-day condition unmeasured.';obj['botanical_reference']='https://vicflora.rbg.vic.gov.au/flora/taxon/a3860b68-24a3-424a-8906-1f43be6d3497';count+=1
bpy.context.scene['authored_date_palm_count']=count;print('VERIFIED authored mapped date palms:',count,'shared mesh faces:',len(mesh.polygons))
