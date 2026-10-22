"""Export spatial roof evidence from evaluated retained scan; scene unchanged."""
import bpy,json,math,statistics,hashlib
from pathlib import Path
from collections import defaultdict
r=Path(bpy.data.filepath).resolve().parents[3];o=bpy.data.objects['Flinders station - municipal 2020 scan, authored colours'];eo=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=eo.to_mesh();m.update();cells=defaultdict(list);counts=defaultdict(int)
for p in m.polygons:
 name=m.materials[p.material_index].name
 if 'weathered zinc canopy' not in name:continue
 c=p.center;counts['all_zinc_faces']+=1
 if c.z<6 or p.normal.z<.7 or not (10<c.x<70 and -60<c.y<65):continue
 cells[(math.floor(c.x),math.floor(c.y))].append((c.z,p.area));counts['selected_faces']+=1
rows=[]
for (x,y),samples in sorted(cells.items()):
 zs=sorted(z for z,a in samples);rows.append({'xy':[x+.5,y+.5],'median_z':statistics.median(zs),'p10_z':zs[int((len(zs)-1)*.1)],'p90_z':zs[int((len(zs)-1)*.9)],'face_count':len(zs),'area_m2':sum(a for z,a in samples)})
source=r/'assets/source/environment/flinders-photomesh-2020.obj'
out={'source_object':o.name,'source_obj_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'capture':'Municipal May 2020 geometry; no photographic textures','selection':'Evaluated authored zinc faces, local z>=6m; x10..70/y-60..65, normal z>=0.7; 1m XY cell median','limits':'Material/normal selection can include upper ornament and exclude steep roof slopes. Cells are evidence, not replacement roof or verified roof ownership. Sparse cells and height spreads require review.','counts':dict(counts),'cells':rows}
(r/'assets/source/environment/flinders-eastern-zinc-captured-cells.json').write_text(json.dumps(out,separators=(',',':'))+'\n');eo.to_mesh_clear()
audit={'cell_count':len(rows),'counts':dict(counts),'height_range':[min(c['median_z'] for c in rows),max(c['median_z'] for c in rows)],'cells_with_p90_p10_over_1m':sum(c['p90_z']-c['p10_z']>1 for c in rows),'limits':out['limits']};(r/'docs/flinders-eastern-zinc-cell-audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit),flush=True)
