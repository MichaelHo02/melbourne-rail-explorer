# Sources, provenance and attribution

Research checked September 19, 2026. An authenticated transport API call has not been made.

## Included building data

**City of Melbourne — 2023 Building Footprints**, licensed CC BY 4.0.

- [Dataset](https://data.melbourne.vic.gov.au/explore/dataset/2023-building-footprints/)
- [Government catalogue](https://discover.data.vic.gov.au/dataset/2023-building-footprints)
- [License](https://creativecommons.org/licenses/by/4.0/)
- Source API: `https://data.melbourne.vic.gov.au/api/explore/v2.1/catalog/datasets/2023-building-footprints/exports/json`
- Query parameter `where`: `within_distance(geo_point_2d, GEOM'POINT(144.961 -37.814)', 2.3km)`
- Raw response: 21,912 building sections. The included derivative contains 8,534 sections after CBD cropping, rejecting tiny shapes, replacing Flinders Street survey blocks with the authored landmark and removing documented Southern Cross conflicts, projecting coordinates, and rounding to decimetres.
- Transformation: `scripts/prepare-city.mjs`. X is east, Y is up, Z is south, using a short-distance local projection at Flinders Street. Vertical offsets are relative to each source structure's minimum elevation; surrounding terrain is currently approximate.
- Changes: geographic crop, simplified data fields, local projection, generated extrusion meshes and façades. This does not imply City of Melbourne endorsement.
- Capture dates in the records include 2018. Neither the dataset title nor this rendering is a statement that every building reflects the current city.
- The source data is bundled, so the game does not depend on a live City of Melbourne API call.

## Included route geometry

**Department of Transport and Planning, Victoria — Public Transport Lines and Stops**, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), [dataset](https://opendata.transport.vic.gov.au/dataset/public-transport-lines-and-stops). Retrieved September 19, 2026; source metadata modified September 7, 2026.

`src/data/route-source.json` retains two complete selected route features (`2-FKN-vpt-1.29.R`, `2-UFD-vpt-35.17.R`), five platform points and attribution. The full lines export download was interrupted, so the selected complete features were recovered and validated; the game does not claim to bundle the full network. The stops export completed. `scripts/prepare-route.py` rebuilds the small derivative from these retained features.

Changes: reverse the Frankston western leg from Flinders Street through Southern Cross and Flagstaff; join the Upfield leg toward Melbourne Central, Parliament and Flinders Street; blend the final 300 metres to close adjacent platform alignments; smooth the path and author elevations/level platforms. This is a fictional continuous training connection, not an operational turnout, surveyed track or current scheduled HCMT service.

## Network references

- [Transport Victoria: City Loop and Metro Tunnel stations](https://transport.vic.gov.au/help-and-support/other-public-transport-help/city-loop-and-metro-tunnel-stations): confirms the City Loop's five stations and distinguishes them from the Metro Tunnel.
- [GTFS Schedule](https://opendata.transport.vic.gov.au/dataset/gtfs-schedule): future geographic route/timetable source; not currently imported into the training alignment.
- [GTFS Realtime](https://opendata.transport.vic.gov.au/dataset/gtfs-realtime): trip updates, vehicle positions and service alerts; API key in `KeyID`; published Metro endpoint limit 24 calls per 60 seconds.
- [PTV Timetable API](https://www.vic.gov.au/public-transport-timetable-api): an alternative departures/routes API with separate credentials/signature flow.

OpenStreetMap geometry was investigated but the attempted Overpass requests failed. **No OpenStreetMap data is included** and the authored railway is not labelled as OSM-derived.

## Candidate detailed city assets (not included)

[City of Melbourne 3D Textured Mesh / Photomesh 2018](https://discover.data.vic.gov.au/dataset/city-of-melbourne-3d-textured-mesh-photomesh-2018): tiled OBJ meshes with MTL/JPG, L13–L20 levels of detail, MGA Zone 55 coordinates and AHD elevation. The catalogue lists a 9.7 GB archive and CC BY 4.0. It is promising for real exterior scenery but requires corridor extraction, format conversion and optimization. No photomesh imagery or geometry is currently bundled.

## Visuals and audio

The bundled daylight HDRI `public/environment/morning-sky.hdr` is **Kloppenheim 06 (Pure Sky)** by Greg Zaal (original) and Jarod Guest (sky edits), from [Poly Haven](https://polyhaven.com/a/kloppenheim_06_puresky), licensed [CC0](https://polyhaven.com/license). It provides natural lighting and sky, not Melbourne geography. The 1K HDR asset is 1,173,154 bytes; downloaded from the asset URL in Poly Haven's public metadata. No preview-page image is repackaged.

Train, landmark, station furniture, tunnel, surface materials and audio are authored locally in source. The exterior recreates the HCMT from user-supplied photographic reference; the cab is gameplay-adapted. The user reference photograph is not redistributed. See `train-assets.md` and `world-review.md` for fidelity boundaries. UI typography uses local Arial/Helvetica; the proprietary PTV Network Sans font is not bundled. See `ui-brand-references.md`.
