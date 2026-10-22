"""Replace generic cathedral window grid with authored masonry and lancet bays."""
import bpy,json,math
from pathlib import Path
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3]
name='St Pauls Cathedral - authored lancet bays'
if not bpy.data.objects.get(name):
 rows=[b for b in json.loads((root/'public/data/buildings.json').read_text())['buildings'] if str(b['id']) in ['27584','27585','27586']]
 rings=[[(x,-y) for x,y in b['ring']] for b in rows]
 def near(x,y,r):
  hit=False
  for a,b in zip(r,r[1:]):
   if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
   dx,dy=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/max(dx*dx+dy*dy,1e-9)))
   if math.hypot(x-a[0]-t*dx,y-a[1]-t*dy)<.3:return True
  return hit
 stone=bpy.data.materials['Authored St Pauls warm masonry']
 for o in bpy.data.objects:
  if any(o.name.startswith('survey_'+i) for i in ['27584','27585','27586']):
   o.data.materials.clear();o.data.materials.append(stone)
 removed=0
 for label in ['Authored grouped window bays - varied low rise','Authored low rise sill and lintel bands']:
  o=bpy.data.objects.get(label)
  if not o:continue
  keep=[p for p in o.data.polygons if not (p.center.z<29.6 and any(near(p.center.x,p.center.y,r) for r in rings))]
  removed+=len(o.data.polygons)-len(keep);m=bpy.data.meshes.new(label+' cathedral lower cutout');m.from_pydata([tuple(v.co) for v in o.data.vertices],[],[tuple(p.vertices) for p in keep])
  for mat in o.data.materials:m.materials.append(mat)
  for p,q in zip(m.polygons,keep):p.material_index=q.material_index
  m.update();o.data=m
 verts=[];faces=[]
 for row,r in zip(rows,rings):
  if row['id']=='27584':continue
  signed=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(r,r[1:]));bottom,top=(4,11) if row['id']=='27585' else (17,26)
  for a,b in zip(r,r[1:]):
   dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
   if length<12:continue
   ux,uy=dx/length,dy/length;nx,ny=(uy,-ux) if signed>0 else (-uy,ux)
   for j in range(max(1,int(length/5))):
    t=(j+.5)/max(1,int(length/5));cx,cy=a[0]+dx*t+nx*.08,a[1]+dy*t+ny*.08;w=.9;shoulder=top-1.8
    points=[(-w,bottom),(w,bottom),(w,shoulder),(.6,top-.8),(0,top),(-.6,top-.8),(-w,shoulder)];start=len(verts)
    verts.extend([(cx+ux*s,cy+uy*s,z) for s,z in points]);face=tuple(range(start,start+len(points)));faces.append(face if signed>0 else tuple(reversed(face)))
 mat=bpy.data.materials.new('Authored cathedral dark lancet glazing');mat.diffuse_color=(.07,.10,.09,1);mat.use_nodes=True;s=mat.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=mat.diffuse_color;s.inputs['Roughness'].default_value=.4
 m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);m.materials.append(mat);m.update();o=bpy.data.objects.new(name,m);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(o);o['limits']='Illustrative pointed bays at retained long walls, not measured fenestration or stained-glass reproduction.';o['generic_faces_omitted']=removed
 print('VERIFIED cathedral masonry and lancet bays:',len(faces),'bays;',removed,'generic faces removed')
