"""Vicmap tram alignments draped onto current road surfaces; unsaved trial."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path(bpy.data.filepath).resolve().parents[3];p=r/'assets/source/environment/city-rails-expanded.json';data=json.loads(p.read_text());dg=bpy.context.evaluated_depsgraph_get();surfaces=[]
for o in bpy.data.objects:
 if o.type!='MESH' or o.hide_render:continue
 if o.name=='Continuous Vicmap road surface' or o.name.startswith('Municipal Swanston bridge approach ') or o.name.startswith('Municipal Princes Bridge tram formation '):
  # Municipal footways/kerbs not considered a rail support surface.
  if o.name.startswith('Municipal Swanston') and o.get('type') not in ('RoadCarriageway','RoadTramFormation'):continue
  surfaces.append((o,BVHTree.FromObject(o,dg)))
def height(x,y):
 hits=[]
 for o,bv in surfaces:
  inv=o.matrix_world.inverted();origin=inv@Vector((x,y,100));direction=inv.to_3x3()@Vector((0,0,-1));hit,n,ix,dist=bv.ray_cast(origin,direction,200)
  if hit is not None and n.z>.75:hits.append((o.matrix_world@hit).z)
 return max(hits) if hits else None
v=[];f=[];ufis=set();missing=0;segments=0
for feature in data['features']:
 if feature['properties']['feature_type_code']!='tramway':continue
 geo=feature['geometry'];lines=[geo['coordinates']] if geo['type']=='LineString' else geo['coordinates']
 for line in lines:
  for aa,bb in zip(line,line[1:]):
   a=Vector(((aa[0]-144.9671)*87939,(aa[1]+37.8183)*111320));b=Vector(((bb[0]-144.9671)*87939,(bb[1]+37.8183)*111320));d=b-a;length=d.length
   if length<.1:continue
   d/=length;n=Vector((-d.y,d.x));steps=math.ceil(length/2)
   for i in range(steps):
    start=a+d*(length*i/steps);end=a+d*(length*(i+1)/steps)
    if not all(-500<q.x<650 and -220<q.y<1050 for q in (start,end)):continue
    for side in (-1,1):
     pts=[start+n*(side*.7425-.025),end+n*(side*.7425-.025),end+n*(side*.7425+.025),start+n*(side*.7425+.025)];hs=[height(q.x,q.y) for q in pts]
     if any(h is None for h in hs) or max(hs)-min(hs)>.5:missing+=1;continue
     k=len(v);v.extend((q.x,q.y,h+.008) for q,h in zip(pts,hs));f.append((k,k+1,k+2,k+3));segments+=1;ufis.add(feature['properties']['ufi'])
m=bpy.data.meshes.new('Trial draped CBD tram rails');m.from_pydata(v,[],f);m.materials.append(bpy.data.materials['Authored rail steel']);m.update();o=bpy.data.objects.new(m.name,m);bpy.context.scene.collection.objects.link(o)
limits='One illustrative rail pair per mapped tram alignment; track multiplicity and exact rail centres unverified. 50mm railhead strips with1435mm inner-face separation on straight segments; 8mm road offset authored. Ground support sampled from current authored road assets; gaps/height jumps rejected. Curves/turnouts not engineering designs.'
a={'source':data['source'],'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'gauge_reference':'https://yarratrams.com.au/media/bacbh2n2/infrastructure-tram-track-design.pdf','source_ufis':sorted(ufis),'rail_segments':segments,'rejected_segments':missing,'support_objects':[o.name for o,b in surfaces],'limits':limits};(r/'docs/cbd-draped-tram-rails-trial-audit.json').write_text(json.dumps(a,indent=2)+'\n');print('DRAPED_TRAM_TRIAL',segments,len(ufis),missing,flush=True)
exec(compile((r/'scripts/blender/render_swanston_approach_detail.py').read_text().replace('observatory-swanston-approach-detail.png','observatory-cbd-draped-tram-rails-trial.png'),'render','exec'))
