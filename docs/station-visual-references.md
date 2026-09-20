# Platform and cab reference pass

Reviewed 19 September 2026. Photographs are visual research links, not redistributed image assets. Dimensions and platform arrangements remain authored; this pass is not a station survey.

- [Flinders Street platforms, Marcus Wong](https://railgallery.wongm.com/flinders-street-station/F130_8206.jpg.html): cream scalloped valances, maroon lower columns, cream upper ironwork, crossed canopy bracing, white coping and stone platform faces. Implemented cream/maroon supports, curved brackets, scalloped edging, slatted benches and tactile detail.
- [Southern Cross PIDS, Sennheiser / InSight Systems](https://newsroom.sennheiser.com/platform-delivery-melbournes-major-public-transport-hub-transforms-its-wireless-audio-solutions-with-sennheiser): blue platform numbers, black departure displays, steel pylons, camera/speaker heads, pale metal seats, dark asphalt.
- [Southern Cross platform equipment designer, Grimshaw](https://grimshaw.global/preview/project-pages-under-construction/honeywell-passenger-information-system/): integrated wayfinding, speakers, emergency interfaces and CCTV.
- [Flagstaff refurbished ceiling, Marcus Wong](https://railgallery.wongm.com/melbourne-underground-rail-loop-upgrade-project/F157_1397.jpg.html): pale curved metal panels over a dark structural vault, tiled wall, continuous lighting, metal handrail. Photo shows works in progress; missing panels are not reproduced as a permanent station condition.
- [Melbourne Central platform photograph, 2017](https://commons.wikimedia.org/wiki/File:Melbourne_Central_Station_Platform_2017.jpg): broad island, pale square columns, faceted metallic soffit, dark opposite wall and warm patterned floor tiles.
- [Parliament platform 1, Marcus Wong](https://railgallery.wongm.com/city-loop/F151_3609.jpg.html): blue panelled walls, pale barrel ceiling, suspended black PID, white signs and stainless fittings. Corrected the former orange wall treatment.
- [HCMT public mock-up, Marcus Wong](https://railgallery.wongm.com/hcmt-mockup/): train exterior and public design evidence. The gameplay controls remain simplified cab-inspired instruments; they are not a verified HCMT DMI reproduction. Speed and interlock status reflect the simulation; no decorative fabricated pressure or signalling telemetry is shown.

Shared small details use native geometry and canvas typography: tactile bump patterns, platform coping, slatted seating, bins, information pylons, cameras and handrails. Station display destinations explicitly describe the fictional City Loop training service rather than advertising invented live departures. Public timetable traffic uses the separate provenance in `traffic-data.md`.

This pass uses actual photographic geometry and authored reference-based fittings; no generated image is claimed to depict a surveyed station. Remaining accuracy work includes surveyed platform geometry, concourses/escalators, current notices and newer post-2020 exterior changes.


## 20 September 2026 architectural refinement

The [Southern Cross architect project description, Grimshaw](https://grimshaw.global/projects/rail-and-mass-transit/southern-cross-station/) documents the dune roof and natural ventilation strategy. The authored roof now has continuous longitudinal purlins, closer transverse ribs and branching supports in two directions, giving its underside depth. Light-transmitting roof strips are rendered immediately below the roof skin so the opaque skin does not conceal them. These are simplified visual inserts, not an engineering representation of the roof or its ventilation system. The supports occupy the back of the playable platform, outside the train and main walking band.

Flagstaff and Parliament have curved panelled soffits with longitudinal seams and continuous recessed light channels. Melbourne Central uses a broader folded soffit and two island lighting lines; it does not have false wall-mounted circulation recesses in the middle of the island. Parliament retains blue walls, Flagstaff its paler finish, and Melbourne Central its darker opposite wall and square columns. Flinders Street now has fitted fluorescent-style canopy lights, narrow gutters and column-aligned downpipes. Existing heritage ironwork and scalloped valances remain the dominant features.

Exit thresholds at Flagstaff and Parliament are shallow dark recesses with jambs and lintels, rather than blank slabs. They suggest circulation beyond the platform; actual stairs, escalators and concourses are not modelled. Exit locations, column bays, luminaire lengths and roof dimensions are authored for this training route, not surveyed or asserted to be exact. Fixtures use shared merged geometry and existing light sources. Longitudinal meshes are subdivided for route curvature; added objects remain direct station-group children so the world's geometry transformation applies to them.

The broad Flinders Street railway apron uses metre-scaled surface UVs even while material textures are still loading. This prevents asynchronous material loading from stretching a single paving/ballast texture across the complete platform. Runtime browser review remains necessary in addition to TypeScript validation, especially for lighting exposure and canopy intersections.


## Platform thresholds and ends

The subsequent bounded pass compared all five `*-refined.png` browser views with the three linked underground platform photos. The Parliament photo clearly shows a suspended black display and overhead service panels; the Flagstaff photo shows framed service doors, handrails and the end circulation threshold; Melbourne Central has an open island, substantial tiled columns and suspended wayfinding. Those differences now guide the fittings instead of using the same Southern Cross equipment pylon underground.

- Underground chamber headwalls follow their own ceiling profile and have 0.75m depth. A concrete collar remains entirely outside the existing tunnel opening; the running-line envelope is unchanged. Framed service doors, small vents and a short platform-floor return give the end wall scale and depth.
- Flagstaff and Parliament each have two 6.4m-wide, approximately 3m-deep return vestibules at authored positions. The platform back wall, seams and trims stop at each opening. Returns, a rear turn, handrails and shallow ceiling lights supply actual parallax; no escalators or concourse topology are asserted. Melbourne Central remains an island without side vestibules.
- All five stations have light end barriers and staff gates outside the train envelope. The two surface stations have short outboard maintenance steps beyond the slab, plus restrained suspended exit wayfinding; their existing heritage/modern structural identities remain intact.
- Underground display boards are suspended, with a small service panel above; Southern Cross retains the integrated equipment pylons. The displays continue to label the fictional training service, not invented real departures. Small help points sit beside the underground thresholds.

All new geometry is authored; reference photographs remain external research and are not included in game assets. Opening positions, maintenance access details, fixture spacing and dimensions are visual approximations. This is an operating-game environment, not a current public wayfinding or emergency-egress model. Browser review targets are each station's platform view, both underground headwalls from the track, and the side vestibules from oblique platform views. Existing route warping still applies to direct child meshes, and no additional point/shadow lights are introduced.

## Southern Cross raised concourse and platform stairs

The user's additional cab photograph shows the missing vertical layer of the station: a dark transverse bridge girder, glazed balustrades, supporting steelwork and long stair flights descending to the islands beneath the dune roof. The [Transport Victoria station access description](https://transport.vic.gov.au/plan-a-journey/network-maps/southern-cross-station-map-and-travel-information) confirms upper-level Collins Street access, Bourke Street Bridge access, and stairs, escalators and lifts serving metropolitan platforms 9–14. [Grimshaw's project description](https://grimshaw.global/projects/rail-and-mass-transit/southern-cross-station/) provides the architectural context. The user photograph remains a private research reference and is not redistributed.

The authored hall now contains a transverse concourse deck with dark edge girders, visible flange/stiffener detail, a lighter soffit, cross-beams and platform-based supports. Transparent balustrade panels have metal posts and real openings at the stairs. Three pairs of stair flights have individual treads/risers, light nosings, intermediate landings, stringers, handrails and restricted understair areas. A glazed scenic lift enclosure connects to the deck by a small spur. The stairs and lift are architectural scenery, not interactive traversal or a representation of current accessible routes.

The concourse is at local z=52 with a deck top 8 m above the route datum; its lowest over-track girder surface is 6.9 m, above the existing 5.9 m authored contact wire. The playable stair occupies the platform-back band at x=5.675–7.925, leaving x=2.8–5.5 and the tactile edge unobstructed. These dimensions, location, simplified supports and the number of stairways are chosen to fit the training route's existing compressed platform hall. They must not be interpreted as surveyed station dimensions or a true engineering/egress model. The platform arrangement still needs survey data for a literal digital twin. No new point lights, textures from the private image or additional image assets are introduced; the structures are batched by six shared materials and warped with their station.

## Boarding edge and moving-train clearance

The platform slab, coping, tactile strip and underground end return now share a station-specific inboard adjustment. This reduces the previously oversized gap exposed by walking boarders while retaining extra clearance on the Southern Cross and Parliament curves. The adjustment is authored from the game's train/track geometry; it is not a measured real-station platform offset.

The shipped HCMT GLB was checked using the full horizontal hull of every visible carriage mesh, including geometry below platform height for a conservative bound. Front, intermediate and reversed rear bodies were swept through the complete 198 m coping span; open platform-side doors were also checked for every car throughout the permitted ±8 m stopping range. The audit uses the actual carriage transforms and route warp, including the mirrored Flinders Street platforms, and compares against the rendered coping's straight 3 m segments. Coarse sweeps were refined around the largest corner excursions with 5 mm carriage increments and 5 cm hull-edge samples.

| Station visit | Coping inner edge from route centre | Smallest refined sampled clearance |
| --- | ---: | ---: |
| Flinders Street departure | 1.79 m | 15.1 cm |
| Southern Cross | 1.91 m | 11.9 cm |
| Flagstaff | 1.77 m | 16.4 cm |
| Melbourne Central | 1.77 m | 17.0 cm |
| Parliament | 1.96 m | 12.6 cm |
| Flinders Street arrival | 1.79 m | 18.2 cm |

A uniform 1.76 m edge was rejected: the moving rear-car envelope crossed that line at Southern Cross and Parliament. `tests/platform-clearance.test.ts` reads the shipped GLB and independently sweeps its three carriage hulls through all six station visits, including open doors at allowed stopping offsets. It requires at least 8 cm sampled clearance, rather than asserting particular offset values. The refined local reports are retained under ignored `artifacts/train-platform-clearance*.json`; the sampled asset SHA-256 is `62c9c519c1274c72748e7dd64dc423e5cabb231e11d0ec8cde1fcfcec3dffeb7`.

These are deterministic game-geometry checks, not a continuous collision solver, surveyed platform gap, engineering loading gauge or railway safety certification. The actual gap at a specific doorway varies with its position on the curve. No invented deployable boarding ramps are used.
