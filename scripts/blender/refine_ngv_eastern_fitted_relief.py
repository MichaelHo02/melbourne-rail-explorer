"""Five capture-supported fitted roof features; feature roles remain unverified."""
import bpy,json
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene;key='federation_ngv_eastern_fitted_relief_revision'
if not s.get(key):
 assert s.get('federation_ngv_eastern_north_revision')=='captured-eastern-north-authored-transition-v1'
 d=json.loads((r/'assets/source/environment/ngv-eastern-fitted-roof-relief.json').read_text());m=bpy.data.meshes.new('NGV eastern captured-fit roof relief');m.from_pydata(d['vertices'],[],d['faces']);m.materials.append(bpy.data.materials['Authored Federation Square zinc']);m.update();assert all(p.area>1e-10 for p in m.polygons)
 o=bpy.data.objects.new(m.name,m);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(o);o['source']=d['source'];o['limits']=d['limits'];s[key]='five-local-captured-fits-v1'
 (r/'docs/ngv-eastern-fitted-relief-audit.json').write_text(json.dumps({'object':o.name,'features':d['features'],'faces':len(m.polygons),'vertices':len(m.vertices),'original_captured_data_retained':True,'existing_meshes_modified':False,'limits':d['limits']},indent=2)+'\n');print('NGV_EASTERN_FITTED_RELIEF_APPLIED',len(d['features']),len(m.polygons),flush=True)
else:print('NGV_EASTERN_FITTED_RELIEF_ALREADY_APPLIED',flush=True)
