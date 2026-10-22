"""Create an evidence-labelled corridor workspace; export only publishable assets.
Run with Blender --background --factory-startup --python this_script.
Re-export edited scene: Blender --background assets/source/environment/corridor-layout.blend
 --python scripts/blender/build_corridor_layout.py -- --export-only
"""
import bpy
import json
import os
import sys
import hashlib
from mathutils import Vector, geometry
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
SOURCE = os.path.join(ROOT, 'assets/source/environment/corridor-layout.blend')
OUTPUT = os.path.join(ROOT, 'public/models/environment/corridor-frontage.glb')

def collection(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c

def move(obj, c):
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    c.objects.link(obj)

if '--export-only' not in sys.argv:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1
    scene['target_era'] = 'Present-day Melbourne (2026); historical geometry requires current-condition verification'
    scene['game_origin_lonlat'] = [144.9671, -37.8183]
    scene['coordinate_frame'] = 'Blender X east, Y north, Z up; GLB X east, Y up, Z south; metres'
    scene['vertical_datum'] = 'Prepared relative game elevations; not AHD or surveyed rail elevation'
    survey = collection('REFERENCE - historical survey envelopes - do not publish')
    published = collection('PUBLISH - verified frontage')
    path = os.path.join(ROOT, 'public/data/buildings.json')
    raw = open(path, 'rb').read()
    data = json.loads(raw)
    scene['survey_sha256'] = hashlib.sha256(raw).hexdigest()
    mat = bpy.data.materials.new('Survey reference - neutral massing')
    mat.diffuse_color = (.42, .48, .52, 1)
    for b in data['buildings']:
        ring = b['ring'][:]
        if ring[0] == ring[-1]: ring.pop()
        # Include complete sections intersecting the bounded western corridor.
        if len(ring) < 3 or not any(-1850 <= x <= 200 and -550 <= z <= 350 for x,z in ring): continue
        n = len(ring)
        top = b['base'] + b['height']
        base = top - min(.6, b['height']) if b.get('kind') in ('Bridge', 'Jetty') else b['base']
        verts = [(x,-z,y) for y in (base,top) for x,z in ring]
        points = [Vector((x,-z,0)) for x,z in ring]
        faces = [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
        for tri in geometry.tessellate_polygon([points]):
            ids = [p if isinstance(p, int) else min(range(n), key=lambda i:(points[i]-p).length_squared) for p in tri]
            faces.append(tuple(i+n for i in ids))
            faces.append(tuple(reversed(ids)))
        mesh = bpy.data.meshes.new('survey_' + b['id'])
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        obj = bpy.data.objects.new('survey_' + b['id'], mesh)
        survey.objects.link(obj)
        mesh.materials.append(mat)
        obj['source_object_id'] = b['id']
        obj['source_url'] = data['url']
        obj['source_license'] = data['license']
        obj['source_dataset'] = data['source']
        obj['currency'] = 'Dataset catalogue: May 2023; retained records may carry older capture dates. Not verified for 2026.'
        obj['fidelity'] = 'Measured horizontal envelope and prepared relative height; no facade evidence'
    bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT, 'public/models/environment/viaduct-frontage.glb'))
    for obj in list(bpy.context.selected_objects): move(obj, published)
    # Keep reference shells separate from publishable objects, including overlap.
    survey.hide_render = True
    scene['reference_section_count'] = len(survey.objects)
    bpy.ops.wm.save_as_mainfile(filepath=SOURCE)

published = bpy.data.collections.get('PUBLISH - verified frontage')
if not published or not published.all_objects:
    raise RuntimeError('Missing publish collection; no asset exported')
bpy.ops.object.select_all(action='DESELECT')
for obj in published.all_objects:
    obj.hide_set(False)
    obj.select_set(True)
bpy.context.view_layer.objects.active = next(iter(published.all_objects))
bpy.ops.export_scene.gltf(filepath=OUTPUT, export_format='GLB', use_selection=True,
    export_yup=True, export_extras=True, export_animations=False, export_lights=False, export_cameras=False)
print('Exported corridor frontage:', OUTPUT)
