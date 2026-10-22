"""Source-fitted Town Hall portico and wing bays; preserve tower/roof passes."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(globals().get('root') or Path(bpy.data.filepath).resolve().parents[3]);s=bpy.context.scene
if s.get('town_hall_review_revision')!='source-fitted-portico-v1':
 d=json.loads((R/'assets/source/environment/town-hall-source-reference.json').read_text());r=next(r for r in d['records'] if r['objectid']=='27725');ring=[Vector(((x-144.9671)*87939,(y+37.8183)*111320,0)) for x,y in r['geo_shape']['geometry']['coordinates'][0][:-1]]
 a=Vector((-55.8,364.26,0));b=Vector((-50.26,349.02,0));t=(b-a).normalized();n=Vector((t.y,-t.x,0));front=(a+b)/2;rear=front-n*7.9;length=(b-a).length
 def portico(p):return abs((Vector((p.x,p.y,0))-front).dot(t))<8.8 and -.3<(Vector((p.x,p.y,0))-rear).dot(n)<8.9
 reference='https://citycollection.melbourne.vic.gov.au/image-of-the-facade-of-melbourne-town-hall-taken-from-swanston-street-2/';limits='1958 municipal facade photo visually inspected: four major front columns, balcony, triangular pediment, three lower arches and arched wing upper windows. Portico set within retained projecting27725 footprint; height intervals, capital simplification, openings, stone colours and bay rhythm approximate; source tower/roof retained except local mansard-portico overlap clip, no photographic textures.'
 def geometry(m):return hashlib.sha256(repr(([tuple(v.co) for v in m.vertices],[tuple(p.vertices) for p in m.polygons])).encode()).hexdigest()
 guards={o.name:geometry(o.data) for o in bpy.data.objects if o.type=='MESH' and ((o.name.startswith('Town Hall') and 'Swanston facade' not in o.name and 'mansard interpretation' not in o.name) or (o.name.startswith('survey_277') and o.name!='survey_27725'))}
 removals={}
 def filtermesh(o,bad,key):
  if not bad:return
  old=o.data;old.use_fake_user=True;o[key]=old.name;o[key+'_removed_faces']=json.dumps(sorted(bad));m=bpy.data.meshes.new(o.name+' after Town Hall portico review');m.from_pydata([tuple(v.co) for v in old.vertices],[],[tuple(p.vertices) for p in old.polygons if p.index not in bad]);[m.materials.append(ma) for ma in old.materials]
  for p,q in zip(m.polygons,[p for p in old.polygons if p.index not in bad]):p.material_index=q.material_index
  m.update();o.data=m;removals[o.name]=len(bad)
 source=bpy.data.objects['survey_27725'];bad=set()
 for p in source.data.polygons:
  co=[source.matrix_world@source.data.vertices[i].co for i in p.vertices]
  if all(portico(v) for v in co) and max((Vector((v.x,v.y,0))-rear).dot(n) for v in co)>1:bad.add(p.index)
 filtermesh(source,bad,'town_hall_review_original_mesh')
 # Remove only portico projections from old cornices/pilasters and generic owned wing windows.
 def distance(p,a,b):
  dd=b-a;return (p-a-dd*max(0,min(1,(p-a).dot(dd)/max(dd.length_squared,1e-12)))).length
 for name in ['Town Hall authored Swanston facade relief','Authored grouped window bays - varied low rise','Authored short low-rise window bays','Authored low rise sill and lintel bands','Authored roof edge cornices','Continuous surveyed roofs - authored finishes']:
  o=bpy.data.objects.get(name)
  if not o:continue
  bad=set()
  for p in o.data.polygons:
   co=[o.matrix_world@o.data.vertices[i].co for i in p.vertices];c=sum(co,Vector())/len(co)
   if not(-65<c.x<20 and 330<c.y<405):continue
   if name in ['Town Hall authored Swanston facade relief','Authored roof edge cornices','Continuous surveyed roofs - authored finishes']:
    if all(portico(v) for v in co) and max(v.z for v in co)<=19.2:bad.add(p.index)
   elif all(.0<=v.z<=19.2 for v in co) and any(all(distance(Vector((v.x,v.y,0)),aa,ring[(j+1)%len(ring)])<.7 for v in co) for j,aa in enumerate(ring)):bad.add(p.index)
  filtermesh(o,bad,'town_hall_review_original_overlay')
 # Clip only old authored mansard region directly over projecting portico; outside3D polygon parts retained.
 roof=bpy.data.objects.get('Town Hall authored slate mansard interpretation')
 if roof:
  from mathutils.geometry import tessellate_polygon
  old=roof.data;vs=[tuple(q.co) for q in old.vertices];fs=[];mis=[];cut=0
  planes=[(t,front+t*8.8),(-t,front-t*8.8),(-n,rear+n*.1),(n,front+n*.4)]
  def clip(poly,axis,origin,keepinside):
   result=[]
   for j,aa in enumerate(poly):
    bb=poly[(j+1)%len(poly)];da=(aa-origin).dot(axis);db=(bb-origin).dot(axis);ia=da<=1e-7 if keepinside else da>=-1e-7;ib=db<=1e-7 if keepinside else db>=-1e-7
    if ia:result.append(aa)
    if ia!=ib:result.append(aa+(bb-aa)*(da/(da-db)))
   return result
  for pp in old.polygons:
   coords=[Vector(old.vertices[ii].co) for ii in pp.vertices];outside=[];intersects=False
   for tri in tessellate_polygon([coords]):
    polygon=[coords[ii] for ii in tri] if isinstance(tri[0],int) else list(tri);fragments=[]
    for axis,origin in planes:
     out=clip(polygon,axis,origin,False)
     if len(out)>=3:fragments.append(out)
     polygon=clip(polygon,axis,origin,True)
     if len(polygon)<3:break
    if len(polygon)>=3 and sum((polygon[j]-polygon[0]).cross(polygon[j+1]-polygon[0]).length for j in range(1,len(polygon)-1))>1e-7:intersects=True
    outside.extend(fragments)
   if not intersects:fs.append(tuple(pp.vertices));mis.append(pp.material_index)
   else:
    cut+=1
    for fragment in outside:
     if len(fragment)<3:continue
     if sum((fragment[j]-fragment[0]).cross(fragment[j+1]-fragment[0]).length for j in range(1,len(fragment)-1))<1e-7:continue
     st=len(vs);vs.extend([tuple(q) for q in fragment]);fs.append(tuple(range(st,st+len(fragment))));mis.append(pp.material_index)
  old.use_fake_user=True;roof['town_hall_review_portico_roof_original']=old.name;m=bpy.data.meshes.new('Town Hall mansard outside fitted portico');m.from_pydata(vs,[],fs);[m.materials.append(ma) for ma in old.materials]
  for pp,ii in zip(m.polygons,mis):pp.material_index=ii
  m.update();roof.data=m;removals['mansard_portico_intersecting_faces']=cut
 stone=bpy.data.materials['Town Hall authored freestone'];slate=bpy.data.materials['Town Hall authored slate'];blue=bpy.data.materials['Town Hall authored bluestone'];glass=bpy.data.materials.get('Town Hall review authored recess') or bpy.data.materials.new('Town Hall review authored recess');glass.use_nodes=True;glass.diffuse_color=(.035,.048,.048,1);p=glass.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=glass.diffuse_color;p.inputs['Roughness'].default_value=.4
 mats=[stone,glass,slate,blue];v=[];f=[];mi=[]
 def face(pp,i):st=len(v);v.extend([tuple(q) for q in pp]);f.append(tuple(range(st,st+len(pp))));mi.append(i)
 def box(c,tt,nn,w,d,h,i):
  pp=[c+tt*u+nn*q+Vector((0,0,z)) for z in [-h/2,h/2] for u,q in [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]]
  for inds in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:face([pp[j] for j in inds],i)
 def arch(center,tt,nn,width,bottom,spring,head,idx):
  cc=center+nn*.04;pp=[cc-tt*width/2+Vector((0,0,bottom)),cc+tt*width/2+Vector((0,0,bottom)),cc+tt*width/2+Vector((0,0,spring))]
  for j in range(1,17):aa=j*math.pi/16;pp.append(cc+tt*(width/2*math.cos(aa))+Vector((0,0,spring+(head-spring)*math.sin(aa))))
  face(pp,idx)
 # Three lower portal arches within portico. Authored recessed background at retained rear edge.
 box(rear+n*.10+Vector((0,0,8)),t,n,length,.2,16,0)
 for u in [-5.2,0,5.2]:
  arch(front+t*u-n*.06,t,n,3.25,.1,3.2,5.3,1)
  arch(rear+t*u+n*.24,t,n,3.25,6.4,13.5,15.4,1)
 # Four solid base piers and shallow lower masonry bands, leaving three dark apertures.
 for u in [-7.55,-2.6,2.6,7.55]:
  cc=front+t*u-n*.55;box(cc+Vector((0,0,2.8)),t,n,1.6,1.3,5.5,0)
  for z in [.55,1.15,1.75,2.35,2.95,3.55,4.15,4.75]:box(cc+n*.04+Vector((0,0,z)),t,n,1.68,1.38,.11,0)
 box(front-n*3.5+Vector((0,0,5.85)),t,n,length,7.4,.35,0)
 for u in [-7.2,-2.4,2.4,7.2]:
  cc=front+t*u-n*.35
  for j in range(24):
   aa=j*math.pi/12;bb=(j+1)*math.pi/12;face([cc+t*(.47*math.cos(aa))+n*(.47*math.sin(aa))+Vector((0,0,6.3)),cc+t*(.47*math.cos(bb))+n*(.47*math.sin(bb))+Vector((0,0,6.3)),cc+t*(.42*math.cos(bb))+n*(.42*math.sin(bb))+Vector((0,0,18.0)),cc+t*(.42*math.cos(aa))+n*(.42*math.sin(aa))+Vector((0,0,18.0))],0)
  for z,w,h in [(6.2,1.25,.3),(18.15,1.25,.45)]:box(cc+Vector((0,0,z)),t,n,w,1.25,h,0)
 # Balcony guard as visible rail rhythm between columns, rather than solid wall.
 for z in [6.3,7.1]:box(front-n*.4+Vector((0,0,z)),t,n,length,.28,.2,0)
 for k in range(39):box(front+t*(-length/2+k*length/38)-n*.4+Vector((0,0,6.7)),t,n,.11,.2,.8,0)
 for z,w,h in [(18.7,length+1,.55),(19.15,length+1.5,.25)]:box(front-n*3.5+Vector((0,0,z)),t,n,w,7.8,h,0)
 peak=24.0
 # Authored vertical closure seals cut mansard edge behind new portico roof.
 box(rear+n*.04+Vector((0,0,22)),t,n,length+1.4,.20,5.6,2)
 for base in [front+n*.03]:face([base-t*(length/2+.6)+Vector((0,0,19.3)),base+t*(length/2+.6)+Vector((0,0,19.3)),base+Vector((0,0,peak))],0)
 for sign in [-1,1]:face([front+t*sign*(length/2+.6)+Vector((0,0,19.3)),rear+t*sign*(length/2+.6)+Vector((0,0,24.8)),rear+Vector((0,0,24.8)),front+Vector((0,0,peak))],2)
 for sign in [-1,1]:face([front+t*sign*(length/2+.6)+Vector((0,0,19.1)),rear+t*sign*(length/2+.6)+Vector((0,0,19.1)),rear+t*sign*(length/2+.6)+Vector((0,0,24.8)),front+t*sign*(length/2+.6)+Vector((0,0,19.3))],2)
 # Source-fitted wing rhythm, retain existing stone pilasters and tower/roof shapes.
 bays=0
 for j,aa in enumerate(ring):
  bb=ring[(j+1)%len(ring)];dt=bb-aa;ll=dt.length
  if ll<5:continue
  tt=dt/ll;nn=Vector((tt.y,-tt.x,0));mid=(aa+bb)/2
  if nn.x>-.85 or mid.x>-35 or portico(mid):continue
  count=max(1,round(ll/4.8))
  for k in range(count):
   cc=aa+tt*((k+.5)*ll/count)+nn*.16
   arch(cc,tt,nn,2.15,6.5,11.4,12.6,1)
   box(cc+nn*.02+Vector((0,0,3.9)),tt,nn,1.9,.12,2.5,1)
   for zz in [6.3,12.8]:box(cc+nn*.10+Vector((0,0,zz)),tt,nn,2.6,.35,.24,0)
   bays+=1
 m=bpy.data.meshes.new('Town Hall review authored portico and facade bays');m.from_pydata(v,[],f);[m.materials.append(ma) for ma in mats];m.update()
 for p,i in zip(m.polygons,mi):p.material_index=i
 o=bpy.data.objects.new(m.name,m);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(o);o['reference']=reference;o['limits']=limits;o['source_id']='27725';s['town_hall_review_revision']='source-fitted-portico-v1';audit={'source_id':'27725','removed_faces':removals,'preserved_geometry_guards':guards,'authored_faces':len(f),'front_columns':4,'wing_bays':bays,'reference':reference,'limits':limits};(R/'docs/town-hall-review-audit.json').write_text(json.dumps(audit,indent=2)+'\n');print('TOWN_HALL_REVIEW',audit,flush=True)
