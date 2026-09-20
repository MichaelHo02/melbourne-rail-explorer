# Sources, provenance and attribution

Research checked September 19, 2026. An authenticated transport API call has not been made.

## Included building data

**City of Melbourne — 2023 Building Footprints**, licensed CC BY 4.0.

- [Dataset](https://data.melbourne.vic.gov.au/explore/dataset/2023-building-footprints/)
- [Government catalogue](https://discover.data.vic.gov.au/dataset/2023-building-footprints)
- [License](https://creativecommons.org/licenses/by/4.0/)
- Source API: `https://data.melbourne.vic.gov.au/api/explore/v2.1/catalog/datasets/2023-building-footprints/exports/json`
- Query parameter `where`: `within_distance(geo_point_2d, GEOM'POINT(144.961 -37.814)', 2.3km)`
- Raw response: 21,912 building sections. The included derivative contains 8,533 sections after CBD cropping, rejecting tiny shapes, replacing Flinders Street survey blocks with the authored landmark and replacing the exact viaduct survey deck 19385 and removing documented Southern Cross conflicts, projecting coordinates, and rounding to decimetres.
- Transformation: `scripts/prepare-city.mjs`. X is east, Y is up, Z is south, using a short-distance local projection at Flinders Street. Vertical offsets are relative to each source structure's minimum elevation; surrounding terrain is currently approximate.
- Changes: geographic crop, simplified data fields, local projection, generated extrusion meshes and façades. This does not imply City of Melbourne endorsement.
- Capture dates in the records include 2018. Neither the dataset title nor this rendering is a statement that every building reflects the current city.
- The source data is bundled, so the game does not depend on a live City of Melbourne API call.

## Included route geometry

**Department of Transport and Planning, Victoria — Public Transport Lines and Stops**, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), [dataset](https://opendata.transport.vic.gov.au/dataset/public-transport-lines-and-stops). Retrieved September 19, 2026; source metadata modified September 7, 2026.

`src/data/route-source.json` retains two complete selected route features (`2-FKN-vpt-1.29.R`, `2-UFD-vpt-35.17.R`), five platform points and attribution. The full lines export download was interrupted, so the selected complete features were recovered and validated; the game does not claim to bundle the full network. The stops export completed. `scripts/prepare-route.py` rebuilds the small derivative from these retained features.

Changes: reverse the Frankston western leg from Flinders Street through Southern Cross and Flagstaff; join the Upfield leg toward Melbourne Central, Parliament and Flinders Street; blend the final 300 metres to close adjacent platform alignments; smooth the path and author elevations/level platforms. This is a fictional continuous training connection, not an operational turnout, surveyed track or current scheduled HCMT service.

## Included river geometry

**State of Victoria (Department of Transport and Planning) — Vicmap Hydro, Water Area (HY_WATER_AREA_POLYGON)**, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). [Official catalogue](https://discover.data.vic.gov.au/dataset/vicmap-hydro-water-polygon), [source API layer](https://vicmap.land.vic.gov.au/agsgis/rest/services/vicmap/Vicmap_Hydro/MapServer/1).

`src/data/river-source.json` retains the Yarra River polygon, source identifiers, query, licence and retrieval time (September 19, 2026). Changes: clipped to central Melbourne, coordinates rounded to eight decimal places, projected and triangulated for rendering. Both banks retain their geographic shape; water level, waves and bank structures remain authored. `scripts/prepare-river.py` regenerates the derivative. See [river geography](river-geography.md) for the exact query and coordinate checks.

## Network references

- [Transport Victoria: City Loop and Metro Tunnel stations](https://transport.vic.gov.au/help-and-support/other-public-transport-help/city-loop-and-metro-tunnel-stations): confirms the City Loop's five stations and distinguishes them from the Metro Tunnel.
- [GTFS Schedule](https://opendata.transport.vic.gov.au/dataset/gtfs-schedule): included fixed-date surrounding-traffic replay; see [traffic provenance](traffic-data.md).
- [GTFS Realtime](https://opendata.transport.vic.gov.au/dataset/gtfs-realtime): trip updates, vehicle positions and service alerts; authenticated access required; see the conflicting official header specifications and server-side integration requirements in [traffic data](traffic-data.md).
- [PTV Timetable API](https://www.vic.gov.au/public-transport-timetable-api): an alternative departures/routes API with separate credentials/signature flow.

OpenStreetMap geometry was investigated but the attempted Overpass requests failed. **No OpenStreetMap data is included** and the authored railway is not labelled as OSM-derived.

## Included photographic city, passengers and traffic

Five cropped patches from **City of Melbourne 3D Textured Mesh (Photomesh) 2020**, CC BY 4.0, are bundled as GLB: 106 I3S tiles, 267,736 source triangles and 36,096,220 bytes. [Photomesh provenance](photomesh.md) records source URLs, served coordinates, cropping and railway/riverbank clipping. This replaces the earlier unimplemented 2018 export proposal. The 2020 aerial scan is not a current or street-level survey.

[Passenger provenance](passenger-assets.md) records CC0 MakeHuman anatomical assets with original Blender-authored clothes, hair and accessories. No reference photographs are redistributed.

[Traffic provenance](traffic-data.md) records Transport Victoria GTFS Schedule, CC BY 4.0, published 18 September and selected for service date 19 September 2026. The game derives timetable positions and uses authored track/fleet presentation; no live API call has been authenticated.

[Audio sources](audio-sources.md) record eaglechopper and melbourne.atmospheres CC0 field recordings and Tanoseki's Parliament departure recording under CC BY 3.0. Exact asset URLs, creator credits, transformations and hashes are bundled in `public/audio/sources.json`. No cloned announcement voice or generated speech is included.

## Visuals and audio

The bundled daylight HDRI `public/environment/morning-sky.hdr` is **Kloppenheim 06 (Pure Sky)** by Greg Zaal (original) and Jarod Guest (sky edits), from [Poly Haven](https://polyhaven.com/a/kloppenheim_06_puresky), licensed [CC0](https://polyhaven.com/license). It provides natural lighting and sky, not Melbourne geography. The 1K HDR asset is 1,173,154 bytes; downloaded from the asset URL in Poly Haven's public metadata. No preview-page image is repackaged.

Train, landmark, viaduct, station furniture and tunnel geometry are authored locally in source. Traction/horn/cue synthesis is original; the location recordings above are third-party licensed assets. Generated materials coexist with the CC0 photographed surface maps below. The exterior recreates the HCMT from user-supplied photographic reference; the cab is gameplay-adapted. The user reference photograph is not redistributed. See `train-assets.md` and `world-review.md` for fidelity boundaries. UI typography uses local Arial/Helvetica; the proprietary PTV Network Sans font is not bundled. See `ui-brand-references.md`.


## Included western corridor geography and surface assets

[Corridor data provenance](corridor-data.md) records the exact public API queries, schemas, licences and preparation checks for the 963,621-byte offline bundle:

- Vicmap Transport © State of Victoria (Department of Transport and Planning), CC BY 4.0: road/path/bridge and railway/tram horizontal alignments. Source records are clipped and selected; widths, bridge approaches, six-track context and overhead infrastructure are authored. `DD` represents one centreline per carriageway, while `DS` represents one centreline for the whole divided road ([official code table](https://vicmap.land.vic.gov.au/agsgis/rest/services/vicmap/Vicmap_Transport/MapServer/17)).
- Urban Forest tree inventory © City of Melbourne, CC BY 4.0: mapped positions and species. Height and canopy dimensions are authored. The raw diameter attribute informs relative size only; the retrieved schema does not declare its unit. Crowns near the approximate elevated alignment are shortened to preserve railway clearance.
- VEAC Metropolitan Melbourne Open Space Inventory © State of Victoria (Department of Energy, Environment and Climate Action), CC BY 4.0: parcel boundaries. Selected parks receive grass; parcels are not measured grass-cover polygons.

`public/textures/surfaces/sources.json` retains the exact original asset URLs, authors, files and physical texture dimensions. Diffuse, OpenGL normal and roughness maps are included at 1K, under [Poly Haven CC0](https://polyhaven.com/license):

- [Gravel Stones](https://polyhaven.com/a/gravel_stones), Amal Kumar, used for ballast.
- [Asphalt 02](https://polyhaven.com/a/asphalt_02), authors retained in the manifest, used for streets.
- [Pavement 04](https://polyhaven.com/a/pavement_04), Jan Burghardt, used for footpaths and hardstanding.

These textures provide surface detail, not Melbourne geographic imagery. `python3 scripts/prepare-surface-textures.py` rebuilds the downloaded assets and attribution manifest. [Viaduct asset documentation](viaduct-assets.md) records primary photographic references, original Blender geometry, authored texture generation and optimization. Reference photographs are not redistributed.

`src/data/bridge-decks.json` is derived alongside the building dataset from retained bridge footprints and relative top elevations. It aligns road bridge surfaces with survey deck meshes; it is not a surveyed absolute elevation model. The removed bank-side railway footprint `19385` is replaced by the Blender kit; neighbouring source structures remain.
