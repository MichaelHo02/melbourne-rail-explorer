"""Replace covered station mockup with public 2020 captured geometry."""
import bpy,json
from pathlib import Path
R=Path(bpy.data.filepath).resolve().parents[3]
report=json.loads((R/'assets/source/environment/flinders-photomesh-2020.json').read_text())
name='Flinders station - municipal 2020 scan, authored colours'
old=bpy.data.objects.get(name)
if old:bpy.data.objects.remove(old,do_unlink=True)
before=set(bpy.data.objects)
bpy.ops.wm.obj_import(filepath=str(R/'assets/source/environment/flinders-photomesh-2020.obj'),forward_axis='Y',up_axis='Z')
objects=[o for o in bpy.data.objects if o not in before];assert len(objects)==1
o=objects[0];o.name=name
col=bpy.data.collections.get('CITY - reference-authored landmarks')
for c in list(o.users_collection):c.objects.unlink(o)
col.objects.link(o)
def material(n,c,rough,metal=0):
 m=bpy.data.materials.get(n) or bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*c,1);s.inputs['Roughness'].default_value=rough;s.inputs['Metallic'].default_value=metal;return m
mats=[material('Scan Flinders authored warm masonry',(.52,.30,.105),.82),material('Scan Flinders authored green roof metal',(.105,.19,.145),.52,.35),material('Scan Flinders authored station ground',(.14,.16,.15),.9),material('Scan Flinders authored warm upper trim',(.62,.46,.22),.8)]
mats.append(material('Scan Flinders authored weathered zinc canopy',(.24,.28,.27),.65,.3))
zone_rings=[q['ring'] for q in json.loads((R/'assets/source/environment/flinders-scan-material-zones.json').read_text())['zones']]
def inside(x,y,ring):
 result=False
 for i,(ax,ay) in enumerate(ring):
  bx,by=ring[i-1]
  if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax:result=not result
 return result
o.data.materials.clear()
for m in mats:o.data.materials.append(m)
o.data.update()
for p in o.data.polygons:
 z=p.center.z;main=any(inside(p.center.x,p.center.y,ring) for ring in zone_rings)
 p.material_index=0 if main and p.normal.z<.65 else 2
 if main and z>18 and p.normal.z>.35:p.material_index=4
 if main and z>31:p.material_index=1
 elif main and z>26 and p.normal.z<.35:p.material_index=3
 if not main and z>6 and p.normal.z>.35:p.material_index=4
 p.use_smooth=True
import runpy
imported_faces=len(o.data.polygons)
cleanup=runpy.run_path(str(R/'scripts/blender/clean_flinders_scan_fragments.py'))['clean_scan_fragments'](o,R,lambda x,y:any(inside(x,y,ring) for ring in zone_rings))
smooth=o.modifiers.new('Authored scan noise reduction - three gentle passes','SMOOTH');smooth.factor=.35;smooth.iterations=3
anchor=bpy.data.objects.get('Flinders Street - runtime placement');hidden=[]
if anchor:
 for item in [anchor,*anchor.children_recursive]:
  if item==anchor or item.name=='Flinders authored eastern platforms 12-13 - schematic':
   item.hide_render=False;item.hide_set(False);continue
  item.hide_render=True;item.hide_set(True);item['replaced_by_scan']=name;hidden.append(item.name)
o['source_url']=report['source'];o['capture']=report['capture'];o['source_license']=report['license'];o['limits']=report['limits']+' Own material assignment uses surveyed section zones and authored height/normal rules; gentle smoothing is authored scan cleanup, not measured surface finishes. Tiny disconnected fragments outside protected main-building zones removed by authored heuristic; raw source OBJ retained.'
bpy.context.scene['flinders_scan_replacement']=name
out={'scan_object':name,'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'source_faces':report['faces'],'importer_removed_faces':report['faces']-imported_faces,'authored_cleanup_removed_faces':cleanup['removed_faces'],'matrix_world':[list(row) for row in o.matrix_world],'hidden_authored_objects':hidden,'limits':o['limits']}
assert report['faces']*.9998<=imported_faces<=report['faces'];assert all(n.type!='TEX_IMAGE' for m in mats for n in m.node_tree.nodes)
(R/'docs/flinders-photomesh-scene-audit.json').write_text(json.dumps(out,indent=2));print('VERIFIED',len(o.data.vertices),len(o.data.polygons),'scan geometry; hidden',len(hidden),'authored station objects',flush=True)
