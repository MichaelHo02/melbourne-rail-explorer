# Town Hall portico review study

Municipal City Collection1958 facade photograph actually inspected. It shows four principal front columns, a triangular pediment, balcony guard, three lower arches and tall arched upper wing windows. This high-impact pass interprets those features within the existing projecting footprint of source27725. Existing clock tower, mansard/gable roofs and other source bodies are preserved. Carving is deliberately simplified.

Front retained edge(−55.8,364.26)→(−50.26,349.02) anchors portico width16.22m. Retained facade envelope18.9m anchors entablature; existing authored mansard24.8m constrains local roof maximum.7.9m setback,6m balcony floor, column heights, guard rhythm and arch dimensions are authored; no measured current construction claims. Eight source portico wall faces are masked with original mesh and face IDs recoverable; outside source vertices/connectivity must stay exact. Wing openings are fitted to retained facade edges.

References:
- https://citycollection.melbourne.vic.gov.au/image-of-the-facade-of-melbourne-town-hall-taken-from-swanston-street-2/
- https://citycollection.melbourne.vic.gov.au/wp-content/uploads/2021/09/1728471.jpg
- https://whatson.melbourne.vic.gov.au/things-to-do/melbourne-town-hall

No photographic textures. Canonical integration belongs to main agent after focused review.

First isolated review exposed the previous authored mansard interpretation projecting as a floating lump over the new portico. Rejected that junction. Final pass aligns portico entablature near19m and pediment24m below retained mansard maximum24.8m. Only old authored roof polygon parts above the projecting portico are clipped; interpolated outside3D polygon parts and original mesh retained. Remaining roof/tower geometry is hash-guarded. This is a local junction exception to leaving earlier roof passes unchanged, not a new roof design.

Study-only isolation hides neighbouring geometry to inspect facade; those hide flags are applied after saving the /tmp study and never saved to canonical. Original city views were obscured by foreground buildings.

A rectangular rear cut closure was rejected because it read as a billboard behind the pediment. Final local roof instead slopes from retained24.8m rear junction to24m front pediment, sealing the same opening while staying within the retained mansard maximum. Three upper arched balcony-door interpretations added. Exact roofing junction remains authored; local clipping does not alter original saved backup.

Final sloped junction preview `/tmp/town-hall-review-roof-junction.png` inspected: recognizable four-column portico, three lower and three upper arched openings, balcony and seven wing bays. Two small authored slate side-fascia quads added afterward to seal roof underside; fresh canonical render must confirm that final seam. Last study verification proves27 other body/tower/gable geometry hashes unchanged and exact outside27725 source connectivity after eight recoverable face removals. Final canonical run refreshes audit/face counts.

Fresh canonical render `docs/images/observatory-town-hall-review-repaired.png` inspected after integration: four columns, balcony, lower arches, wing rhythm and closed sloped roof/fascia visible. Camera moved inside street corridor to avoid neighbouring tower occlusion; no objects hidden and no scene save performed.27 guards and780 authored faces reported by canonical verifier.
