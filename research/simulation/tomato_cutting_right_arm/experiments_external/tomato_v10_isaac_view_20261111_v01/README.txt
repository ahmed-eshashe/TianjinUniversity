Visible Isaac Sim replay of the v10 GPU blade-motion block test.

Reopen with:
bash /home/omen/Documents/Codex/experiments/tomato_v10_isaac_view_20261111_v01/launch_view.sh

The separate display-only scene loops automatically. Use Pause / Play, Restart,
Inspect final gap, Block close-up, Whole knife, or Knife surface on/off.

Gold line: actual finite straight cutting edge from the original saved CAD.
Blue wireframe: original full knife CAD. Teal and orange distinguish eventual
pieces; a color boundary does not by itself indicate a crack. Spatial positions
and the final gap are not amplified. The block is 12 mm across.

This replays 14 saved GPU traversal states plus the withdrawn and opened states.
Continuous material basis fields are tessellated for display. Intermediate
rendered frames interpolate the saved positions for viewing, not physics.
Withdrawal is an instant transition to the saved clearance-query pose: there
is no integrated withdrawal/contact trajectory. The final 1 ms opening is shown
by endpoint interpolation and comes from auxiliary +/-0.4 N loads, not the knife.
The saved final gap is 0.45054 mm. No mechanics were advanced to build this view.

This is a geometric cutting component test, not a physically qualified tomato
slice. Cutting forces, fracture energy, general deformation and RL remain open.
No original Isaac/DiSECt robot, kitchen, grip, solver or evidence was modified.
Close this viewer before starting another heavy Isaac Sim application.
