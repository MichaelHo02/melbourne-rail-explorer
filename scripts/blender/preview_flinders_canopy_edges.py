import bpy,json,math
from pathlib import Path
R=Path(bpy.data.filepath).resolve().parents[3];d=json.loads((R/'assets/source/environment/flinders-captured-canopy-panels.json').read_text());o=bpy.data.objects['Flinders station - municipal 2020 scan, authored colours'];m=o.data;slot=next(i for i,a in enumerate(m.materials) if a and a.name=='Flinders canopy covered captured faces - reversible transparency')
def dist(x,y,r):
 best=1e9
 for i,a in enumerate(r):
  b=r[i-1];dx=b[0]-a[0];dy=b[1]-a[1];t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy))) if dx*dx+dy*dy else 0;best=min(best,math.hypot(x-a[0]-t*dx,y-a[1]-t*dy))
 return best
counts=[0]*5;areas=[0.]*5
for f in m.polygons:
 for i,p in enumerate(d['panels']):
  c=p['plane_coefficients'];q=f.center;z=c[0]*q.x+c[1]*q.y+c[2]+p['plane_lift_above_grid_m'];gap=z-q.z
  if .6<gap<2.3 and dist(q.x,q.y,p['boundaries'][0])<1.2 and abs(f.normal.z)<.8:
   f.material_index=slot;counts[i]+=1;areas[i]+=f.area;break
m.update();report={'candidate_faces':counts,'surface_area_m2':areas,'band_below_roof_m':[.6,2.3],'edge_distance_m':1.2,'status':'Temporary render experiment only. Source blend not saved. May hide genuine canopy supports; not accepted repair.'};(R/'docs/flinders-canopy-edge-experiment.json').write_text(json.dumps(report,indent=2)+'\n')
s=bpy.context.scene;s.camera=bpy.data.objects['34 Flinders captured facade inspection'];s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.cycles.samples=32;s.render.filepath=str(R/'docs/images/observatory-flinders-edge-experiment.png');bpy.ops.render.render(write_still=True)
