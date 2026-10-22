"""Coordinate finishes across inferred Westin source sections; optical colours authored."""
import bpy,json
from pathlib import Path
R=Path(bpy.data.filepath).resolve().parents[3];groups=json.loads((R/'assets/source/environment/city-facade-groups.json').read_text())['groups'];data=json.loads((R/'public/data/buildings.json').read_text())['buildings'];records=[]
def mat(name,c,rough,metal=0):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*c,1);s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*c,1);s.inputs['Roughness'].default_value=rough;s.inputs['Metallic'].default_value=metal;return m
upper=mat('Westin authored pale warm upper wall',(.61,.55,.44),.82);terrace=mat('Westin authored warm mineral horizontal cap',(.39,.34,.26),.87);roof=mat('Westin authored coordinated neutral roof cap',(.21,.235,.25),.5,.25)
for b in data:
 key=str(b['id'])
 if str(groups[key]['structure_id'])!='804903':continue
 o=bpy.data.objects.get('survey_'+key)
 if not o or len(o.data.materials)<2:continue
 old=[m.name if m else None for m in o.data.materials];o['previous_westin_section_finish']=o.get('previous_westin_section_finish',json.dumps(old))
 if key!='26410':o.data.materials[0]=upper
 o.data.materials[1]=terrace if b['base']<49 else roof
 o['westin_section_finish_limits']='Historical west elevation informs warm lower/paler upper relationship. RGB colours, horizontal cap and roof finish authored. Section height boundaries follow retained geometry, not actual material survey; current finish condition unverified.'
 records.append({'section':key,'base':b['base'],'height':b['height'],'previous':old,'current':[m.name for m in o.data.materials]})
(R/'docs/westin-section-finish-audit.json').write_text(json.dumps({'reference':'https://nationalprecast.com.au/wp-content/uploads/2015/09/Precaster-24.pdf','changed':records,'limits':'Location-based building identity inferred. Finish relationships authored from historical reference, not calibrated colour/as-built finish measurement. Existing separate authored gable/hip overlays retained; complex upper geometry remains unresolved.'},indent=2)+'\n')
print('VERIFIED coordinated Westin section finishes',len(records),flush=True)
# Original caps were replaced by a city-wide union mesh; update that render surface too.
o=bpy.data.objects.get('Continuous surveyed roofs - authored finishes');changed=0
if o:
 slots={}
 for m in [terrace,roof]:
  idx=next((i for i,existing in enumerate(o.data.materials) if existing==m),None)
  if idx is None:idx=len(o.data.materials);o.data.materials.append(m)
  slots[m.name]=idx
 def inside(x,y,ring):
  result=False
  for i,(ax,ay) in enumerate(ring):
   bx,by=ring[i-1]
   if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax:result=not result
  return result
 parts=[b for b in data if str(groups[str(b['id'])]['structure_id'])=='804903']
 for p in o.data.polygons:
  c=o.matrix_world@p.center
  for b in parts:
   if abs(c.z-(b['base']+b['height']))>.025:continue
   if inside(c.x,-c.y,b['ring']):
    p.material_index=slots[(terrace if b['base']<49 else roof).name];changed+=1;break
 o['westin_cap_finish_limits']='Westin candidate horizontal triangles selected by source height and centroid inside retained section rings; authored coordinated finish, not installed material survey.'
 print('VERIFIED continuous roof cap triangles recoloured',changed,flush=True)
audit=R/'docs/westin-section-finish-audit.json';d=json.loads(audit.read_text());d['continuous_roof_cap_triangles_changed']=changed;d['selection']='Source relative top height within .025m and triangle centroid inside corresponding source ring.';audit.write_text(json.dumps(d,indent=2)+'\n')
