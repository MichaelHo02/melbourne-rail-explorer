# Blender commuter assets

The six clothed commuter variants replace the former capsule people at all five stations. They use MakeHuman's **hm08 basemesh**, skeleton and weights, graphical core assets explicitly released under CC0. See the [official asset licensing explanation](https://static.makehumancommunity.org/about/license.html) and the retained `assets/source/passengers/CC0-MakeHuman.md`. The OBJ itself records the September 2020 CC0 release and credits Data Collection AB, Joel Palmius and Jonas Hauquier. This project includes graphical data, not MakeHuman or MPFB program code.

`scripts/blender/build_passengers.py` creates original clothing, hair, shoes, bags, colour variations and frozen commuter poses around the anatomical mesh. Blender applies the supplied bone weights offline. It exports the editable `assets/source/passengers/commuters.blend` and `public/models/passengers/commuters.glb`. No Blender addon is needed.

Rebuild with:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --python scripts/blender/build_passengers.py
```

The GLB is 4,284,620 bytes. Six full variants and six reduced meshes share five materials. Heights range from 1.65 to 1.85 metres; feet are at Y=0 and front is +Z in glTF. Source nodes are `commuter_01` through `commuter_06`, with `_low` equivalents. The runtime instances each variant/material, uses full detail within 40 metres, reduced geometry from 40–150 metres, and hides distant people. There are 24 placements per unique station.

The Blender lineup was visually checked and clothing seams, arm positions, footwear gaps and colour conversion corrected before export. These are static authored people with anatomical proportions, not scanned actors, facial animation or walking/boarding simulation. Station crowd movement remains future work; the service dwell timer does not claim to animate boarding.
