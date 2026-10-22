"""Small captured roof features; authored contact skirts, no image textures."""
import bpy,json
from pathlib import Path
r=Path(bpy.data.filepath).resolve().parents[3];s=bpy.context.scene;key='federation_ngv_eastern_relief_revision'
if not s.get(key):
 assert s.get('federation_ngv_eastern_north_revision')=='captured-eastern-north-authored-transition-v1'
 d=json.loads((r/'assets/source/environment/ngv-eastern-captured-roof-relief.json').read_text());old=json.loads((r/'docs/federation-ngv-roof-regions-audit.json').read_text())['diagnostic_bands'][2]['plane'];new=json.loads((r/'assets/source/environment/ngv-eastern-north-roof-plane.json').read_text())['plane']
 vs=list(d['vertices']);fs=list(d['faces']);edges={}
 for face in fs:
  for a,b in zip(face,face[1:]+face[:1]):edges.setdefault(tuple(sorted((a,b))),[]).append((a,b))
 def contact(x,y):
  h0=old[0]*x+old[1]*y+old[2];h1=new[0]*x+new[1]*y+new[2];w=max(0,min(1,(x-235)/5));w=w*w*(3-2*w);return h0+(h1-h0)*w+.003
 skirts=0
 for occurrences in edges.values():
  if len(occurrences)!=1:continue
  a,b=occurrences[0];p,q=vs[a],vs[b];k=len(vs);vs.extend([(q[0],q[1],contact(q[0],q[1])),(p[0],p[1],contact(p[0],p[1]))]);fs.append((b,a,k+1,k));skirts+=1
 m=bpy.data.meshes.new('NGV retained eastern roof relief');m.from_pydata(vs,[],fs);m.materials.append(bpy.data.materials['Authored Federation Square zinc']);m.update();assert all(p.area>1e-10 for p in m.polygons)
 o=bpy.data.objects.new(m.name,m);bpy.data.collections['CITY - reference-authored landmarks'].objects.link(o);o['source']=d['source'];o['limits']=d['limits']+' Boundary skirts down to corrected roof are authored contact approximations, including internal holes. Feature functions and exact current appearance unverified.'
 s[key]='captured-five-features-authored-contact-v1';(r/'docs/ngv-eastern-captured-relief-audit.json').write_text(json.dumps({'captured_triangles':len(d['faces']),'features':len(d['components']),'authored_contact_quads':skirts,'object':o.name,'original_capture_retained':True,'limits':o['limits']},indent=2)+'\n');print('NGV_EASTERN_CAPTURED_RELIEF_APPLIED',len(d['faces']),skirts,flush=True)
else:print('NGV_EASTERN_CAPTURED_RELIEF_ALREADY_APPLIED',flush=True)
