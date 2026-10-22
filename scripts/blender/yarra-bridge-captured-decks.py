"""Install disclosed authored footprint union; reject unsupported capture fitting."""
import bpy,json,os
from pathlib import Path
import numpy as np
ROOT=globals().get('root') or Path(__file__).resolve().parents[2]
s=bpy.context.scene
authored=os.environ.get('YARRA_BRIDGE_AUTHORED_UNION')=='1'
revision='yarra_authored_unified_decks_revision' if authored else 'yarra_captured_unified_decks_revision'
if not s.get(revision):
    filename='yarra-bridge-authored-union-deck.json' if authored else 'yarra-bridge-unified-captured-decks.json'
    data=json.loads((ROOT/'assets/source/environment'/filename).read_text())
    assert data['parts'],'Capture does not prove any complete bridge deck profile; refuse installation'
    collection=bpy.data.collections['Yarra bridges - source guided authored structure']
    roof=bpy.data.objects['Continuous surveyed roofs - authored finishes'];backup=roof.data.copy();backup.use_fake_user=True;roof['yarra_western_original_roof_mesh']=backup.name
    removal=set()
    def inside(x,y,ring):
        yes=False
        for a,b in zip(ring,ring[1:]):
            ay=-a[1];by=-b[1]
            if (ay>y)!=(by>y) and x<(b[0]-a[0])*(y-ay)/(by-ay)+a[0]:yes=not yes
        return yes
    for part in data['parts']:
        cloud=np.array(part['vertices'])
        def level(x,y):
            return float(np.dot([x,y,1],part['plane_coefficients']))
        for sid,ring,top in zip(part['ids'],part['source_polygons'],part['old_tops']):
            o=bpy.data.objects['survey_'+sid];o['yarra_original_hide_render']=o.hide_render;o['yarra_original_hide_viewport']=o.hide_viewport;o.hide_render=True;o.hide_viewport=True
            for p in roof.data.polygons:
                if abs(p.center.z-top)<.01 and inside(p.center.x,p.center.y,ring):removal.add(p.index)
            road=bpy.data.objects.get('Vicmap bridge carriageway on survey '+sid)
            if road:
                old=road.data.copy();old.use_fake_user=True;road['yarra_original_road_mesh']=old.name;road.data=road.data.copy()
                if authored or (part['name']=='Kings' and sid=='39117'):road.hide_render=True;road.hide_viewport=True
                else:
                    for v in road.data.vertices:v.co.z=level(v.co.x,v.co.y)+.03
                    road.data.update()
            for o in collection.objects:
                if o.type!='MESH' or str(o.get('source_id',''))!=sid:continue
                old=o.data.copy();old.use_fake_user=True;o['yarra_original_structure_mesh']=old.name;o.data=o.data.copy()
                for v in o.data.vertices:
                    if v.co.z>.25:v.co.z+=level(v.co.x,v.co.y)-top
                o.data.update()
        mesh=bpy.data.meshes.new('Yarra '+part['name']+(' unified authored5m deck' if authored else ' unified captured deck'))
        mesh.from_pydata(part['vertices'],[],part['faces']);mesh.materials.append(bpy.data.materials['Yarra bridge authored neutral pedestrian deck']);mesh.update()
        o=bpy.data.objects.new(mesh.name,mesh);collection.objects.link(o);o['source']=data['source'];o['capture']=data['capture'];o['limits']=data['limits'];o['source_ids']=','.join(part['ids'])
        if authored:
            roadmesh=bpy.data.meshes.new('Yarra Kings retained road union on authored5m deck');roadmesh.from_pydata(part['road_vertices'],[],part['road_faces']);roadmesh.materials.append(bpy.data.materials['Authored asphalt']);roadmesh.update();roadobj=bpy.data.objects.new(roadmesh.name,roadmesh);collection.objects.link(roadobj);roadobj['limits']='Union of existing Vicmap alignment buffers clipped to retained deck union. Width remains authored9m per alignment; top5.03m inferred, not municipal lane allocation.'
        # Authored600mm closed structural slab along every triangulated edge.
        # Internal walls coincide harmlessly; outer edges close the visible deck.
        v=[];f=[]
        for p in mesh.polygons:
            pts=[mesh.vertices[i].co for i in p.vertices]
            for a,b in zip(pts,pts[1:]+pts[:1]):
                k=len(v);v.extend([tuple(a),tuple(b),(b.x,b.y,b.z-.6),(a.x,a.y,a.z-.6)]);f.append((k,k+1,k+2,k+3))
        side=bpy.data.meshes.new(mesh.name+' slab edges');side.from_pydata(v,[],f);side.materials.append(mesh.materials[0]);side.update();obj=bpy.data.objects.new(side.name,side);collection.objects.link(obj)
    assert removal
    old=roof.data;new=bpy.data.meshes.new(old.name+' Yarra caps removed');new.from_pydata([tuple(v.co) for v in old.vertices],[],[tuple(p.vertices) for p in old.polygons if p.index not in removal]);new.update()
    for mat in old.materials:new.materials.append(mat)
    for p,q in zip(new.polygons,[p for p in old.polygons if p.index not in removal]):p.material_index=q.material_index;p.use_smooth=q.use_smooth
    roof.data=new;s[revision]='retained-footprint-union-explicit-authored5m-v1' if authored else 'footprint-union-local-historical-height-fit-v1'
    print('YARRA_CAPTURED_DECKS',len(removal),'old cap faces removed',flush=True)
