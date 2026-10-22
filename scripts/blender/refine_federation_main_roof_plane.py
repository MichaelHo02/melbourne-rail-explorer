"""Replace illustrative main gable with complete capture-supported shallow roof."""
import bpy,json,math
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];key='federation_main_roof_plane_revision'
if not bpy.context.scene.get(key):
 d=json.loads((r/'assets/source/environment/federation-main-roof-plane.json').read_text());old=next(s for s in json.loads((r/'assets/source/environment/federation-authored-gables.json').read_text())['sections'] if str(s['id'])=='20247');c=d['plane'];base=d['base']
 def height(x,y):return c[0]*x+c[1]*y+c[2]
 mesh=bpy.data.meshes.new('Federation captured shallow main roof');mesh.from_pydata(d['vertices'],[],d['faces']);mesh.materials.append(bpy.data.materials['Authored Federation Square zinc']);mesh.update();assert all(p.normal.z>0 and p.area>0 for p in mesh.polygons)
 o=bpy.data.objects.new(mesh.name,mesh);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(o);o['limits']=d['limits'];o['source']='https://discover.data.vic.gov.au/dataset/city-of-melbourne-3d-textured-mesh-photomesh-2020'
 # Complete perimeter closure preserves the source footprint while keeping original tapered walls recoverable.
 ring=old['ring'];vs=[];fs=[]
 for a,b in zip(ring,ring[1:]):
  length=math.hypot(b[0]-a[0],b[1]-a[1]);pieces=max(1,math.ceil(length/3))
  for i in range(pieces):
   p=[a[j]+(b[j]-a[j])*i/pieces for j in range(2)];q=[a[j]+(b[j]-a[j])*(i+1)/pieces for j in range(2)];k=len(vs);vs.extend([(p[0],p[1],base),(q[0],q[1],base),(q[0],q[1],height(*q)),(p[0],p[1],height(*p))]);fs.append((k,k+1,k+2,k+3))
 m=bpy.data.meshes.new('Federation shallow roof perimeter closure');m.from_pydata(vs,[],fs);m.materials.append(bpy.data.materials['Authored Federation Square zinc']);m.update();o=bpy.data.objects.new(m.name,m);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(o);o['limits']='Authored zinc-like closure from source section base to fitted roof. Exact facade layout, openings and edge construction unresolved; no photographic textures.'
 source=bpy.data.objects['survey_20247'];source['main_roof_previous_visibility']=json.dumps({'render':source.hide_render,'viewport':source.hide_get()});source.hide_render=True;source.hide_set(True)
 cladding=bpy.data.objects['Federation Square - authored triangular cladding'];attr=cladding.data.attributes['source_section'];selected=[p.index for p in cladding.data.polygons if attr.data[p.index].value==20247];assert selected
 mask=bpy.data.materials.new('Federation obsolete main gable cladding mask');mask.use_nodes=True;ns=mask.node_tree.nodes;ns.clear();t=ns.new('ShaderNodeBsdfTransparent');out=ns.new('ShaderNodeOutputMaterial');mask.node_tree.links.new(t.outputs[0],out.inputs['Surface']);slot=len(cladding.data.materials);cladding.data.materials.append(mask);txt=bpy.data.texts.new('Federation main gable cladding original assignments.json');txt.write(json.dumps({str(i):cladding.data.polygons[i].material_index for i in selected}));cladding['main_roof_cladding_recovery']=txt.name
 for i in selected:cladding.data.polygons[i].material_index=slot
 previous=bpy.data.objects['Federation retained authored roof 20247'];previous.hide_render=True;previous.hide_set(True);previous['replacement']='Federation captured shallow main roof; source profile retained for recovery'
 bpy.context.scene[key]='captured-shallow-main-v1';(r/'docs/federation-main-roof-plane-audit.json').write_text(json.dumps({'replacement_faces':len(mesh.polygons),'closure_faces':len(fs),'old_profile_recoverable':True,'original_geometry_changed':False,'masked_obsolete_cladding_faces':len(selected),'fit_inliers':d['inliers'],'fit_samples_after_exclusion':d['after_upper_footprint_exclusion'],'median_residual':d['median_residual'],'limits':d['limits']},indent=2));print('MAIN_ROOF_PLANE_APPLIED',len(mesh.polygons),len(fs),flush=True)
else:print('MAIN_ROOF_PLANE_ALREADY_APPLIED',flush=True)
