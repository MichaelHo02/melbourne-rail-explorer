"""Top-down capture rays distinguish roof envelope from centroid medians."""
import bpy,json,statistics
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).resolve().parents[3];d=json.loads((r/'assets/source/environment/federation-ngv-complete-captured-roof.json').read_text());old=json.loads((r/'docs/ngv-transition-capture-audit.json').read_text());m=bpy.data.meshes.new('Temporary captured upward roof');m.from_pydata(d['vertices'],[],d['faces']);m.update();cap=bpy.data.objects.new(m.name,m);bpy.context.scene.collection.objects.link(cap);roof=bpy.data.objects['Continuous surveyed roofs - authored finishes'];rows=[]
for a in old['samples']:
 x,y,z=a['capture_xyz'];hit,p,n,i=cap.ray_cast(Vector((x,y,80)),Vector((0,0,-1)))
 if not hit:continue
 rows.append({'xy':[x,y],'cell_median_z':z,'captured_upper_z':p.z,'authored_z':a['authored_z'],'upper_residual_m':a['authored_z']-p.z,'median_to_upper_m':p.z-z})
result={'source':d['source'],'capture':d['capture'],'rows':rows,'ray_hits':len(rows),'cell_count':len(old['samples']),'median_absolute_upper_residual_m':statistics.median(abs(q['upper_residual_m']) for q in rows),'median_cell_to_upper_difference_m':statistics.median(q['median_to_upper_m'] for q in rows),'limits':'Rays test retained upward triangles only; gaps produce misses. Cell centroid medians can mix stacked or sloping captured surfaces. No geometry repair applied.'};(r/'docs/ngv-transition-upper-capture-audit.json').write_text(json.dumps(result,indent=2)+'\n');print('UPPER_CAPTURE_AUDIT',result['ray_hits'],result['median_absolute_upper_residual_m'],result['median_cell_to_upper_difference_m'],flush=True)
