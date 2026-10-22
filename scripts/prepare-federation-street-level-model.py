import json,math
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];rawsamples=json.loads((R/'assets/source/environment/federation-street-captured-samples.json').read_text());a=np.array(rawsamples);filtered=[];reject=0
for x,y,z in a:
 d=((a[:,:2]-[x,y])**2).sum(axis=1);vals=a[d<144,2];m=float(np.median(vals))
 if z>m+1.2:reject+=1;continue
 filtered.append([float(x),float(y),m])
a=np.array(filtered)
def weight(x,y):
 edge=min(x+80,260-x,y+60,250-y);w=max(0,min(1,edge/50));d=float(np.min(((a[:,:2]-[x,y])**2).sum(axis=1)))**.5;return w*max(0,min(1,(40-d)/28))
raw={str(q['objectid']):q for q in json.loads((R/'assets/source/environment/federation-street-building-source-records.json').read_text())['records']};b=json.loads((R/'public/data/buildings.json').read_text())['buildings'];old=json.loads((R/'assets/source/environment/federation-ground-datum-sections.json').read_text());oldstructures={q['structure_id'] for q in old};groups={}
for p in b:
 if p['base']!=0:continue
 r=raw.get(str(p['id']))
 if not r:continue
 structure=str(r['structure_id'])
 if structure in oldstructures:continue
 ring=[(x,-y) for x,y in p['ring']];x=sum(v[0] for v in ring)/len(ring);y=sum(v[1] for v in ring)/len(ring);w=max([weight(x,y)]+[weight(a,b) for a,b in ring])
 if w>.03:groups[structure]=max(w,groups.get(structure,0))
sections=[]
for p in b:
 r=raw.get(str(p['id']))
 if not r or str(r['structure_id']) not in groups:continue
 w=groups[str(r['structure_id'])];sections.append({'id':str(p['id']),'structure_id':str(r['structure_id']),'offset':(r['structure_min_elevation']-4.1)*w,'weight':w,'ring':[(x,-y) for x,y in p['ring']],'base':p['base'],'height':p['height']})
d={'samples':filtered,'sections':sections,'sample_count':len(rawsamples),'accepted_samples':len(filtered),'rejected_high_points':reject,'limits':'2020 geometry-only capture. Road corridor widths illustrative; 4m samples,12m median neighbourhood,1.2m high-point rejection, authored AHD minus4.1m local reference. Core transition weights from bounds x-80..260,y-60..250 over50m, supported-point distance12..40m taper. Boundary transitions and building structure shifts approximate; source building minima not entrance thresholds.'};# Preserve explicit provenance and presentation limits from the applied model.
prior=json.loads((R/'assets/source/environment/federation-street-level-model.json').read_text())
for key in ['source','capture','license','limits']:d[key]=prior[key]
(R/'assets/source/environment/federation-street-level-model.json').write_text(json.dumps(d));print('STREET_MODEL',len(filtered),'rejected',reject,'structures',len(groups),'sections',len(sections));print('CATHEDRAL',[(p['id'],p['offset']) for p in sections if p['structure_id']=='819362'])
