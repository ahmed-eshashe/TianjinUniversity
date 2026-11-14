Smooth tomato display — same approximate physics

Run launch_live.sh to open the isolated live Isaac Sim view. It starts paused so
that the intact appearance can be inspected. Use “Run / Pause cut” to start the
scripted cut, “Reset intact tomato” to reset, and “Smooth surface / particles” to
compare the new display with the unchanged collision representation.

Appearance changes
- Continuous, rounded red skin with smooth shading and restrained gloss.
- Green calyx and a gently curved stem.
- Warm flesh/gel colours and cosmetic seeds on exposed cut faces.
- Local cracks and separated pieces follow actual particle motion and broken
  bonds. No preset cutting plane, fake slice swap, or opening animation is added.

How the display follows the solver
The renderer uses cells clipped to the previous tomato exterior. Internal faces
are exposed only when their corresponding physical bond has broken. Nearby
particle displacements deform the surface. Interpolation groups split at broken
local connections; they cannot blend motion between disconnected pieces. The
stem is attached to one material piece. The raw particle view remains available.

Scope
This is a visual upgrade, not a new material model. The smooth skin fills the
particle gaps visually. Skin, calyx, gel colours and seeds are not new simulated
tissues or colliders. The physical approximation, collision stops, cutting law,
reset logic and headless learning interface remain the v28 implementation.
Additional surface rendering costs display time; it is not part of headless RL.
The original robot, kitchen and DiSECt setup are not modified.

Evidence
reports/build.json records the reference source hashes.
reports/surface_checks.json checks intact, partially cut, two-piece and four-piece
states, visible-face provenance, finite geometry and absence of cross-piece
interpolation. reports/live_check.json records the live appearance test once run.
The definitive viewer is view_live.py; the initial generator is retained under
reports/prepare_view_initial.py only as implementation history.
