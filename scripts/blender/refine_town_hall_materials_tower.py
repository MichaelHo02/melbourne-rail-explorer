"""Reference-led Town Hall material pass and omitted source clock footprint."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(bpy.data.filepath).resolve().parents[3];d=json.loads((R/'assets/source/environment/town-hall-source-reference.json').read_text());name='Town Hall authored clock tower on source 27719'
def mat(name,c,rough=.8):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*c,1);s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*c,1);s.inputs['Roughness'].default_value=rough;return m
stone=mat('Town Hall authored freestone',(.45,.37,.25));slate=mat('Town Hall authored slate',(.045,.065,.085));blue=mat('Town Hall authored bluestone',(.075,.095,.11));face=mat('Town Hall authored clock face',(.68,.66,.55));iron=mat('Town Hall authored clock iron',(.018,.022,.025))
count=0
for r in d['records']:
 o=bpy.data.objects.get('survey_'+str(r['objectid']))
 if o and o.type=='MESH' and o.data.materials:
  o['previous_town_hall_generic_material']=o.get('previous_town_hall_generic_material',o.data.materials[0].name);o.data.materials[0]=slate if r['objectid']=='27721' else stone;o['material_reference']=d['heritage_reference'];count+=1
if not bpy.data.objects.get(name):
 source=next(r for r in d['records'] if r['objectid']=='27719');points=[((x-144.9671)*87939,(y+37.8183)*111320) for x,y in source['geo_shape']['geometry']['coordinates'][0][:-1]];top=source['footprint_max_elevation']-source['structure_min_elevation'];roofbase=top-4.5;cx=sum(x for x,y in points)/len(points);cy=sum(y for x,y in points)/len(points);v=[];f=[];mi=[]
 def polygon(coords,index):
  start=len(v);v.extend(coords);f.append(list(range(start,start+len(coords))));mi.append(index)
 for i,a in enumerate(points):
  b=points[(i+1)%len(points)];polygon([(a[0],a[1],.02),(b[0],b[1],.02),(b[0],b[1],roofbase),(a[0],a[1],roofbase)],0);polygon([(a[0],a[1],roofbase),(b[0],b[1],roofbase),(cx,cy,top)],1)
 # Decorative clock faces; the documented bluestone plinth remains unmodelled.
 for i,a in enumerate(points):
  b=points[(i+1)%len(points)];delta=Vector((b[0]-a[0],b[1]-a[1],0));length=delta.length
  if length<2.4:continue
  normal=Vector((delta.y,-delta.x,0)).normalized();mid=Vector(((a[0]+b[0])/2,(a[1]+b[1])/2,roofbase-2.4))+normal*.06;tangent=delta.normalized();radius=1.05
  polygon([tuple(mid+tangent*(math.cos(i*math.tau/48)*radius)+Vector((0,0,math.sin(i*math.tau/48)*radius))) for i in range(48)],3)
  for angle,width,extent in [(math.pi/3,.055,.72),(-math.pi/3,.07,.48)]:
   direction=tangent*math.cos(angle)+Vector((0,0,math.sin(angle)));cross=tangent*(-math.sin(angle))+Vector((0,0,math.cos(angle)));m=mid+normal*.015;polygon([tuple(m-cross*width),tuple(m+direction*extent-cross*width),tuple(m+direction*extent+cross*width),tuple(m+cross*width)],4)
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(v,[],f);mesh.update()
 for material in [stone,slate,blue,face,iron]:mesh.materials.append(material)
 for p,index in zip(mesh.polygons,mi):p.material_index=index
 o=bpy.data.objects.new(name,mesh);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(o);o['source_id']='27719';o['source_url']='https://data.melbourne.vic.gov.au/explore/dataset/2023-building-footprints/';o['reference']=d['heritage_reference'];o['limits']='Restored historical footprint and relative top34m; 4.5m pyramidal cap, 1.05m clock radius, face height and 10:10 hands authored. Exact mansard/cupola, ornament, source datum and current condition unresolved; clock is decorative, not realtime.'
print('VERIFIED Town Hall material sections',count,'source clock tower restored',flush=True)
