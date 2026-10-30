# Actual saved mesh transfer registry

Source hashes match the accepted forward checkpoint. A bounded offline audit
checks node identity, mass assignment coverage, unique positive-rest-length
bonds, exact interface-to-patch ownership, side-preserving triangle indices,
absence of bulk/volume cross-cut coupling and fixture nodes only on remainder.
Eight deliberate-error controls pass. This is a registry audit, not a complete
native mesh-quality/contact validation or an implemented asset converter.

Actual counts: 4032 nodes;34399 bonds,33996 bulk and403 registered interface;
47 patches; total assigned mass0.12167126547965468kg; minimum bond rest length
0.00021741602314809928m. Slice/remainder have1664/3840 surface triangles,
including448 cut triangles each. Fixture has25 remainder nodes. Pair-class
reference permits opposing cut faces and external blade/board/fixture contact;
it excludes only explicitly declared local same-side adjacency.

Critical transfer distinction: numerical_rest_gap_m is0 for the paired cut
faces, while original graph bond rest lengths are positive. The current evolved
surface-cohesive energy law is not automatically equivalent to attaching native
springs between coincident pairs. Neither direct zero-length spring construction
nor substitution of the403 old interface graph edges is a validated transfer of
that law. Native coupon construction should use its own explicitly finite test
geometry and disclose constitutive differences. Integrated tomato equivalence
remains pending. Do not change geometry/mass/patch energy to force a native pass.

Next: dedicated launch guard, with production guard preserved. Resource policy
inspected in rl/guard_benchmark.py:HOST_WARNING=3000000*1024,
HOST_STOP=2000000*1024; startup=max(HOST_START,10000000000),4GiBfreeVRAM;
runtimewarning1.5GiBVRAM/hard1GiBVRAM;three monitoring errors stop. Test pure
policy and dummy process lifecycle separately. Dry-run must launch nothing;
native execution remains disabled before upgrade and explicit authorization.
The native60second budget includes setup/JIT/cooking. Offline test worker remains
512MiB/45CPU/55alarm/60parent,one thread,bothlocks and actualquota reads.
