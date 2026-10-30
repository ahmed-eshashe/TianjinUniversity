# Native contact coupon source: partial preparation only

Read installed VBD gripper triangle/grid examples, ModelBuilder.add_body,
add_particle,add_triangle,add_spring,add_shape_mesh and ShapeConfig.configure_sdf.
Prepared lazy-import candidate construction in rl/tomato_native_coupon.py using
those exact API shapes. The CLI only prints a description and pending items;
default build call refuses before any engine import. Six source/schema/refusal
checks pass. The function was NEVER called with authorization and no simulator,
Newton, Warp or pxr was imported. This is not a native-build compatibility pass.

The tetrahedron is a small synthetic nonfracturing contact coupon: three fixed
base nodes, one free node, finite springs, explicit surface triangles. Triangle
FEM stiffness is set to zero to avoid silently double-counting membrane energy.
There is no native volume term, damage law or equivalence to the accepted tomato.
Synthetic stiffness/mass are diagnostic proposals, not calibrated material data.
Full-surface contact uses VBD and an explicitly capped128-resolution mesh SDF.
That cap does not prove thin-edge accuracy; required SDF comparisons may refuse
this resolution. No thick box substituted for the real blade.

Builder needs a complete explicitly measured real-blade SI export; its schema
checker cannot establish that a supplied hash matches actual geometry. Actual
asset/transform/hash validation is still pending. The inspected source scene
rl/scene/minimal_benchmark.usda contains an ASCII CollisionBlade mesh with
literal point/index arrays. Its parent/mesh transforms and stage units must be
resolved without pxr imports (for example a narrowly supported authored-file
extractor with explicit rejection of unsupported USD constructs). Do NOT copy
raw point arrays as metres or use assets/knives/RL_Proxy_Knife.obj merely because
it is easier; the current grasp uses a specific CollisionBlade representation.
Original blade measured dimensions in tomato_blade_damage.py are
length0.26593121886253357m,height0.0504381824284792m,
max_thickness0.00760862766765058m; its synthetic8mm wedge bevel is not a measured
full native cutting-edge profile. Verify actual collision geometry and frame.

The future worker also needs initially separated placement, a safe prescribed
trajectory/state update, bounded traces, native reaction/energy collection,
contact capacity completeness, reset and the two-piece contact case. Current
build returns model/solver/state objects only and has no runtime stepping route.
Native execution remains disabled until after upgrade and explicit approval.

NEXT P6b real blade SI export and trajectory, then native soft-reaction extraction
source review. Preserve production assets/controllers and all baseline hashes.
Do not use rigid-only collect_rigid_contact_forces as deformable reaction proof.
