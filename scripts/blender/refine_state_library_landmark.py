"""Reversible primary-reference-led Library landmark; no photographic textures."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(globals().get('root') or Path(bpy.data.filepath).resolve().parents[3]);s=bpy.context.scene
if s.get('state_library_revision')!='portico-dome-v1':
 groups=json.loads((R/'assets/source/environment/city-facade-groups.json').read_text())['groups'];ids={k for k,v in groups.items() if v['structure_id']=='805833'};src={b['id']:b for b in json.loads((R/'public/data/buildings.json').read_text())['buildings'] if b['id'] in ids}
 reference='https://www.slv.vic.gov.au/visit/our-magnificent-spaces/swanston-street-welcome-zone';limits='Primary references support sandstone Palladian facade, Corinthian portico and 35m reading-room dome. Survey envelopes retained recoverably. Portico dimensions, six-front/two-return column interpretation, simplified capitals, facade bay positions, dome external profile and colours authored, not measured; no photographic textures.'
 def mat(name,col,rough=.75,metal=0):
  m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*col,1);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=m.diffuse_color;p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
 mats=[mat('State Library authored sandstone',(.48,.405,.29)),mat('State Library authored shadow glazing',(.045,.067,.071),.3),mat('State Library authored pale dome',(.5,.52,.48),.6),mat('State Library authored slate',(.085,.105,.11),.6),mat('State Library authored dark base',(.16,.175,.17))]
 for ident in ids:
  o=bpy.data.objects.get('survey_'+ident)
  if not o:continue
  backup=o.data.copy();backup.name='State Library original envelope '+ident;backup.use_fake_user=True;o['state_library_original_mesh']=backup.name;o.data=o.data.copy();o.data.materials[0]=mats[0]
  for i in range(1,len(o.data.materials)):o.data.materials[i]=mats[3]
  o['state_library_reference']=reference;o['state_library_limits']=limits
 # Remove only generic faces attributable to Library source boundaries/heights.
 polygons=[]
 for ident,b in src.items():
  ring=[Vector((x,-y,0)) for x,y in b['ring'][:-1]];polygons.append((ident,ring,b['base'],b['base']+b['height']))
 def distance(p,a,b):
  d=b-a;return (p-(a+d*max(0,min(1,(p-a).dot(d)/max(d.length_squared,1e-10))))).length
 def inside(v,ring):
  p=Vector((v.x,v.y,0))
  if any(distance(p,a,ring[(j+1)%len(ring)])<.15 for j,a in enumerate(ring)):return True
  hit=False
  for j,a in enumerate(ring):
   b=ring[(j+1)%len(ring)]
   if (a.y>p.y)!=(b.y>p.y) and p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x:hit=not hit
  return hit
 removals={}
 for name in ['Authored grouped window bays - varied low rise','Authored low rise sill and lintel bands','Authored roof edge cornices','Continuous surveyed roofs - authored finishes']:
  o=bpy.data.objects.get(name)
  if not o or o.type!='MESH':continue
  bad=set()
  for p in o.data.polygons:
   co=[o.matrix_world@o.data.vertices[i].co for i in p.vertices];centre=sum(co,Vector())/len(co)
   if not(-250<centre.x<-35 and 875<centre.y<1040):continue
   for ident,ring,lo,hi in polygons:
    # Vertical overlays: all face XY points hug one retained edge, all Z within section.
    if name!='Continuous surveyed roofs - authored finishes':
     if min(v.z for v in co)<lo-.5 or max(v.z for v in co)>hi+.5:continue
     if any(all(distance(Vector((v.x,v.y,0)),a,ring[(j+1)%len(ring)])<.7 for v in co) for j,a in enumerate(ring)):bad.add(p.index);break
    elif all(abs(v.z-hi)<.3 for v in co):
     # Only roofs within verified drum/lantern bounding extents. Avoid neighbours.
     if all(inside(v,ring) for v in co):bad.add(p.index);break
  if bad:
   old=o.data;old.use_fake_user=True;o['state_library_overlay_original_mesh']=old.name;m=bpy.data.meshes.new(name+' without State Library generic overlays');m.from_pydata([tuple(v.co) for v in old.vertices],[],[tuple(p.vertices) for p in old.polygons if p.index not in bad]);[m.materials.append(ma) for ma in old.materials]
   for p,q in zip(m.polygons,[p for p in old.polygons if p.index not in bad]):p.material_index=q.material_index
   m.update();o.data=m;removals[name]=len(bad)
 # Remove whole authored equipment units from the captured dome footprint only.
 plant=bpy.data.objects.get('Authored rooftop equipment - illustrative')
 if plant:
  old=plant.data;bad=set();drum=next(r for ident,r,lo,hi in polygons if ident=='12851')
  for p in old.polygons:
   co=[plant.matrix_world@old.vertices[i].co for i in p.vertices]
   if all(v.z>=29.4 and inside(v,drum) for v in co):bad.add(p.index)
  if bad:
   old.use_fake_user=True;plant['state_library_original_equipment_mesh']=old.name;m=bpy.data.meshes.new('Rooftop equipment without State Library dome');m.from_pydata([tuple(v.co) for v in old.vertices],[],[tuple(p.vertices) for p in old.polygons if p.index not in bad]);[m.materials.append(ma) for ma in old.materials]
   for p,q in zip(m.polygons,[p for p in old.polygons if p.index not in bad]):p.material_index=q.material_index
   m.update();plant.data=m;removals['dome_equipment_faces']=len(bad)
 # Upper source is tall narrow envelope; retain hidden for recovery, replace silhouette.
 bpy.data.objects['survey_12852'].hide_render=True;bpy.data.objects['survey_12852'].hide_set(True)
 v=[];f=[];mi=[]
 def face(points,idx):
  st=len(v);v.extend([tuple(p) for p in points]);f.append(tuple(range(st,st+len(points))));mi.append(idx)
 def box(c,t,n,w,d,h,idx):
  pp=[c+t*u+n*q+Vector((0,0,z)) for z in [-h/2,h/2] for u,q in [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]]
  for ii in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:face([pp[i] for i in ii],idx)
 # Survey envelopes contain walls only. Tessellate retained top rings explicitly.
 from mathutils.geometry import tessellate_polygon
 for ident,b in src.items():
  if ident=='12852':continue
  ring=[Vector((x,-y,b['base']+b['height']+.04)) for x,y in b['ring'][:-1]]
  for triangle in tessellate_polygon([ring]):
   points=[ring[i] for i in triangle] if isinstance(triangle[0],int) else list(triangle)
   if (points[1]-points[0]).cross(points[2]-points[0]).z<0:points.reverse()
   face(points,2 if ident=='12851' else 3)
 t=Vector((.342,.94,0));n=Vector((-.94,.342,0));c=Vector((-220.8,926.5,0))
 for k in range(5):box(c+n*(4-k*.45)+Vector((0,0,1.25+k*.3)),t,n,25-k*.5,9-k*.5,.3,0)
 for u,depth in [(u,7) for u in [-9.5,-5.7,-1.9,1.9,5.7,9.5]]+[(-9.5,1.5),(9.5,1.5)]:
  cc=c+t*u+n*depth
  for j in range(20):
   a=j*2*math.pi/20;b=(j+1)*2*math.pi/20
   face([cc+t*(math.cos(a)*.55)+n*(math.sin(a)*.55)+Vector((0,0,3)),cc+t*(math.cos(b)*.55)+n*(math.sin(b)*.55)+Vector((0,0,3)),cc+t*(math.cos(b)*.46)+n*(math.sin(b)*.46)+Vector((0,0,12)),cc+t*(math.cos(a)*.46)+n*(math.sin(a)*.46)+Vector((0,0,12))],0)
  for z,w,h in [(2.8,1.4,.4),(12.1,1.35,.45)]:box(cc+Vector((0,0,z)),t,n,w,1.35,h,0)
 box(c+n*4+Vector((0,0,12.9)),t,n,24,8.2,1.2,0)
 front=c+n*8.2;back=c+n*.1
 face([front-t*12+Vector((0,0,13.5)),front+t*12+Vector((0,0,13.5)),front+Vector((0,0,17))],0)
 face([back-t*12+Vector((0,0,13.5)),front-t*12+Vector((0,0,13.5)),front+Vector((0,0,17)),back+Vector((0,0,17))],3)
 face([back+Vector((0,0,17)),front+Vector((0,0,17)),front+t*12+Vector((0,0,13.5)),back+t*12+Vector((0,0,13.5))],3)
 # Fit wing openings and pilasters onto actual retained west-facing wall edges.
 ring=[Vector((x,-y,0)) for x,y in src['12840']['ring'][:-1]]
 facade_bays=0
 for j,a in enumerate(ring):
  b=ring[(j+1)%len(ring)];dt=b-a;length=dt.length
  if length<5:continue
  tt=dt/length;nn=Vector((tt.y,-tt.x,0))
  if nn.x>-.85 or (a.x+b.x)/2>-190:continue
  mid=(a+b)/2+nn*.12
  for z,h in [(2,.4),(13.6,.45),(15.1,.35)]:box(mid+Vector((0,0,z)),tt,nn,length,.3,h,0)
  # Central wall sits behind portico. Wings get ordered two-tier rectangular bays.
  bays=max(1,round(length/4.6))
  for k in range(bays):
   cc=a+tt*((k+.5)*length/bays)+nn*.15
   for zz,hh in [(5.2,3.4),(10,3.8)]:
    box(cc+Vector((0,0,zz)),tt,nn,1.85,.10,hh,1)
    if zz==10:
     center=cc+nn*.07+Vector((0,0,zz+hh/2))
     for q in range(12):
      aa=q*math.pi/12;bb=(q+1)*math.pi/12;face([center,center+tt*(.925*math.cos(aa))+Vector((0,0,.925*math.sin(aa))),center+tt*(.925*math.cos(bb))+Vector((0,0,.925*math.sin(bb)))],1)
    for z in [zz-hh/2-.13,zz+hh/2+.13]:box(cc+nn*.08+Vector((0,0,z)),tt,nn,2.25,.32,.24,0)
   box(a+tt*(k*length/bays+.3)+nn*.12+Vector((0,0,8)),tt,nn,.65,.35,10.8,0)
   facade_bays+=1
 # Primary engineering record: octagonal plan,16 ribs,40.8m external incl buttresses,9.8m lantern.
 dc=Vector((-167.3,945.7,0));segments=64;rings=10;amax=math.acos(4.9/20.4)
 def domepoint(k,j):
  aa=k/rings*amax;ang=j/segments*2*math.pi;rr=20.4*math.cos(aa);factor=math.cos(math.pi/8)/math.cos((ang%(math.pi/4))-math.pi/8)
  return dc+Vector((rr*factor*math.cos(ang),rr*factor*math.sin(ang),29.5+9*math.sin(aa)/math.sin(amax)))
 for k in range(rings):
  for j in range(segments):face([domepoint(k,j),domepoint(k,j+1),domepoint(k+1,j+1),domepoint(k+1,j)],1 if 3<=k<=6 and j%8 in [2,3,4,5] else 2)
 for j in range(0,segments,4):
  for k in range(rings):
   a=domepoint(k,j);b=domepoint(k+1,j);nn=Vector((-math.sin(j/segments*2*math.pi),math.cos(j/segments*2*math.pi),0));face([a-nn*.13+Vector((0,0,.055)),a+nn*.13+Vector((0,0,.055)),b+nn*.13+Vector((0,0,.055)),b-nn*.13+Vector((0,0,.055))],2)
 # Octagonal glazed lantern:9.8m outer width interpretation; low cap below retained43.5m max.
 for j in range(8):
  aa=j*math.pi/4;bb=(j+1)*math.pi/4;a=dc+Vector((4.9*math.cos(aa),4.9*math.sin(aa),38.5));b=dc+Vector((4.9*math.cos(bb),4.9*math.sin(bb),38.5));face([a,b,b+Vector((0,0,2.5)),a+Vector((0,0,2.5))],1);box((a+b)/2+Vector((0,0,2.55)),(b-a).normalized(),Vector((0,0,1)),(b-a).length,.25,.35,2)
 face([dc+Vector((4.9*math.cos(j*math.pi/4),4.9*math.sin(j*math.pi/4),41.3)) for j in range(8)],2)
 m=bpy.data.meshes.new('State Library authored portico facade and dome');m.from_pydata(v,[],f);[m.materials.append(ma) for ma in mats];m.update()
 for p,i in zip(m.polygons,mi):p.material_index=i;p.use_smooth=False
 o=bpy.data.objects.new(m.name,m);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(o);o['source_structure']='805833';o['reference']=reference;o['limits']=limits
 s['state_library_revision']='portico-dome-v1';audit={'source_structure':'805833','source_ids':sorted(ids),'removed_generic_faces':removals,'authored_faces':len(f),'facade_bays':facade_bays,'columns':8,'references':[reference,'https://blogs.slv.vic.gov.au/our-stories/ask-a-librarian/dome-to-catacomb/','https://portal.engineersaustralia.org.au/system/files/engineering-heritage-australia/nomination-title/State_Library_Dome.pdf','https://latrobejournal.slv.vic.gov.au/latrobejournal/issue/latrobe-08/t1-g-t1.html'],'limits':limits};(R/'docs/state-library-landmark-audit.json').write_text(json.dumps(audit,indent=2)+'\n');print('STATE_LIBRARY',audit,flush=True)
