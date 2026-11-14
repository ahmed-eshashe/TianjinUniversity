Robot + kitchen + approximate tomato — isolated integration v31

The existing Isaac/DiSECt/research files remain intact. This is a separate launcher and scene layer.

User-authorized blade: original handle, hand grip, fixed mount and robot retained;
a visible 120 mm straight triangular-prism blade replaces the curved CAD blade.
The visible blade matches the blade used by the approximate material solver.
Original 0.25 kg tool mass, centre of mass and inertia are retained as an explicit
controlled-tool approximation, not a new measurement of this replacement blade.

The robot first closes its fingers on the supported handle, transfers the ideal
fixture attachment to the ideal hand mount, lifts, approaches, and follows a
scripted slicing stroke. It is not a friction-only grasp or a learned policy.
The left arm and backward-elbow posture are retained. The tomato remains on the existing board. The empty pickup cradle retracts
110 mm after the knife is lifted. Its visible posts and native collision bodies
move together; this is an ideal kinematic support actuator in this version.
Withdrawal is horizontal: along the blade first, then towards the robot body.

Material: unchanged v28 approximate elastic bond network, with the v30 smooth
slicing motion and v29 cosmetic surface. The bottom particle layer stays fixed;
it is not held by the left hand. Skin, seeds and calyx are display details.
The fracture law is synthetic and experimental tomato validation is pending.
This is not DiSECt, official CRESSim or a validated continuum tomato model.

Coupling: the measured native knife poses, rather than desired joint targets,
drive material contact. The material integrates at 0.1 ms with its existing
0.05 ms fallback. The validated demo uses a 1 ms exchange interval. Its accumulated
force and moment are transformed to the native tool COM and applied once in
the next native interval. The one-interval delay is explicit. This is not a
motor-work validation. The 2 N summed blade-load stop and 0.1 mm particle
penetration stop remain active. These do not certify continuous surface contact.

Validation results are stored under runs/ and reports/. A failed run is retained;
only integration_result.json with pass=true establishes that run's stated scope.
Native robot stepping/rendering is additional cost; the standalone batched
material's RL throughput must not be quoted for this full kitchen simulation.

Verified complete cycle: see RESULT.txt and runs/cut03_margin.
Launch:
  bash /home/omen/Documents/Codex/experiments/tomato_robot_integration_20261113_v31/launch_integrated.sh

Press Play in Isaac Sim when the scene is ready. Pause pauses the controller.
The completed scene stays open. To repeat from a fresh robot and tomato state,
close this window and launch again. Do not run two Isaac Sim windows together.

Both the headless complete cycle and the visible robot/kitchen cycle passed.
The latest visible result is runs/live_20261113_185712/integration_result.json.
The two portions remain close together because their bottom support is fixed.
The cosmetic straight-blade mesh follows the measured native knife pose; its
physical collider remains attached to the original tool body.
