"""Isolated, recoverable central pedestrian bridge treatment; never saves a file."""
import bpy, json, math, os
from pathlib import Path
from mathutils import Vector

ROOT = globals().get('root') or Path(__file__).resolve().parents[2]
ROOT = Path(ROOT)
scene = bpy.context.scene
key = 'yarra_bridge_pedestrian_revision'
if not scene.get(key):
    collection = bpy.data.collections.new('Yarra bridges - source guided authored structure')
    scene.collection.children.link(collection)
    def material(name, color, metal=0):
        m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
        m.use_nodes = True
        m.diffuse_color = (*color, 1)
        p = m.node_tree.nodes.get('Principled BSDF')
        p.inputs['Base Color'].default_value = m.diffuse_color
        p.inputs['Metallic'].default_value = metal
        p.inputs['Roughness'].default_value = .48
        return m
    white = material('Yarra bridge authored pale coated steel', (.62,.64,.61), .18)
    grey = material('Yarra bridge authored grey green steel', (.12,.17,.155), .6)
    deck = material('Yarra bridge authored neutral pedestrian deck', (.24,.255,.25))
    def beams(name, segments, width, mat):
        v=[]; f=[]
        for a,b in segments:
            a=Vector(a); b=Vector(b); t=(b-a).normalized(); u=t.cross(Vector((0,0,1)))
            if u.length < .01: u=Vector((1,0,0))
            u.normalize(); n=t.cross(u).normalized(); i=len(v)
            for c in (a,b):
                v.extend(tuple(c+u*x*width/2+n*y*width/2) for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)])
            f.extend(tuple(i+j for j in q) for q in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
        mesh=bpy.data.meshes.new(name); mesh.from_pydata(v,[],f); mesh.materials.append(mat); mesh.update()
        o=bpy.data.objects.new(name,mesh); collection.objects.link(o)
        assert all(p.area>0 for p in mesh.polygons)
        return o
    sources = json.loads((ROOT/'public/data/buildings.json').read_text())['buildings']
    roofs=bpy.data.objects['Continuous surveyed roofs - authored finishes']
    roof_backup=roofs.data.copy();roof_backup.use_fake_user=True
    roofs['yarra_bridge_original_roof_mesh']=roof_backup.name
    roofs.data=roofs.data.copy();roofs.data.materials.append(deck);deck_index=len(roofs.data.materials)-1
    report=[]
    for sid,label in [('17604','Evan Walker'),('20327','Sandridge')]:
        q=next(b for b in sources if b['id']==sid)
        ring=[(x,-y) for x,y in q['ring']]
        def inside(x,y):
            yes=False
            for a,b in zip(ring,ring[1:]):
                if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]: yes=not yes
            return yes
        for p in roofs.data.polygons:
            if abs(p.center.z-7)<.01 and inside(p.center.x,p.center.y):p.material_index=deck_index
        o=bpy.data.objects['survey_'+sid]
        backup=o.data.copy(); backup.use_fake_user=True; o['yarra_bridge_original_mesh']=backup.name
        o.data=o.data.copy(); o.data.materials.clear(); o.data.materials.append(deck)
        for p in o.data.polygons: p.material_index=0
        # Rail follows retained outline; omit tiny survey chatter, without changing deck.
        segments=[]
        for a,b in zip(ring,ring[1:]):
            length=math.dist(a,b)
            if length<.3: continue
            segments.append(((*a,8.05),(*b,8.05)))
            for j in range(max(1,math.ceil(length/2))+1):
                t=j/max(1,math.ceil(length/2)); x=a[0]+t*(b[0]-a[0]); y=a[1]+t*(b[1]-a[1])
                segments.append(((x,y,7.02),(x,y,8.05)))
        beams('Yarra '+label+' authored outline railing',segments,.07,white if sid=='17604' else grey)
        if sid=='17604':
            # Primary contractor photograph shows pale arch and diagonal hangers.
            a=Vector((-177.5,-166,7)); b=Vector((-170,-118,7))
            pts=[a.lerp(b,i/48)+Vector((0,0,12*4*(i/48)*(1-i/48))) for i in range(49)]
            beams('Yarra Evan Walker authored pale arch',list(zip(pts,pts[1:])),.6,white)
            hangers=[]
            for j in range(1,8):
                t=j/8; c=a.lerp(b,t)+Vector((0,0,12*4*t*(1-t)))
                foot=a.lerp(b,max(0,t-.12)); foot.z=7.1
                hangers.append((c,foot))
            beams('Yarra Evan Walker authored diagonal hangers',hangers,.10,white)
            reference='https://old2.awsservices.com.au/aws-projects/evan-walker-bridge/'
        else:
            # Municipal heritage report establishes deep plate girders and column supports.
            a=Vector((-440,-284,6)); b=Vector((-306,-142,6)); t=(b-a).normalized(); n=Vector((-t.y,t.x,0))
            girders=[]
            for side in [-2.2,2.2]:
                for z in [5.9,6.7]: girders.append((a+n*side+Vector((0,0,z-6)),b+n*side+Vector((0,0,z-6))))
            beams('Yarra Sandridge authored plate girder chords',girders,.35,grey)
            verts=[]; faces=[]
            for side in [-2.2,2.2]:
                i=len(verts)
                verts.extend(tuple(p+n*side+Vector((0,0,z-6))) for p,z in [(a,5.9),(b,5.9),(b,6.7),(a,6.7)])
                faces.append((i,i+1,i+2,i+3))
            mesh=bpy.data.meshes.new('Yarra Sandridge authored plate girder webs')
            mesh.from_pydata(verts,[],faces);mesh.materials.append(grey);mesh.update()
            web=bpy.data.objects.new(mesh.name,mesh);collection.objects.link(web)
            supports=[]
            for fraction in [.22,.44,.66,.86]:
                c=a.lerp(b,fraction)
                for side in [-1.8,1.8]: supports.append((c+n*side+Vector((0,0,-5.8)),c+n*side))
            beams('Yarra Sandridge authored support columns',supports,.8,grey)
            reference='https://mvga-prod-files.s3.ap-southeast-4.amazonaws.com/public/2024-07/central-city-heritage-study-review-1993-p5.pdf'
        assert [tuple(v.co) for v in o.data.vertices]==[tuple(v.co) for v in backup.vertices]
        assert [tuple(p.vertices) for p in o.data.polygons]==[tuple(p.vertices) for p in backup.polygons]
        report.append({'survey_id':sid,'name':label,'reference':reference,'original_mesh':backup.name,'deck_geometry_unchanged':True})
    scene[key]='retained-decks-authored-primary-reference-structure-v1'
    for o in collection.objects:
        o['limits']='Source-guided aerial approximation; original municipal deck footprint unchanged. Arch48m/rise12m, rail1.03m/posts2m, girder placement and column widths/positions authored, not engineering dimensions. No textures. Original geometry recoverable. Sculptural installations omitted.'
    print('YARRA_BRIDGE_REPAIR',json.dumps(report),flush=True)

collection=bpy.data.collections['Yarra bridges - source guided authored structure']
grey=bpy.data.materials['Yarra bridge authored grey green steel']
deck=bpy.data.materials['Yarra bridge authored neutral pedestrian deck']
if 'beams' not in globals():
    def beams(name,segments,width,mat):
        vertices=[];faces=[]
        for a,b in segments:
            a=Vector(a);b=Vector(b);t=(b-a).normalized();u=t.cross(Vector((0,0,1)))
            if u.length<.01:u=Vector((1,0,0))
            u.normalize();n=t.cross(u).normalized();k=len(vertices)
            for c in [a,b]:vertices.extend(tuple(c+u*x*width/2+n*y*width/2) for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)])
            faces.extend(tuple(k+j for j in q) for q in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.materials.append(mat);mesh.update();o=bpy.data.objects.new(name,mesh);collection.objects.link(o);return o
if not scene.get('yarra_western_bridge_structure_revision'):
    # Primary structure families; existing deck footprints remain the planform.
    collection=bpy.data.collections.get('Yarra bridges - source guided authored structure')
    sources=json.loads((ROOT/'public/data/buildings.json').read_text())['buildings']
    definitions=[('24181','Queens',5,'iron plate girders','https://www.engineersaustralia.org.au/sites/default/files/resource-files/2017-01/walk_tour_brochure.op_.v11.august_2013.pdf'),('39116','Kings',4,'steel plate girders','https://planning-schemes.app.planning.vic.gov.au/static/incorporateddocs/legacy/Melbourne/402131/C305melb-Southbank-Statements-of-Significance-Dec-2020.pdf'),('22347','Spencer',3,'variable depth steel girders','https://planning-schemes.app.planning.vic.gov.au/static/incorporateddocs/legacy/Melbourne/402131/C305melb-Southbank-Statements-of-Significance-Dec-2020.pdf')]
    for sid,label,spans,family,reference in definitions:
        q=next(b for b in sources if b['id']==sid);ring=[(x,-y) for x,y in q['ring']];top=q['base']+q['height']
        rails=[]
        for a,b in zip(ring,ring[1:]):
            length=math.dist(a,b)
            if length<.5:continue
            rails.append(((*a,top+1.05),(*b,top+1.05)))
            for j in range(max(1,math.ceil(length/2))+1):
                t=j/max(1,math.ceil(length/2));x=a[0]+t*(b[0]-a[0]);y=a[1]+t*(b[1]-a[1])
                rails.append(((x,y,top), (x,y,top+1.05)))
        rail=beams('Yarra '+label+' authored deck railing',rails,.08,grey)
        # Approximate visible structural core centered within original envelope.
        cx=(min(x for x,y in ring)+max(x for x,y in ring))/2
        low=min(y for x,y in ring)+4;high=max(y for x,y in ring)-4
        half=(max(x for x,y in ring)-min(x for x,y in ring))/2-1
        supports=[]
        for j in range(1,spans):
            y=low+(high-low)*j/spans
            for x in [cx-half*.65,cx+half*.65]:supports.append(((x,y,.2),(x,y,top-1.1)))
        piers=beams('Yarra '+label+' authored simplified supports',supports,1.2,grey)
        girder=beams('Yarra '+label+' authored girder lines',[((cx+side*half,low,top-.8),(cx+side*half,high,top-.8)) for side in [-1,1]],.65,grey)
        for o in [rail,piers,girder]:
            o['source_id']=sid;o['reference']=reference;o['structure_family']=family
            o['limits']='Authored aerial approximation on retained footprint. Queens five/Spencer three span families primary-supported; Kings four spans applies only this cropped river core and is unmeasured. Girder, support positions/widths and railing1.05m/posts2m approximate; exact current ornament deferred. Existing deck levels await capture reconciliation.'
    scene['yarra_western_bridge_structure_revision']='source-family-authored-structure-v1'

if not scene.get('yarra_western_bridge_deck_finish_revision'):
    roof=bpy.data.objects['Continuous surveyed roofs - authored finishes']
    backup=roof.data.copy();backup.use_fake_user=True;roof['yarra_western_finish_original_mesh']=backup.name
    roof.data=roof.data.copy();roof.data.materials.append(deck);slot=len(roof.data.materials)-1
    changed=0
    for sid in ['24181','39116','22347']:
        b=next(q for q in json.loads((ROOT/'public/data/buildings.json').read_text())['buildings'] if q['id']==sid);ring=b['ring'];top=b['base']+b['height']
        def hit(x,y):
            inside=False
            for a,c in zip(ring,ring[1:]):
                ay=-a[1];cy=-c[1]
                if (ay>y)!=(cy>y) and x<(c[0]-a[0])*(y-ay)/(cy-ay)+a[0]:inside=not inside
            return inside
        for p in roof.data.polygons:
            if abs(p.center.z-top)<.01 and hit(p.center.x,p.center.y):p.material_index=slot;changed+=1
        o=bpy.data.objects['survey_'+sid];old=o.data.copy();old.use_fake_user=True;o['yarra_original_deck_finish_mesh']=old.name;o.data=o.data.copy();o.data.materials.clear();o.data.materials.append(deck)
        for p in o.data.polygons:p.material_index=0
    scene['yarra_western_bridge_deck_finish_revision']='authored-neutral-deck-source-footprints-v1'
    print('YARRA_WESTERN_DECK_FINISH',changed,'cap faces',flush=True)

if os.environ.get('YARRA_BRIDGE_ISOLATE_KINGS')=='1' and not scene.get('yarra_kings_ambiguous_layer_revision'):
    # Diagnostic isolation, not a measured replacement of the complete bridge.
    for name in ['survey_39117','Vicmap bridge carriageway on survey 39117']:
        o=bpy.data.objects.get(name)
        if o:
            o['yarra_ambiguous_original_visibility']=[o.hide_render,o.hide_viewport]
            o.hide_render=True;o.hide_viewport=True
    ring=next(b for b in json.loads((ROOT/'public/data/buildings.json').read_text())['buildings'] if b['id']=='39117')['ring']
    def covered(x,y):
        yes=False
        for a,b in zip(ring,ring[1:]):
            ay=-a[1];by=-b[1]
            if (ay>y)!=(by>y) and x<(b[0]-a[0])*(y-ay)/(by-ay)+a[0]:yes=not yes
        return yes
    roof=bpy.data.objects['Continuous surveyed roofs - authored finishes'];old=roof.data
    backup=old.copy();backup.use_fake_user=True;roof['yarra_kings_ambiguous_original_roof_mesh']=backup.name
    kept=[p for p in old.polygons if not(abs(p.center.z-11)<.01 and covered(p.center.x,p.center.y))]
    mesh=bpy.data.meshes.new(old.name+' Kings ambiguous cap isolated');mesh.from_pydata([tuple(v.co) for v in old.vertices],[],[tuple(p.vertices) for p in kept]);mesh.update()
    for mat in old.materials:mesh.materials.append(mat)
    for p,q in zip(mesh.polygons,kept):p.material_index=q.material_index;p.use_smooth=q.use_smooth
    roof.data=mesh;scene['yarra_kings_ambiguous_layer_revision']='unverified-upper-envelope-isolated-v1'
    print('YARRA_KINGS_AMBIGUOUS_LAYER_ISOLATED',len(old.polygons)-len(kept),'cap faces',flush=True)

# Reconcile the demonstrably disconnected south approach within existing mapped
# road/kerb/pavement ownership; never create a guessed carriageway footprint.
if os.environ.get('YARRA_BRIDGE_LANDING_TRIAL')=='1' and not scene.get('yarra_princes_south_landing_revision'):
    patched=[]
    names=['Continuous Vicmap road surface','Authored kerbs - retained road edges']
    for o in bpy.data.objects:
        if o.type!='MESH' or o.hide_render: continue
        if o.name not in names and not any(t in o.name.lower() for t in ['pavement','footway','tram rails','road markings']): continue
        # Conservative corridor on the southward extension of the retained deck.
        selected=[]
        for v in o.data.vertices:
            p=o.matrix_world@v.co
            centre=125+(p.y+180)*(-.35/.94)
            if -365<p.y<-179 and abs(p.x-centre)<30 and -.5<p.z<2: selected.append(v.index)
        if not selected: continue
        backup=o.data.copy();backup.use_fake_user=True;o['yarra_south_landing_original_mesh']=backup.name
        o.data=o.data.copy()
        for i in selected:
            v=o.data.vertices[i];p=o.matrix_world@v.co
            centre=125+(p.y+180)*(-.35/.94)
            cross=abs(p.x-centre)
            lateral=max(0,min(1,(30-cross)/10));lateral=lateral*lateral*(3-2*lateral)
            t=max(0,min(1,(-p.y-195)/170));t=t*t*(3-2*t)
            lift=5.945*(1-t)*lateral
            p.z+=lift;v.co=o.matrix_world.inverted()@p
        o.data.update();patched.append({'object':o.name,'vertices':len(selected)})
        o['yarra_south_landing_limits']='Authored smooth170m grade from captured6.2m deck to existing flat ground,30m half corridor/10m edge blend. Existing mapped road/footway ownership preserved. Exact southern ground elevations unverified; not a surveyed ramp. Recovery mesh retained.'
    scene['yarra_princes_south_landing_revision']='mapped-surfaces-authored-gradual-grade-v1'
    print('YARRA_SOUTH_LANDING_PATCH',json.dumps(patched),flush=True)

if os.environ.get('YARRA_BRIDGE_CAPTURED_LANDING_TRIAL')=='1' and not scene.get('yarra_princes_captured_landing_revision'):
    import numpy as np
    samples=np.array(json.loads((ROOT/'assets/source/environment/yarra-bridge-captured-levels.json').read_text())['bridges']['princes_south']['samples'])
    def road_height(x,y):
        # Capture demonstrates5.5..6.2m road corridor; discard adjacent roofs.
        # Source corridor checks support about5.77m atY-210, falling gently south.
        # Use a coherent authored longitudinal fit, avoiding traffic/kerb noise.
        h=5.77+.003*(y+210)
        anchor=max(0,min(1,(y+198)/19));anchor=anchor*anchor*(3-2*anchor)
        h=h*(1-anchor)+6.2*anchor
        # Authored extension outside historical sample bounds, clearly disclosed.
        t=max(0,min(1,(-y-280)/100));t=t*t*(3-2*t)
        return h*(1-t)+.22*t
    for o in bpy.data.objects:
        if o.type!='MESH' or o.hide_render:continue
        if o.name not in ['Continuous Vicmap road surface','Authored kerbs - retained road edges','Continuous authored pavement bands','Retained Vicmap tram rails - authored road-draped gauge']:continue
        # Original city triangles cross the entire approach. Subdivide locally
        # before height fitting, otherwise road interpolation sinks under apron.
        if o.name!='Retained Vicmap tram rails - authored road-draped gauge':
            original=o.data.copy();original.use_fake_user=True;o['yarra_captured_landing_original_unsubdivided_mesh']=original.name
            points=[];triangles=[];materials=[]
            def add_triangle(xyz,mat):
                world=[o.matrix_world@Vector(p) for p in xyz]
                near=min(p.x for p in world)<245 and max(p.x for p in world)>80 and min(p.y for p in world)<-160 and max(p.y for p in world)>-390
                lengths=[(world[(j+1)%3]-world[j]).length for j in range(3)];j=max(range(3),key=lambda j:lengths[j])
                if near and lengths[j]>6:
                    k=(j+1)%3;l=(j+2)%3;mid=tuple((Vector(xyz[j])+Vector(xyz[k]))/2)
                    add_triangle([xyz[j],mid,xyz[l]],mat);add_triangle([mid,xyz[k],xyz[l]],mat);return
                start=len(points);points.extend(xyz);triangles.append((start,start+1,start+2));materials.append(mat)
            for face in original.polygons:
                xyz=[tuple(original.vertices[i].co) for i in face.vertices]
                for j in range(1,len(xyz)-1):add_triangle([xyz[0],xyz[j],xyz[j+1]],face.material_index)
            mesh=bpy.data.meshes.new(original.name+' locally subdivided landing');mesh.from_pydata(points,[],triangles);mesh.update()
            for m in original.materials:mesh.materials.append(m)
            for face,mat in zip(mesh.polygons,materials):face.material_index=mat
            o.data=mesh
        selected=[]
        for v in o.data.vertices:
            p=o.matrix_world@v.co;centre=125+(p.y+180)*(-.35/.94)
            if -380<p.y<-165 and abs(p.x-centre)<26 and -.5<p.z<2:selected.append(v.index)
        if not selected:continue
        backup=o.data.copy();backup.use_fake_user=True;o['yarra_captured_landing_original_mesh']=backup.name;o.data=o.data.copy()
        for i in selected:
            v=o.data.vertices[i];p=o.matrix_world@v.co;offset=max(0,p.z-.22);p.z=road_height(p.x,p.y)+offset;v.co=o.matrix_world.inverted()@p
        o.data.update()
    # A closed approach terrace beneath the carriageways and median prevents
    # lifted road faces floating above an untouched flat ground island.
    verts=[];faces=[]
    sections=[-180,-190,-205,-220,-235,-250,-265,-280,-295,-310,-325,-340,-355,-370,-380]
    for y in sections:
        cx=125+(y+180)*(-.35/.94)
        for dx in [-26,-13,0,13,26]:
            x=cx+dx;verts.append((x,y,road_height(x,y)-.25))
    for row in range(len(sections)-1):
        for col in range(4):
            a=row*5+col;faces.append((a,a+5,a+6,a+1))
    last=(len(sections)-1)*5
    boundary=[*range(5),*[r*5+4 for r in range(1,len(sections))],*range(last+3,last-1,-1),*[r*5 for r in range(len(sections)-2,0,-1)]]
    for a,b in zip(boundary,boundary[1:]+boundary[:1]):
        pa=verts[a];pb=verts[b];k=len(verts);verts.extend([(pa[0],pa[1],-.39),(pb[0],pb[1],-.39)]);faces.append((a,k,k+1,b))
    mesh=bpy.data.meshes.new('Yarra Princes authored captured-context approach apron');mesh.from_pydata(verts,[],faces);mesh.materials.append(deck);mesh.update();o=bpy.data.objects.new(mesh.name,mesh);collection.objects.link(o)
    o['limits']='Authored52m wide approach apron within existing street corridor, fitted to nearby historical5.7m road context, closed retaining edges to flat model ground. Exact terrace footprint/retaining design unmeasured. Own concrete finish; existing road/pavement overlays retained.'
    scene['yarra_princes_captured_landing_revision']='historical-context-authored-closed-apron-v2'
