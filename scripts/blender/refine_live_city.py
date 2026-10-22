"""Apply a small, visible detail pass to the open city without rebuilding it.
Run in Blender's console: exec(compile(open(PATH).read(), PATH, 'exec'))
Does not reload, delete user objects or save over the current file.
"""
import bpy
from mathutils import Vector

def colour_relief(name, dark, light, scale, bump_distance=0):
    mat=bpy.data.materials.get(name)
    if not mat or not mat.use_nodes:return
    nodes=mat.node_tree.nodes;links=mat.node_tree.links;shader=nodes.get('Principled BSDF')
    noise=nodes.get('Live authored grain') or nodes.new('ShaderNodeTexNoise');noise.name='Live authored grain';noise.inputs['Scale'].default_value=scale;noise.inputs['Detail'].default_value=3
    geometry=nodes.get('Live metre coordinates') or nodes.new('ShaderNodeNewGeometry');geometry.name='Live metre coordinates';links.new(geometry.outputs['Position'],noise.inputs['Vector'])
    ramp=nodes.get('Live authored tones') or nodes.new('ShaderNodeValToRGB');ramp.name='Live authored tones';ramp.color_ramp.elements[0].color=(*dark,1);ramp.color_ramp.elements[1].color=(*light,1);links.new(noise.outputs['Fac'],ramp.inputs[0]);links.new(ramp.outputs['Color'],shader.inputs['Base Color'])
    if bump_distance:
        bump=nodes.get('Live subtle surface relief') or nodes.new('ShaderNodeBump');bump.name='Live subtle surface relief';bump.inputs['Strength'].default_value=.22;bump.inputs['Distance'].default_value=bump_distance;links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],shader.inputs['Normal'])

colour_relief('Authored asphalt',(.035,.04,.044),(.09,.10,.105),2.5,.018)
colour_relief('Authored stone pavement',(.25,.27,.27),(.46,.45,.41),.8,.012)
colour_relief('Authored pale roof finish',(.23,.25,.25),(.39,.40,.38),.16,.025)
colour_relief('Authored warm roof finish',(.27,.25,.21),(.44,.40,.32),.16,.025)
colour_relief('Authored light zinc roof finish',(.36,.40,.41),(.53,.55,.53),.2,.015)
colour_relief('Authored tree foliage',(.055,.14,.065),(.18,.31,.095),.45)
colour_relief('Authored Yarra water colour',(.045,.14,.12),(.10,.25,.21),.12,.035)
# Pitched zinc roof is authored landmark detail, not a surveyed height.
anchor=bpy.data.objects.get('Flinders Street - runtime placement')
if anchor and not bpy.data.objects.get('Flinders authored pitched zinc roof'):
    mat=bpy.data.materials.new('Authored Flinders weathered zinc');mat.diffuse_color=(.22,.25,.23,1);mat.use_nodes=True;shader=mat.node_tree.nodes.get('Principled BSDF');shader.inputs['Base Color'].default_value=(.22,.25,.23,1);shader.inputs['Roughness'].default_value=.7;shader.inputs['Metallic'].default_value=.3
    mesh=bpy.data.meshes.new('Flinders authored pitched zinc roof');mesh.from_pydata([(-291,-11.8,26.7),(-3,-11.8,26.7),(-3,0,29.1),(-291,0,29.1),(-291,11.8,26.7),(-3,11.8,26.7)],[],[(0,1,2,3),(3,2,5,4),(0,3,4),(1,5,2)]);mesh.materials.append(mat);mesh.update();obj=bpy.data.objects.new(mesh.name,mesh);anchor.users_collection[0].objects.link(obj);obj.parent=anchor;obj['appearance']='Authored pitched zinc roof; exact profile unverified'
# Immediate preview framing: retain all existing objects and the user's saved file.
scene=bpy.context.scene
scene.cycles.preview_samples=8
camera=bpy.data.objects.get('02 Flinders precinct')
if camera and scene.camera is None:scene.camera=camera
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='RENDERED'
scene['live_detail_pass']='Procedural material grain and authored Flinders pitched zinc roof, 2026-10-05'
print('LIVE CITY PASS APPLIED — switch back to 3D View to see it')

# Small roof plant gives large flat roofs a readable aerial scale. Placement is
# constrained to actual surveyed roof faces; the equipment itself is illustrative.
import math
collection=bpy.data.collections.get('CITY - surveyed envelopes with authored facade materials')
plant_name='Authored rooftop equipment - illustrative'
if collection and not bpy.data.objects.get(plant_name):
    vertices=[];faces=[]
    def plant_box(x,y,z,sx,sy,sz):
        start=len(vertices)
        vertices.extend([(x+dx*sx/2,y+dy*sy/2,z+dz*sz) for dz in (0,1) for dx,dy in [(-1,-1),(1,-1),(1,1),(-1,1)]])
        faces.extend([tuple(start+i for i in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]])
    for obj in list(collection.objects):
        if not obj.name.startswith('survey_') or obj.type!='MESH':continue
        points=[v.co for v in obj.data.vertices]
        high=max(p.z for p in points);low=min(p.z for p in points)
        if high-low<12:continue
        roof_faces=[p for p in obj.data.polygons if p.normal.z>.99 and p.area>45]
        if not roof_faces:continue
        face=max(roof_faces,key=lambda p:p.area)
        center=face.center
        # Triangle inradius ensures the unit remains safely inside the roof.
        edges=[(obj.data.vertices[face.vertices[i-1]].co,obj.data.vertices[face.vertices[i]].co) for i in range(len(face.vertices))]
        margin=min((center-a).cross(b-a).length/(b-a).length for a,b in edges if (b-a).length)
        if margin<2:continue
        size=min(4,margin*.8)
        plant_box(center.x,center.y,center.z+.1,size,size*.7,1.3)
        plant_box(center.x,center.y,center.z+1.4,size*.85,size*.6,.15)
    if vertices:
        mat=bpy.data.materials.get('Authored roof plant metal') or bpy.data.materials.new('Authored roof plant metal');mat.use_nodes=True;mat.diffuse_color=(.17,.19,.18,1)
        shader=mat.node_tree.nodes.get('Principled BSDF');shader.inputs['Base Color'].default_value=mat.diffuse_color;shader.inputs['Metallic'].default_value=.35;shader.inputs['Roughness'].default_value=.6
        data=bpy.data.meshes.new(plant_name);data.from_pydata(vertices,[],faces);data.materials.append(mat);data.update()
        obj=bpy.data.objects.new(plant_name,data);collection.objects.link(obj);obj['appearance']='Illustrative rooftop mechanical units, not measured equipment';obj['unit_count']=len(vertices)//16
        print('Added rooftop equipment units:',obj['unit_count'])

# Complete major Hoddle-grid junction surfaces using retained Vicmap endpoint
# connections. Crossing/stop-line dimensions are authored, not traffic controls.
import json
from pathlib import Path
from collections import defaultdict
root=Path(globals().get('ROOT') or Path(bpy.data.filepath).parents[3])
road_file=root/'src/data/observatory-roads.json'
ground=bpy.data.collections.get('GROUND - official horizontal geography, authored levels')
name='Authored CBD junction crossings - illustrative'
if ground and road_file.exists() and not bpy.data.objects.get(name):
    source=json.loads(road_file.read_text());nodes=defaultdict(list)
    major={'FLINDERS STREET','COLLINS STREET','BOURKE STREET','LONSDALE STREET','LA TROBE STREET','SWANSTON STREET','ELIZABETH STREET','QUEEN STREET','WILLIAM STREET','KING STREET','SPENCER STREET','RUSSELL STREET','EXHIBITION STREET','SPRING STREET'}
    for feature in source['features']:
        road=str(feature['properties'].get('ezi_road_name','')).upper()
        if road not in major or str(feature['properties'].get('vehicular_access'))!='1':continue
        lines=[feature['geometry']['coordinates']] if feature['geometry']['type']=='LineString' else feature['geometry']['coordinates']
        for line in lines:
            for p,q in [(line[0],line[1]),(line[-1],line[-2])]:
                a=Vector(((p[0]-144.9671)*87939,(p[1]+37.8183)*111320,0));b=Vector(((q[0]-144.9671)*87939,(q[1]+37.8183)*111320,0));direction=b-a
                if not (-1800<a.x<800 and 0<a.y<1600) or direction.length<15:continue
                nodes[(round(a.x/2),round(a.y/2))].append((road,a,direction.normalized()))
    vertices=[];faces=[];surface_vertices=[];surface_faces=[];junctions=0
    def strip(vs,fs,a,b,half,z):
        direction=(b-a).normalized();normal=Vector((-direction.y,direction.x,0))*half;start=len(vs)
        vs.extend([(v.x,v.y,z) for v in (a-normal,b-normal,b+normal,a+normal)]);fs.append(tuple(start+i for i in range(4)))
    for entries in nodes.values():
        if len({e[0] for e in entries})<2:continue
        center=sum((e[1] for e in entries),Vector())/len(entries);directions=[]
        for _,_,direction in entries:
            if not any(direction.dot(d)>.95 for d in directions):directions.append(direction)
        if len(directions)<3:continue
        junctions+=1
        # Join otherwise separate road ribbons through the intersection centre.
        for direction in directions:
            strip(surface_vertices,surface_faces,center,center+direction*14,9,.255)
            normal=Vector((-direction.y,direction.x,0))
            for distance in (10.5,13.5):
                for offset in range(-8,8,2):
                    a=center+direction*distance+normal*offset
                    strip(vertices,faces,a,a+normal*.8,.055,.28)
            # Stop bar on the inbound half of each approach; indicative only.
            a=center+direction*16-normal*8.3;b=center+direction*16-normal*.5
            strip(vertices,faces,a,b,.14,.281)
    for obj_name,vs,fs,material_name in [('Authored CBD junction asphalt infill',surface_vertices,surface_faces,'Authored asphalt'),(name,vertices,faces,'Authored worn lane paint')]:
        if not vs:continue
        data=bpy.data.meshes.new(obj_name);data.from_pydata(vs,[],fs);data.materials.append(bpy.data.materials[material_name]);data.update();obj=bpy.data.objects.new(obj_name,data);ground.objects.link(obj)
        obj['source_url']=source['source'];obj['source_license']=source['license'];obj['appearance']='Vicmap junction connections; illustrative surface widths and dashed pedestrian crossing guides, current signal controls unverified';obj['junction_count']=junctions
    print('Completed major CBD junctions:',junctions)

# Unioned geometry removes coplanar overlaps in the original road ribbons.
# Original generated objects remain recoverable, hidden rather than deleted.
surface_file=root/'assets/source/environment/city-road-surfaces.json'
if ground and surface_file.exists():
    surfaces=json.loads(surface_file.read_text())
    for key,label,material_name,z in [('asphalt','Continuous Vicmap road surface','Authored asphalt',.255),('paving','Continuous authored pavement bands','Authored stone pavement',.20)]:
        if bpy.data.objects.get(label):continue
        part=surfaces[key];data=bpy.data.meshes.new(label);data.from_pydata([(x,y,z) for x,y in part['vertices']],[],part['faces']);data.materials.append(bpy.data.materials[material_name]);data.update()
        obj=bpy.data.objects.new(label,data);ground.objects.link(obj);obj['source_url']=surfaces['source'];obj['source_license']=surfaces['license'];obj['appearance']=surfaces['limits'];obj['plan_area_m2']=part['area']
    for old_name in ['Roads - official Vicmap centrelines','Pavements - illustrative widths on official road alignment','Authored CBD junction asphalt infill']:
        old=bpy.data.objects.get(old_name)
        if old:old.hide_render=True;old.hide_viewport=True;old['replacement']='Continuous unioned road and pavement meshes'
    print('Continuous road and pavement meshes applied')

# Consistent upward normals for daylight and procedural surface relief.
import bmesh
for label in ['Continuous Vicmap road surface','Continuous authored pavement bands']:
    obj=bpy.data.objects.get(label)
    if obj:
        bm=bmesh.new();bm.from_mesh(obj.data);bm.normal_update();down=[f for f in bm.faces if f.normal.z<0]
        if down:bmesh.ops.reverse_faces(bm,faces=down);bm.to_mesh(obj.data);obj.data.update()
        bm.free()

# Replace overlapping generated caps with coplanar unions at the surveyed height.
roof_file=root/'assets/source/environment/city-roof-surfaces.json'
roof_label='Continuous surveyed roofs - authored finishes'
if collection and roof_file.exists() and not bpy.data.objects.get(roof_label):
    roofs=json.loads(roof_file.read_text());data=bpy.data.meshes.new(roof_label);data.from_pydata(roofs['vertices'],[],roofs['faces'])
    for finish in ['Authored pale roof finish','Authored warm roof finish','Authored light zinc roof finish']:data.materials.append(bpy.data.materials[finish])
    for face,index in zip(data.polygons,roofs['materials']):face.material_index=index
    data.update();obj=bpy.data.objects.new(roof_label,data);collection.objects.link(obj);obj['source_url']=roofs['source'];obj['source_license']=roofs['license'];obj['appearance']=roofs['limits'];obj['source_section_count']=len(roofs['source_ids'])
    cleaned=0
    for source_id in roofs['source_ids']:
        original=bpy.data.objects.get('survey_'+source_id)
        if not original or original.type!='MESH':continue
        bm=bmesh.new();bm.from_mesh(original.data);top=max(v.co.z for v in bm.verts)
        caps=[f for f in bm.faces if all(abs(v.co.z-top)<.001 for v in f.verts)]
        if caps:bmesh.ops.delete(bm,geom=caps,context='FACES_ONLY');bm.to_mesh(original.data);original.data.update();cleaned+=1
        bm.free();original['roof_surface']='Continuous surveyed roofs - authored finishes'
    print('Cleaned overlapping roof caps:',cleaned)

# Sleeper rhythm follows retained rail polylines; dimensions are authored.
rail_detail_label='Flinders precinct authored rail sleepers'
if ground and not bpy.data.objects.get(rail_detail_label):
    corridor=json.loads((root/'src/data/corridor-source.json').read_text())
    vertices=[];faces=[];source_ids=set();count=0
    for feature in corridor['layers']['rails']['features']:
        if feature['properties'].get('feature_type_code')!='railway':continue
        lines=[feature['geometry']['coordinates']] if feature['geometry']['type']=='LineString' else feature['geometry']['coordinates']
        for line in lines:
            for start,end in zip(line,line[1:]):
                a=Vector(((start[0]-144.9671)*87939,(start[1]+37.8183)*111320,0));b=Vector(((end[0]-144.9671)*87939,(end[1]+37.8183)*111320,0));delta=b-a;length=delta.length
                if length<.6:continue
                tangent=delta/length;normal=Vector((-tangent.y,tangent.x,0))
                for step in range(int(length/.65)):
                    centre=a+tangent*(step*.65+.325)
                    if not (-650<centre.x<90 and -130<centre.y<55):continue
                    base=len(vertices)
                    for z in (.405,.445):
                        for dx,dy in [(-.12,-1.22),(.12,-1.22),(.12,1.22),(-.12,1.22)]:
                            v=centre+tangent*dx+normal*dy;vertices.append((v.x,v.y,z))
                    faces.extend([tuple(base+i for i in face) for face in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]])
                    count+=1;source_ids.add(feature['properties']['ufi'])
    mat=bpy.data.materials.get('Authored sleeper concrete') or bpy.data.materials.new('Authored sleeper concrete');mat.diffuse_color=(.32,.31,.27,1);mat.use_nodes=True
    shader=mat.node_tree.nodes.get('Principled BSDF');shader.inputs['Base Color'].default_value=(.32,.31,.27,1);shader.inputs['Roughness'].default_value=.9
    data=bpy.data.meshes.new(rail_detail_label);data.from_pydata(vertices,[],faces);data.materials.append(mat);data.update();obj=bpy.data.objects.new(rail_detail_label,data);ground.objects.link(obj)
    obj['source_url']=corridor['sources']['rails']['url'];obj['source_license']='CC BY 4.0';obj['source_ufis']=','.join(str(i) for i in sorted(source_ids));obj['sleeper_count']=count;obj['appearance']='Illustrative concrete sleepers at 0.65m spacing and flat datum on retained Vicmap rail centrelines; not surveyed sleeper material, individual track coverage or present-day station layout'
    colour_relief('Authored ballast',(.10,.095,.085),(.25,.23,.20),7,.04)
    print('Added station precinct rail sleepers:',count)

# PTV's schematic establishes platform topology, not surveyed dimensions.
platform_label='Flinders authored platform precinct - PTV schematic'
if anchor and not bpy.data.objects.get(platform_label):
    pv=[];pf=[];pm=[]
    def platform_box(x,y,z,sx,sy,sz,material_index):
        start=len(pv)
        pv.extend([(x+dx*sx/2,y+dy*sy/2,z+dz*sz/2) for dz in (-1,1) for dx,dy in [(-1,-1),(1,-1),(1,1),(-1,1)]])
        pf.extend([tuple(start+i for i in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]]);pm.extend([material_index]*6)
    # Four paired islands, plus northern and southern side platforms.
    # Layout follows the official schematic; levels, widths and extents illustrative.
    for y,width in [(-18,6),(-33,5.2),(-46,5.2),(-59,5.2),(-72,5.2),(-84,4)]:
        platform_box(-160,y,.95,250,width,1.1,0)
        for side in (-1,1):platform_box(-160,y+side*(width/2-.22),1.515,250,.20,.03,1)
    for y in (-33,-46,-59,-72):
        platform_box(-155,y,6.6,220,5.8,.22,2)
        # Ridge and repeated seams give authored metal roofs a readable rhythm.
        platform_box(-155,y,6.77,220,.22,.12,2)
        for x in range(-260,-44,12):
            platform_box(x,y,4, .18,.18,5.2,3)
            platform_box(x,y,6.4,.14,5.6,.18,3)
        for x in range(-263,-44,3):platform_box(x,y,6.735,.055,5.8,.055,2)
    finishes=[]
    for name,color,rough,metal in [('Authored station platform paving',(.24,.25,.23),.9,0),('Authored platform safety edge',(.64,.50,.18),.8,0),('Authored station canopy zinc',(.30,.34,.32),.65,.3),('Authored station canopy iron',(.09,.13,.11),.55,.4)]:
        mat=bpy.data.materials.get(name) or bpy.data.materials.new(name);mat.diffuse_color=(*color,1);mat.use_nodes=True;shader=mat.node_tree.nodes.get('Principled BSDF');shader.inputs['Base Color'].default_value=(*color,1);shader.inputs['Roughness'].default_value=rough;shader.inputs['Metallic'].default_value=metal;finishes.append(mat)
    data=bpy.data.meshes.new(platform_label);data.from_pydata(pv,[],pf)
    for mat in finishes:data.materials.append(mat)
    for face,index in zip(data.polygons,pm):face.material_index=index
    data.update();obj=bpy.data.objects.new(platform_label,data);anchor.users_collection[0].objects.link(obj);obj.parent=anchor
    obj['source_url']='https://www.ptv.vic.gov.au/assets/DTP1124-FlindersStreetStation-Precinct-Map_Degraves-Subway_web_Stage-1_v3.pdf';obj['appearance']='Platform 1, paired islands 2-3/4-5/6-7/8-9 and side platform 10 topology from PTV schematic. Dimensions, canopy forms and colours authored approximations. East platforms 12-13 and present-day changes not yet resolved.';obj['platform_deck_count']=6;obj['island_canopy_count']=4
    colour_relief('Authored station canopy zinc',(.19,.23,.22),(.36,.40,.37),.7,.012)
    colour_relief('Authored station platform paving',(.17,.18,.17),(.30,.31,.28),1.2,.012)
    print('Added 6 schematic platform decks and 4 authored island canopies')

# Authored pitched shells make the platform roofs read as metal canopies.
# Heritage references support metal verandahs, not this exact roof profile.
canopy_label='Flinders authored pitched platform canopy shells'
if anchor and not bpy.data.objects.get(canopy_label):
    cv=[];cf=[]
    for y in (-33,-46,-59,-72):
        base=len(cv)
        cv.extend([(-265,y-2.9,6.85),(-45,y-2.9,6.85),(-45,y,7.65),(-265,y,7.65),(-265,y+2.9,6.85),(-45,y+2.9,6.85)])
        cf.extend([tuple(base+i for i in face) for face in [(0,1,2,3),(3,2,5,4),(0,3,4),(1,5,2)]])
    data=bpy.data.meshes.new(canopy_label);data.from_pydata(cv,[],cf);data.materials.append(bpy.data.materials['Authored station canopy zinc']);data.update()
    obj=bpy.data.objects.new(canopy_label,data);anchor.users_collection[0].objects.link(obj);obj.parent=anchor
    obj['source_url']='https://bigbuild.vic.gov.au/__data/assets/pdf_file/0008/229967/MT-Historical-Heritage-Impact-Assessment.PDF'
    obj['appearance']='Four authored shallow pitched metal canopy shells above the PTV schematic islands. Exact profile, ridge level and extents unverified; no surveyed roof claim.'
    obj['canopy_count']=4
    print('Added four pitched platform canopy shells')

# A restrained authored palette breaks the repeated four-finish appearance.
# Selection uses retained source IDs for reproducibility, not a material survey.
if collection:
    palette={
        'stone':[(.46,.40,.31),(.52,.49,.41),(.39,.37,.32),(.56,.51,.43)],
        'concrete':[(.40,.43,.42),(.48,.48,.44),(.34,.37,.38),(.52,.53,.50)],
        'terracotta':[(.34,.19,.13),(.40,.28,.21),(.30,.23,.20),(.44,.34,.27)],
        'glass':[(.10,.18,.20),(.16,.23,.25),(.18,.23,.22),(.12,.17,.23)]}
    applied=0
    for obj in collection.objects:
        if not obj.name.startswith('survey_') or obj.type!='MESH' or not obj.data.materials:continue
        source=obj.get('source_id')
        if source is None:continue
        first=obj.data.materials[0]
        kind=next((k for k in palette if first and first.name.startswith('Authored '+k+' facade')),None)
        if not kind:continue
        variant=(int(source)*2654435761>>8)%4
        label='Authored '+kind+' facade palette '+str(variant)+' - unsurveyed colour'
        mat=bpy.data.materials.get(label)
        if not mat:
            original=bpy.data.materials['Authored '+kind+' facade - not individual photographic evidence'];mat=original.copy();mat.name=label
            shader=mat.node_tree.nodes.get('Principled BSDF');link=next((l for l in mat.node_tree.links if l.to_node==shader and l.to_socket==shader.inputs['Base Color']),None)
            if link and link.from_node.type=='MIX_RGB':link.from_node.inputs[1].default_value=(*palette[kind][variant],1)
            mat.diffuse_color=(*palette[kind][variant],1)
            mat['appearance']='Authored palette variation; colour assignment is illustrative and not surveyed'
        obj.data.materials[0]=mat;obj['colour_basis']='Deterministic authored palette on retained source ID; actual building colour unverified';applied+=1
    print('Authored facade palette applied:',applied)

# A narrow authored bank coping traces the retained water boundary.
# Clip-box edges are excluded: they are data cuts, not riverbanks.
bank_label='Yarra authored bank edge on Vicmap water boundary'
if ground and not bpy.data.objects.get(bank_label):
    river=json.loads((root/'src/data/river-source.json').read_text());bounds=river['clipBounds'];bv=[];bf=[];segments=0
    ring=river['geometry']['coordinates'][0]
    for a,b in zip(ring,ring[1:]):
        if any(abs(a[axis]-edge)<1e-7 and abs(b[axis]-edge)<1e-7 for axis,edge in [(0,bounds[0]),(0,bounds[2]),(1,bounds[1]),(1,bounds[3])]):continue
        aa=Vector(((a[0]-144.9671)*87939,(a[1]+37.8183)*111320,0));bb=Vector(((b[0]-144.9671)*87939,(b[1]+37.8183)*111320,0));delta=bb-aa
        if delta.length<.05:continue
        normal=Vector((-delta.y,delta.x,0)).normalized()*.45;base=len(bv)
        for z in (.10,.46):
            bv.extend([(p.x,p.y,z) for p in (aa-normal,bb-normal,bb+normal,aa+normal)])
        bf.extend([tuple(base+i for i in face) for face in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]]);segments+=1
    mat=bpy.data.materials.new('Authored Yarra bank coping');mat.diffuse_color=(.29,.30,.27,1);mat.use_nodes=True;shader=mat.node_tree.nodes.get('Principled BSDF');shader.inputs['Base Color'].default_value=(.29,.30,.27,1);shader.inputs['Roughness'].default_value=.88
    data=bpy.data.meshes.new(bank_label);data.from_pydata(bv,[],bf);data.materials.append(mat);data.update();obj=bpy.data.objects.new(bank_label,data);ground.objects.link(obj)
    obj['source_url']=river['sourceUrl'];obj['source_license']=river['license'];obj['segment_count']=segments;obj['appearance']='Authored 0.9m coping and flat bank datum trace retained Vicmap water boundary. Actual bank type, vertical profile, railings and present-day condition unverified. Data clip edges excluded.'
    colour_relief('Authored Yarra bank coping',(.21,.23,.22),(.40,.40,.34),2,.015)
    print('Added river boundary segments:',segments)
colour_relief('Authored park grass',(.12,.23,.09),(.23,.32,.14),.035,.015)

# Preserve inventory holes and avoid rendering named promenades as lawn.
park_file=root/'assets/source/environment/city-park-surfaces.json'
if ground and park_file.exists():
    parks=json.loads(park_file.read_text())
    for part in parks['parts']:
        label='Retained open space '+part['id']+'_'+str(part['index'])
        if not bpy.data.objects.get(label):
            data=bpy.data.meshes.new(label);data.from_pydata(part['vertices'],[],part['faces']);data.materials.append(bpy.data.materials[['Authored park grass','Authored stone pavement','Authored neutral urban ground'][part['finish']]]);data.update()
            obj=bpy.data.objects.new(label,data);ground.objects.link(obj);obj['source_url']=parks['source'];obj['source_license']=parks['license'];obj['source_id']=part['id'];obj['inventory_name']=part['name'];obj['plan_area_m2']=part['area'];obj['hole_count']=part['hole_count'];obj['appearance']=parks['limits']
        old=bpy.data.objects.get('Park parcel '+part['id']+'_'+str(part['index']))
        if old:old.hide_render=True;old.hide_viewport=True;old['replacement']=label
    print('Applied retained park surfaces with holes:',len(parks['parts']))

bridge_file=root/'assets/source/environment/city-bridge-surfaces.json'
if ground and bridge_file.exists():
    bridges=json.loads(bridge_file.read_text())
    for part in bridges['parts']:
        label='Vicmap bridge carriageway on survey '+part['survey_id']
        if bpy.data.objects.get(label):continue
        data=bpy.data.meshes.new(label);data.from_pydata(part['vertices'],[],part['faces']);data.materials.append(bpy.data.materials['Authored asphalt']);data.update();obj=bpy.data.objects.new(label,data);ground.objects.link(obj)
        obj['source_url']=bridges['road_source'];obj['survey_source']=bridges['survey_source'];obj['source_license']=bridges['license'];obj['source_id']=part['survey_id'];obj['road_ufis']=','.join(str(i) for i in part['source_ufis']);obj['plan_area_m2']=part['area'];obj['appearance']=bridges['limits']
    print('Applied retained bridge road surfaces:',len(bridges['parts']))

# Procedural daylight supplies a sky gradient for reflections without images.
# This is an authored preview atmosphere, not live Melbourne weather.
world=bpy.context.scene.world
sun=bpy.data.objects.get('Preview sun')
if world and world.use_nodes and sun:
    import math
    nodes=world.node_tree.nodes;links=world.node_tree.links
    sky=nodes.get('Authored procedural daylight sky') or nodes.new('ShaderNodeTexSky');sky.name='Authored procedural daylight sky';sky.sky_type='MULTIPLE_SCATTERING';sky.sun_disc=False
    direction=sun.rotation_euler.to_matrix() @ Vector((0,0,1))
    sky.sun_elevation=math.asin(max(-1,min(1,direction.z)));sky.sun_rotation=math.atan2(direction.y,direction.x);sky.air_density=1;sky.aerosol_density=.7;sky.ozone_density=1
    tone=nodes.get('Authored sky saturation') or nodes.new('ShaderNodeHueSaturation');tone.name='Authored sky saturation';tone.inputs['Saturation'].default_value=.6;links.new(sky.outputs['Color'],tone.inputs['Color'])
    background=nodes.get('Background');links.new(tone.outputs['Color'],background.inputs['Color']);background.inputs['Strength'].default_value=.055
    world['appearance']='Authored procedural daylight atmosphere aligned with the preview sun; illustrative air and aerosol parameters, no live weather or photographic environment map.'
    print('Applied procedural daylight sky')

# Shared organic crown geometry keeps mapped tree instances lightweight.
# Shape is authored; it does not assert surveyed species or canopy dimensions.
tree_objects=[o for o in bpy.data.objects if o.name.startswith('tree_') and o.type=='MESH']
if tree_objects:
    crown=tree_objects[0].data
    if crown.get('authored_detail_version',0)<1:
        import math
        bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=3,radius=1)
        for vertex in bm.verts:
            p=vertex.co;radius=1+.06*math.sin(p.x*6)*math.sin(p.y*5)+.04*math.cos(p.z*7+p.x*3);vertex.co*=radius
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(crown);bm.free();crown.update()
        for polygon in crown.polygons:polygon.use_smooth=True
        crown['authored_detail_version']=1;crown['appearance']='Authored smooth irregular crown; mapped positions retained, canopy dimensions and species appearance unverified'
        for obj in tree_objects:obj['shape']='Authored smooth irregular crown; retained City of Melbourne Urban Forest position; canopy dimensions and species appearance unverified'
        print('Refined shared crown geometry for mapped trees:',len(tree_objects))

path_file=root/'assets/source/environment/city-park-paths.json'
path_label='Retained Vicmap park trails - authored surface'
if ground and path_file.exists() and not bpy.data.objects.get(path_label):
    paths=json.loads(path_file.read_text());mat=bpy.data.materials.get('Authored pale park path') or bpy.data.materials.new('Authored pale park path');mat.diffuse_color=(.40,.38,.30,1);mat.use_nodes=True;shader=mat.node_tree.nodes.get('Principled BSDF');shader.inputs['Base Color'].default_value=(.40,.38,.30,1);shader.inputs['Roughness'].default_value=.95
    data=bpy.data.meshes.new(path_label);data.from_pydata(paths['vertices'],[],paths['faces']);data.materials.append(mat);data.update();obj=bpy.data.objects.new(path_label,data);ground.objects.link(obj)
    obj['source_url']=paths['source'];obj['park_source']=paths['park_source'];obj['source_license']=paths['license'];obj['source_ufis']=','.join(str(i) for i in paths['source_ufis']);obj['trail_feature_count']=len(paths['source_ufis']);obj['plan_area_m2']=paths['area'];obj['appearance']=paths['limits']
    colour_relief('Authored pale park path',(.29,.28,.23),(.48,.45,.35),4,.012)
    print('Added mapped park trails:',len(paths['source_ufis']))

expanded_file=root/'assets/source/environment/city-road-surfaces-expanded.json'
if ground and expanded_file.exists():
    expanded=json.loads(expanded_file.read_text())
    for key,label,material_name,z in [('asphalt','Continuous Vicmap road surface','Authored asphalt',.255),('paving','Continuous authored pavement bands','Authored stone pavement',.20)]:
        obj=bpy.data.objects.get(label)
        if not obj or obj.get('coverage_revision')=='expanded-clipped-20261006':continue
        part=expanded[key];data=bpy.data.meshes.new(label+' expanded coverage');data.from_pydata([(x,y,z) for x,y in part['vertices']],[],part['faces']);data.materials.append(bpy.data.materials[material_name]);data.update()
        bm=bmesh.new();bm.from_mesh(data);tiny=[f for f in bm.faces if f.calc_area()<1e-6]
        if tiny:bmesh.ops.delete(bm,geom=tiny,context='FACES_ONLY')
        bm.normal_update();down=[f for f in bm.faces if f.normal.z<0]
        if down:bmesh.ops.reverse_faces(bm,faces=down)
        bm.to_mesh(data);bm.free();data.update();obj.data=data
        obj['preview_clip_bounds']=expanded['preview_clip_bounds'];obj['coverage_revision']='expanded-clipped-20261006';obj['source_url']=expanded['source'];obj['source_license']=expanded['license'];obj['source_feature_count']=expanded['feature_count'];obj['plan_area_m2']=part['area'];obj['appearance']=expanded['limits']+'; expanded data clipped to survey preview bounds; float-degenerate microfaces omitted'
    print('Expanded retained road coverage applied:',expanded['feature_count'])

expanded_trees_file=root/'assets/source/environment/city-trees-expanded.json'
if expanded_trees_file.exists() and tree_objects:
    inventory=json.loads(expanded_trees_file.read_text());digest=inventory['sourceSha256']
    if bpy.context.scene.get('expanded_tree_inventory_digest')!=digest:
        tc=bpy.data.collections['TREES - mapped locations, authored crowns'];crown=tree_objects[0].data;active_ids=set();tv=[];tf=[];added=0
        for record in inventory['records']:
            source_id=str(record['com_id']);active_ids.add(source_id);label='tree_'+source_id;obj=bpy.data.objects.get(label)
            if not obj:obj=bpy.data.objects.new(label,crown);tc.objects.link(obj);added+=1
            x=(record['longitude']-144.9671)*87939;y=(record['latitude']+37.8183)*111320;size=2.5+(int(source_id)%17)/10
            obj.location=(x,y,5);obj.scale=(size,size*.92,size*1.25);obj.hide_render=False;obj.hide_viewport=False;obj['source_id']=source_id;obj['source_url']=inventory['source'];obj['source_license']=inventory['license'];obj['inventory_revision']=digest;obj['common_name']=record.get('common_name') or '';obj['shape']='Public inventory point; authored crown dimensions and seasonal appearance, current condition unverified'
            base=len(tv);tv.extend([(x+dx*.14,y+dy*.14,z) for z in (.32,4.6) for dx,dy in [(-1,-1),(1,-1),(1,1),(-1,1)]]);tf.extend([tuple(base+i for i in face) for face in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]])
        for obj in tree_objects:
            if str(obj.get('source_id')) not in active_ids:obj.hide_render=True;obj.hide_viewport=True;obj['inventory_status']='Not in expanded export; retained hidden for recovery, condition unverified'
        data=bpy.data.meshes.new('Expanded authored tree trunks');data.from_pydata(tv,[],tf);data.materials.append(bpy.data.materials['Authored tree bark']);data.update();obj=bpy.data.objects.get('Expanded authored tree trunks')
        if obj:obj.data=data
        else:obj=bpy.data.objects.new(data.name,data);tc.objects.link(obj)
        obj['tree_count']=len(active_ids);obj['appearance']='Authored trunk dimensions on public inventory positions; DBH units not inferred';old=bpy.data.objects.get('Authored tree trunks')
        if old:old.hide_render=True;old.hide_viewport=True
        bpy.context.scene['expanded_tree_inventory_digest']=digest;bpy.context.scene['expanded_tree_inventory_count']=len(active_ids)
        print('Expanded public tree inventory applied:',len(active_ids),'new instances:',added)

expanded_parks_file=root/'assets/source/environment/city-park-surfaces-expanded.json'
if ground and expanded_parks_file.exists():
    parks=json.loads(expanded_parks_file.read_text());active_labels=set()
    for part in parks['parts']:
        label='Retained open space '+part['id']+'_'+str(part['index']);active_labels.add(label);obj=bpy.data.objects.get(label)
        if obj and obj.get('inventory_revision')==parks['revision']:continue
        data=bpy.data.meshes.new(label+' expanded coverage');data.from_pydata(part['vertices'],[],part['faces']);data.materials.append(bpy.data.materials[['Authored park grass','Authored stone pavement','Authored neutral urban ground'][part['finish']]]);data.update()
        bm=bmesh.new();bm.from_mesh(data);tiny=[f for f in bm.faces if f.calc_area()<1e-6]
        if tiny:bmesh.ops.delete(bm,geom=tiny,context='FACES_ONLY')
        bm.normal_update();down=[f for f in bm.faces if f.normal.z<0]
        if down:bmesh.ops.reverse_faces(bm,faces=down)
        bm.to_mesh(data);bm.free();data.update()
        if obj:obj.data=data
        else:obj=bpy.data.objects.new(label,data);ground.objects.link(obj)
        obj.hide_render=False;obj.hide_viewport=False;obj['inventory_revision']=parks['revision'];obj['source_url']=parks['source'];obj['source_license']=parks['license'];obj['source_id']=part['id'];obj['inventory_name']=part['name'];obj['plan_area_m2']=part['area'];obj['hole_count']=part['hole_count'];obj['appearance']=parks['limits']+'; clipped to survey preview extent, 1cm precision grid'
    for obj in ground.objects:
        if obj.name.startswith('Retained open space ') and obj.name not in active_labels:obj.hide_render=True;obj.hide_viewport=True
    bpy.context.scene['expanded_park_parcel_count']=len(active_labels)
    print('Expanded retained park surfaces applied:',len(active_labels))

expanded_paths_file=root/'assets/source/environment/city-park-paths-expanded.json'
if ground and expanded_paths_file.exists():
    paths=json.loads(expanded_paths_file.read_text());obj=bpy.data.objects.get('Retained Vicmap park trails - authored surface')
    if obj and obj.get('coverage_revision')!=paths['revision']:
        data=bpy.data.meshes.new('Expanded retained park trails');data.from_pydata(paths['vertices'],[],paths['faces']);data.materials.append(bpy.data.materials['Authored pale park path']);data.update()
        bm=bmesh.new();bm.from_mesh(data);tiny=[f for f in bm.faces if f.calc_area()<1e-6]
        if tiny:bmesh.ops.delete(bm,geom=tiny,context='FACES_ONLY')
        bm.normal_update();down=[f for f in bm.faces if f.normal.z<0]
        if down:bmesh.ops.reverse_faces(bm,faces=down)
        bm.to_mesh(data);bm.free();data.update();obj.data=data;obj['coverage_revision']=paths['revision'];obj['source_url']=paths['source'];obj['park_source']=paths['park_source'];obj['source_license']=paths['license'];obj['source_ufis']=','.join(str(i) for i in paths['source_ufis']);obj['trail_feature_count']=len(paths['source_ufis']);obj['plan_area_m2']=paths['area'];obj['appearance']=paths['limits']
        print('Expanded retained park trails applied:',len(paths['source_ufis']))

# Restore the excluded Southern Cross roof with authored curvature on its actual
# retained survey footprint. No photograph or photomesh is used as a surface.
southern_file=root/'assets/source/environment/southern-cross-authored-roof.json'
if southern_file.exists() and not bpy.data.objects.get('Southern Cross - authored dune roof'):
    roof=json.loads(southern_file.read_text());mat=bpy.data.materials.new('Authored Southern Cross zinc');mat.use_nodes=True
    shader=mat.node_tree.nodes.get('Principled BSDF');shader.inputs['Base Color'].default_value=(.38,.42,.43,1);shader.inputs['Metallic'].default_value=.55;shader.inputs['Roughness'].default_value=.48
    mesh=bpy.data.meshes.new('Survey bounded Southern Cross authored waves');mesh.from_pydata(roof['vertices'],[],roof['faces']);mesh.materials.append(mat);mesh.update()
    import bmesh
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);bm.to_mesh(mesh);bm.free();mesh.update()
    obj=bpy.data.objects.new('Southern Cross - authored dune roof',mesh);bpy.data.collections.get('CITY - reference-authored landmarks').objects.link(obj)
    for face in mesh.polygons:face.use_smooth=True
    obj['source_id']=roof['source_id'];obj['source_url']=roof['url'];obj['source_license']=roof['license'];obj['architect_reference']=roof['architect_reference'];obj['limits']=roof['limits'];obj['plan_area_m2']=roof['plan_area_m2']
    colour_relief(mat.name,(.30,.34,.35),(.46,.49,.48),.28,.008)
    print('Applied authored Southern Cross dune roof on retained footprint 3296')

seams_file=root/'assets/source/environment/southern-cross-authored-seams.json'
if seams_file.exists() and not bpy.data.objects.get('Southern Cross - authored standing seams'):
    seams=json.loads(seams_file.read_text());roof_obj=bpy.data.objects.get('Southern Cross - authored dune roof')
    if roof_obj:
        curve=bpy.data.curves.new('Southern Cross curved standing seams','CURVE');curve.dimensions='3D';curve.bevel_depth=.025;curve.bevel_resolution=0;curve.resolution_u=1
        for line in seams['lines']:
            spline=curve.splines.new('POLY');spline.points.add(len(line)-1)
            for point,position in zip(spline.points,line):
                x,y,z=position;hit,location,normal,index=roof_obj.ray_cast(Vector((x,y,100)),Vector((0,0,-1)))
                point.co=(x,y,location.z+.032 if hit else z,1)
        mat=bpy.data.materials.new('Authored Southern Cross seam metal');mat.use_nodes=True;shader=mat.node_tree.nodes.get('Principled BSDF');shader.inputs['Base Color'].default_value=(.19,.23,.24,1);shader.inputs['Metallic'].default_value=.65;shader.inputs['Roughness'].default_value=.5;curve.materials.append(mat)
        obj=bpy.data.objects.new('Southern Cross - authored standing seams',curve);roof_obj.users_collection[0].objects.link(obj);obj['source_id']=seams['source_id'];obj['source_url']=seams['source_url'];obj['architect_reference']=seams['architect_reference'];obj['limits']=seams['limits'];obj['seam_guides']=len(seams['lines'])
        print('Applied authored Southern Cross standing seams:',len(seams['lines']))

support_file=root/'assets/source/environment/southern-cross-authored-supports.json'
if support_file.exists() and not bpy.data.objects.get('Southern Cross - authored Y supports'):
    support=json.loads(support_file.read_text());roof_obj=bpy.data.objects.get('Southern Cross - authored dune roof')
    if roof_obj:
        sv=[];sf=[]
        def support_tube(a,b,radius):
            a=Vector(a);b=Vector(b);axis=(b-a).normalized();side=axis.cross(Vector((0,0,1)))
            if side.length<.001:side=Vector((1,0,0))
            side.normalize();other=axis.cross(side).normalized();start=len(sv)
            for end in (a,b):
                for i in range(8):sv.append(tuple(end+radius*(side*math.cos(i*math.tau/8)+other*math.sin(i*math.tau/8))))
            sf.extend([(start+i,start+(i+1)%8,start+8+(i+1)%8,start+8+i) for i in range(8)]);sf.append(tuple(start+i for i in reversed(range(8))));sf.append(tuple(start+8+i for i in range(8)))
        for item in support['supports']:
            x,y,z=item['base'];neck=(x,y,5.5);support_tube((x,y,z),neck,.42)
            for fx,fy in item['forks']:
                hit,location,normal,index=roof_obj.ray_cast(Vector((fx,fy,100)),Vector((0,0,-1)));assert hit,'Support branch outside roof'
                support_tube(neck,(fx,fy,location.z-.18),.24)
        mesh=bpy.data.meshes.new('Authored Southern Cross Y steel');mesh.from_pydata(sv,[],sf);mesh.materials.append(bpy.data.materials['Authored Southern Cross seam metal']);mesh.update();obj=bpy.data.objects.new('Southern Cross - authored Y supports',mesh);roof_obj.users_collection[0].objects.link(obj)
        obj['support_count']=len(support['supports']);obj['limits']=support['limits'];obj['source_id']=support['source_id'];obj['rail_source']=support['rail_source'];obj['rail_ufis']=','.join(str(i) for i in support['rail_ufis']);obj['architect_reference']=support['architect_reference']
        if not roof_obj.modifiers.get('Authored thin roof edge'):
            modifier=roof_obj.modifiers.new('Authored thin roof edge','SOLIDIFY');modifier.thickness=.18;modifier.offset=-1
        print('Applied authored Southern Cross Y supports:',len(support['supports']))

rooflight_file=root/'assets/source/environment/southern-cross-authored-rooflights.json'
roof_obj=bpy.data.objects.get('Southern Cross - authored dune roof')
if rooflight_file.exists() and roof_obj and roof_obj.get('rooflight_revision')!='authored-bands-v1':
    lights=json.loads(rooflight_file.read_text());mat=bpy.data.materials.get('Authored Southern Cross diffusing ETFE') or bpy.data.materials.new('Authored Southern Cross diffusing ETFE');mat.use_nodes=True
    shader=mat.node_tree.nodes.get('Principled BSDF');shader.inputs['Base Color'].default_value=(.65,.73,.74,1);shader.inputs['Roughness'].default_value=.42;shader.inputs['Transmission Weight'].default_value=.65;shader.inputs['IOR'].default_value=1.4
    mesh=bpy.data.meshes.new('Southern Cross roof with authored skylight bands');mesh.from_pydata(lights['vertices'],[],lights['faces']);mesh.materials.append(bpy.data.materials['Authored Southern Cross zinc']);mesh.materials.append(mat);mesh.update()
    for face,material in zip(mesh.polygons,lights['materials']):face.material_index=material;face.use_smooth=True
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);tiny=[f for f in bm.faces if f.calc_area()<1e-8]
    if tiny:bmesh.ops.delete(bm,geom=tiny,context='FACES_ONLY')
    bm.normal_update();down=[f for f in bm.faces if f.normal.z<0]
    if down:bmesh.ops.reverse_faces(bm,faces=down)
    bm.to_mesh(mesh);bm.free();mesh.update();roof_obj.data=mesh;roof_obj['rooflight_revision']='authored-bands-v1';roof_obj['rooflight_plan_area_m2']=lights['rooflight_plan_area_m2'];roof_obj['rooflight_limits']=lights['limits'];roof_obj['rooflight_reference']=lights['reference']
    print('Applied separate authored ETFE rooflight faces:',len(mesh.polygons))

facade_script=root/'scripts/blender/refine_city_facades.py'
if facade_script.exists():exec(compile(facade_script.read_text(),str(facade_script),'exec'))

tower_script=root/'scripts/blender/refine_city_tower_materials.py'
if tower_script.exists():exec(compile(tower_script.read_text(),str(tower_script),'exec'))

trackbed_file=root/'assets/source/environment/city-trackbeds.json'
if trackbed_file.exists() and not bpy.data.objects.get('Continuous authored railway ballast beds'):
    bed=json.loads(trackbed_file.read_text());mesh=bpy.data.meshes.new('Unioned ordinary railway trackbeds');mesh.from_pydata(bed['vertices'],[],bed['faces']);mesh.materials.append(bpy.data.materials['Authored ballast']);mesh.update();obj=bpy.data.objects.new('Continuous authored railway ballast beds',mesh);ground.objects.link(obj);obj['source_url']=bed['source_url'];obj['source_ufis']=','.join(str(i) for i in bed['source_ufis']);obj['limits']=bed['limits'];obj['area_m2']=bed['area_m2']
    assert all(p.normal.z>0 and p.area>0 for p in mesh.polygons)
    old=bpy.data.objects.get('Railway ballast - authored level on Vicmap alignment')
    if old:old.hide_render=True;old.hide_set(True);old['replacement']=obj.name
    colour_relief('Authored ballast',(.13,.12,.105),(.28,.27,.24),6,.025)
    print('VERIFIED continuous ordinary railway ballast beds:',len(mesh.polygons))

# Eastern platform topology from PTV's schematic. Federation Square covers this
# precinct; do not invent exposed island canopies from the main-station pattern.
east_label='Flinders authored eastern platforms 12-13 - schematic'
if anchor and not bpy.data.objects.get(east_label):
    ev=[];ef=[];em=[]
    def east_box(x,y,z,sx,sy,sz,material):
        start=len(ev);ev.extend([(x+dx*sx/2,y+dy*sy/2,z+dz*sz/2) for dz in (-1,1) for dx,dy in [(-1,-1),(1,-1),(1,1),(-1,1)]]);ef.extend([tuple(start+i for i in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]]);em.extend([material]*6)
    east_box(97.5,-79,.95,175,5.2,1.1,0)
    for side in (-1,1):east_box(97.5,-79+side*2.38,1.515,175,.20,.03,1)
    mesh=bpy.data.meshes.new(east_label);mesh.from_pydata(ev,[],ef);mesh.materials.append(bpy.data.materials['Authored station platform paving']);mesh.materials.append(bpy.data.materials['Authored platform safety edge']);mesh.update()
    for face,index in zip(mesh.polygons,em):face.material_index=index
    obj=bpy.data.objects.new(east_label,mesh);anchor.users_collection[0].objects.link(obj);obj.parent=anchor;obj.location.z=-3.5;obj['source_url']='https://www.ptv.vic.gov.au/assets/DTP1124-FlindersStreetStation-Precinct-Map_Degraves-Subway_web_Stage-1_v3.pdf';obj['platforms']='12,13';obj['limits']='Schematic paired eastern deck beyond Swanston Street, no exposed canopy. Extent, width, height and platform pairing authored; schematic not a survey. Retained rail alignments here classified underground. Exact rail clearances and Federation Square support geometry unresolved.'
    assert all(p.area>0 for p in mesh.polygons)
    print('VERIFIED authored eastern platform schematic added')

federation_script=root/'scripts/blender/refine_federation_square.py'
if federation_script.exists():exec(compile(federation_script.read_text(),str(federation_script),'exec'))

kerb_script=root/'scripts/blender/refine_city_kerbs.py'
if kerb_script.exists():exec(compile(kerb_script.read_text(),str(kerb_script),'exec'))

gable_script=root/'scripts/blender/refine_federation_gables.py'
if gable_script.exists():exec(compile(gable_script.read_text(),str(gable_script),'exec'))

plaza_script=root/'scripts/blender/refine_federation_plaza.py'
if plaza_script.exists():exec(compile(plaza_script.read_text(),str(plaza_script),'exec'))

trim_script=root/'scripts/blender/refine_federation_roof_trim.py'
if trim_script.exists():exec(compile(trim_script.read_text(),str(trim_script),'exec'))

masonry_script=root/'scripts/blender/refine_city_masonry_materials.py'
if masonry_script.exists():exec(compile(masonry_script.read_text(),str(masonry_script),'exec'))

feature_lights_script=root/'scripts/blender/refine_city_feature_lights.py'
if feature_lights_script.exists():exec(compile(feature_lights_script.read_text(),str(feature_lights_script),'exec'))

princes_script=root/'scripts/blender/refine_princes_bridge.py'
if princes_script.exists():exec(compile(princes_script.read_text(),str(princes_script),'exec'))

date_palm_script=root/'scripts/blender/refine_city_date_palms.py'
if date_palm_script.exists():exec(compile(date_palm_script.read_text(),str(date_palm_script),'exec'))

crown_script=root/'scripts/blender/refine_city_tree_crowns.py'
if crown_script.exists():exec(compile(crown_script.read_text(),str(crown_script),'exec'))

st_pauls_script=root/'scripts/blender/refine_st_pauls_spires.py'
if st_pauls_script.exists():exec(compile(st_pauls_script.read_text(),str(st_pauls_script),'exec'))

st_pauls_masonry=root/'scripts/blender/refine_st_pauls_masonry.py'
if st_pauls_masonry.exists():exec(compile(st_pauls_masonry.read_text(),str(st_pauls_masonry),'exec'))

st_pauls_roof=root/'scripts/blender/refine_st_pauls_roof.py'
if st_pauls_roof.exists():exec(compile(st_pauls_roof.read_text(),str(st_pauls_roof),'exec'))

flinders_ballast=root/'scripts/blender/refine_flinders_ballast.py'
if flinders_ballast.exists():exec(compile(flinders_ballast.read_text(),str(flinders_ballast),'exec'))

flinders_trim=root/'scripts/blender/refine_flinders_canopy_trim.py'
if flinders_trim.exists():exec(compile(flinders_trim.read_text(),str(flinders_trim),'exec'))

flinders_main_roof=root/'scripts/blender/refine_flinders_main_roof.py'
if flinders_main_roof.exists():exec(compile(flinders_main_roof.read_text(),str(flinders_main_roof),'exec'))

southbank_paving=root/'scripts/blender/refine_southbank_paving.py'
if southbank_paving.exists():exec(compile(southbank_paving.read_text(),str(southbank_paving),'exec'))

cbd_pavement=root/'scripts/blender/refine_cbd_pavement.py'
if cbd_pavement.exists():exec(compile(cbd_pavement.read_text(),str(cbd_pavement),'exec'))

arts_spire=root/'scripts/blender/refine_arts_centre_spire.py'
if arts_spire.exists():exec(compile(arts_spire.read_text(),str(arts_spire),'exec'))

arts_theatre=root/'scripts/blender/refine_arts_centre_theatre.py'
if arts_theatre.exists():exec(compile(arts_theatre.read_text(),str(arts_theatre),'exec'))

hamer_hall=root/'scripts/blender/refine_hamer_hall.py'
if hamer_hall.exists():exec(compile(hamer_hall.read_text(),str(hamer_hall),'exec'))

hamer_bays=root/'scripts/blender/refine_hamer_hall_bays.py'
if hamer_bays.exists():exec(compile(hamer_bays.read_text(),str(hamer_bays),'exec'))

city_seats=root/'scripts/blender/refine_city_seats.py'
if city_seats.exists():exec(compile(city_seats.read_text(),str(city_seats),'exec'))

city_edges=root/'scripts/blender/refine_city_edge_light.py'
if city_edges.exists():exec(compile(city_edges.read_text(),str(city_edges),'exec'))

qvm_roofs=root/'scripts/blender/refine_qvm_roofs.py'
if qvm_roofs.exists():exec(compile(qvm_roofs.read_text(),str(qvm_roofs),'exec'))

qvm_open=root/'scripts/blender/refine_qvm_open_sheds.py'
if qvm_open.exists():exec(compile(qvm_open.read_text(),str(qvm_open),'exec'))

qvm_finish=root/'scripts/blender/refine_qvm_roof_finish.py'
if qvm_finish.exists():exec(compile(qvm_finish.read_text(),str(qvm_finish),'exec'))

qvm_south=root/'scripts/blender/refine_qvm_south.py'
if qvm_south.exists():exec(compile(qvm_south.read_text(),str(qvm_south),'exec'))

qvm_lanterns=root/'scripts/blender/refine_qvm_lanterns.py'
if qvm_lanterns.exists():exec(compile(qvm_lanterns.read_text(),str(qvm_lanterns),'exec'))

survey_gables=root/'scripts/blender/refine_survey_gables.py'
if survey_gables.exists():exec(compile(survey_gables.read_text(),str(survey_gables),'exec'))

survey_hips=root/'scripts/blender/refine_survey_hips.py'
if survey_hips.exists():exec(compile(survey_hips.read_text(),str(survey_hips),'exec'))

parking_paint=root/'scripts/blender/refine_parking_markings.py'
if parking_paint.exists():exec(compile(parking_paint.read_text(),str(parking_paint),'exec'))

city_daylight=root/'scripts/blender/refine_city_daylight.py'
if city_daylight.exists():exec(compile(city_daylight.read_text(),str(city_daylight),'exec'))

eureka_crown=root/'scripts/blender/refine_eureka_crown.py'
if eureka_crown.exists():exec(compile(eureka_crown.read_text(),str(eureka_crown),'exec'))

princes_arches=root/'scripts/blender/refine_princes_arches.py'
if princes_arches.exists():exec(compile(princes_arches.read_text(),str(princes_arches),'exec'))

facade_consistency=root/'scripts/blender/refine_facade_group_colours.py'
if facade_consistency.exists():exec(compile(facade_consistency.read_text(),str(facade_consistency),'exec'))

expanded_rails=root/'scripts/blender/refine_expanded_rails.py'
if expanded_rails.exists():exec(compile(expanded_rails.read_text(),str(expanded_rails),'exec'))

expanded_sleepers=root/'scripts/blender/refine_expanded_sleepers.py'
if expanded_sleepers.exists():exec(compile(expanded_sleepers.read_text(),str(expanded_sleepers),'exec'))

sleeper_union=root/'scripts/blender/refine_sleeper_junction_union.py'
if sleeper_union.exists():exec(compile(sleeper_union.read_text(),str(sleeper_union),'exec'))

rialto_colours=root/'scripts/blender/refine_rialto_colour_consistency.py'
if rialto_colours.exists():exec(compile(rialto_colours.read_text(),str(rialto_colours),'exec'))

upper_tower_colours=root/'scripts/blender/refine_upper_tower_consistency.py'
if upper_tower_colours.exists():exec(compile(upper_tower_colours.read_text(),str(upper_tower_colours),'exec'))

steel_seats=root/'scripts/blender/refine_city_steel_seats.py'
if steel_seats.exists():exec(compile(steel_seats.read_text(),str(steel_seats),'exec'))

bourke_paving=root/'scripts/blender/refine_bourke_paving.py'
if bourke_paving.exists():exec(compile(bourke_paving.read_text(),str(bourke_paving),'exec'))

hardware_paving=root/'scripts/blender/refine_hardware_paving.py'
if hardware_paving.exists():exec(compile(hardware_paving.read_text(),str(hardware_paving),'exec'))

roof_tones=root/'scripts/blender/refine_generic_roof_tones.py'
if roof_tones.exists():exec(compile(roof_tones.read_text(),str(roof_tones),'exec'))

crown_detail=root/'scripts/blender/refine_tree_crown_detail.py'
if crown_detail.exists():exec(compile(crown_detail.read_text(),str(crown_detail),'exec'))

window_tones=root/'scripts/blender/refine_window_tones.py'
if window_tones.exists():exec(compile(window_tones.read_text(),str(window_tones),'exec'))

flinders_palette=root/'scripts/blender/refine_flinders_restored_palette.py'
if flinders_palette.exists():exec(compile(flinders_palette.read_text(),str(flinders_palette),'exec'))

flinders_masonry=root/'scripts/blender/refine_flinders_masonry.py'
if flinders_masonry.exists():exec(compile(flinders_masonry.read_text(),str(flinders_masonry),'exec'))

flinders_arch_glass=root/'scripts/blender/refine_flinders_arch_glazing.py'
if flinders_arch_glass.exists():exec(compile(flinders_arch_glass.read_text(),str(flinders_arch_glass),'exec'))

civic_paving=root/'scripts/blender/refine_civic_surfaces.py'
if civic_paving.exists():exec(compile(civic_paving.read_text(),str(civic_paving),'exec'))

stadium_roof=root/'scripts/blender/refine_stadium_roof.py'
if stadium_roof.exists():exec(compile(stadium_roof.read_text(),str(stadium_roof),'exec'))
stadium_cleanup=root/'scripts/blender/refine_stadium_roof_cleanup.py'
if stadium_cleanup.exists():exec(compile(stadium_cleanup.read_text(),str(stadium_cleanup),'exec'))

stadium_supports=root/'scripts/blender/refine_stadium_panel_supports.py'
if stadium_supports.exists():exec(compile(stadium_supports.read_text(),str(stadium_supports),'exec'))

# Subsequent authored detail passes; each owns its scene revision marker.
for detail_script in ["refine_ballast_grain.py", "refine_flinders_platform_ends.py", "refine_cbd_lane_guides.py", "refine_qvm_carpark_surface.py", "refine_flat_roof_parapets.py", "refine_short_lowrise_facades.py", "refine_city_colour_separation.py", "refine_rail_precinct_ground.py", "refine_pedestrian_area_surfaces.py", "refine_town_hall_materials_tower.py", "refine_town_hall_slate_roof.py", "refine_town_hall_roof_junctions.py", "refine_town_hall_gable.py", "refine_town_hall_facade_relief.py", "refine_cbd_signal_hardware.py", "refine_tree_fine_clusters.py"]:
    detail_path=root/"scripts/blender"/detail_script
    if detail_path.exists():exec(compile(detail_path.read_text(),str(detail_path),"exec"))

stone_grain=root/'scripts/blender/refine_bluestone_grain.py'
if stone_grain.exists():exec(compile(stone_grain.read_text(),str(stone_grain),'exec'))

tree_cluster_shading=root/'scripts/blender/refine_tree_cluster_shading.py'
if tree_cluster_shading.exists():exec(compile(tree_cluster_shading.read_text(),str(tree_cluster_shading),'exec'))

city_square=root/'scripts/blender/refine_city_square_surfaces.py'
if city_square.exists():exec(compile(city_square.read_text(),str(city_square),'exec'))

city_square_gardens=root/'scripts/blender/refine_city_square_gardens.py'
if city_square_gardens.exists():exec(compile(city_square_gardens.read_text(),str(city_square_gardens),'exec'))

city_square_terraces=root/'scripts/blender/refine_city_square_terraces.py'
if city_square_terraces.exists():exec(compile(city_square_terraces.read_text(),str(city_square_terraces),'exec'))

city_square_canopy=root/'scripts/blender/refine_city_square_canopy.py'
if city_square_canopy.exists():exec(compile(city_square_canopy.read_text(),str(city_square_canopy),'exec'))

city_square_portal=root/'scripts/blender/refine_city_square_portal.py'
if city_square_portal.exists():exec(compile(city_square_portal.read_text(),str(city_square_portal),'exec'))

city_square_guards=root/'scripts/blender/refine_city_square_guards.py'
if city_square_guards.exists():exec(compile(city_square_guards.read_text(),str(city_square_guards),'exec'))

westin_facade=root/'scripts/blender/refine_westin_facade.py'
if westin_facade.exists():exec(compile(westin_facade.read_text(),str(westin_facade),'exec'))

westin_relief=root/'scripts/blender/refine_westin_facade_relief.py'
if westin_relief.exists():exec(compile(westin_relief.read_text(),str(westin_relief),'exec'))

westin_finishes=root/'scripts/blender/refine_westin_section_finishes.py'
if westin_finishes.exists():exec(compile(westin_finishes.read_text(),str(westin_finishes),'exec'))

westin_mansard=root/'scripts/blender/refine_westin_mansard_finish.py'
if westin_mansard.exists():exec(compile(westin_mansard.read_text(),str(westin_mansard),'exec'))

westin_mansard_geometry=root/'scripts/blender/refine_westin_mansard_geometry.py'
if westin_mansard_geometry.exists():exec(compile(westin_mansard_geometry.read_text(),str(westin_mansard_geometry),'exec'))

flinders_ground_margins=root/'scripts/blender/refine_flinders_ground_margins.py'
if flinders_ground_margins.exists():exec(compile(flinders_ground_margins.read_text(),str(flinders_ground_margins),'exec'))

flinders_neighbours=root/'scripts/blender/refine_flinders_neighbours.py'
if flinders_neighbours.exists() and not all(bpy.data.objects.get('survey_'+b['id']) for b in json.loads((root/'assets/source/environment/flinders-neighbour-restoration.json').read_text())['restored']):exec(compile(flinders_neighbours.read_text(),str(flinders_neighbours),'exec'))

flinders_scan=root/'scripts/blender/refine_flinders_photomesh.py'
if flinders_scan.exists() and (root/'assets/source/environment/flinders-photomesh-2020.obj').exists():exec(compile(flinders_scan.read_text(),str(flinders_scan),'exec'))

flinders_scan_roofs=root/'scripts/blender/refine_flinders_scan_roofs.py'
if flinders_scan_roofs.exists() and bpy.data.objects.get('Flinders station - municipal 2020 scan, authored colours'):exec(compile(flinders_scan_roofs.read_text(),str(flinders_scan_roofs),'exec'))

flinders_canopy_surfaces=root/'scripts/blender/refine_flinders_canopy_surfaces.py'
if flinders_canopy_surfaces.exists() and bpy.data.objects.get('Flinders station - municipal 2020 scan, authored colours'):exec(compile(flinders_canopy_surfaces.read_text(),str(flinders_canopy_surfaces),'exec'))

flinders_canopy_panels=root/'scripts/blender/refine_flinders_canopy_panels.py'
if flinders_canopy_panels.exists() and bpy.data.objects.get('Flinders captured canopy fitted metal skins'):exec(compile(flinders_canopy_panels.read_text(),str(flinders_canopy_panels),'exec'))

flinders_canopy_overlaps=root/'scripts/blender/refine_flinders_canopy_overlaps.py'
if flinders_canopy_overlaps.exists() and bpy.data.objects.get('Flinders scan-fitted clean canopy panels and eaves'):exec(compile(flinders_canopy_overlaps.read_text(),str(flinders_canopy_overlaps),'exec'))
flinders_canopy_supports=root/'scripts/blender/refine_flinders_canopy_supports.py'
if flinders_canopy_supports.exists() and bpy.data.objects.get('Flinders scan-fitted clean canopy panels and eaves'):exec(compile(flinders_canopy_supports.read_text(),str(flinders_canopy_supports),'exec'))

flinders_scan_facades=root/'scripts/blender/refine_flinders_scan_facades.py'
if flinders_scan_facades.exists() and bpy.data.objects.get('Flinders station - municipal 2020 scan, authored colours'):exec(compile(flinders_scan_facades.read_text(),str(flinders_scan_facades),'exec'))

