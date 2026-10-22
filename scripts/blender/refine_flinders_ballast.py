"""Add authored railway ballast margins on retained Flinders alignments."""
import bpy,json
from pathlib import Path
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3];name='Flinders authored wider ballast margins'
if not bpy.data.objects.get(name):
 d=json.loads((root/'assets/source/environment/flinders-authored-ballast.json').read_text());m=bpy.data.meshes.new(name);m.from_pydata(d['vertices'],[],d['faces']);m.materials.append(bpy.data.materials['Authored ballast']);m.update();o=bpy.data.objects.new(name,m);bpy.data.collections['GROUND - official horizontal geography, authored levels'].objects.link(o)
 for k in ['source_url','source_sha256','limits','area_m2']:o[k]=d[k]
 o['source_ufis']=','.join(map(str,d['source_ufis']));print('VERIFIED Flinders wider ballast:',len(m.polygons),'faces;',d['area_m2'],'m2')

# Existing saved meshes also need upward surface normals.
import bmesh
o=bpy.data.objects.get(name)
if o:
 bm=bmesh.new();bm.from_mesh(o.data);bm.normal_update();down=[f for f in bm.faces if f.normal.z<0]
 if down:bmesh.ops.reverse_faces(bm,faces=down);bm.to_mesh(o.data);o.data.update()
 bm.free();assert all(p.normal.z>0 for p in o.data.polygons)
 print('VERIFIED Flinders ballast upward normals:',len(o.data.polygons),'corrected',len(down),flush=True)
