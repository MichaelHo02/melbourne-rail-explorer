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

The full desk follows the three supplied photographs: one continuous charcoal instrument fascia above a curved silver worktop, a tall annunciator grid on the left, grouped switches and round instruments in the centre, a low left-hand power/brake handle, and a pale upright radio-style terminal with handset on the right. It is an authored interpretation of the VLocity reference beneath the existing HCMT exterior, not an HCMT equipment specification or a certified cab replica.

The working controls are the power/brake handle, passenger-door release and close, horn, and red mushroom emergency button. The handle is an accessible native range input with nine positions (four brake, coast, four power); its position follows the accepted simulation state. Pulling down selects power and pushing up selects braking. W/S remain the driving shortcuts, and the range also retains native keyboard adjustment.

The ivory speedometer needle and inset number show simulation speed. The two dark flanking dials explicitly show **power demand percentage** and **brake demand percentage**, rather than invented brake-pipe or reservoir pressure. Door interlock inhibits positive power demand; brake demand and the emergency latch remain visible with the doors open. The small right-hand instrument shows the route's modeled speed limit. Six annunciators report the accepted door, stopped, power, brake, overspeed and emergency states; the remaining cells are blank reference details.

Release and close are distinct commands for the same modeled passenger-door state; there is no simulated left/right selection. Release is available only while driving, stopped at the current station marker, with doors closed. Close is available only after the eight-second boarding dwell with doors open. The buttons' illumination follows accepted open/closed state, the adjacent text shows boarding time and door instructions, and D still toggles the doors through the simulation's checks. Emergency-button depression follows the emergency latch.

Climate, marker-light, wiper, exterior-light and auxiliary safety hardware, plus the radio keypad and handset, are subdued, noninteractive reference details. They have no click or hover affordance, never receive keyboard focus and are excluded from assistive navigation. The terminal screen shows real simulation next-stop, distance and service-status information; the enclosure does not imply a functioning railway radio. Coupling, fire protection, vigilance, lights and wipers are not modeled train systems.

Route, guide, camera and sound buttons have been removed from the desk, together with their old bindings and side-console styling. Route, guide, sound and pause actions belong in the header. Camera selection has been removed: driving uses the seated cab, with an automatic fixed platform camera only while stopped at a station with open doors; closing the doors restores the cab. The desk remains the operator control surface during this authored door-check feed. The station progress line is informational and no longer opens the route map. This keeps the desk's interactive controls specific to driving the train.

The desk occupies the bottom **240 pixels** of one fixed **1280 × 720** composition. The canvas and interface scale proportionally together for other window dimensions, with letterboxing as required; there is no compact/mobile reflow or alternate arrangement. The former cab/exterior-view, timetable date, formation and clock footer remains removed. Timetable provenance remains in the Guide. Map, guide and pause surfaces gate scene dragging.

Further operational cab modelling would require an HCMT-specific desk reference. Wipers and lights should affect the rendered scene; radio/PA should convey service information. Vigilance could support an optional more demanding driving mode rather than adding interruptions to the selected approachable experience. Coupling, fire systems and maintenance controls have no routine purpose in the current City Loop service.
