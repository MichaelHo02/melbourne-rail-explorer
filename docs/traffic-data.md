# Train traffic data research

Verified 19 September 2026 against primary Transport Victoria sources. The bundled implementation is a fixed-date timetable replay, not live vehicle tracking.

## Official schedule

- [GTFS Schedule collection](https://opendata.transport.vic.gov.au/dataset/gtfs-schedule).
- [Download resource and field dictionary](https://opendata.transport.vic.gov.au/dataset/gtfs-schedule/resource/fb152201-859f-4882-9206-b768060b50ad).
- [Public statewide ZIP](https://opendata.transport.vic.gov.au/dataset/3f4e292e-7f8a-4ffe-831f-1953be0fe448/resource/fb152201-859f-4882-9206-b768060b50ad/download/gtfs.zip).

The resource was last modified 18 September 2026. HTTP HEAD reported 292,748,591 bytes, with byte ranges supported. Reading the final 65,536 bytes identified the Metro member `2/google_transit.zip`; a single bounded range extracted its 23,973,356-byte compressed payload without downloading the other modes. The resulting Metro archive is 25,297,577 bytes. Research copy: `/tmp/gtfs-metro.zip` (not a bundled game asset).

The archive contains agency, stops, pathways, transfers, levels, routes, trips, calendar, calendar_dates, stop_times and shapes files. Agency timezone is `Australia/Melbourne`. Calendar records must be evaluated together with exceptions; actual records in this export include special services on 17 September and future periods ending 20 December 2026. Do not assume every trip is valid throughout that span or indefinitely repeat this timetable.

The five City Loop station parents are `vic:rail:FSS`, `vic:rail:SSS`, `vic:rail:FGS`, `vic:rail:MCE`, `vic:rail:PAR`. Child platform stops include platform codes and geographic coordinates. Select actual train platform locations, excluding entrances and replacement-bus stops. Preserve trip IDs, service IDs, shape IDs, stop sequences and shape distances. GTFS times can exceed 24:00:00; interpret these against the service date in Melbourne, not modulo midnight.

For Saturday 19 September 2026, applying calendars and exceptions yields 1,279 trips calling at least one of those five stations. This is a verification result, not a fixed target count. Example: source trip `02-CGB--67-T2-5201`, service `T2`, Craigieburn headsign, shape `2-CGB-vpt-67.1.H`: Flinders Street platform 5 (`11216`) 05:35, Southern Cross platform 11 (`22190`) 05:39, source shape distances 0 and 1515.33 metres. These are timetable positions, not observed vehicle positions.

License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Attribute State of Victoria, Department of Transport and Planning / Transport Victoria, identify extraction date and derived interpolation. Shapes establish public geographic routing, not a surveyed track assignment, elevation, fleet consist or signalling authority. Fleet and visual track offsets must be explicitly authored unless separately verified.

## Live Metro feed requirements

- [GTFS Realtime collection](https://opendata.transport.vic.gov.au/dataset/gtfs-realtime).
- [Metro vehicle-position resource](https://opendata.transport.vic.gov.au/dataset/gtfs-realtime/resource/e2158e21-e6cb-4611-919f-90117b36a610).
- [Downloadable OpenAPI specification](https://opendata.transport.vic.gov.au/dataset/2d9a7228-5b81-40d3-8075-ae7a3da42198/resource/e2158e21-e6cb-4611-919f-90117b36a610/download/gtfsr_metro_train_vehicle_positions.openapi.json).
- [Portal migration and key setup](https://opendata.transport.vic.gov.au/news-and-updates/consolidating-access-to-transport-apis).

Current vehicle-position endpoint in the OpenAPI document:
`https://api.opendata.transport.vic.gov.au/opendata/public-transport/gtfs/realtime/v1/metro/vehicle-positions`.

Create a Transport Victoria Open Data Portal account and generate/use its subscription key. Old Data Exchange Platform credentials ceased being valid after September 2025. Credentials available in this repository/runtime: **false** (checked environment-file presence and candidate variable names only; no values logged).

The official documents conflict: the collection page says `KeyID` request header and 24 calls per minute; the downloadable OpenAPI says `Ocp-Apim-Subscription-Key` and describes 20–27 calls per minute with a 30-second cache. Verify the authenticated endpoint/header with the user's provisioned key before claiming connectivity. A server-side polling proxy at roughly 30-second intervals is appropriate; never expose keys through `VITE_*`, browser requests, query strings or committed files.

Decode Protocol Buffers, validate feed and vehicle timestamps, retain trip/service-date identifiers and join to the matching schedule export. Surface expired/authentication/failed states explicitly. Never label timetable interpolation as live or silently replace unavailable live data with invented traffic. The live feed alone does not establish every train's position, especially through tunnels or when a record is absent; vehicle timestamps and missing data must remain visible in diagnostics.

## Bundled replay and integration

Rebuild with `python3 scripts/prepare-traffic.py /path/to/metro/google_transit.zip --date 2026-09-19`. The input is the Metro folder `2` ZIP inside the statewide download. Input SHA-256 is retained in `src/data/traffic-schedule.json`; this makes exact rebuild provenance verifiable even after the public download is updated. Only Python standard-library dependencies are required. Transport Victoria uses extended route type `400` for these metropolitan rail routes; replacement-bus route variants and replacement-bus stops are excluded.

The derived bundle contains 735 consecutive City Loop trip sections across 50 official shapes (~775 KB JSON). This differs from the 1,279 station-serving trips above because single-station calls cannot establish a between-station traffic segment, and trips with intervening non-city calls are split rather than drawing an invented shortcut. Full selected-service calendars and their exceptions accompany the snapshot.

`sampleTraffic(elapsedSeconds)` returns active trip sections for 19 September 2026 at 06:42:00 plus elapsed simulation time. Pass `Simulation.state.time`, so pauses and restored saves retain the same surrounding traffic. There is no wall-clock dependency, random spawn interval, automatic next-day repetition, or live-data fallback. At the end of retained service sections trains disappear; suburban portions are omitted.

Each sample provides a section `id`, original `tripId`, route ID/name, headsign, direction ID, world position/heading, source shape distance, scheduled speed, source platform and adjacent station names. `sampleTrafficTrip(sectionId, elapsedSeconds, distanceBehind)` places additional cars on the same shape and returns null if outside the retained geometry. `sourcePlatform` is the current published platform during a stop and the next published platform while travelling.

Published arrival/departure intervals produce stationary dwell. Where GTFS publishes equal arrival/departure times, no dwell duration is invented. Between calls, distance is interpolated uniformly over scheduled travel time; this is a visual timetable estimate, not traction physics, acceleration modelling or observed delay. World X/Z use the source shape; Y borrows the nearest authored player-route vertical profile. Renderer-supplied adjacent-track offsets and fleet visuals are presentation choices, not source-confirmed track or rolling-stock assignments. The player train remains independently simulated and must not collide with timetable replay trains.

Validation covers selected-service calendar validity, a concrete official Craigieburn call pair, monotonic stop/shape references, dwell, service times beyond midnight, finite deterministic positions, car spacing and no automatic day wrapping. Browser appearance and rendered track clearance require the root integration's visual review.

## Visible traffic subset

The renderer maps source positions to two authored adjacent exterior tracks on the Flinders Street–Southern Cross corridor. The official sampler remains unchanged and still exposes every retained active service. Rendering first rejects unmappable/distant candidates, sorts viable candidates by camera distance, then selects at most eight trains. It reserves a conservative 170-metre seven-car interval with 10-metre end margins on each presentation lane and omits overlapping candidates. Opposing directions occupy separate lanes. This prevents distinct timetable platform movements from being drawn through each other when several real tracks are represented by only two visual lanes.

This is a disclosed visual subset, not live track occupancy, a dispatcher simulation, a delay applied to source services, or evidence that omitted trains did not operate. Selection can change with camera proximity and service progress. Underground neighbouring tunnels are not rendered as visible traffic through tunnel walls. Regression coverage includes the real Lilydale/Upfield overlap at replay elapsed 270 seconds, opposing-direction separation and rejection before the visible-count cap.

The traffic visual asset is derived from the project’s authored HCMT GLB with `npx @gltf-transform/cli@4.5.0 simplify public/models/melbourne-commuter.glb public/models/traffic-commuter.glb --ratio 0.22 --error 0.004`. Actual reduction is 27,760 to 20,785 triangles (966,564 bytes); the simplifier preserves material boundaries. It does not establish the real fleet assigned to a GTFS trip.
