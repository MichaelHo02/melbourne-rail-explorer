"""Replace scaled-ring Town Hall study with triangulated inset roof bands."""
import bpy,json
from pathlib import Path
R=Path(bpy.data.filepath).resolve().parents[3];d=json.loads((R/'assets/source/environment/town-hall-authored-roof.json').read_text());o=bpy.data.objects['Town Hall authored slate mansard interpretation']
mesh=bpy.data.meshes.new('Town Hall true-offset slate roof');mesh.from_pydata(d['vertices'],[],d['faces']);mesh.materials.append(bpy.data.materials['Town Hall authored slate']);mesh.update();assert all(p.normal.z>0 for p in mesh.polygons);o.data=mesh;o['limits']=d['limits'];o['roof_junction_revision']=2
print('VERIFIED corrected Town Hall roof',len(mesh.polygons),'upward triangles',flush=True)
