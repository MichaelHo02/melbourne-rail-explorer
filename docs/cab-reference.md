# Cab controls and approachable driving

The three cab photographs supplied by the user on 20 September 2026 are VLocity-style references, including a visible car number 1220 in the first photograph. They are not an HCMT equipment specification. The photographs are not included in the public repository. The current game continues to depict a seven-car High Capacity Metro Train with explicitly simplified, cab-inspired controls.

## Observed reference controls

The clearest front-facing photograph shows a combined power/brake handle at the driver's left, analogue air/brake-pressure instruments, speed indication, separate left/right door release and close buttons, vigilance, uncouple, fire extinguish, parking brake, marker lights, exterior lighting, horn, windscreen wiper speed/mode, climate controls, an annunciator bank and a radio/keypad. Small unreadable labels and unlabeled red buttons are not assigned speculative functions.

The ATSB's VLocity investigation RO-2020-007, section “Train 8185 braking system” and Figure 18, verifies a centre-off power/brake controller: six power notches when pulled back, continuous service braking when pushed forward, and emergency braking at the forward extremity. This is VLocity-specific evidence, not justification to copy its handle positions, engine behaviour or notch count into an HCMT model.

- [ATSB VLocity power/brake controller and braking system](https://www.atsb.gov.au/investigations/ro-2020-007)
- [Victorian Government HCMT project](https://www.vic.gov.au/high-capacity-metro-trains-project)
- [Metro's HCMT cab simulator training reference](https://www.metrotrains.com.au/drivers-getting-up-to-speed-for-new-trains/)

## Current game treatment

The playable layer retains four power and four brake notches, coast, door interlock, emergency brake and horn. These are approachable game controls, not verified fleet calibration. The training stop guide integrates the same acceleration, braking ramp and authored route gradients as the simulation. Its prediction is advice for this game's stop marker, not an operational braking curve. Door animation and mechanical audio follow the simulation's accepted actions and pause clock.

## Photo-inspired driving desk

The bottom driving interface now uses the supplied photograph's curved silver moulding, charcoal instrument fascia, left-hand power/brake handle, round analogue instruments, illuminated blue passenger-door control and red mushroom emergency button. It is an authored visual interpretation of the VLocity reference beneath the existing HCMT exterior, not a claim that the photo depicts an HCMT or that this is its certified desk layout.

The handle remains an accessible native range input with nine positions (four brake, coast, four power); the physical handle moves with the accepted simulation state. Pulling down selects power, pushing up selects braking. W/S keyboard actions are unchanged. The speed needle and inset numeric display use simulation speed. The secondary dial explicitly reports **demand percentage**, switching its label between power, brake and neutral effort; it does not invent brake-pipe or reservoir pressure. Door interlock inhibits positive power demand in the display; brake demand and the emergency latch remain visible with the doors open. Door illumination follows accepted open/closed state; the same button shows boarding countdown and close/open instructions. Emergency-button depression follows the emergency latch.

The desktop desk occupies 174 pixels at the bottom of the playfield, with a 166-pixel compact arrangement. The previous cab/exterior-view, timetable date, train formation and clock footer has been removed at the user's request. Timetable provenance remains in Controls and information. There are no decorative switches pretending to operate safety, maintenance, lighting or pressure systems.

Further operational cab modelling would require an HCMT-specific desk reference. Wipers and lights should affect the rendered scene; radio/PA should convey service information. Vigilance could support an optional more demanding driving mode rather than adding interruptions to the selected approachable experience. Coupling, fire systems and maintenance controls have no routine purpose in the current City Loop service.
