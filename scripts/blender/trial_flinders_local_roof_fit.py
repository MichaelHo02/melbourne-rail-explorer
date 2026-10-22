"""Trial one low-residual captured roof patch; canonical file unchanged."""
import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).resolve().parents[3];cs=json.loads((r/'assets/source/environment/flinders-upper-zinc-captured-cells.json').read_text())['cells'];a=[c for c in cs if -120<c['xy'][0]<-80 and 0<c['xy'][1]<20 and c['p90_z']-c['p10_z']<.4 and c['median_z']<30]
# Normal equations solved with Blender's matrix library; captured cells only.
from mathutils import Matrix
A=Matrix([[sum(([c['xy'][0],c['xy'][1],1][i])*([c['xy'][0],c['xy'][1],1][j]) for c in a) for j in range(3)] for i in range(3)])
b=Vector([sum([c['xy'][0],c['xy'][1],1][i]*c['median_z'] for c in a) for i in range(3)]);fit=A.inverted()@b
v=[];f=[];accepted=[]
for c in a:
 x,y=c['xy'];pred=fit.x*x+fit.y*y+fit.z
 if abs(pred-c['median_z'])>.15:continue
 k=len(v)
 for dx,dy in [(-.5,-.5),(.5,-.5),(.5,.5),(-.5,.5)]:v.append((x+dx,y+dy,fit.x*(x+dx)+fit.y*(y+dy)+fit.z+.04))
 f.append((k,k+1,k+2,k+3));accepted.append(c)
m=bpy.data.meshes.new('Trial captured Flinders local roof panel');m.from_pydata(v,[],f);m.materials.append(bpy.data.materials['Scan Flinders authored weathered zinc canopy']);m.update();o=bpy.data.objects.new(m.name,m);bpy.context.scene.collection.objects.link(o);o.matrix_world=bpy.data.objects['Flinders station - municipal 2020 scan, authored colours'].matrix_world.copy();o['limits']='Trial authored plane and one-metre cell boundaries; excludes high residual cells. Scan retained; overlap visibility unproven.'
(r/'docs/flinders-local-roof-fit-trial-audit.json').write_text(json.dumps({'cells_selected':len(a),'cells_accepted':len(accepted),'plane':list(fit),'offset_m':.04,'limits':o['limits']},indent=2)+'\n')
exec(compile((r/'scripts/blender/render_swanston_approach_detail.py').read_text().replace('observatory-swanston-approach-detail.png','observatory-flinders-local-roof-trial.png'),'render','exec'))
