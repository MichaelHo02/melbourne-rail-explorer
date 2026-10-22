# Driving simulation review

The first playable service uses an authored approximate City Loop alignment, not surveyed track, signalling, or a real train's performance envelope. `src/data/route.ts` preserves that provenance. No official GTFS replacement was attempted during this bounded correctness review: it would require coordinated changes to station and environment placement, and would not establish surveyed gradients or signalling.

## Corrected defects

- Opening doors below the permitted 0.05 m/s stopping tolerance now sets speed to zero immediately. Previously a snapshot taken before the next simulation frame contained open doors and nonzero speed and could not be restored.
- Non-finite controller input and non-positive/non-finite timestep input no longer poison the simulation state.
- Save restoration now rejects impossible open-door platform positions, exhausted station indices in active services, moving completed services, extreme acceleration, excess stop history, unknown station names, and inconsistent served/missed stop errors. Rejected saves leave the active service unchanged.

## Verification

`npm test -- --run tests/simulation.test.ts`: 13 tests passed. Regression coverage includes traction/door interlocks, boarding dwell, accuracy recording, emergency stop and release, pause freezing both boarding and controls, atomic save rejection, stop overruns, and an entire six-visit service driven by a simple feedback controller.

The route tests verify ordered stops, metre-scale positional continuity, unit tangents, coincident loop endpoints, and a grade magnitude below 5.5 percent. This bound establishes that the authored profile remains usable by the arcade traction model; it is not a claim about real City Loop grades.

The existing `src/main.ts` accumulator advances simulation in 1/60 second steps and caps frame accumulation at 0.1 seconds. This avoids giant physics steps after a tab stall. Dynamics intentionally omit reverse running and hold a stopped train against downhill creep with a neutral/braking controller, consistent with the approachable controls brief.

These are simulation and route checks only. They do not establish visual route accuracy, native Blender provenance, browser controls, or real operational training suitability.
