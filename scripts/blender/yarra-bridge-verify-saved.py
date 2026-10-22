"""Audit and render the saved accepted bridge pass. Never save scene changes."""
import bpy,json,os
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
s=bpy.context.scene
expected={
'yarra_bridge_pedestrian_revision':'retained-decks-authored-primary-reference-structure-v1',
'yarra_western_bridge_structure_revision':'source-family-authored-structure-v1',
'yarra_western_bridge_deck_finish_revision':'authored-neutral-deck-source-footprints-v1',
'yarra_princes_captured_landing_revision':'historical-context-authored-closed-apron-v2',
'yarra_authored_unified_decks_revision':'retained-footprint-union-explicit-authored5m-v1'}
checks={k:s.get(k)==v for k,v in expected.items()}
backups=[]
for o in bpy.data.objects:
    for key in o.keys():
        if key.startswith('yarra_') and ('original_mesh' in key or 'original_road_mesh' in key or 'original_roof_mesh' in key or 'unsubdivided_mesh' in key or 'finish_original_mesh' in key or 'original_deck_finish_mesh' in key or 'original_structure_mesh' in key):
            name=o[key];exists=isinstance(name,str) and name in bpy.data.meshes
            backups.append({'object':o.name,'property':key,'mesh':name,'exists':exists})
checks['all_recovery_meshes_exist']=bool(backups) and all(x['exists'] for x in backups)
for sid in ['17604','20327']:
    o=bpy.data.objects['survey_'+sid];old=bpy.data.meshes[o['yarra_bridge_original_mesh']]
    checks[sid+'_retained_geometry']=len(o.data.vertices)==len(old.vertices) and len(o.data.polygons)==len(old.polygons) and all((a.co-b.co).length<1e-6 for a,b in zip(o.data.vertices,old.vertices)) and all(tuple(a.vertices)==tuple(b.vertices) for a,b in zip(o.data.polygons,old.polygons))
for sid in ['39116','39117']:
    checks[sid+'_source_hidden']=bpy.data.objects['survey_'+sid].hide_render and bpy.data.objects['survey_'+sid].hide_viewport
    o=bpy.data.objects['Vicmap bridge carriageway on survey '+sid]
    checks[sid+'_old_road_hidden']=o.hide_render and o.hide_viewport
part=json.loads((ROOT/'assets/source/environment/yarra-bridge-authored-union-deck.json').read_text())['parts'][0]
for name,verts,faces in [('Yarra Kings unified authored5m deck',part['vertices'],part['faces']),('Yarra Kings retained road union on authored5m deck',part['road_vertices'],part['road_faces'])]:
    mesh=bpy.data.objects[name].data
    checks[name+'_matches_authored_union']=len(mesh.vertices)==len(verts) and len(mesh.polygons)==len(faces) and all((v.co-Vector(p)).length<.001 for v,p in zip(mesh.vertices,verts)) and all(tuple(p.vertices)==tuple(f) for p,f in zip(mesh.polygons,faces))
apron=bpy.data.objects['Yarra Princes authored captured-context approach apron']
ys=[v.co.y for v in apron.data.vertices]
checks['full_southern_approach_supported']=abs(min(ys)+380)<.001 and abs(max(ys)+180)<.001 and len(apron.data.polygons)==92
for name in ['Continuous Vicmap road surface','Authored kerbs - retained road edges','Continuous authored pavement bands']:
    o=bpy.data.objects[name]
    checks[name+'_landing_recoverable']='yarra_captured_landing_original_unsubdivided_mesh' in o and 'yarra_captured_landing_original_mesh' in o
checks['bridge_materials_have_no_image_textures']=all(n.type!='TEX_IMAGE' for m in bpy.data.materials if m.name.startswith('Yarra') and m.use_nodes for n in m.node_tree.nodes)
audit={'saved_blend':bpy.data.filepath,'checks':checks,'recovery_meshes':backups,'passed':all(checks.values()),'visual_review':'Pending render inspection','limits':'Kings5m chosen from retained lower authored layer, not surveyed fit. Princes52m apron and southern100m grade authored from sparse historical road context. Structural dimensions approximate.'}
path=ROOT/'docs/yarra-bridge-saved-audit.json';path.write_text(json.dumps(audit,indent=2)+'\n')
print('YARRA_SAVED_AUDIT',audit['passed'],[k for k,v in checks.items() if not v],flush=True)
assert audit['passed'], 'Saved bridge audit failed'
if os.environ.get('YARRA_BRIDGE_VERIFY_RENDER','1')=='1':
    c=bpy.data.objects.new('Yarra saved-scene audit camera',bpy.data.cameras.new('Yarra saved-scene audit camera'));s.collection.objects.link(c);s.camera=c;c.data.type='ORTHO';c.data.clip_end=12000
    s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=1500;s.render.resolution_y=900;s.render.resolution_percentage=100
    for label,loc,target,scale in [('western',(-780,-620,200),(-750,-355,4),650),('princes-landing',(400,-350,170),(160,-280,3),375)]:
        c.location=loc;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale
        s.render.filepath=str(ROOT/'docs/images'/('yarra-bridge-'+label+'-saved.png'));bpy.ops.render.render(write_still=True)
