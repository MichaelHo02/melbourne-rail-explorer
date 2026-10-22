"""Assemble an editable, coloured Melbourne aerial preview from retained evidence.
Blender -b --factory-startup --python scripts/blender/build_city_observatory.py
All city finishes are authored; survey geometry is evidence, not current photographic coverage.
"""
import bpy, bmesh, json, math, os, hashlib
from mathutils import Vector, geometry
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'../..'))
def read(p):
    with open(os.path.join(ROOT,p)) as f:return json.load(f)
def project(p,z=0):return ((p[0]-144.9671)*87939,(p[1]+37.8183)*111320,z)
def col(name):
    c=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(c);return c
def move(o,c):
    for old in list(o.users_collection):old.objects.unlink(o)
    c.objects.link(o)
def material(name,color,rough=.8,metal=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
def mesh(name,verts,faces,mat,c):
    m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();o=bpy.data.objects.new(name,m);c.objects.link(o);m.materials.append(mat);return o
def imported(path,c):
    bpy.ops.object.select_all(action='DESELECT');bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT,'public',path.lstrip('/')))
    objects=list(bpy.context.selected_objects)
    for o in objects:move(o,c)
    return objects
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
scene['target_era']='Present-day Melbourne target; historical survey/photography dates retained'
scene['geographic_origin']=[144.9671,-37.8183];scene['coordinate_frame']='X east Y north Z up, metres; relative authored ground datum'
scene['appearance_limits']='All city colours and facade patterns are authored. Survey catalogue May 2023; retained records may be older. Terrain levels and road widths are illustrative. No photographic textures or photomesh used.'
city=col('CITY - surveyed envelopes with authored facade materials');landmarks=col('CITY - reference-authored landmarks');geo=col('GROUND - official horizontal geography, authored levels');trees=col('TREES - mapped locations, authored crowns');preview=col('PREVIEW - lighting and aerial camera')
roof=material('Authored pale roof finish',(.32,.34,.33));roofs=[roof,material('Authored warm roof finish',(.39,.34,.27)),material('Authored light zinc roof finish',(.48,.51,.49))];glass=material('Authored slate blue glazing',(.18,.28,.32),.28,.3)
facades=[]
for name,color in [('stone',(.46,.40,.31)),('concrete',(.40,.43,.42)),('terracotta',(.34,.19,.13)),('glass',(.10,.18,.20))]:
    m=material('Authored '+name+' facade - not individual photographic evidence',color,.45 if name=='glass' else .85,.15 if name=='glass' else 0)
    n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');pos=n.new('ShaderNodeNewGeometry');xyz=n.new('ShaderNodeSeparateXYZ');l.new(pos.outputs['Position'],xyz.inputs[0]);normal=n.new('ShaderNodeSeparateXYZ');l.new(pos.outputs['Normal'],normal.inputs[0]);absolute=n.new('ShaderNodeMath');absolute.operation='ABSOLUTE';l.new(normal.outputs['X'],absolute.inputs[0]);wall=n.new('ShaderNodeMixRGB');l.new(absolute.outputs[0],wall.inputs[0]);l.new(xyz.outputs['X'],wall.inputs[1]);l.new(xyz.outputs['Y'],wall.inputs[2])
    mods=[]
    # Fine floor spandrels and broad wall bays in metre coordinates.
    for axis,period,width in [('X',3,.17),('Z',3.8,.2)]:
        mod=n.new('ShaderNodeMath');mod.operation='PINGPONG';mod.inputs[1].default_value=period/2;l.new(wall.outputs[0] if axis=='X' else xyz.outputs[axis],mod.inputs[0]);cut=n.new('ShaderNodeMath');cut.operation='LESS_THAN';cut.inputs[1].default_value=width;l.new(mod.outputs[0],cut.inputs[0]);mods.append(cut)
    maximum=n.new('ShaderNodeMath');maximum.operation='MAXIMUM';l.new(mods[0].outputs[0],maximum.inputs[0]);l.new(mods[1].outputs[0],maximum.inputs[1]);mix=n.new('ShaderNodeMixRGB');mix.inputs[1].default_value=(*color,1);mix.inputs[2].default_value=(.055,.12,.16,1);l.new(maximum.outputs[0],mix.inputs[0]);l.new(mix.outputs[0],p.inputs['Base Color']);noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1.8;noise.inputs['Detail'].default_value=2;l.new(pos.outputs['Position'],noise.inputs['Vector']);bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.08;bump.inputs['Distance'].default_value=.025;l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],p.inputs['Normal']);facades.append(m)
def inside(x,z,ring):
    hit=False
    for i,a in enumerate(ring):
        b=ring[i-1]
        if (a[1]>z)!=(b[1]>z) and x<(b[0]-a[0])*(z-a[1])/(b[1]-a[1])+a[0]:hit=not hit
    return hit
front=read('public/models/environment/viaduct-frontage.json');front_ids={i for s in front['structures'].values() for i in s['objectIds']}
data=read('public/data/buildings.json');count=0
window_vertices=[];window_faces=[];edge_vertices=[];edge_faces=[]
def quad_batch(vertices,faces,points):
    start=len(vertices);vertices.extend(points);faces.append(tuple(range(start,start+4)))
for b in data['buildings']:
    ring=b['ring'][:]
    if ring[0]==ring[-1]:ring.pop()
    if len(ring)<3 or b['id'] in front_ids:continue
    cx=sum(p[0] for p in ring)/len(ring);cz=sum(p[1] for p in ring)/len(ring)
    if not (-2000<=cx<=1250 and -1750<=cz<=800):continue
    base=b['base'];top=base+b['height'];
    if b['kind'] in ('Bridge','Jetty'):top=max(3,top);base=top-1.2
    n=len(ring);verts=[(x,-z,y) for y in (base,top) for x,z in ring];faces=[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];points=[Vector((x,-z,0)) for x,z in ring]
    faces.extend([tuple(range(n,n*2)),tuple(reversed(range(n)))])
    finish=facades[3 if b['height']>45 else int(b['id'])%3];o=mesh('survey_'+b['id'],verts,faces,finish,city);o.data.materials.append(roofs[int(b['id'])%3])
    for polygon in o.data.polygons:
        if polygon.normal.z>.9:polygon.material_index=1
    o['source_id']=b['id'];o['source_url']=data['url'];o['source_license']=data['license'];o['appearance']='Authored facade, survey-derived envelope, current condition unverified';count+=1
    # Authored window bays and roof edge strips: geometry creates readable highlights.
    if b['kind']=='Structure' and b['height']>=8:
        signed=sum(ring[i-1][0]*(-ring[i][1])-ring[i][0]*(-ring[i-1][1]) for i in range(n))
        for i,(x,z) in enumerate(ring):
            bx,bz=ring[(i+1)%n];a=Vector((x,-z,0));v=Vector((bx-x,z-bz,0));length=v.length
            if length<3:continue
            tangent=v/length;normal=Vector((tangent.y,-tangent.x,0))*(1 if signed>0 else -1)
            bays=min(30,int(length/3.4));floors=min(45,int(b['height']/3.6))
            for floor in range(floors):
                low=base+1+floor*3.6;high=min(top-.6,low+2.15)
                if high<=low:continue
                for bay in range(bays):
                    center=(bay+.5)*length/bays;half=min(1.25,length/bays*.36)
                    left=a+tangent*(center-half)+normal*.045;right=a+tangent*(center+half)+normal*.045
                    quad_batch(window_vertices,window_faces,[(left.x,left.y,low),(right.x,right.y,low),(right.x,right.y,high),(left.x,left.y,high)])
            # Shallow projecting cornice makes roof boundaries legible without assumed roof plant.
            aa=a+normal*.12;bb=a+v+normal*.12
            quad_batch(edge_vertices,edge_faces,[(aa.x,aa.y,top-.3),(bb.x,bb.y,top-.3),(bb.x,bb.y,top+.15),(aa.x,aa.y,top+.15)])
if window_faces:
    detail=mesh('Authored window bays - illustrative spacing',window_vertices,window_faces,glass,city);detail['appearance']='Authored glazing bays; individual fenestration unverified'
if edge_faces:mesh('Authored roof edge cornices',edge_vertices,edge_faces,roofs[0],city)
# Imported GLB coordinate transforms match the existing game-to-Blender frame.
imported('/models/environment/corridor-frontage.glb',landmarks)
objects=imported('/models/stations-flinders.glb',landmarks);anchor=bpy.data.objects.new('Flinders Street - runtime placement',None);landmarks.objects.link(anchor);anchor.location=project([144.96714,-37.81793]);anchor.rotation_euler.z=math.atan2((-37.81743935+37.81815818)*111320,(144.96744569-144.96497587)*87939)
for o in objects:
    if o.parent is None:o.parent=anchor
# Flat preview ground is explicitly authored, not an elevation survey.
ground=material('Authored neutral urban ground',(.22,.25,.22));mesh('Authored flat ground', [(-2800,-1600,-.4),(2100,-1600,-.4),(2100,2500,-.4),(-2800,2500,-.4)],[(0,1,2,3)],ground,geo)
water=material('Authored Yarra water colour',(.07,.24,.23),.3,.05);river=read('src/data/river-source.json');ring=river['geometry']['coordinates'][0][:-1];verts=[project(p,.15) for p in ring]
o=mesh('Yarra - Vicmap Hydro water boundary',verts,[tuple(range(len(verts)))],water,geo);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o['source_url']=river['sourceUrl'];o['source_license']=river['license'];o['vertical_level']='Authored preview level'
roads=read('src/data/observatory-roads.json');roadmat=material('Authored asphalt',(.075,.085,.09));paving=material('Authored stone pavement',(.42,.40,.35));verts=[];faces=[];pavement_verts=[];pavement_faces=[];mark_vertices=[];mark_faces=[];kerb_vertices=[];kerb_faces=[]
for f in roads['features']:
    if str(f['properties'].get('vehicular_access'))!='1':continue
    lines=[f['geometry']['coordinates']] if f['geometry']['type']=='LineString' else f['geometry']['coordinates']
    for line in lines:
        for a,b in zip(line,line[1:]):
            a=project(a,.24);b=project(b,.24);dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy)
            if not length:continue
            width=6 if int(f['properties'].get('class_code',5))<4 else 3.2
            if str(f['properties'].get('ezi_road_name','')).upper() in ('FLINDERS STREET','COLLINS STREET','BOURKE STREET','LONSDALE STREET','LA TROBE STREET','SWANSTON STREET','ELIZABETH STREET','QUEEN STREET','WILLIAM STREET','KING STREET','SPENCER STREET'):width=9
            if width>=6 and length>35:
                tangent=Vector((dx/length,dy/length,0));normal=Vector((-dy/length,dx/length,0));origin=Vector(a)
                for offset in (-width*.5,width*.5):
                    for distance in range(18,int(length)-18,10):
                        start=origin+tangent*distance+normal*offset;end=start+tangent*3
                        quad_batch(mark_vertices,mark_faces,[(start.x-normal.x*.07,start.y-normal.y*.07,.27),(end.x-normal.x*.07,end.y-normal.y*.07,.27),(end.x+normal.x*.07,end.y+normal.y*.07,.27),(start.x+normal.x*.07,start.y+normal.y*.07,.27)])
                for side in (-1,1):
                    start=origin+normal*width*side;end=start+tangent*length
                    quad_batch(kerb_vertices,kerb_faces,[(start.x,start.y,.24),(end.x,end.y,.24),(end.x,end.y,.38),(start.x,start.y,.38)])
            for vertices,polygons,half,z in [(pavement_verts,pavement_faces,width+2,.20),(verts,faces,width,.24)]:
                nx=-dy/length*half;ny=dx/length*half;start=len(vertices);vertices.extend([(a[0]+nx,a[1]+ny,z),(a[0]-nx,a[1]-ny,z),(b[0]-nx,b[1]-ny,z),(b[0]+nx,b[1]+ny,z)]);polygons.append(tuple(start+i for i in range(4)))
o=mesh('Roads - official Vicmap centrelines',verts,faces,roadmat,geo);o['source_url']=roads['source'];o['source_license']=roads['license'];o['widths_and_levels']='Authored preview widths and flat datum'
p=mesh('Pavements - illustrative widths on official road alignment',pavement_verts,pavement_faces,paving,geo);p['appearance']='Authored 2m pavement bands; not surveyed kerbs'
if mark_faces:
    markings=mesh('Authored illustrative lane dashes',mark_vertices,mark_faces,material('Authored worn lane paint',(.65,.64,.55)),geo);markings['limits']='Illustrative generic lane spacing, not verified lane allocation or junction controls'
if kerb_faces:mesh('Authored shallow kerb edges',kerb_vertices,kerb_faces,paving,geo)
corridor=read('src/data/corridor-source.json');green=material('Authored tree foliage',(.10,.25,.12));trunk=material('Authored tree bark',(.21,.15,.10));bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1);template=bpy.context.object;template.data.materials.append(green);crown=template.data;bpy.data.objects.remove(template,do_unlink=True)
for f in corridor['layers']['trees']['features']:
    p=project(f['geometry']['coordinates']);o=bpy.data.objects.new('tree_'+str(f['properties']['com_id']),crown);trees.objects.link(o);o.location=(p[0],p[1],5);size=2.5+(int(f['properties']['com_id'])%17)/10;o.scale=(size,size*.92,size*1.25);o['source_id']=f['properties']['com_id'];o['shape']='Authored crown; position from City of Melbourne Urban Forest'
# Rail alignments retained from Vicmap; exclude explicitly underground features.
rail_v=[];rail_f=[];bed_v=[];bed_f=[]
for feature in corridor['layers']['rails']['features']:
    kind=feature['properties'].get('feature_type_code')
    if kind not in ('railway','tramway'):continue
    lines=[feature['geometry']['coordinates']] if feature['geometry']['type']=='LineString' else feature['geometry']['coordinates']
    for line in lines:
        for start,end in zip(line,line[1:]):
            a=Vector(project(start));b=Vector(project(end));direction=b-a;length=direction.length
            if length<.1:continue
            direction/=length;normal=Vector((-direction.y,direction.x,0));level=.29 if kind=='tramway' else .46
            if kind=='railway':
                quad_batch(bed_v,bed_f,[tuple(a-normal*1.8+Vector((0,0,.4))),tuple(b-normal*1.8+Vector((0,0,.4))),tuple(b+normal*1.8+Vector((0,0,.4))),tuple(a+normal*1.8+Vector((0,0,.4)))])
            for offset in (-.8,.8):
                left=a+normal*(offset-.055);right=b+normal*(offset-.055);outer=b+normal*(offset+.055);back=a+normal*(offset+.055)
                quad_batch(rail_v,rail_f,[(v.x,v.y,level) for v in (left,right,outer,back)])
if bed_f:
    obj=mesh('Railway ballast - authored level on Vicmap alignment',bed_v,bed_f,material('Authored ballast',(.19,.18,.16)),geo);obj['source_url']=corridor['sources']['rails']['url'];obj['source_license']='CC BY 4.0';obj['limits']='Authored flat level and gauge; no surveyed vertical alignment'
if rail_f:mesh('Rail and tram steel - authored gauge',rail_v,rail_f,material('Authored rail steel',(.24,.27,.28),.3,.7),geo)
trunk_v=[];trunk_f=[]
for obj in list(trees.objects):
    x,y,_=obj.location;r=.18;h=max(2,obj.scale.z)
    for dx,dy,ex,ey in [(-r,-r,r,-r),(r,-r,r,r),(r,r,-r,r),(-r,r,-r,-r)]:
        quad_batch(trunk_v,trunk_f,[(x+dx,y+dy,.35),(x+ex,y+ey,.35),(x+ex,y+ey,h),(x+dx,y+dy,h)])
mesh('Authored tree trunks',trunk_v,trunk_f,trunk,trees)
# Authored neutral environment and directional daylight.
world=bpy.data.worlds.new('Authored neutral daylight');world.use_nodes=True;scene.world=world;world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.68,.76,.85,1);world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.22
light=bpy.data.lights.new('Preview sun','SUN');light.energy=3.2;light.color=(1,.90,.78);light.angle=.075;o=bpy.data.objects.new('Preview sun',light);preview.objects.link(o);o.rotation_euler=(.5,-.4,-.5)
cam=bpy.data.cameras.new('Aerial overview');o=bpy.data.objects.new('Aerial overview',cam);preview.objects.link(o);scene.camera=o;o.location=(1000,-1650,1400);target=Vector((-650,600,25));o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler();cam.type='ORTHO';cam.ortho_scale=3400;cam.clip_end=20000
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.preview_samples=8;scene.cycles.use_preview_denoising=True;scene.cycles.use_denoising=True
scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG'
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active;space.clip_end=20000;space.shading.type='RENDERED';space.shading.use_scene_world=True;space.shading.use_scene_lights=True;space.overlay.show_overlays=False;space.region_3d.view_perspective='CAMERA';space.region_3d.view_camera_zoom=12
scene['survey_envelope_count']=count;scene['pavement_limits']='Illustrative 2m bands on official road centrelines, no surveyed kerb geometry'
# Save the completed assembly below after park geometry.
lawn=material('Authored park grass',(.19,.29,.13))
for feature in corridor['layers']['openSpaces']['features']:
    if feature['properties'].get('os_group')!='Parkland and garden':continue
    polygons=feature['geometry']['coordinates'] if feature['geometry']['type']=='MultiPolygon' else [feature['geometry']['coordinates']]
    for index,polygon in enumerate(polygons):
        points=[Vector(project(p,.32)) for p in polygon[0][:-1]];faces=[tuple(range(len(points)))]
        obj=mesh('Park parcel '+str(feature['properties']['veac_id'])+'_'+str(index),[tuple(p) for p in points],faces,lawn,geo);obj['appearance']='Authored grass on inventory park parcel; not measured land cover'
cam.ortho_scale=3400
scene.view_settings.exposure=0
# Extend preview ground beyond the camera crop; keep its authored datum explicit.
geo.objects['Authored flat ground'].scale=(3,3,1)
# Reuse the same incremental material pass shown in the live Blender window.
exec(compile(open(os.path.join(os.path.dirname(__file__), 'refine_live_city.py')).read(), 'refine_live_city.py', 'exec'))
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'assets/source/environment/city-observatory.blend'),compress=True)
scene.render.filepath=os.path.join(ROOT,'docs/images/observatory-blender-preview.png');bpy.ops.render.render(write_still=True)
print('Rendered colour preview; generic envelopes:',count)

# Named inspection cameras retained for the design walkthrough.
for name,position,target,scale,filename in [
    ('02 Flinders precinct', (350,-600,460), (0,100,18), 1000, 'observatory-flinders-detail.png'),
    ('03 Hoddle grid streets', (-450,-250,600), (-550,650,35), 1100, 'observatory-street-detail.png')]:
    camera=bpy.data.cameras.new(name);obj=bpy.data.objects.new(name,camera);preview.objects.link(obj);obj.location=position;obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler();camera.type='ORTHO';camera.ortho_scale=scale;camera.clip_end=20000;scene.camera=obj;scene.render.filepath=os.path.join(ROOT,'docs/images',filename);bpy.ops.render.render(write_still=True)
scene.camera=preview.objects['Aerial overview']
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'assets/source/environment/city-observatory.blend'),compress=True)
