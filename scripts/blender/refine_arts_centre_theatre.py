"""Reference-led authored concrete, ribbed bronze and horizontal glazing."""
import bpy,json,math
from pathlib import Path
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3];name='Arts Centre authored theatre glazing bands'
if not bpy.data.objects.get(name):
 rows=[b for b in json.loads((root/'public/data/buildings.json').read_text())['buildings'] if str(b['id']) in ['25564','25565','25566','25567']];rings=[[(x,-y) for x,y in b['ring']] for b in rows]
 mats=[]
 for label,color,metal in [('Authored Arts theatre bush hammered concrete',(.42,.40,.35),0),('Authored Arts theatre bronze ribbed aluminium',(.22,.16,.10),.55),('Authored Arts theatre horizontal glazing',(.06,.09,.10),.2)]:
  m=bpy.data.materials.new(label);m.use_nodes=True;m.diffuse_color=(*color,1);s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=m.diffuse_color;s.inputs['Roughness'].default_value=.8 if metal==0 else .4;s.inputs['Metallic'].default_value=metal;mats.append(m)
 for b in rows:
  o=bpy.data.objects.get('survey_'+str(b['id']));o.data.materials.clear();o.data.materials.append(mats[1 if b['base']>=19 else 0])
 # Own fine relief; no photographic textures.
 for m,scale,distance in [(mats[0],18,.008),(mats[1],24,.003)]:
  n=m.node_tree.nodes;l=m.node_tree.links;g=n.new('ShaderNodeNewGeometry');t=n.new('ShaderNodeTexNoise' if m==mats[0] else 'ShaderNodeTexWave')
  if m==mats[1]:t.wave_type='BANDS';t.bands_direction='X'
  t.inputs['Scale'].default_value=scale;l.new(g.outputs['Position'],t.inputs['Vector']);b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.18;b.inputs['Distance'].default_value=distance;l.new(t.outputs['Fac'],b.inputs['Height']);l.new(b.outputs['Normal'],n.get('Principled BSDF').inputs['Normal'])
 def near(x,y,r):
  hit=False
  for a,b in zip(r,r[1:]):
   if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
   dx,dy=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/max(dx*dx+dy*dy,1e-9)))
   if math.hypot(x-a[0]-t*dx,y-a[1]-t*dy)<.3:return True
  return hit
 removed=0
 for label in ['Authored grouped window bays - varied low rise','Authored low rise sill and lintel bands']:
  o=bpy.data.objects.get(label)
  if not o:continue
  keep=[]
  for p in o.data.polygons:
   x,y,z=p.center
   if 86<x<147 and -405<y<-301 and z<30.01 and any(near(x,y,r) for r in rings):removed+=1
   else:keep.append(p)
  m=bpy.data.meshes.new(label+' theatre cutout');m.from_pydata([tuple(v.co) for v in o.data.vertices],[],[tuple(p.vertices) for p in keep])
  for mat in o.data.materials:m.materials.append(mat)
  for p,q in zip(m.polygons,keep):p.material_index=q.material_index
  m.update();o.data=m
 v=[];f=[]
 for b,r in zip(rows,rings):
  if str(b['id']) not in ['25565','25567']:continue
  z1,z2=(17.2,18.2) if str(b['id'])=='25565' else (6.4,7.4);area=sum(a[0]*c[1]-c[0]*a[1] for a,c in zip(r,r[1:]))
  for a,c in zip(r,r[1:]):
   dx,dy=c[0]-a[0],c[1]-a[1];length=math.hypot(dx,dy)
   if length<.1:continue
   nx,ny=(dy/length,-dx/length) if area>0 else (-dy/length,dx/length);i=len(v);v.extend([(a[0]+nx*.06,a[1]+ny*.06,z1),(c[0]+nx*.06,c[1]+ny*.06,z1),(c[0]+nx*.06,c[1]+ny*.06,z2),(a[0]+nx*.06,a[1]+ny*.06,z2)]);f.append((i,i+1,i+2,i+3))
 m=bpy.data.meshes.new(name);m.from_pydata(v,[],f);m.materials.append(mats[2]);m.update();o=bpy.data.objects.new(name,m);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(o);o['limits']='Reference-led material hierarchy and illustrative horizontal glazing on retained theatre outlines. Exact glazing/balcony extents, levels and panel orientation/current works unresolved.';o['reference']='https://assets.heritagecouncil.vic.gov.au/assets/HCV-DETERMINATION-AND-ED-RECCOMENDATION-HER1067-R11128-ARTS-CENTRE-AMEND.pdf';o['generic_faces_removed']=removed;print('VERIFIED theatre facade:',len(f),'bands;',removed,'generic faces removed')
