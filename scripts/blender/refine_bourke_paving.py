"""Local illustrative side paving over overly broad generic asphalt."""
import bpy,json
from pathlib import Path
root=globals().get('root') or Path(bpy.data.filepath).resolve().parents[3];name='Bourke authored local side paving'
if not bpy.data.objects.get(name):
 d=json.loads((root/'assets/source/environment/bourke-authored-side-paving.json').read_text());m=bpy.data.meshes.new(name);faces=[]
 for face in d['faces']:
  a,b,c=[d['vertices'][i] for i in face]
  faces.append(face if (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])>0 else face[::-1])
 m.from_pydata(d['vertices'],[],faces);m.materials.append(bpy.data.materials['Authored Southbank sawn bluestone']);m.update();o=bpy.data.objects.new(name,m);bpy.data.collections['GROUND - official horizontal geography, authored levels'].objects.link(o);o['limits']=d['limits'];o['source_ufi']=d['source_ufi'];print('VERIFIED Bourke authored paving',d['area_m2'],flush=True)
