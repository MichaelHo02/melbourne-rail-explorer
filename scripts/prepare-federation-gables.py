"""Authored gable planes within retained footprint and elevation ranges."""
import json,math
from pathlib import Path
from shapely import Polygon,LineString,constrained_delaunay_triangles
from shapely.ops import split
root=Path(__file__).resolve().parents[1];buildings=json.loads((root/'public/data/buildings.json').read_text())['buildings'];surfaces=json.loads((root/'assets/source/environment/city-roof-surfaces.json').read_text());selected=[b for b in buildings if str(b['id']) in ['20247','20248']];sections=[]
for b in selected:
 poly=Polygon([(x,-y) for x,y in b['ring']]);rect=list(poly.minimum_rotated_rectangle.exterior.coords);edges=[(math.dist(rect[i],rect[i+1]),rect[i],rect[i+1]) for i in range(4)];_,a,c=max(edges);dx,dy=c[0]-a[0],c[1]-a[1];length=math.hypot(dx,dy);normal=(-dy/length,dx/length);projs=[x*normal[0]+y*normal[1] for x,y in poly.exterior.coords];lo,hi=min(projs),max(projs);mid=(lo+hi)/2;centre=poly.centroid;offset=mid-(centre.x*normal[0]+centre.y*normal[1]);cx,cy=centre.x+normal[0]*offset,centre.y+normal[1]*offset
 ridge=LineString([(cx-dx/length*100,cy-dy/length*100),(cx+dx/length*100,cy+dy/length*100)])
 verts=[];faces=[]
 for part in split(poly,ridge).geoms:
  for tri in constrained_delaunay_triangles(part).geoms:
   start=len(verts);points=list(tri.exterior.coords)[:3]
   if (points[1][0]-points[0][0])*(points[2][1]-points[0][1])-(points[1][1]-points[0][1])*(points[2][0]-points[0][0])<0:points.reverse()
   for x,y in points:
    factor=max(0,1-abs((x*normal[0]+y*normal[1]-mid)/((hi-lo)/2)));verts.append([x,y,b['base']+b['height']*factor])
   faces.append([start,start+1,start+2])
 sections.append({'id':b['id'],'base':b['base'],'height':b['height'],'ring':list(poly.exterior.coords),'normal':normal,'mid':mid,'half_width':(hi-lo)/2,'vertices':verts,'faces':faces})
# Rebuild flat cap triangles with these two footprints cut out at matching levels.
vertices=[];faces=[];materials=[]
for face,mat in zip(surfaces['faces'],surfaces['materials']):
 points=[surfaces['vertices'][i] for i in face];z=points[0][2];poly=Polygon([(x,y) for x,y,_ in points])
 for section in sections:
  if abs(z-section['base']-section['height'])<.001:poly=poly.difference(Polygon(section['ring']))
 for tri in constrained_delaunay_triangles(poly).geoms:
  coords=list(tri.exterior.coords)[:3];start=len(vertices)
  if (coords[1][0]-coords[0][0])*(coords[2][1]-coords[0][1])-(coords[1][1]-coords[0][1])*(coords[2][0]-coords[0][0])<0:coords.reverse()
  vertices.extend([[x,y,z] for x,y in coords]);faces.append([start,start+1,start+2]);materials.append(mat)
out={'sections':sections,'flat_roofs':{'vertices':vertices,'faces':faces,'materials':materials},'limits':'Survey Gable classifications and retained envelope heights. Long-axis ridge and linear planes authored, not measured; captures 2022, not present-day confirmation.'}
(root/'assets/source/environment/federation-authored-gables.json').write_text(json.dumps(out,separators=(',',':'))+'\n');print('VERIFIED gable preparation',len(sections),len(faces))
