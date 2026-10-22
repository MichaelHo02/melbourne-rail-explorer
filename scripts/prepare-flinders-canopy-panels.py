"""Fit five large canopy panels to exported scan-supported grid surfaces.
Requires NumPy and Shapely2.1. Input is geometry, never photographs.
"""
import argparse,json,hashlib,math
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon,Point,LineString
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
ap=argparse.ArgumentParser();ap.add_argument('--input',default='/tmp/flinders-canopy-surface-grid.json');ap.add_argument('--output',required=True);a=ap.parse_args();source=Path(a.input);raw=source.read_bytes();grid=json.loads(raw);v=np.array(grid['vertices']);shape=unary_union([Polygon([v[i,:2] for i in f]) for f in grid['triangles']]);parts=[]
for index,g in enumerate(sorted(shape.geoms,key=lambda p:-p.area)[:5]):
 pts=np.array([p for p in v if g.covers(Point(p[:2]))]);matrix=np.c_[pts[:,0],pts[:,1],np.ones(len(pts))];coef=np.linalg.lstsq(matrix,pts[:,2],rcond=None)[0];res=pts[:,2]-matrix@coef;rmse=float(np.sqrt(np.mean(res*res)));assert rmse<.1
 # Close narrow scan tears, then remove stair-stepped sample edges.
 # Hausdorff bound below prevents simplification exceeding the existing repair envelope.
 panel=g.buffer(1.2).buffer(-1.2).simplify(1.5,preserve_topology=True);assert panel.geom_type=='Polygon';assert panel.hausdorff_distance(g)<2.5;assert g.envelope.buffer(1e-6).covers(panel)
 lift=float(np.quantile(res,.99))+.04
 def height(x,y):return float(coef[0]*x+coef[1]*y+coef[2]+lift)
 def ring(r):return [[float(x),float(y),height(x,y)] for x,y in list(r.coords)[:-1]]
 tris=[ring(t.exterior) for t in constrained_delaunay_triangles(panel).geoms];boundaries=[ring(panel.exterior),*[ring(q) for q in panel.interiors]]
 seams=[];qmin=min(y-.36*x for x,y in panel.exterior.coords);qmax=max(y-.36*x for x,y in panel.exterior.coords)
 for j in range(math.ceil(qmin/.9),math.floor(qmax/.9)+1):
  q=j*.9;line=LineString([(-400,-144+q),(100,36+q)]).intersection(panel)
  for segment in ([line] if line.geom_type=='LineString' else getattr(line,'geoms',[])):
   if segment.geom_type=='LineString' and segment.length>1:seams.append([[float(x),float(y),height(x,y)+.016] for x,y in segment.coords])
 parts.append({'index':index,'support_vertices':len(pts),'scan_support_area_m2':g.area,'panel_area_m2':panel.area,'filled_projected_area_m2':panel.difference(g).area,'trimmed_projected_area_m2':g.difference(panel).area,'plane_coefficients':coef.tolist(),'support_rmse_m':rmse,'plane_lift_above_grid_m':lift,'max_outline_displacement_m':panel.hausdorff_distance(g),'original_ring':ring(g.exterior),'original_holes':[ring(r) for r in g.interiors],'triangles':tris,'boundaries':boundaries,'seams':seams})
result={'source':'Municipal May2020 scan; captured-grid-derived geometry. Original station mesh unchanged.','input_sha256':hashlib.sha256(raw).hexdigest(),'assumptions':{'gap_closing_radius_m':1.2,'outline_simplification_m':1.5,'seam_spacing_m':.9,'seam_width_m':.018,'fascia_depth_m':.55,'grid_base_lift_m':.055},'limits':'Five low captured canopy strips only. Planar least-squares fits, statistical lift, footprint cleanup and seams authored; not measured as-built roof detail. Larger unsupported roofs remain.','panels':parts}
Path(a.output).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps([{k:q[k] for k in ['index','support_vertices','scan_support_area_m2','panel_area_m2','filled_projected_area_m2','support_rmse_m']} for q in parts],indent=2))
