"""Primary built-facade interpretation; retained Parliament envelopes recoverable."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(globals().get('root') or Path(bpy.data.filepath).resolve().parents[3]);s=bpy.context.scene
if s.get('parliament_revision')!='built-colonnade-v1':
 groups=json.loads((R/'assets/source/environment/city-facade-groups.json').read_text())['groups'];ids={k for k,v in groups.items() if v['structure_id']=='812895'};src={b['id']:b for b in json.loads((R/'public/data/buildings.json').read_text())['buildings'] if b['id'] in ids}
 reference='https://www.parliament.vic.gov.au/about/history-and-heritage/building/construction';limits='Municipal listing point verifies retained structure812895. Official1901 built-facade photo establishes long colonnade, stepped approach, rectilinear entablature and high end blocks. Column count/spacing, steps, inner wall setback, windows, capitals and colour authored unmeasured. No unbuilt dome or photographic textures.'
 def mat(name,col,rough=.75,metal=0):
  m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*col,1);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=m.diffuse_color;p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
 mats=[mat('Parliament authored sandstone',(.47,.39,.28)),mat('Parliament authored recess glazing',(.047,.057,.055),.3),mat('Parliament authored zinc-grey roofs',(.17,.19,.18),.55,.25),mat('Parliament authored dark stone plinth',(.19,.18,.15))]
 polygons=[]
 for ident,b in src.items():polygons.append((ident,[Vector((x,-y,0)) for x,y in b['ring'][:-1]],b['base'],b['base']+b['height']))
 def dist(p,a,b):
  d=b-a;return (p-a-d*max(0,min(1,(p-a).dot(d)/max(d.length_squared,1e-10)))).length
 def inside(v,ring):
  p=Vector((v.x,v.y,0))
  if any(dist(p,a,ring[(j+1)%len(ring)])<.15 for j,a in enumerate(ring)):return True
  hit=False
  for j,a in enumerate(ring):
   b=ring[(j+1)%len(ring)]
   if (a.y>p.y)!=(b.y>p.y) and p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x:hit=not hit
  return hit
 removals={};sourcehashes={}
 def geom(m):return hashlib.sha256(repr(([tuple(v.co) for v in m.vertices],[tuple(p.vertices) for p in m.polygons])).encode()).hexdigest()
 for ident in ids:
  o=bpy.data.objects.get('survey_'+ident)
  if not o:continue
  old=o.data.copy();old.name='Parliament original envelope '+ident;old.use_fake_user=True;o['parliament_original_mesh']=old.name;sourcehashes[o.name]=geom(old);o.data=o.data.copy();o.data.materials[0]=mats[0]
  for i in range(1,len(o.data.materials)):o.data.materials[i]=mats[2]
  o['parliament_reference']=reference;o['parliament_limits']=limits
 for name in ['Authored grouped window bays - varied low rise','Authored short low-rise window bays','Authored low rise sill and lintel bands','Authored roof edge cornices','Continuous surveyed roofs - authored finishes']:
  o=bpy.data.objects.get(name)
  if not o:continue
  old=o.data;bad=set()
  for p in old.polygons:
   co=[o.matrix_world@old.vertices[i].co for i in p.vertices];ce=sum(co,Vector())/len(co)
   if not(535<ce.x<640 and 715<ce.y<860):continue
   for ident,ring,lo,hi in polygons:
    if name=='Continuous surveyed roofs - authored finishes':
     if all(abs(v.z-hi)<.3 and inside(v,ring) for v in co):bad.add(p.index);break
    elif min(v.z for v in co)>=lo-.5 and max(v.z for v in co)<=hi+.5 and any(all(dist(Vector((v.x,v.y,0)),a,ring[(j+1)%len(ring)])<.7 for v in co) for j,a in enumerate(ring)):bad.add(p.index);break
  if bad:
   old.use_fake_user=True;o['parliament_original_overlay_mesh']=old.name;m=bpy.data.meshes.new(name+' without Parliament overlays');m.from_pydata([tuple(v.co) for v in old.vertices],[],[tuple(p.vertices) for p in old.polygons if p.index not in bad]);[m.materials.append(ma) for ma in old.materials]
   for p,q in zip(m.polygons,[p for p in old.polygons if p.index not in bad]):p.material_index=q.material_index
   m.update();o.data=m;removals[name]=len(bad)
 v=[];f=[];mi=[]
 def face(pp,idx):
  st=len(v);v.extend([tuple(p) for p in pp]);f.append(tuple(range(st,st+len(pp))));mi.append(idx)
 def box(c,t,n,w,d,h,idx):
  pp=[c+t*u+n*q+Vector((0,0,z)) for z in [-h/2,h/2] for u,q in [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]]
  for ii in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:face([pp[i] for i in ii],idx)
 from mathutils.geometry import tessellate_polygon
 for ident,b in src.items():
  ring=[Vector((x,-y,b['base']+b['height']+.04)) for x,y in b['ring'][:-1]]
  for tri in tessellate_polygon([ring]):
   pp=[ring[i] for i in tri] if isinstance(tri[0],int) else list(tri)
   if (pp[1]-pp[0]).cross(pp[2]-pp[0]).z<0:pp.reverse()
   face(pp,2)
 # Retained central west front edge at548.4,805.8 to563.3,765.4.
 a=Vector((548.4,805.8,0));b=Vector((563.3,765.4,0));t=(b-a).normalized();n=Vector((t.y,-t.x,0));c=(a+b)/2;length=(b-a).length
 # Freestanding source-guided front colonnade, outside filled survey wall by3.1m.
 for k in range(12):
  cc=a+t*(1.2+(length-2.4)*k/11)+n*3.1
  for j in range(24):
   aa=j*math.pi/12;bb=(j+1)*math.pi/12;ra=.63 if j%2 else .66;rb=.63 if (j+1)%2 else .66
   face([cc+t*(ra*math.cos(aa))+n*(ra*math.sin(aa))+Vector((0,0,7.9)),cc+t*(rb*math.cos(bb))+n*(rb*math.sin(bb))+Vector((0,0,7.9)),cc+t*(rb*.9*math.cos(bb))+n*(rb*.9*math.sin(bb))+Vector((0,0,20.1)),cc+t*(ra*.9*math.cos(aa))+n*(ra*.9*math.sin(aa))+Vector((0,0,20.1))],0)
  for z,w,d,h in [(7.4,1.6,1.6,.5),(7.8,1.4,1.4,.3),(20.3,1.55,1.55,.5)]:box(cc+Vector((0,0,z)),t,n,w,d,h,0)
 box(c+n*1.6+Vector((0,0,21.25)),t,n,length+2,5.1,1.5,0)
 box(c+n*1.6+Vector((0,0,22.1)),t,n,length+2.5,5.5,.3,0)
 # Long stepped approach ties illustrative ground0.5 to retained entrance7m.
 for k in range(26):
  z=.5+(k+1)*.25;depth=14-k*.46;box(c+n*(depth/2+1)+Vector((0,0,z-.125)),t,n,length+4,depth,.25,0)
 # Behind colonnade: tall dark ordered apertures and shallow stone surrounds.
 for k in range(10):
  cc=a+t*((k+.5)*length/10)+n*.12
  box(cc+Vector((0,0,13.1)),t,n,2,.12,8.5,1)
  for u in [-1.2,1.2]:box(cc+t*u+n*.11+Vector((0,0,13.1)),t,n,.3,.3,9.2,0)
  for z in [8.6,17.7]:box(cc+n*.11+Vector((0,0,z)),t,n,2.7,.4,.35,0)
 # End blocks: place relief directly on actual west-facing source boundary edges.
 ring=[Vector((x,-y,0)) for x,y in src['1597']['ring'][:-1]];sign=1 if sum(ring[j-1].x*ring[j].y-ring[j].x*ring[j-1].y for j in range(len(ring)))>0 else -1
 end_bays=0
 for j,aa in enumerate(ring):
  bb=ring[(j+1)%len(ring)];dt=bb-aa;ll=dt.length
  if ll<4:continue
  tt=dt/ll;nn=Vector((tt.y,-tt.x,0))*sign
  mid=(aa+bb)/2
  if nn.x>-.85 or mid.x>575:continue
  if 0<(mid-a).dot(t)<length and dist(mid,a,b)<1:continue
  for z,h in [(7,.5),(21.5,.55),(24.5,.35)]:box(mid+nn*.12+Vector((0,0,z)),tt,nn,ll,.5,h,0)
  count=max(1,round(ll/4.2))
  for k in range(count):
   cc=aa+tt*((k+.5)*ll/count)+nn*.16
   for z,h in [(11,4.8),(18.2,3.5)]:
    box(cc+Vector((0,0,z)),tt,nn,1.6,.10,h,1)
    for u in [-1,1]:box(cc+tt*u+nn*.12+Vector((0,0,z)),tt,nn,.32,.3,h+.6,0)
    for zz in [z-h/2-.2,z+h/2+.2]:box(cc+nn*.12+Vector((0,0,zz)),tt,nn,2.3,.4,.3,0)
   end_bays+=1
 m=bpy.data.meshes.new('Parliament authored built colonnade and steps');m.from_pydata(v,[],f);[m.materials.append(ma) for ma in mats];m.update()
 for p,i in zip(m.polygons,mi):p.material_index=i
 o=bpy.data.objects.new(m.name,m);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(o);o['source_structure']='812895';o['reference']=reference;o['limits']=limits;s['parliament_revision']='built-colonnade-v1'
 audit={'source_structure':'812895','source_ids':sorted(ids),'source_geometry_hashes':sourcehashes,'removed_generic_faces':removals,'authored_faces':len(f),'columns':12,'end_bays':end_bays,'steps':26,'point_source':'https://whatson.melbourne.vic.gov.au/things-to-do/parliament-house','verified_local_point':[591.0380189999004,807.4150920015586],'reference':reference,'limits':limits};(R/'docs/parliament-landmark-audit.json').write_text(json.dumps(audit,indent=2)+'\n');print('PARLIAMENT',audit,flush=True)
