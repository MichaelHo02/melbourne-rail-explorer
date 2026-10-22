import bpy,json
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene
if not s.get('swanston_municipal_approach_revision'):
 d=json.loads((r/'assets/source/environment/swanston-approach-authored-surfaces.json').read_text());col=bpy.data.objects['Municipal Princes Bridge carriageway 1425102'].users_collection[0]
 for p in d['parts']:
  source=p['surface_material'];mat='Authored asphalt' if source.startswith('HMA') else ('Authored Princes Bridge bluestone' if 'Bluestone' in source else 'Authored Princes Bridge tram concrete');name='Municipal Swanston bridge approach '+p['assetid'];m=bpy.data.meshes.new(name);m.from_pydata(p['vertices'],[],p['faces']);m.materials.append(bpy.data.materials[mat]);m.update();o=bpy.data.objects.new(name,m);col.objects.link(o)
  for k in ['assetid','type','surface_material','area_m2']:o[k]=p[k]
  o['source_url']=d['source_url'];o['source_sha256']=d['source_sha256'];o['limits']=d['limits']
 s['swanston_municipal_approach_revision']='mapped-polygons-captured-height-v1';print('MUNICIPAL_APPROACH_APPLIED',len(d['parts']),flush=True)
if not s.get('swanston_approach_overlap_cut_revision'):
 cuts=json.loads((r/'assets/source/environment/swanston-approach-overlap-cuts.json').read_text());audit={}
 for name,replacements in cuts.items():
  if not replacements:continue
  o=bpy.data.objects[name];old=o.data;backup=old.copy();backup.use_fake_user=True;o['swanston_approach_original_mesh']=backup.name;vertices=[tuple(v.co) for v in old.vertices];faces=[];materials=[]
  for p in old.polygons:
   if str(p.index) not in replacements:faces.append(list(p.vertices));materials.append(p.material_index);continue
   for tri in replacements[str(p.index)]:
    k=len(vertices);vertices.extend(tri);faces.append([k,k+1,k+2]);materials.append(p.material_index)
  m=bpy.data.meshes.new(name+' outside mapped Swanston approach');m.from_pydata(vertices,[],faces)
  for mat in old.materials:m.materials.append(mat)
  for p,mi in zip(m.polygons,materials):p.material_index=mi
  m.update();o.data=m;audit[name]={'replaced_faces':len(replacements),'original_faces':len(old.polygons),'result_faces':len(m.polygons),'recovery_mesh':backup.name}
 s['swanston_approach_overlap_cut_revision']='mapped-planform-subtraction-v1';(r/'docs/swanston-approach-surface-audit.json').write_text(json.dumps({'old_surface_cuts':audit,'limits':json.loads((r/'assets/source/environment/swanston-approach-authored-surfaces.json').read_text())['limits']},indent=2)+'\n');print('APPROACH_OLD_SURFACES_CUT',audit,flush=True)
