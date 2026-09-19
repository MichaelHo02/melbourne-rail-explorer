# Yarra River geometry

## Source and permission

The bundled water boundary comes from the Victorian Government's **Vicmap Hydro — Water Area (HY_WATER_AREA_POLYGON)** service, queried for `YARRA RIVER`. The [official DataVic catalogue](https://discover.data.vic.gov.au/dataset/vicmap-hydro-water-polygon) licenses this dataset under [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/). The [Vicmap Hydro product page](https://www.land.vic.gov.au/maps-and-spatial/spatial-data/vicmap-catalogue/vicmap-hydro) describes the hydrological mapping product. No API key was required for this read-only public query.

API layer: <https://vicmap.land.vic.gov.au/agsgis/rest/services/vicmap/Vicmap_Hydro/MapServer/1>

Attribution: © State of Victoria (Department of Transport and Planning). Vicmap Hydro, CC BY 4.0. Clipped to central Melbourne for this game.

The originally proposed Planning GIS service was inspected. Its `Inner City Reach` layer is a management-area polygon, and its `river bed, soil and banks` layer includes river land. Neither should be painted entirely as water. The canonical Vicmap **water area** polygon was available directly and gives the appropriate river surface.

## Data and renderer contract

- File: `src/data/river-source.json`.
- Geometry: GeoJSON `Polygon`, one outer ring, no interior holes in this clipped reach.
- Coordinates: EPSG:4326 `[longitude, latitude]`, not game metres.
- Ring: 611 vertices, explicitly closed.
- Bounds: `[144.935, -37.826, 144.987, -37.814]`.
- Source identifiers: `ufi=76462130`, `pfi=8156874`, `named_feature_id=9758`, `id=35`.
- Source properties, query, fetch time, licence and modifications are retained in the JSON.

For each point, call the existing `project(lon, lat, waterHeight)`. Create a polygon mesh from those projected banks and use the existing water material. Do **not** fit a spline or add a fixed ribbon width: that would displace banks back onto Southbank. If constructing a Three.js shape in its default XY plane before rotating −π/2 about X, shape coordinates should be `(projected.x, -projected.z)`, producing the desired world `(x, height, z)`. The outer ring is clockwise in game XZ coordinates. Three.js ShapeGeometry can triangulate the concave ring.

Water height, wave amplitude, bank structures and reflections remain authored rendering choices. The dataset supplies the horizontal water boundary, not a current surveyed water level or bathymetry. Rectangle clipping closes the river at the scene extent; those cap edges should remain outside the primary camera composition.

## Reproduction and checks

Run `python3 scripts/prepare-river.py`. It queries the official polygon, clips to the stated rectangle using Sutherland–Hodgman, rounds to eight decimal places and writes an approximately 18.4KB JSON. Bank vertices are otherwise retained without smoothing. It stops for review if source selection becomes ambiguous or the clipped geometry gains additional rings.

Checked that the ring closes, every point is within the clipping bounds, and a central-city reference point `(144.965, -37.8197)` is inside water while the former authored anchor `(144.965, -37.8209)` is outside. At longitude 144.965, the actual banks cross approximately latitudes −37.820049 and −37.819290. The old centre anchor was approximately 137 metres south of the measured river centre there, explaining the building intersections.

This change does not delete building footprints or infer that every footprint overlapping the water is erroneous: real bridges and wharves need separate handling. Final water appearance and camera composition must be checked in the integrated renderer.
