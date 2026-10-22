"""Approximate entrance apron joining authored floor to historical captured exterior ground."""
import bpy,bmesh,json,statistics,math
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene;key='federation_entrance_apron_revision'
if not s.get(key):
 assert s.get('federation_atrium_floor_contact_revision')
 samples=json.loads((r/'assets/source/environment/federation-entrance-ground-evidence.json').read_text())['samples'];north=json.loads((r/'docs/federation-entrance-ground-audit.json').read_text())['median_z']
 a=Vector((194.1893005923935,132.9081363091356,0));b=Vector((214.23831677004776,138.92288999870829,0));axis=(b-a).normalized();normal=Vector((-axis.y,axis.x,0));vs=[];fs=[]
 for j in range(5):
  t=j/4
  for i in range(13):
   q=a.lerp(b,i/12)+normal*(7*t);close=sorted([p for p in samples if 6<p[2]<7.4],key=lambda p:(p[0]-q.x)**2+(p[1]-q.y)**2)[:9];captured=statistics.median(p[2] for p in close);entry=north+(12.2-north)*max(0,min(1,(139-a.lerp(b,i/12).y)/90));z=entry*(1-t)+captured*t+.012;vs.append((q.x,q.y,z))
 for j in range(4):
  for i in range(12):
   k=j*13+i;fs.extend([(k,k+1,k+14),(k,k+14,k+13)])
 me=bpy.data.meshes.new('Atrium captured entrance apron');me.from_pydata(vs,[],fs);me.update();m=bpy.data.materials.get('Authored Atrium polished concrete');me.materials.append(m);o=bpy.data.objects.new(me.name,me);bpy.data.collections['Federation Atrium - source guided authored enclosure'].objects.link(o)
 ground=bpy.data.objects['Authored ground with City Square portal'];old=ground.data;old.use_fake_user=True;ground['entrance_ground_original_mesh']=old.name;meground=old.copy();ground.data=meground;bm=bmesh.new();bm.from_mesh(meground)
 for _ in range(8):
  edges=[e for e in bm.edges if e.calc_length()>3 and max(v.co.x for v in e.verts)>180 and min(v.co.x for v in e.verts)<230 and max(v.co.y for v in e.verts)>123 and min(v.co.y for v in e.verts)<160]
  if not edges:break
  bmesh.ops.subdivide_edges(bm,edges=edges,cuts=1,use_grid_fill=True)
 bm.to_mesh(meground);bm.free();groundchanged=0
 for v in meground.vertices:
  q=v.co;u=(q-a).dot(axis);t=(q-a).dot(normal);distance=math.hypot(max(0,-u,u-(b-a).length),max(0,-t,t-7));weight=max(0,1-distance/8)
  if not weight:continue
  close=sorted([p for p in samples if 6<p[2]<7.4],key=lambda p:(p[0]-q.x)**2+(p[1]-q.y)**2)[:9];z=statistics.median(p[2] for p in close)
  if 0<=u<=(b-a).length and 0<=t<=7:
   fi=min(11.999999,u/(b-a).length*12);fj=min(3.999999,t/7*4);ii,jj=int(fi),int(fj);du,dv=fi-ii,fj-jj;k=jj*13+ii;z00,z10,z01,z11=[vs[n][2] for n in [k,k+1,k+13,k+14]];z=(z00*(1-du)+z10*(du-dv)+z11*dv if dv<=du else z00*(1-dv)+z11*du+z01*(dv-du))-.025
  q.z+=(z-q.z)*weight;groundchanged+=1
 meground.update()
 limits='Authored7m exterior apron and subdivision. Outer heights median of nearest9 retained May2020 ground cells filtered6..7.4m; threshold follows approximate interior floor. Concrete finish and boundaries assumed; neutral ground fitted with authored8m falloff; exact paving joints, stairs, street datum and present-day condition unverified.';o['limits']=limits;o['source']='https://discover.data.vic.gov.au/dataset/city-of-melbourne-3d-textured-mesh-photomesh-2020';s[key]='captured-exterior-approximate-bounds-v1';(r/'docs/federation-entrance-apron-audit.json').write_text(json.dumps({'vertices':len(vs),'faces':len(fs),'width_m':7,'ground_changed_vertices':groundchanged,'ground_backup':old.name,'z_range':[min(v[2] for v in vs),max(v[2] for v in vs)],'limits':limits},indent=2)+'\n');print('ENTRANCE_APRON_APPLIED',flush=True)
else:print('ENTRANCE_APRON_ALREADY_APPLIED',flush=True)
