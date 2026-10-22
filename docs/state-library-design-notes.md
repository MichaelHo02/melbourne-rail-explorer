# State Library landmark study

Retained municipal 2023 structure 805833 supplies location, envelope footprint and section levels. Main Swanston front is survey12840; reading-room drum12851 and upper section12852 supply retained height constraints. Source envelopes are copied into recoverable mesh datablocks before changing materials; tall narrow upper envelope is hidden rather than deleted.

Official Library references establish the Corinthian Swanston portico added in1870 and 35m reading-room dome. Study adds simplified shafts/capitals, pediment, sandstone wings and an authored38m external dome inside retained43.5m apex. Column count, exact projections, openings, dome profile, finish colours and slate appearance are illustrative. No photographic texture nodes are introduced.

Generic window, lintel and cornice faces are removed only when every vertex follows one Library section boundary within0.7m, with matching section height. Combined meshes retain original backing datablocks. This geometric attribution does not replace original per-face source IDs; check neighbouring boundaries during final integration.

References:
- https://www.slv.vic.gov.au/visit/our-magnificent-spaces/swanston-street-welcome-zone
- https://blogs.slv.vic.gov.au/our-stories/ask-a-librarian/dome-to-catacomb/

Run new refinement script against canonical loaded scene; save only /tmp study until reviewed. Canonical integration belongs to main agent.

Inspected corrected focused study `/tmp/state-library-study-corrected.png`: portico and dome recognisable; Library roof holes/striping covered by upward tessellation of retained section top rings. Existing envelope meshes contain walls, so new roofs use retained rings rather than nonexistent cap polygons. Rear wings remain simplified blank masonry. Nearby black high-rise roof/wall artefact is outside Library ownership and was preserved; it needs separate generic-city diagnosis. Current camera is partly occluded by neighbouring towers; use a closer Swanston facade camera for final façade acceptance.

## Primary-reference correction after first study

Engineering Heritage Australia nomination, inspected PDF pages6,8,9, specifies octagonal dome plan,16 concrete ribs,35.1m clear internal span,40.8m external extent including flying buttresses, and9.8m lantern diameter. The former smooth white38m dome and tiny square lantern were rejected. Latest script uses faceted octagonal roofing,16 shallow authored rib strips, grouped dark skylight-like panels and9.8m octagonal lantern; dome height, rib width, external surface layout and glazing placement remain approximations within retained height limits. The conspicuous tiny cuboid on first dome was the undersized authored lantern, not generic equipment. A scoped equipment-face removal guards against actual generic units within the dome section.

Official Library La Trobe Journal1971 essay specifies eight Corinthian columns. Six front/two return arrangement follows the inspected historical facade image in engineering nomination; carving remains simplified.21 bay positions now fit retained west-facing wall edges directly, rather than a single approximate straight facade plane. Upper bays receive shallow arched tops; exact original bay count and dimensions remain unmeasured.

Additional primary sources:
- https://portal.engineersaustralia.org.au/system/files/engineering-heritage-australia/nomination-title/State_Library_Dome.pdf
- https://latrobejournal.slv.vic.gov.au/latrobejournal/issue/latrobe-08/t1-g-t1.html

Final inspected study: `/tmp/state-library-final-reference-study.png` shows full dome, octagonal lantern and fitted Swanston bays/portico. No neighbours were hidden; foreground roof still occludes some lower steps. Facade close study `/tmp/state-library-swanston-corrected.png` confirms arched upper bays and ordered stone relief. Geometry verification: all15 source envelopes unchanged;2681 authored faces; no photographic material nodes. Historical reference establishes recognizable architecture but does not prove measured present-day facade or full refurbishment details.
