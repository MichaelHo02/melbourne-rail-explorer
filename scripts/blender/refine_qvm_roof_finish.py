"""Authored corrugated metal grain and ridge/eave guides on market roofs."""
import bpy,json,math
from pathlib import Path
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3];d=json.loads((root/'assets/source/environment/qvm-authored-roofs.json').read_text());ox,oy=d['origin'];ux,uy=d['axis'];nx,ny=d['normal'];mat=bpy.data.materials['Authored market galvanised roof']
if not mat.get('authored_corrugation'):
 n=mat.node_tree.nodes;l=mat.node_tree.links;s=n.get('Principled BSDF');g=n.new('ShaderNodeNewGeometry');dot=n.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=(ux,uy,0);l.new(g.outputs['Position'],dot.inputs[0]);freq=n.new('ShaderNodeMath');freq.operation='MULTIPLY';freq.inputs[1].default_value=2*math.pi/.076;l.new(dot.outputs['Value'],freq.inputs[0]);wave=n.new('ShaderNodeMath');wave.operation='SINE';l.new(freq.outputs[0],wave.inputs[0]);bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.22;bump.inputs['Distance'].default_value=.008;l.new(wave.outputs[0],bump.inputs['Height']);l.new(bump.outputs['Normal'],s.inputs['Normal']);noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1.4;noise.inputs['Detail'].default_value=2;l.new(g.outputs['Position'],noise.inputs['Vector']);r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=(.29,.32,.31,1);r.color_ramp.elements[1].color=(.43,.46,.44,1);l.new(noise.outputs['Fac'],r.inputs[0]);l.new(r.outputs['Color'],s.inputs['Base Color']);mat['authored_corrugation']='76 mm pitch / 8 mm bump illustrative, not measured; procedural world-position grain.'
name='Queen Victoria Market authored ridge and eave guides'
if not bpy.data.objects.get(name):
 row=json.loads((root/'assets/source/environment/qvm-source-audit.json').read_text())['survey_section'];ring=[(x,-y) for x,y in row['ring']]
 def world(x,y,z):return (ox+x*ux+y*nx,oy+x*uy+y*ny,z)
 def inside(x,y):
  hit=False
  for a,b in zip(ring,ring[1:]):
   if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
  return hit
 curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.bevel_depth=.07;curve.bevel_resolution=1;count=0
 for i in range(5):
  for y,z in [(i*20.65+.15,6.93),(i*20.65+8.2,10.04),(i*20.65+16.25,6.93)]:
   run=[]
   def finish():
    global count
    if len(run)>1:
     sp=curve.splines.new('POLY');sp.points.add(len(run)-1)
     for p,v in zip(sp.points,run):p.co=(*v,1)
     count+=1
   for j in range(329):
    x=j*.5;px,py,_=world(x,y,z)
    if inside(px,py):run.append(world(x,y,z))
    else:finish();run=[]
   finish()
 curve.materials.append(mat);o=bpy.data.objects.new(name,curve);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(o);o['limits']='Authored ridge and gutter guides; dimensions unmeasured. Current solar installations unresolved.';o['guide_runs']=count;print('VERIFIED market ridge/eave guide runs',count,flush=True)
