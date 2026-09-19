# Victorian rail wayfinding direction

Reviewed 19 September 2026. The interface is an original rail-simulator interface inspired by Melbourne public transport wayfinding. It does not reproduce the official PTV/Metro logo or claim operator endorsement.

## Primary references

- [Transport Victoria metropolitan maps](https://transport.vic.gov.au/plan-a-journey/network-maps/melbourne-public-transport-maps) links the [September 2026 Victorian train network map](https://edge.sitecorecloud.io/stategovernc45d-cftw-production-c9ca/media/Project/TransportWebsite/Forms/Vic-Train-Network-Map-Sept-2026.pdf). The UI takes the rail-wayfinding approach of destination-first labels, mode pictograms, strong route colours, linked station markers and compact service information. The blue used for the training route is a design choice, not a claim that the whole City Loop is one official blue line.
- [Network Sans designer Michael Bojkowski's project](https://okinterrupt.website/Network-Sans) identifies Network Sans as Victoria's public-transport type family, including signs and passenger information displays. It states that the shown family is available exclusively to PTV. It also describes Neo/Geo and condensed variants developed for different signage contexts.
- [Wayfound Victoria V2.0, official PDF](https://wayfoundvictoria.vic.gov.au/wp-content/uploads/2020/11/Wayfound-Victoria-V2.0.pdf) is an additional public-signage reference. The web reader rejected its 16.9 MB size, so this build does not claim to have audited or followed the complete technical standard.

## Implemented visual system

- A solid navy header and white-on-blue train mode roundels establish the metropolitan-rail identity. The menu is a departure sign: City Loop destination, all-stations stopping pattern, 06:42 departure, HCMT / 7 cars fleet label.
- A white departure card separates operational information from the navy destination panel. Squared corners, strong divider rules and transport-sized text replace translucent lifestyle cards, gold accents and widely tracked marketing copy.
- Palette: navy `#071c39`, train blue `#0072ce`, cyan accent `#00b5e2`, white and blue-grey secondary text. These are authored approximations rather than certified official colour specifications.
- A short linked-station diagram occupies the upper right; next-stop information occupies a small upper-left sign. The controller, speed, doors and emergency controls stay along the bottom, preserving the central windshield view.
- Station-map colours use the same blue/white system. Emergency control retains red and keyboard focus uses highly visible yellow, separate from service colour.

## Typography and ownership

The UI uses the locally available `Arial, Helvetica, sans-serif` stack. Bold destination names and tabular speed numerals approximate the clear hierarchy of Melbourne rail signage. **This is not Network Sans.** No proprietary font was downloaded, bundled or extracted from official sites. The previous external Google Fonts import was removed, so UI rendering does not depend on font-network requests.

The train pictogram is an original inline SVG, not an imported brand asset. UI hooks, keyboard controls and required action names remain intact, including Take the driver's seat (typographic apostrophe in UI), Continue saved service, Back to the cab, Open doors and Close doors.

## Verification boundary

`npx tsc --noEmit` passes after the redesign. A local headless Chrome screenshot attempt ended during browser launch with SIGABRT under the restricted process environment; no visual result was claimed from that attempt. Final menu/cab screenshot review belongs to the integrated browser pass.
