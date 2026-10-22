"""Conservative authored cleanup; raw captured OBJ remains untouched."""
import bpy,bmesh,json
from collections import defaultdict

def clean_scan_fragments(obj,root,in_main_zone):
 mesh=obj.data;parents=list(range(len(mesh.vertices)))
 def find(i):
  while parents[i]!=i:parents[i]=parents[parents[i]];i=parents[i]
  return i
 for edge in mesh.edges:
  a,b=edge.vertices;aa=find(a);bb=find(b)
  if aa!=bb:parents[bb]=aa
 groups=defaultdict(list)
 for face in mesh.polygons:groups[find(face.vertices[0])].append(face)
 removed=[];indices=[];retained=0
 for faces in groups.values():
  area=sum(f.area for f in faces)
  if area>=1:retained+=1;continue
  vertex_ids={i for f in faces for i in f.vertices};points=[mesh.vertices[i].co for i in vertex_ids];low=[min(v[j] for v in points) for j in range(3)];high=[max(v[j] for v in points) for j in range(3)];center=[(a+b)/2 for a,b in zip(low,high)]
  # Protect surveyed main-building zones: small dome/roof details may be real.
  if max(b-a for a,b in zip(low,high))>=2 or in_main_zone(center[0],center[1]):retained+=1;continue
  removed.append({'faces':len(faces),'surface_area_m2':area,'bounds':[low,high]});indices.extend(f.index for f in faces)
 before=len(mesh.polygons);bm=bmesh.new();bm.from_mesh(mesh);bm.faces.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.faces[i] for i in indices],context='FACES');bm.to_mesh(mesh);bm.free();mesh.update()
 result={'rule':'Disconnected component area<1m², maximum bounding span<2m, outside surveyed main-building material zones. Authored heuristic; fragment identity not individually surveyed.','source_components':len(groups),'removed_components':removed,'preserved_components':retained,'faces_before':before,'faces_after':len(mesh.polygons),'removed_faces':len(indices),'raw_source_obj_modified':False,'limits':'Conservative small-fragment cleanup; larger scan holes, noisy connected edges and patch seams remain. Main building components protected; uncovered small platform details could also satisfy this heuristic.'}
 assert before-len(mesh.polygons)==len(indices)
 assert len(mesh.polygons)>before*.998
 (root/'docs/flinders-scan-fragment-cleanup.json').write_text(json.dumps(result,indent=2)+'\n');obj['fragment_cleanup']=result['rule'];print('VERIFIED removed',len(removed),'small components',len(indices),'faces; kept',retained,'components',flush=True)
 return result
