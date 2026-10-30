# Initial backend decision — source inspection only

Prefer an isolated Newton VBD full-surface contact coupon as the first candidate
experiment. This is preparation for a future native runtime experiment, not a
selection validated by execution and not a replacement for the CPU PhysX robot.

The actual installed collision pipeline documents full soft surface edges and
triangle interiors against rigid SDFs at collide.py:1276–1284. It requires rigid
SDFs and only VBD consumes these records. VBD reads spring rest lengths,
stiffness and damping in its force/Hessian accumulation at solver_vbd.py:3203–3218.
The semi-implicit solver documents unsupported equality/mimic constraints at
solver_semi_implicit.py:51–53. Its use as a whole-hand drop-in is excluded.

Important source finding: VBD exposes coupling_supports_full_surface_soft_contacts
at line 1205 and coupling_harvest_proxy_wrenches at line 1271 (approximate; verify
exact symbol location before implementation). The latter explicitly harvests
CONTACT-ONLY proxy wrenches, rather than inferring all feedback from momentum.
These are leads to inspect, not proof of supported CPU PhysX-to-Newton coupling.
Next trace the coupling owner, spatial-vector component order, moment reference,
force versus impulse cadence, proxy history/reset, and any available contact
collector for prescribed rigid motion. Do not use private hooks blindly.

The pipeline also warns that per-vertex/per-edge self-contact candidate buffers
can silently drop excess pairs at collide.py:2002–2005. A positive runtime result
needs completeness evidence, not merely absence of an overflow exception.

All 16 source entries from the October 19 capability audit are byte-identical
and present. Preserve that audit; refreshed hashes are recorded separately.
Add collide.py and VBD source hashes below for this decision. No solver imports,
GPU warmup, native execution or training occurred.

Read-only hardware query: NVIDIA GeForce RTX 5060 Laptop GPU, total 8151 MiB,
free 7227 MiB at inspection. These are a snapshot, not a future resource lease.
The expected host upgrade is 32 GB; remeasure host and GPU reserves after it.

Next: complete the source-grounded coupling decision and define backend-neutral
sample/work/reset contracts. Native contact, fracture, release, hand coupling
and training readiness remain unverified.
