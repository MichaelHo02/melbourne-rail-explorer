# Flinders Street–Southern Cross scenery source

`src/data/corridor-source.json` is a **963,621 byte** bundle of official horizontal geography, prepared by `python3 scripts/prepare-corridor.py`. No runtime API or API key is required. The bounding rectangle is `[144.949, -37.8245, 144.972, -37.814]` in EPSG:4326, covering the rail corridor, adjacent city streets and both banks of the Yarra.

## Renderer contract

`layers` contains GeoJSON FeatureCollections. All positions use `[longitude, latitude]` and can be passed through the game's existing `project()` function. Attributes retain their source names. Null fields are omitted.

| Layer | Count | Geometry | Important properties |
|---|---:|---|---|
| `roads` | 804 | LineString / MultiLineString | `ufi`, `pfi`, `feature_type_code`, `ezi_road_name`, `class_code`, `div_rd`, `road_status`, `vehicular_access` |
| `rails` | 188 | LineString / MultiLineString | `ufi`, `pfi`, `feature_type_code`, `tracks_number_of`, `rail_gauge`, `structure_name` where supplied |
| `roadStructures` | 38 | Point | `feature_type_code`, `name`, `rotation`, dimensions where supplied |
| `railStructures` | 25 | Point | `feature_type_code`, `name`, `rotation` |
| `trees` | 3,100 | Point | `com_id`, integer `species`, raw `diameter_breast_height` when supplied, `located_in` |
| `openSpaces` | 40 | MultiPolygon | `veac_id`, `name`, `os_group`, `polygon_source` |

`treeSpecies[feature.properties.species]` resolves to `{common_name, scientific_name}`. Dictionary encoding avoids repeating species names thousands of times. No tree height or crown spread was present; these remain authored model choices. The API field metadata does not declare a unit for its trunk-diameter attribute, so the bundle preserves it without turning it into metres.

### Roads, paths, bridges and tunnels

Road feature types are **618 `road`, 129 `trail`, 33 `bridge`, 12 `foot_bridge`, 12 `tunnel`**. Trails and footbridges must not become normal road surfaces, and tunnel segments should not be painted across the city ground. Bridge spans are represented by the actual clipped line segments, not just a marker point. Their elevation, deck width and structure appearance still need authored geometry: every queried road segment had an absent/zero `width_m` value.

`roadClasses` is copied from the official reference table: **2 arterial, 3 sub-arterial, 4 collector, 5 local, 6 minor, 9 trail** are the values occurring here. Road widths chosen from these classes are rendering defaults, not measured lane widths. A divided road can have separate carriageway centre lines; avoid interpreting each one as the full width of the entire road corridor.

Named bridge spans include Princes Bridge, Queens Bridge, Kings Bridge, Spencer Street Bridge, Charles Grimes Bridge, Sandridge Pedestrian Bridge, Evan Walker Bridge, Seafarers Bridge and Jim Stynes Bridge. Preserve contiguous segments of the same named structure when building bridge decks.

Rail feature types are **50 `railway`, 45 `tramway`, 32 `bridge_rail_o`, 61 `rail_uground_o`**. Underground rail is not surface scenery. The Vicmap rail layer is a network representation: it does not establish every individual operational track, turnout, overhead wire or signal. It is useful for bridge/viaduct placement and nearby rail/tram context without replacing the authored playable train alignment silently.

### Open space is not synonymous with grass

Two source parcels are explicitly named **Batman Park and Enterprise Park**: `P383229` and `P361466`. These are useful for locating the park beside the viaduct. Other parcels include Alexandra Gardens, Queen Victoria Gardens, Birrarung Marr, promenades, squares, the Aquarium and boat berths. Preserve `os_group` and choose visible park surfaces deliberately; do not paint the entire open-space inventory green. Even a park parcel includes paths and structures and is not a measured grass-cover polygon. Source polygons and interior rings are preserved through clipping.

## Sources and licences

All included source datasets are **CC BY 4.0**, verified from their official publisher/catalogue metadata. Full source URLs, selected field schemas, exact queries and attributions are retained under `sources` in the JSON.

- [Vicmap Transport — Road Line](https://discover.data.vic.gov.au/dataset/vicmap-transport-road-line) and [Vicmap Transport dataset series](https://discover.data.vic.gov.au/dataset/vicmap-transport), State of Victoria, Department of Transport and Planning. The [official product description](https://www.land.vic.gov.au/maps-and-spatial/spatial-data/vicmap-catalogue/vicmap-transport) describes road centrelines, railway/tramway and infrastructure features. Queried the public `Vicmap_Transport/MapServer` layers 0–3 and reference table 24.
- [Trees, with species and dimensions](https://data.melbourne.vic.gov.au/explore/dataset/trees-with-species-and-dimensions-urban-forest/information/), City of Melbourne. Publisher API explicitly provides the [CC BY 4.0 licence](https://creativecommons.org/licenses/by/4.0/legalcode). The returned data-processing timestamp is September 2025; this is a mapped inventory, not live tree monitoring.
- [VEAC Metropolitan Melbourne Open Space Inventory](https://discover.data.vic.gov.au/dataset/veac-metropolitan-melbourne-open-space-inventory), State of Victoria, Department of Energy, Environment and Climate Action. Queried its published GeoServer WFS layer `open-data-platform:veac_metro_open_space`, retaining parcel identity and category.

Attribution to include in game/source documentation: “Vicmap Transport © State of Victoria (Department of Transport and Planning); VEAC Metropolitan Melbourne Open Space Inventory © State of Victoria (Department of Energy, Environment and Climate Action); Urban Forest tree inventory © City of Melbourne. CC BY 4.0. Data clipped and selected for this game.”

## Preparation and checks

Road and rail segments are clipped with Liang–Barsky; disjoint pieces become MultiLineStrings. Open-space rings are clipped to the rectangle; coordinates are rounded to eight decimal places. Original IDs, feature categories and selected attributes remain. Point selection is geographic, not randomly generated. The script refuses a potentially truncated query or a final bundle larger than one million bytes.

Checks passed: all coordinates are finite and within the rectangle; polygon rings close; expected named Batman Park parcels are present; feature counts are consistent; output is below 1MB. This validates the source bundle, not its eventual rendering or collision behavior. No renderer or browser changes were made in this task.

## Bounded photomesh investigation

The [City of Melbourne Photomesh 2020 dataset](https://data.melbourne.vic.gov.au/explore/dataset/city-of-melbourne-3d-textured-mesh-photomesh-2020/information/) is also CC BY 4.0. Its current public preview resolves to genuine **I3S 1.8 IntegratedMesh** services rather than only an opaque whole-city download:

- [CBD scene layer metadata](https://tiles.arcgis.com/tiles/KGdHCCUjGBpOPPac/arcgis/rest/services/CBD_WGS84/SceneServer/layers/0?f=json)
- [Southbank scene layer metadata](https://tiles.arcgis.com/tiles/KGdHCCUjGBpOPPac/arcgis/rest/services/Southbank_WGS84/SceneServer/layers/0?f=json)
- [OBJ download-region index](https://services1.arcgis.com/KGdHCCUjGBpOPPac/ArcGIS/rest/services/Photomesh_2020_OBJ_Grid/FeatureServer/0)

The CBD root node index was fetched successfully (863 decompressed bytes). The metadata advertises hierarchical node pages, JPEG textures, raw vertex buffers and Draco-compressed alternatives; horizontal WGS84 and vertical EGM96 are declared. Responses may be gzip encoded. This establishes a promising small-tile route, but no mesh geometry was downloaded or decoded and no claim of a usable runtime photomesh is made. An I3S-to-game-coordinate/GLB conversion or streaming loader is a separate bounded implementation. No multi-gigabyte archive was downloaded.
