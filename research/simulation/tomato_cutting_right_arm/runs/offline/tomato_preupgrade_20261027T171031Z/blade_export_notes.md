# Authored collision blade export — actual geometry, scoped reader

The current phase3 layer ALREADY bakes the original uniform0.76249998scale into
CollisionBlade points and replaces the knife body transform with a unit-scale
rigid pose. Copying minimal_benchmark's raw points would therefore be wrong.
The new narrow ASCII reader uses phase3's74points and the base144triangles,
requires metersPerUnit1, validates the phase3 rotation and its single-op stack,
and rejects blade-local transforms/composition it does not support. World pose
is intentionally excluded from blade_local coordinates. No pxr imports used.

Measured local bounding dimensions from this export are
[0.26593122,0.050438182,0.007608628]metres. They agree within1e-8m with the existing
saved wedge's blade dimension reference (comparison tolerance for text/float
rounding only, not a modified physical acceptance threshold). Four tests pass:
local-frame extraction, scaled/extra transforms refusal, missing/wrong units and
actual source dimension comparison. Exact source hashes and raw authored indices
are retained in blade_export.json. This is not a generic USD composer.

Important representation distinction: the original PhysX CollisionBlade requests
convexHull approximation. The exported authored triangle surface is not a
validated convex-hull/SDF equivalent. Full USD runtime composition, stronger
layers, native mesh/SDF topology, zero surface accuracy and actual contact remain
unverified. This geometry must not silently replace the production robot asset.
The candidate isolated Newton test can explicitly disclose triangle/SDF usage.
Schema validation checks the form of a hash, not truth of arbitrary supplied
geometry; the dedicated launcher must verify the exported file hash and its exact
source assets before runtime. Freeze source/recipe/config provenance together.

NEXT: P6c initial separated placement and bounded prescribed trajectory; use the
real exported coordinates with a declared rigid local-to-world orientation.
The shape's local x is length, local y is width/height and local z is thickness.
A cyclic rotation mapping local z->world x, local x->world y, local y->world z
is right handed if useful for the coupon. Compute start from transformed bounds
with positive clearance, then bounded indentation/withdrawal. Validate surface
watertightness/orientation and SDF error budget separately; bounding boxes cannot
prove the cutting edge/profile or contact completeness. Native soft reaction
collector/source integration and the two-piece case are still pending.
