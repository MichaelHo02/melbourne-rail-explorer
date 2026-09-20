"""Build the surveyed Flinders viaduct frontage pair as cleaned Blender solids.

Run from the repository root:
  /Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup \
    --python scripts/blender/build_viaduct_frontage.py

The City of Melbourne section polygons and their prepared game elevations are
the only dimensional inputs. Boolean union removes coincident section walls
and hidden internal faces before facade articulation is added.
"""
import bpy
import bmesh
import json
import math
import os
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
DATA_PATH = os.path.join(ROOT, 'public/data/buildings.json')
OUTPUT = os.path.join(ROOT, 'public/models/environment/viaduct-frontage.glb')
SOURCE = os.path.join(ROOT, 'assets/source/environment/viaduct-frontage.blend')
MANIFEST = os.path.join(ROOT, 'public/models/environment/viaduct-frontage.json')

STRUCTURES = {
    '817607': {'objectIds': ['17612', '17613', '17614', '17615', '17616'], 'address': '15–33 William Street', 'floors2014': 25,
               'photo': 'https://www.commercialrealestate.com.au/property/15-william-street-melbourne-vic-3000-14849344',
               'style': 'Reflective blue-grey curtain wall with slender projecting silver vertical fins and fine floor transoms; dark glazed podium.'},
    '806929': {'objectIds': ['25125', '25126', '25127', '25128', '25129', '25130', '25131', '25132'], 'address': '452–470 Flinders Street', 'floors2014': 23,
               'photo': 'https://www.cushmanwakefield.com/en/australia/news/2020/09/deka-immobilien-acquires-melbourne-office-tower-for-%24454-million',
               'style': 'Deep blue reflective curtain wall with prominent pale structural framing and a regular rectangular grid.'},
}
# Reproducibility guard: these are the actual prepared source ring bounds.
# They are narrower than the related photomesh exclusion hulls by design.
EXPECTED_BOUNDS = {
    '817607': [-733.9, 57.3, -658.1, 159.7],
    '806929': [-784.8, 85.2, -718.9, 178.1],
}
ATTRIBUTION = 'City of Melbourne, 2023 Building Footprints, CC BY 4.0'
SOURCE_URL = 'https://data.melbourne.vic.gov.au/explore/dataset/2023-building-footprints/'
ORIGIN = [144.9671, -37.8183]


def reset_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.materials:
        bpy.data.materials.remove(block)


def game_to_blender(x, y, z):
    # Projected game frame is X east, Y up, Z south. Blender is Z up.
    return (x, -z, y)


def material(name, color, roughness=0.86, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Roughness'].default_value = roughness
    shader.inputs['Metallic'].default_value = metallic
    if 'Coat Weight' in shader.inputs:
        shader.inputs['Coat Weight'].default_value = .18 if metallic > .25 else .06
        shader.inputs['Coat Roughness'].default_value = .18
    return mat


def ring_mesh(name, ring, base, top):
    points = ring[:-1] if math.dist(ring[0], ring[-1]) < 0.01 else ring
    n = len(points)
    verts = [game_to_blender(x, base, z) for x, z in points]
    verts += [game_to_blender(x, top, z) for x, z in points]
    faces = []
    # Use Blender's own polygon tessellator for concave surveyed footprints.
    polygon = [Vector((x, z, 0)) for x, z in points]
    for tri in bpy_extras_tessellate(polygon):
        indices = []
        for j in range(3):
            if isinstance(tri[j], int):
                index = tri[j]
            else:
                index = min(range(n), key=lambda k: (polygon[k] - tri[j]).length_squared)
                if (polygon[index] - tri[j]).length > 1e-4:
                    raise RuntimeError('Footprint tessellation returned an unmatched vertex: ' + name)
            indices.append(index)
        faces.append(tuple(reversed(indices)))
        faces.append(tuple(i + n for i in indices))
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, j + n, i + n))
    mesh = bpy.data.meshes.new(name + '_mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def bpy_extras_tessellate(points):
    # Imported lazily so the script remains usable on Blender's bundled Python.
    from mathutils import geometry
    return geometry.tessellate_polygon([points])


def union_sections(buildings, structure_id, finish_material):
    sections = [b for b in buildings if b['id'] in STRUCTURES[structure_id]['objectIds']]
    expected = STRUCTURES[structure_id]['objectIds']
    if sorted(b['id'] for b in sections) != sorted(expected):
        raise RuntimeError('Missing surveyed building sections for structure ' + structure_id)
    solids = []
    for section in sections:
        solid = ring_mesh('survey_section_' + section['id'], section['ring'], section['base'], section['base'] + section['height'])
        solids.append(solid)
    # Exact solver handles the measured coincident and intersecting floor slabs.
    result = solids[0]
    result.name = 'structure_' + structure_id + '_clean_envelope'
    for index, operand in enumerate(solids[1:], 1):
        bpy.context.view_layer.objects.active = result
        result.select_set(True)
        operand.select_set(False)
        modifier = result.modifiers.new('survey_union_' + str(index), 'BOOLEAN')
        modifier.operation = 'UNION'
        modifier.solver = 'EXACT'
        modifier.object = operand
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        bpy.data.objects.remove(operand, do_unlink=True)
    result.data.materials.clear()
    result.data.materials.append(finish_material[0])
    result.data.materials.append(finish_material[1])
    result.data.materials.append(finish_material[2])
    for polygon in result.data.polygons:
        center_y = sum(result.data.vertices[i].co.z for i in polygon.vertices) / len(polygon.vertices)
        if polygon.normal.z > .95:
            polygon.material_index = 2  # roof cap
        elif center_y < 12:
            polygon.material_index = 1  # dark glazed street podium
        else:
            polygon.material_index = 0  # continuous curtain-wall envelope
    result['source_structure_id'] = structure_id
    result['source_object_ids'] = ','.join(expected)
    result['source_attribution'] = ATTRIBUTION
    result['source_url'] = SOURCE_URL
    result['source_origin_lonlat'] = ORIGIN
    result['game_coordinates'] = 'projected X east, Y elevation, Z south; metres'
    result['section_union'] = True
    return result, sections


def make_mesh_object(name, verts, faces, mat, role):
    if not faces:
        return None
    mesh = bpy.data.meshes.new(name + '_mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj['articulation'] = role
    return obj


def add_box_beam(verts, faces, horizontal, normal, plane, s0, s1, y0, y1, depth, projection):
    """Append a shallow rectangular beam on one surveyed wall plane."""
    c = plane + normal * projection
    corners = [c + horizontal * s0 + Vector((0, 0, y0)),
               c + horizontal * s1 + Vector((0, 0, y0)),
               c + horizontal * s1 + Vector((0, 0, y1)),
               c + horizontal * s0 + Vector((0, 0, y1))]
    back = [p - normal * depth for p in corners]
    start = len(verts)
    verts.extend(tuple(p) for p in corners + back)
    faces.extend([(start, start+1, start+2, start+3), (start+7, start+6, start+5, start+4),
                  (start, start+4, start+5, start+1), (start+1, start+5, start+6, start+2),
                  (start+2, start+6, start+7, start+3), (start+3, start+7, start+4, start)])


def add_facade_detail(envelope, name, glass_material, podium_material, frame_material,
                      fine_frame_material, floor_count, facade_kind):
    """Articulate cleaned survey walls with two photo-derived facade families.

    Bay widths/depths are an authored visual rhythm; the surveyed sections
    alone control placement, roofline, floor bands, and setbacks.
    """
    mesh = envelope.data
    frame_verts, frame_faces = [], []
    fine_verts, fine_faces = [], []
    base_y = min(v.co.z for v in mesh.vertices)
    top_y = max(v.co.z for v in mesh.vertices)
    floor_height = (top_y - base_y) / floor_count
    for face in mesh.polygons:
        normal = face.normal
        if abs(normal.z) > 0.035:  # Blender Z is vertical.
            continue
        coords = [mesh.vertices[i].co for i in face.vertices]
        ys = [p.z for p in coords]
        low, high = min(ys), max(ys)
        if high - low < 2.2:
            continue
        horizontal = Vector((-normal.y, normal.x, 0)).normalized()
        along = [p.dot(horizontal) for p in coords]
        start, end = min(along), max(along)
        width = end - start
        if width < 3.2:
            continue
        # Plane offset contains only the XY location; vertical levels below are absolute.
        plane = Vector((normal.x, normal.y, 0)) * coords[0].dot(normal)
        if facade_kind == 'fins':
            bay = 2.35
            fin_width, fin_depth, frame_step, frame_width = .14, .24, floor_height, .045
        else:
            bay = 8.0
            fin_width, fin_depth, frame_width = .34, .28, .26
            frame_step = floor_height * 3
            frame_width = .26
        count = max(1, math.ceil(width / bay))
        bay_width = width / count
        floor_first = max(0, math.floor((low - base_y) / floor_height))
        floor_last = min(floor_count, math.ceil((high - base_y) / floor_height))
        for col in range(count):
            cell_a = start + width * col / count
            cell_b = start + width * (col + 1) / count
            # Long vertical fins on William; heavier vertical frame at Flinders.
            if facade_kind == 'fins':
                add_box_beam(frame_verts, frame_faces, horizontal, normal, plane,
                             cell_a + bay_width*.5 - fin_width*.5, cell_a + bay_width*.5 + fin_width*.5,
                             max(low, base_y), min(high, top_y), fin_depth, fin_depth)
            elif col % max(1, round(8.0 / bay_width)) == 0:
                add_box_beam(frame_verts, frame_faces, horizontal, normal, plane,
                             cell_a - fin_width*.5, cell_a + fin_width*.5,
                             max(low, base_y), min(high, top_y), fin_depth, fin_depth)
        if facade_kind == 'fins':
            # Fine floor transoms distinguish the curtain wall without imitating reflections.
            for floor in range(floor_first, floor_last + 1):
                y = base_y + floor * floor_height
                if low + .1 < y < high - .1:
                    add_box_beam(frame_verts, frame_faces, horizontal, normal, plane,
                                 start, end, y-frame_width*.5, y+frame_width*.5, .07, .07)
        else:
            # Strong pale grid follows the reference's broad structural frame.
            y = base_y + math.ceil(max(0, (low-base_y)/frame_step)) * frame_step
            while y < high:
                add_box_beam(frame_verts, frame_faces, horizontal, normal, plane,
                             start, end, y-frame_width*.5, y+frame_width*.5, .24, .24)
                y += frame_step
            # Fine curtain-wall subdivisions remain visible inside the deeper frame.
            fine_step = 1.7
            for col in range(count):
                cell_a = start + width * col / count
                cell_b = start + width * (col + 1) / count
                inner_count = max(1, round((cell_b-cell_a) / fine_step))
                for mullion in range(1, inner_count):
                    s = cell_a + (cell_b-cell_a) * mullion / inner_count
                    add_box_beam(fine_verts, fine_faces, horizontal, normal, plane,
                                 s-.025, s+.025, max(low,base_y), min(high,top_y), .075, .105)
            for floor in range(floor_first, floor_last + 1):
                y = base_y + floor * floor_height
                if low + .1 < y < high - .1:
                    add_box_beam(fine_verts, fine_faces, horizontal, normal, plane,
                                 start, end, y-.025, y+.025, .075, .105)
    frame = make_mesh_object(name + ('_vertical_fins_and_transoms' if facade_kind == 'fins' else '_structural_grid'),
                             frame_verts, frame_faces, frame_material,
                             'Photo-derived physically projecting facade framing; spacing is authored.')
    fine = make_mesh_object(name + '_fine_mullions_and_transoms', fine_verts, fine_faces, fine_frame_material,
                            'Photo-derived secondary glazing grid; fine lines sit behind the broad structural frame.')
    if frame:
        frame['envelope_object'] = envelope.name
    if fine:
        fine['envelope_object'] = envelope.name
    return frame, fine


def main():
    reset_scene()
    with open(DATA_PATH, encoding='utf-8') as f:
        data = json.load(f)
    buildings = data['buildings']
    blue_glass = material('blue_grey_reflective_curtain_wall', (0.14, 0.20, 0.22), roughness=0.18, metallic=0.32)
    dark_glass = material('dark_glazed_podium', (0.055, 0.085, 0.09), roughness=0.28, metallic=0.18)
    deep_blue_glass = material('deep_blue_grey_curtain_wall', (0.10, 0.16, 0.21), roughness=0.17, metallic=0.32)
    roof_william = material('william_roof_spandrel', (0.18, 0.20, 0.20), roughness=0.5, metallic=0.12)
    roof_flinders = material('flinders_roof_spandrel', (0.43, 0.45, 0.44), roughness=0.5, metallic=0.1)
    silver_fins = material('anodised_silver_vertical_fins', (0.48, 0.54, 0.57), roughness=0.4, metallic=0.5)
    pale_frame = material('pale_structural_frame', (0.58, 0.60, 0.59), roughness=0.44, metallic=0.18)
    fine_frame = material('fine_curtain_wall_mullions', (0.39, 0.45, 0.47), roughness=0.32, metallic=0.42)
    sources = {}
    for structure_id, finish, roof, glass, frame, facade_kind in (
        ('817607', blue_glass, roof_william, blue_glass, silver_fins, 'fins'),
        ('806929', deep_blue_glass, roof_flinders, deep_blue_glass, pale_frame, 'grid')):
        envelope, sections = union_sections(buildings, structure_id, (finish, dark_glass, roof))
        facade = add_facade_detail(envelope, 'structure_' + structure_id, glass, dark_glass,
                                   frame, fine_frame, STRUCTURES[structure_id]['floors2014'], facade_kind)
        xs = [p[0] for b in sections for p in b['ring']]
        zs = [p[1] for b in sections for p in b['ring']]
        bbox = [round(min(xs), 1), round(min(zs), 1), round(max(xs), 1), round(max(zs), 1)]
        if bbox != EXPECTED_BOUNDS[structure_id]:
            raise RuntimeError('Surveyed ring bounds changed for structure ' + structure_id + ': ' + str(bbox))
        sources[structure_id] = {
            'objectIds': STRUCTURES[structure_id]['objectIds'],
            'sectionCount': len(sections),
            'surveyRingBoundsXZMetres': bbox,
            'verticalRangeMetres': [round(min(b['base'] for b in sections), 3), round(max(b['base'] + b['height'] for b in sections), 3)],
            'verticalDatum': 'base = max(0, footprint_min_elevation - structure_min_elevation) in scripts/prepare-city.mjs; relative game datum, not the 2014 model z or source AHD elevation.',
            'sectionVerticalIntervalsMetres': [
                {'objectId': b['id'], 'base': round(b['base'], 3), 'top': round(b['base'] + b['height'], 3)}
                for b in sorted(sections, key=lambda section: int(section['id']))
            ],
            'union': True,
            'address': STRUCTURES[structure_id]['address'],
            'identityCrossReference': {
                'dataset': 'City of Melbourne Building Outlines 2014',
                'datasetUrl': 'https://discover.data.vic.gov.au/dataset/building-outlines-2014',
                'mccidInt': 110091 if structure_id == '817607' else 103998,
                'floorCount': STRUCTURES[structure_id]['floors2014'],
                'modelHeightMetres': 91.35 if structure_id == '817607' else 89.55,
                'verticalValuesUsedForAsset': False,
            },
            'facadeReference': STRUCTURES[structure_id]['photo'],
            'appearanceNotes': STRUCTURES[structure_id]['style'],
            'facadeObjects': [obj.name for obj in facade if obj],
            'attribution': ATTRIBUTION,
            'sourceUrl': SOURCE_URL,
            'sourceTransform': {'originLonLat': ORIGIN, 'projectedMetresPerDegree': {'longitude': 87939, 'latitude': -111320}, 'gameAxes': 'X east, Y up, Z south', 'units': 'metres'},
            'photomeshMask': {'path': 'src/data/photomesh-foreground.json', 'modified': False, 'purpose': 'Existing broader photographic exclusion; does not define this asset geometry.'},
        }
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    os.makedirs(os.path.dirname(SOURCE), exist_ok=True)
    with open(MANIFEST, 'w', encoding='utf-8') as f:
        json.dump({'asset': 'Flinders viaduct frontage buildings', 'source': 'public/data/buildings.json', 'license': 'CC BY 4.0', 'structures': sources}, f, indent=2)
        f.write('\n')
    bpy.ops.wm.save_as_mainfile(filepath=SOURCE)
    bpy.ops.object.select_all(action='SELECT')
    bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
    bpy.ops.export_scene.gltf(filepath=OUTPUT, export_format='GLB', use_selection=True,
                              export_yup=True, export_animations=False,
                              export_cameras=False, export_lights=False, export_extras=True)
    print('Wrote cleaned viaduct frontage asset:', OUTPUT)


if __name__ == '__main__':
    main()
