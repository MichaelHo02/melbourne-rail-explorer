"""Reference-led, illustrative bluestone finish on central CBD pavement bands."""
import bpy
name='Continuous authored pavement bands';o=bpy.data.objects[name]
if not o.get('cbd_bluestone_finish'):
 mat=bpy.data.materials['Authored Southbank sawn bluestone'].copy();mat.name='Authored central CBD bluestone - coverage illustrative';o.data.materials.append(mat);idx=len(o.data.materials)-1;count=0
 for p in o.data.polygons:
  x,y,z=p.center
  if -1400<x<250 and 60<y<1400:p.material_index=idx;count+=1
 o['cbd_bluestone_finish']=True;o['bluestone_faces']=count;o['bluestone_reference']='https://mvga-prod-files.s3.ap-southeast-4.amazonaws.com/public/2024-08/operating-procedure-bluestone.pdf';o['bluestone_limits']='Authored finish on approximate central-CBD pavement region. Standard 1m by 0.5m paver rhythm; joints, colour and placement illustrative. City guidance explicitly says bluestone coverage is incomplete; this assignment is not an existing-surface inventory.';print('VERIFIED illustrative CBD bluestone:',count,'faces')
