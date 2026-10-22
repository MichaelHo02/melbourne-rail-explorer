"""Bounded reversible replacement of one illustrative Federation roof profile."""
import bpy,json
from pathlib import Path
root=Path(bpy.data.filepath).resolve().parents[3];scene=bpy.context.scene
if not scene.get('federation_captured_roof_revision'):
 assert scene.get('federation_street_levels_revision')=='captured-streets-v1'
 fit=json.loads((root/'assets/source/environment/federation-captured-roof-fit.json').read_text());old=json.loads((root/'assets/source/environment/federation-authored-gables.json').read_text())['sections'];attr=bpy.data.objects['Federation Square - authored triangular cladding'].data.attributes['source_section'];cladding=bpy.data.objects['Federation Square - authored triangular cladding'];changed={}
 for d in fit['sections']:
  s=next(s for s in old if str(s['id'])==str(d['id']));base=s['base']+4
  def height(x,y):
   a,b,c=d['plane'];return a*x+b*y+c
  target=bpy.data.objects['survey_'+str(d['id'])];meshes=[(target,list(range(len(target.data.vertices)))),(cladding,sorted({i for p,a in zip(cladding.data.polygons,attr.data) if a.value==int(d['id']) for i in p.vertices}))]
  for o,indices in meshes:
   backup=o.data.copy();backup.name=o.name+' before captured roof fit';backup.use_fake_user=True;o['captured_roof_original_mesh']=backup.name
   if o is cladding:
    shared=[p.index for p,a in zip(o.data.polygons,attr.data) if a.value!=int(d['id']) and any(i in indices for i in p.vertices)];assert not shared
   for i in indices:
    v=o.data.vertices[i];world=o.matrix_world@v.co;x,y,z=world;n=s['normal'];factor=max(0,1-abs((x*n[0]+y*n[1]-s['mid'])/s['half_width']));oldtop=base+s['height']*factor
    if oldtop-base>.05:
     ratio=max(0,min(1,(z-base)/(oldtop-base)));world.z=base+ratio*(height(x,y)-base);v.co=o.matrix_world.inverted()@world
   o.data.update();changed[o.name]=changed.get(o.name,0)+len(indices)
  ring=s['ring'];wallverts=[];wallfaces=[]
  for a,b in zip(ring,ring[1:]):
   k=len(wallverts);wallverts.extend([(a[0],a[1],base),(b[0],b[1],base),(b[0],b[1],height(*b)),(a[0],a[1],height(*a))]);wallfaces.append((k,k+1,k+2,k+3))
  wm=bpy.data.meshes.new('Federation fitted roof edge closures');wm.from_pydata(wallverts,[],wallfaces);wm.materials.append(bpy.data.materials['Authored Federation Square zinc']);wm.update();wo=bpy.data.objects.new(wm.name,wm);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(wo);wo['limits']='Authored vertical closure from captured plane to source section base; exact fascia and glazing unresolved.'
  name='Federation captured-height roof '+str(d['id']);m=bpy.data.meshes.new(name);m.from_pydata(d['vertices'],[],d['faces']);m.materials.append(bpy.data.materials['Authored Federation Square zinc']);m.update();assert all(p.area>0 and p.normal.z>0 for p in m.polygons);o=bpy.data.objects.new(name,m);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(o);o['limits']=fit['limits'];o['source']='https://discover.data.vic.gov.au/dataset/city-of-melbourne-3d-textured-mesh-photomesh-2020'
 for d in fit['retained_sections']:
  name='Federation retained authored roof '+str(d['id']);m=bpy.data.meshes.new(name);m.from_pydata([(x,y,z+4) for x,y,z in d['vertices']],[],d['faces']);m.materials.append(bpy.data.materials['Authored Federation Square zinc']);m.update();o=bpy.data.objects.new(name,m);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(o)
 for name in ['Federation Square - authored gable roof profiles','Federation Square - authored gable edge trim','Federation Square - authored zinc seams']:
  o=bpy.data.objects.get(name)
  if o:o.hide_render=True;o.hide_set(True);o['replacement']='captured plane and retained larger profile'
 scene['federation_captured_roof_revision']='captured-one-plane-v1';(root/'docs/federation-captured-roof-audit.json').write_text(json.dumps({'changed_vertices':changed,'limits':fit['limits'],'source_roof_sections':['20248'],'old_profiles_recoverable':True},indent=2));print('CAPTURED_ROOF_FIT',changed,flush=True)
else:print('CAPTURED_ROOF_ALREADY_APPLIED',flush=True)
