"""Reversible Atrium surface clipping. Replacement enclosure remains separate."""
import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).resolve().parents[3];key='federation_atrium_void_revision'
if not bpy.context.scene.get(key):
 d=json.loads((r/'assets/source/environment/federation-atrium-surface-cuts.json').read_text());mask=bpy.data.materials.new('Federation Atrium clipped source mask');mask.use_nodes=True;ns=mask.node_tree.nodes;ns.clear();t=ns.new('ShaderNodeBsdfTransparent');out=ns.new('ShaderNodeOutputMaterial');mask.node_tree.links.new(t.outputs[0],out.inputs['Surface']);report={}
 # Validate every original face before any material mutation.
 for name,records in d['patches'].items():
  o=bpy.data.objects[name]
  for rec in records:
   p=o.data.polygons[rec['index']];actual=[o.matrix_world@o.data.vertices[j].co for j in p.vertices];assert len(actual)==len(rec['original_vertices']);assert all((v-Vector(q)).length<.0001 for v,q in zip(actual,rec['original_vertices']))
 for name,records in d['patches'].items():
  o=bpy.data.objects[name];slot=len(o.data.materials);original={str(rec['index']):o.data.polygons[rec['index']].material_index for rec in records};txt=bpy.data.texts.new(name+' Atrium original assignments.json');txt.write(json.dumps(original));o['atrium_cut_recovery']=txt.name
  vs=[];fs=[];mi=[];owned=[];attr=o.data.attributes.get('source_section')
  for rec in records:
   for tri in rec['outside_triangles']:
    k=len(vs);vs.extend(tri);fs.append((k,k+1,k+2));mi.append(rec['material']);owned.append(attr.data[rec['index']].value if attr else 0)
  if fs:
   mesh=bpy.data.meshes.new(name+' Atrium retained outside fragments');mesh.from_pydata(vs,[],fs)
   for material in o.data.materials:mesh.materials.append(material)
   mesh.update()
   for p,i in zip(mesh.polygons,mi):p.material_index=i
   if attr:
    a=mesh.attributes.new('source_section','INT','FACE')
    for item,i in zip(a.data,owned):item.value=i
   replacement=bpy.data.objects.new(mesh.name,mesh);o.users_collection[0].objects.link(replacement);replacement['limits']=d['limits']
  o.data.materials.append(mask)
  for rec in records:o.data.polygons[rec['index']].material_index=slot
  report[name]={'masked_faces':len(records),'outside_fragment_faces':len(fs)}
 bpy.context.scene[key]='schematic-void-v1';(r/'docs/federation-atrium-void-audit.json').write_text(json.dumps({'objects':report,'limits':d['limits'],'original_geometry_retained':True},indent=2));print('ATRIUM_VOID_APPLIED',report,flush=True)
else:print('ATRIUM_VOID_ALREADY_APPLIED',flush=True)
