"""Explicit surface-tag pedestrian infill; authored material response."""
import bpy,json
from pathlib import Path
R=Path(bpy.data.filepath).resolve().parents[3];d=json.loads((R/'assets/source/environment/city-pedestrian-area-surfaces.json').read_text());m=bpy.data.materials.get('Authored compacted pedestrian aggregate') or bpy.data.materials.new('Authored compacted pedestrian aggregate');m.use_nodes=True;s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(.27,.22,.14,1);s.inputs['Roughness'].default_value=.94
count=0
for part in d['parts']:
 name='OSM tagged pedestrian surface '+part['id']
 if bpy.data.objects.get(name):continue
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(part['vertices'],[],part['faces']);material=m if part['surface']=='compacted' else bpy.data.materials['Authored asphalt'] if part['surface']=='asphalt' else bpy.data.materials['Authored stone pavement'];mesh.materials.append(material);mesh.update();assert all(p.normal.z>.99 for p in mesh.polygons);o=bpy.data.objects.new(name,mesh);bpy.data.collections['GROUND - official horizontal geography, authored levels'].objects.link(o);o['source_url']='https://www.openstreetmap.org/way/'+part['id'];o['source_surface_tag']=part['surface'];o['source_license']=d['license'];o['attribution']=d['attribution'];o['limits']=d['limits'];o['area_m2']=part['area_m2'];count+=1
print('VERIFIED tagged pedestrian surfaces',count,'new polygons',flush=True)
