"""Additional ordinary railway features; authored flat gauge and levels."""
import bpy,json,math
from pathlib import Path
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3]
name='Expanded ordinary railway ballast additions'
if not bpy.data.objects.get(name):
 d=json.loads((root/'assets/source/environment/city-trackbeds-expanded-additions.json').read_text());collection=bpy.data.collections['GROUND - official horizontal geography, authored levels'];m=bpy.data.meshes.new(name);m.from_pydata(d['vertices'],[],d['faces']);m.materials.append(bpy.data.materials['Authored ballast']);m.update();o=bpy.data.objects.new(name,m);collection.objects.link(o);o['limits']=d['limits'];o['source_url']=d['source_url'];o['source_ufis']=','.join(map(str,d['source_ufis']))
 curve=bpy.data.curves.new('Expanded ordinary railway steel - authored flat gauge','CURVE');curve.dimensions='3D';curve.bevel_depth=.045;curve.bevel_resolution=1
 for line in d['alignments']:
  for a,b in zip(line,line[1:]):
   dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
   if length<.01:continue
   # Only complete segments in the preview bounds; no extension beyond data extent.
   if not all(-2000<=p[0]<=1250 and -800<=p[1]<=1750 for p in [a,b]):continue
   nx,ny=-dy/length,dx/length
   for side in [-.8,.8]:
    s=curve.splines.new('POLY');s.points.add(1)
    for point,xy in zip(s.points,[a,b]):point.co=(xy[0]+nx*side,xy[1]+ny*side,.50,1)
 curve.materials.append(bpy.data.materials['Authored rail steel']);o=bpy.data.objects.new(curve.name,curve);collection.objects.link(o);o['limits']='Authored 1.6 m gauge, steel radius and flat .50 m datum on additional explicit ordinary railway lines. Per-feature line may represent multiple tracks; exact gauge, sleepers, elevation and clearances unresolved.'
 print('VERIFIED expanded rails',len(d['source_ufis']),'source features',len(m.polygons),'ballast triangles',len(curve.splines),'steel segments',flush=True)
