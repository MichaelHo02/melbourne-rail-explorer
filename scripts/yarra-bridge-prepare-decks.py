"""Union Kings survey sections, fit smooth historical deck elevations."""
import json,numpy as np
from pathlib import Path
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'assets/source/environment/yarra-bridge-captured-levels.json').read_text())
buildings=json.loads((ROOT/'public/data/buildings.json').read_text())['buildings'];out=[];rejected=[]
for label,ids in [('Queens',['24181']),('Kings',['39116','39117']),('Spencer',['22347'])]:
    source=[next(b for b in buildings if b['id']==sid) for sid in ids]
    poly=unary_union([Polygon([(x,-y) for x,y in b['ring']]) for b in source])
    sample=np.array([p for sid in ids for p in data['bridges'][sid]['samples']])
    if len(sample)<=50 or len(sample)<=.25*poly.area:
        rejected.append({'name':label,'reason':'capture coverage insufficient','cells':len(sample),'plan_area':poly.area})
        continue
    # Narrow capture strips cannot constrain crossfall; fit along bridge Y only.
    design=np.column_stack((sample[:,1],np.ones(len(sample))))
    coeff=np.linalg.lstsq(design,sample[:,2],rcond=None)[0]
    for _ in range(5):
        residual=np.abs(design@coeff-sample[:,2]);keep=residual<=np.quantile(residual,.65)
        coeff=np.linalg.lstsq(design[keep],sample[keep,2],rcond=None)[0]
    coeff=np.array([0.,coeff[0],coeff[1]])
    predicted=[float(np.dot([x,y,1],coeff)) for b in source for x,y in [(x,-y) for x,y in b['ring']]]
    if min(predicted)<2.5 or abs(coeff[1])>.03:
        rejected.append({'name':label,'reason':'captured strips do not constrain a plausible complete deck profile','coefficients':coeff.tolist(),'predicted_bounds':[min(predicted),max(predicted)]})
        continue
    def height(x,y):return float(np.dot([x,y,1],coeff))
    vertices=[];faces=[]
    def add(xy):
        lengths=[np.linalg.norm(np.array(xy[(i+1)%3])-xy[i]) for i in range(3)];i=int(np.argmax(lengths))
        if lengths[i]>5:
            j=(i+1)%3;k=(i+2)%3;mid=tuple((np.array(xy[i])+xy[j])/2);add([xy[i],mid,xy[k]]);add([mid,xy[j],xy[k]]);return
        if (xy[1][0]-xy[0][0])*(xy[2][1]-xy[0][1])-(xy[1][1]-xy[0][1])*(xy[2][0]-xy[0][0])<0:xy.reverse()
        k=len(vertices);vertices.extend((x,y,height(x,y)) for x,y in xy);faces.append([k,k+1,k+2])
    for tri in constrained_delaunay_triangles(poly).geoms:add(list(tri.exterior.coords)[:3])
    out.append({'name':label,'ids':ids,'source_polygons':[b['ring'] for b in source],'old_tops':[b['base']+b['height'] for b in source],'vertices':vertices,'faces':faces,'plane_coefficients':coeff.tolist(),'plane_median_residual_m':float(np.median(np.abs(design@coeff[1:]-sample[:,2]))),'source_cells':len(sample),'height_quantiles':np.quantile([p[2] for p in vertices],[.1,.5,.9]).tolist()})
(ROOT/'assets/source/environment/yarra-bridge-unified-captured-decks.json').write_text(json.dumps({'parts':out,'rejected':rejected,'source':data['source'],'capture':data['capture'],'limits':'Unchanged union of retained municipal bridge footprints. Local24-neighbour lower-quartile historical height fit suppresses traffic/railing artefacts;5m triangulation authored. Not present-day measured engineering profile. Kings survey section overlap represented once; rejected bridges retain current approximate deck.'})+'\n')
print('CAPTURED_DECKS_PREPARED',[(p['name'],p['height_quantiles']) for p in out],rejected,flush=True)
