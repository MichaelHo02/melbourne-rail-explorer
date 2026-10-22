# Flinders viaduct frontage buildings

The authored frontage asset replaces 13 overlapping City of Melbourne 2023 survey sections with two joined envelopes and lightweight facade framing. It covers 15–33 William Street (structure `817607`, objects `17612`–`17616`) and 452–470 Flinders Street (structure `806929`, objects `25125`–`25132`). Both identities were confirmed by intersecting the bounded 2014 Building Outlines records (`mccid_int` 110091 and 103998) with the corresponding bundled 2023 hulls; 474 Flinders Street was checked and is not the matching record.

The 2023 polygons, captured May 2023, are attributed to the City of Melbourne under CC BY 4.0. The asset builder reads the prepared sections in `public/data/buildings.json`. Their game-relative vertical intervals come from `footprint_min_elevation - structure_min_elevation`, clamped at zero, and the section extrusion. The 2014 model heights and floor counts identify the buildings and inform facade rhythm; its elevations are not used for asset placement. The exact prepared ring bounds and every section's base/top are recorded in `public/models/environment/viaduct-frontage.json`. Those ring bounds are smaller than the broader photomesh exclusion hulls in `src/data/photomesh-foreground.json`; the exclusion hulls do not define or enlarge these buildings.

The identity cross-check used the bounded City API query around `POINT(144.9588 -37.81935)` with a 200 m radius, selecting `geo_point_2d`, `geo_shape`, `fmtaddress`, `mccid_int`, `mccid_str`, `height`, `zmin`, `zmax`, `floors` and `build_year` from the 2014 dataset. See `docs/viaduct-frontage-reference.json` for the query, result and per-section source data. Geographic rings use the repository origin `[144.9671, -37.8183]`, projected X east and Z south, and metre units.

Facade appearance is based on inspected public listing photos: [15 William Street](https://www.commercialrealestate.com.au/property/15-william-street-melbourne-vic-3000-14849344) shows reflective blue-grey curtain wall and slender projecting fins; [452–470 Flinders Street](https://www.cushmanwakefield.com/en/australia/news/2020/09/deka-immobilien-acquires-melbourne-office-tower-for-%24454-million) shows deep blue glazing, broad pale framing and finer glazing lines. The photos are reference only and are not redistributed or included in the GLB. `docs/assets/viaduct-facade-model-study.png` and its prompt note are an original generated modelling study: use them only for facade rhythm and shallow frame depth, not for survey dimensions, roof shape, lighting, or textures.

The deterministic Blender builder joins intersecting section solids before adding the facade pieces. The browser receives the self-contained `public/models/environment/viaduct-frontage.glb`; if either surveyed envelope or its complete section-ID list is missing at load time, runtime keeps the source building sections. `src/data/photomesh-foreground.json` is unchanged.

Rebuild and check the asset from the repository root:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python scripts/blender/build_viaduct_frontage.py
node scripts/check-viaduct-frontage.mjs
npm run build
```
