# Authored Melbourne CBD preview

Open `assets/source/environment/city-observatory.blend` in Blender 5.2.2. The saved camera view uses rendered shading with overlays hidden. The companion render is `docs/images/observatory-blender-preview.png`.

Rebuild from retained source evidence:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python scripts/blender/build_city_observatory.py
```

The preview uses building sections from the City of Melbourne survey catalogue (`public/data/buildings.json`), Vicmap road centrelines (`src/data/observatory-roads.json`), the Vicmap Hydro Yarra polygon (`src/data/river-source.json`), and mapped trees and park inventory parcels (`src/data/corridor-source.json`). Object custom properties and the source manifests retain attribution. The Flinders Street and corridor frontage models are previously authored geometry.

All city surface colours, window patterns and roof finishes are authored materials. No photographic city mesh or photographic surface textures are included. Daylight is procedural. The scene is a consistent modelling foundation, not a surveyed replica of every facade: generic window spacing, flat ground levels, road widths, vegetation crowns and park grass are illustrative. The building catalogue is historical and has not been reconciled against every present-day redevelopment. Bridge decks use an authored thin section to avoid solid walls across the water.

The browser observatory remains a separate work in progress. This Blender pass does not update its older photographic assets or establish visual parity with the website.

## Geometry refinement

Coincident mesh vertices are merged before triangulation and face-normal recalculation. Survey roofs receive a deterministic palette of pale, warm and zinc finishes. Dark asphalt is bordered by illustrative 2m stone pavement bands on the retained road alignment. These bands are visual approximations, not official kerb or accessibility geometry.

## Shading pass

The saved viewport uses Cycles rendered shading with preview denoising. Neutral environment light and a warmer directional sun provide cast shadows; glass is muted steel green and masonry uses subdued earth colours. Facades use subtle procedural bump relief without image textures. Roof audits found no inverted top caps or missing roof-material assignments. Distinctive landmark detailing remains unfinished.

## Modelled detail pass and walkthrough

Survey structures above 8m now receive batched authored window bays and shallow roof cornices. Major named CBD streets have illustrative wider carriageways, shallow kerbs and generic lane dashes; none are claims about actual lane allocation. Railway and tram alignments use the retained Vicmap rail features; explicitly underground features and bridge rail features are excluded from this flat-level pass. Gauge, ballast width and vertical placement are authored. Tree crowns vary in size and have modelled trunks. Flinders station heading is derived from a retained Flinders Street tram segment rather than the previous runtime rotation.

Three camera renders accompany the [design walkthrough](blender-design-walkthrough.md). The aerial scene remains incomplete as a detailed present-day replica: station platforms and rail elevations, landmark ornament, terrain and current redevelopment checks remain necessary. Generated imagery is used only as an artistic palette study and is not embedded in scene materials.
