"""Differentiate schematic official Square from broader captured precinct deck."""
import bpy,json
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];key='federation_square_paving_regions_revision'
if not bpy.context.scene.get(key):
 d=json.loads((r/'assets/source/environment/federation-square-paving-regions.json').read_text());source=json.loads((r/'assets/source/environment/federation-fitted-deck.json').read_text());o=bpy.data.objects['Federation fitted captured-height deck'];assert len(o.data.vertices)==len(source['vertices']);assert all(sum((v.co[j]-p[j])**2 for j in range(3))<1e-6 for v,p in zip(o.data.vertices,source['vertices']))
 backup=o.data;backup.use_fake_user=True;o['paving_regions_original_mesh']=backup.name;neutral=bpy.data.materials['Authored Main Square sandstone pavers'].copy();neutral.name='Authored Federation surrounding neutral stone - assumed'
 for n in neutral.node_tree.nodes:
  if n.type=='TEX_BRICK':n.inputs['Color1'].default_value=(.115,.12,.118,1);n.inputs['Color2'].default_value=(.17,.178,.17,1);n.inputs['Mortar'].default_value=(.075,.08,.078,1)
 neutral['limits']='Authored neutral surrounding precinct finish; not verified exact paving material or distribution.';assert not any(n.type=='TEX_IMAGE' for n in neutral.node_tree.nodes)
 mesh=bpy.data.meshes.new('Federation deck with official schematic Square regions');faces=[f if sum(d['vertices'][f[k]][0]*d['vertices'][f[(k+1)%3]][1]-d['vertices'][f[(k+1)%3]][0]*d['vertices'][f[k]][1] for k in range(3))>0 else list(reversed(f)) for f in d['faces']];mesh.from_pydata(d['vertices'],[],faces);mesh.materials.append(bpy.data.materials['Authored Main Square sandstone pavers']);mesh.materials.append(neutral);mesh.update()
 for p,i in zip(mesh.polygons,d['materials']):p.material_index=i
 assert all(p.area>0 and p.normal.z>0 for p in mesh.polygons);o.data=mesh;o['paving_regions_limits']=d['limits'];o['paving_regions_reference']='https://fedsquare.com/map';bpy.context.scene[key]='official-map-square-v1';(r/'docs/federation-square-paving-regions-audit.json').write_text(json.dumps({'faces':len(mesh.polygons),'projected_region_areas':d['region_projected_areas'],'original_projected_area':d['original_projected_area'],'original_mesh_recoverable':backup.name,'limits':d['limits']},indent=2));print('PAVING_REGIONS_APPLIED',len(mesh.polygons),flush=True)
else:print('PAVING_REGIONS_ALREADY_APPLIED',flush=True)
