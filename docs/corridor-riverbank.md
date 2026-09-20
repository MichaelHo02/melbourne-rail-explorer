# Northbank surface refinement

Reviewed 20 September 2026. Existing City of Melbourne imagery, rather than proposed Greenline renders, informs this bounded pass:

- [Batman Park, What's On Melbourne](https://whatson.melbourne.vic.gov.au/things-to-do/batman-park): official existing-place photograph shows eucalypts, lawn, a narrow path, a low sloping stone river edge and sparse backless benches.
- [Enterprize Park, What's On Melbourne](https://whatson.melbourne.vic.gov.au/things-to-do/enterprize-park): establishes the adjacent park and its Scar Project. The artwork is not reproduced or replaced with invented sculpture.
- [River Park Precinct, Participate Melbourne](https://participate.melbourne.vic.gov.au/greenline/river-park-precinct): describes a future vision whose exact locations remain subject to design and consultation. It is not treated as an as-built furniture or planting survey.
- [Greenline project](https://participate.melbourne.vic.gov.au/greenline): the December 2025 Birrarung Marr Site 1 works lie between Batman Avenue and the eastern edge of Federation Square. That new boardwalk/planting scheme is not transplanted into Batman Park beside this western viaduct.

## Geometry and materials

The existing official open-space parcels and holes remain unchanged. Named lawns get a deterministic authored turf texture with gentle spatial colour variation. Triangulation is subdivided only to support that variation: 434 original lawn triangles become 11,546 triangles, still merged into one draw. Texture coordinates repeat in physical metres; the grass is not an aerial image, land-cover survey or species claim. Existing mapped roads and paths remain above the lawn. No broad park parcel is repaved.

River-wall and coping surfaces reuse the already bundled CC0 Poly Haven paving colour, normal and roughness maps, with UVs generated in segment-local metres before rotation. Their material readiness is included in corridor readiness. Attribution and source dimensions remain in `public/textures/surfaces/sources.json`.

Only eligible north-facing bank segments adjoining the mapped Batman/Enterprise park parcels become low stone revetments. The 17 selected segments slope from the existing path edge at approximately y=-0.82 to a submerged toe at y=-1.85, using the corrected authored water plane y=-1.65. Ground/lawn/path heights are unchanged. Other retaining walls extend below the new water plane rather than floating above it. These vertical dimensions are presentation choices, not surveyed river or flood levels.

Three simple backless benches sit at the inland edge of the existing authored promenade. Placement requires membership in the park parcel, clearance from mapped roads/bridges and at least 65m separation; it is not a mapped furniture inventory. The benches and frames use two merged meshes. No extra decorative railing is placed on the low park bank, consistent with the existing-place photo. No additional lights, external models or photographic textures are introduced.

## Checks and browser targets

TypeScript and whitespace checks accompany the change. A source-coordinate check found 17 eligible sloped segments and three benches around world X -832 to -975, Z 373 to 458. Review the lawn and north riverbank from the surface-viaduct camera, then an oblique bank view to verify the slope meets the path, the water is visible below it, and mapped bridge landings remain clear. The world ground must contain a river hole when lowering the water plane, otherwise its former y=-1 ground would cover the new water surface.
