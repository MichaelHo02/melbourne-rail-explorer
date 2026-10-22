"""Fine authored metal relief on the survey-bounded gable preview."""
import bpy,json
from pathlib import Path
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3];d=json.loads((root/'assets/source/environment/federation-authored-roof-trim.json').read_text());m=bpy.data.materials.get('Authored Federation roof trim') or bpy.data.materials.new('Authored Federation roof trim');m.use_nodes=True;s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(.25,.29,.30,1);s.inputs['Metallic'].default_value=.55;s.inputs['Roughness'].default_value=.48
for key,label,radius in [('seams','Federation Square - authored zinc seams',.018),('edges','Federation Square - authored gable edge trim',.035)]:
 if bpy.data.objects.get(label):continue
 curve=bpy.data.curves.new(label,'CURVE');curve.dimensions='3D';curve.resolution_u=1;curve.bevel_depth=radius;curve.bevel_resolution=1;curve.materials.append(m)
 for points in d[key]:
  spline=curve.splines.new('POLY');spline.points.add(len(points)-1)
  for p,xyz in zip(spline.points,points):p.co=(*xyz,1)
 obj=bpy.data.objects.new(label,curve);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(obj);obj['limits']=d['limits'];obj['guide_count']=len(d[key]);obj['reference']='https://fedsquare.com/history-design';print('VERIFIED authored roof trim',key,len(d[key]))
