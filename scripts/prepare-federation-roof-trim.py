"""Authored zinc seam layout on the two authored gable planes."""
import json,math
from pathlib import Path
from shapely import Polygon,LineString
root=Path(__file__).resolve().parents[1];d=json.loads((root/'assets/source/environment/federation-authored-gables.json').read_text());seams=[];edges=[]
for section in d['sections']:
 poly=Polygon(section['ring']);n=section['normal'];t=(-n[1],n[0]);mid=section['mid'];half=section['half_width'];c=poly.centroid
 def height(x,y):return section['base']+section['height']*max(0,1-abs((x*n[0]+y*n[1]-mid)/half))+.025
 for index in range(-math.floor(half/.9),math.floor(half/.9)+1):
  proj=mid+index*.9;delta=proj-(c.x*n[0]+c.y*n[1]);cx,cy=c.x+n[0]*delta,c.y+n[1]*delta;cut=LineString([(cx-t[0]*100,cy-t[1]*100),(cx+t[0]*100,cy+t[1]*100)]).intersection(poly)
  for line in ([cut] if cut.geom_type=='LineString' else getattr(cut,'geoms',[])):
   if line.geom_type!='LineString' or line.length<.3:continue
   seams.append([[x,y,height(x,y)] for x,y in line.coords])
 for a,b in zip(section['ring'],section['ring'][1:]):
  length=math.dist(a,b);count=max(1,math.ceil(length/.4));points=[]
  for i in range(count+1):
   x=a[0]+(b[0]-a[0])*i/count;y=a[1]+(b[1]-a[1])*i/count;points.append([x,y,height(x,y)])
  edges.append(points)
(root/'assets/source/environment/federation-authored-roof-trim.json').write_text(json.dumps({'seams':seams,'edges':edges,'spacing_m':.9,'limits':'Authored .9 m metal seam spacing and edge trim fitted to authored gables. Zinc family supported by official design description; actual roof detailing, panel schedule and present-day finish unmeasured.'},indent=2)+'\n');print('VERIFIED roof trim preparation',len(seams),len(edges))
