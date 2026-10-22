"""Project red orthographic diagnostic pixels onto saved fallback ground plane."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from collections import Counter
R=Path(bpy.data.filepath).resolve().parents[3];a=json.loads((R/'docs/visible-placeholder-ground-audit.json').read_text());s=bpy.context.scene;s.camera=bpy.data.objects[a['camera']];w,h=a['resolution'];s.render.resolution_x=w;s.render.resolution_y=h;s.render.resolution_percentage=100;c=s.camera;assert c.data.type=='ORTHO';frame=c.data.view_frame(scene=s);xmin=min(p.x for p in frame);xmax=max(p.x for p in frame);ymin=min(p.y for p in frame);ymax=max(p.y for p in frame);direction=c.matrix_world.to_quaternion()@Vector((0,0,-1));g=bpy.data.objects['Authored ground with City Square portal'];ground_z=min((g.matrix_world@v.co).z for v in g.data.vertices);im=bpy.data.images.load(str(R/'docs/images/observatory-placeholder-ground-mask.png'),check_existing=False);pixels=list(im.pixels);counts=Counter()
for j in range(0,h,2):
 for i in range(0,w,2):
  k=(j*w+i)*4
  if not (pixels[k]>.8 and pixels[k+1]<.2 and pixels[k+2]<.2):continue
  origin=c.matrix_world@Vector((xmin+(i+.5)/w*(xmax-xmin),ymin+(j+.5)/h*(ymax-ymin),0));p=origin+direction*((ground_z-origin.z)/direction.z);counts[(math.floor(p.x/40),math.floor(p.y/40))]+=1
cells=[{'centre_xy_m':[40*x+20,40*y+20],'centre_lonlat':[144.9671+(40*x+20)/87939,-37.8183+(40*y+20)/111320],'sample_pixels':count} for (x,y),count in counts.most_common(20)];out={'camera':a['camera'],'source_mask':'observatory-placeholder-ground-mask.png','ground_plane_z':ground_z,'cell_size_m':40,'sampling_stride_pixels':2,'largest_cells':cells,'limits':'Approximate orthographic projection of diagnostic red pixels onto flat fallback plane. Pixel count ranks screen-space visibility, not real land area. Cell centres locate review areas, not classified surface types; nearby buildings/footways may lie inside each cell.'};(R/'docs/placeholder-ground-patch-locations.json').write_text(json.dumps(out,indent=2)+'\n');print('VERIFIED largest placeholder cells',json.dumps(cells[:8]),flush=True)
