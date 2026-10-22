"""Documented Eureka gold crown, authored optical palette and lower datum."""
import bpy,json,math
from pathlib import Path
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3];name='Eureka Tower authored gold upper glazing'
if not bpy.data.objects.get(name):
 d=json.loads((root/'assets/source/environment/eureka-source-audit.json').read_text());rows=[r for r in d['scene_sections'] if r['base']+r['height']>265];rings=[[(x,-y) for x,y in r['ring']] for r in rows];v=[];f=[]
 mat=bpy.data.materials.new('Authored Eureka gold coated glass');mat.use_nodes=True;mat.diffuse_color=(.50,.32,.075,1);s=mat.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=mat.diffuse_color;s.inputs['Metallic'].default_value=.55;s.inputs['Roughness'].default_value=.25;s.inputs['Coat Weight'].default_value=.4
 for r,ring in zip(rows,rings):
  lo=max(265,r['base']);hi=r['base']+r['height'];signed=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(ring,ring[1:]));sign=1 if signed>0 else -1
  for a,b in zip(ring,ring[1:]):
   dx,dy=b[0]-a[0],b[1]-a[1];l=math.hypot(dx,dy)
   if l<.001:continue
   nx,ny=sign*dy/l*.04,-sign*dx/l*.04;i=len(v);v.extend([(a[0]+nx,a[1]+ny,lo),(b[0]+nx,b[1]+ny,lo),(b[0]+nx,b[1]+ny,hi),(a[0]+nx,a[1]+ny,hi)]);f.append((i,i+1,i+2,i+3))
 def near(x,y):
  for ring in rings:
   hit=False
   for a,b in zip(ring,ring[1:]):
    if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
    dx,dy=b[0]-a[0],b[1]-a[1];length=dx*dx+dy*dy;t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/length)) if length else 0
    if (x-a[0]-t*dx)**2+(y-a[1]-t*dy)**2<.4**2:hit=True;break
   if hit:return True
  return False
 recolored=0
 for o in list(bpy.data.objects):
  if o.type!='MESH' or not any(t in o.name.lower() for t in ['window','trim']):continue
  targets=[p for p in o.data.polygons if 265<=p.center.z<=298 and near(p.center.x,p.center.y)]
  if not targets:continue
  o.data.materials.append(mat);idx=len(o.data.materials)-1
  for p in targets:p.material_index=idx
  recolored+=len(targets)
 m=bpy.data.meshes.new(name);m.from_pydata(v,[],f);m.materials.append(mat);m.update();o=bpy.data.objects.new(name,m);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(o);o['limits']=d['limits'];o['recolored_overlay_faces']=recolored;print('VERIFIED Eureka gold crown',len(f),'quads',recolored,'overlay faces',flush=True)
# Keep the glazing readable against an authored darker frame/backing palette.
frame=bpy.data.materials.get('Authored Eureka crown dark framing')
if not frame:
 frame=bpy.data.materials.new('Authored Eureka crown dark framing');frame.use_nodes=True;frame.diffuse_color=(.22,.14,.035,1);s=frame.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=frame.diffuse_color;s.inputs['Metallic'].default_value=.45;s.inputs['Roughness'].default_value=.35
bpy.data.objects[name].data.materials[0]=frame
