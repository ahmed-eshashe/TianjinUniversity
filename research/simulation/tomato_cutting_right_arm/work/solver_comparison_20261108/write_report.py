from pathlib import Path
import json
w=Path(__file__).resolve().parent;d=json.loads((w/'comparison.json').read_text());c=d['current'];tim=c.get('explicit_timers_repeat',{})
text=f'''SOLVER FEASIBILITY COMPARISON — 2026-11-08

Decision: do not use the current implementation as the primary learning backend at its measured speed. Keep Isaac Sim, robot, kitchen, fixed grip and motion interface. No replacement engine has been adopted. The production run is intentionally checkpointed at step 6925, not finished or failed through loss of data.

These are laptop feasibility measurements, NOT equal-accuracy speedups. Different objects, material laws, resolutions, speeds and contact algorithms are involved. All measurements are forward-only and headless; they do not measure RL training or reverse-mode gradients. Experimental tomato validation remains pending.

CURRENT SOLVER
Four accepted coupled intervals from run17 checkpoint 6400: 0.0066667 seconds of simulated time. First profile: {c['profile_wall_s']:.3f} seconds wall time, or {c['wall_s_per_sim_s']:.0f} wall seconds per simulated second. Startup/pickup/approach replay excluded. cProfile overhead included.
Nonlinear solve: {c['nonlinear_solve_s']:.3f} s. Contact-packet geometry refresh: {c['contact_packet_refresh_s']:.3f} s. Cut eligibility overlap: {c['cut_eligibility_overlap_s']:.3f} s. NumPy/text/archive-copy writes: {c['numpy_write_s']+c['text_write_s']+c['copy_file_s']:.4f} s.
Explicit repeated segment timers: {json.dumps(tim)}
30,052 Warp array-to-NumPy calls consumed 28.316 cumulative seconds, including GPU synchronization. This overlaps the solve/contact timings and must NOT be added to them. 298 linear solves in four intervals. These data identify nonlinear solving, contact geometry and host/GPU synchronization as priorities, not the kitchen or recording files.
Model: 4,032 nodes, 16,291 tetrahedral cells, 33,996 springs, 47 cohesive patches; custom bulk spring/volume and cohesive law. Float64 material state, material interval 1/600 s, native robot 1/2400 s. All 47 material connections remained intact in this loaded withdrawal sample. This is not a full slicing-time benchmark. Checkpoint restore audit passed; physical accuracy is not established by slow convergence.
Observed process memory about 4.2 GiB RAM and 2.1 GiB GPU (includes Isaac Sim). Direct writers mostly hit OS buffering, not forced durable disk flushes.

DISECT
Official basic_cutting.py prism configuration and SlicingMotion, same 5 s duration and 1e-4 s timestep, GUI removed and gradients disabled. Original ANSYS mesh loaded via its current reader API. 1,011 source nodes / 4,536 tets; after cutting preprocessing: 1,187 nodes / 4,950 tets / 304 cutting springs. Published prism, not our tomato; prescribed knife, no robot coupling.
Two runs advanced all 50,000 steps in 9.865 and 11.193 seconds: 1.97–2.24 wall seconds per simulated second. Setup was separately measured; initial CUDA compilation excluded. Observed process memory ~2.0 GiB RAM, 224 MiB GPU; Torch peak allocation ~82 MiB is a different, narrower metric.
Peak net resultant in first run: 1.525 model newtons; peak sum of contact-force magnitudes: 63.262. Do not confuse these quantities or compare them directly to our different specimen/law. Both runs sampled finite states. Final repeated mesh had no inverted tets (minimum signed volume ratio 0.9942); this is a final-state check, not all-step convergence validation.
Compatibility FAIL: both runs reported a native mesh-cutting failure flag and segfaulted in garbage collection after writing results. The additional native mesher log was empty. Underlying cause is unresolved; do not assume this is harmless teardown. Repeat final positions differed by up to 0.340 mm; 303 versus 302 of 304 spring stiffnesses reached zero. Independent detached-component qualification was not established. This is promising provisional throughput, not an adoption pass.
Compatibility changes: Python collections/AST updates, removal of invalid compiler flag, CUDA sm_120 target, current ANSYS reader, modern dependencies. Original material settings were not tuned to pass. Full patches and logs retained.

ROBONINJA MLS-MPM
Original Taichi physics and knife geometry/action implementation. Forward benchmark adapted from the provided block scene: 200 x 175 x 150 mm food block, particle density 8e6, quality=2, 128^3 grid (7.8125 mm spacing), dt=6.6667e-5 s, 30 substeps per action. No rigid core, external support fixture, renderer or loss; floor represented by upstream grid boundary. This is not the unchanged full core-cutting notebook and not a tomato.
Three runs completed 60 actions / 0.12 simulated seconds:
- Straight nominal block: 42,000 particles; warmed 23.87 wall seconds per simulated second.
- Curved planar translation: 42,000 particles; warmed 23.58 wall seconds per simulated second.
- Straight 0.8-scale block: 21,504 particles; warmed 17.89 wall seconds per simulated second.
First action/JIT compilation excluded from warmed timing and retained in result JSON. Nominal memory ~4.74 GiB GPU; smaller block ~4.17 GiB. RAM ~0.9–1.0 GiB. Default backward-capable dense grid alone needs ~7.28 GB before particles and other buffers. We disabled only grid gradient allocation for these forward tests; no training-memory claim follows.
All sampled states finite and all processes exited normally after compatibility fixes. However, particles passed below the configured grid-boundary height by approximately 7.5–8.4 mm transiently. This configuration does not meet our board-clearance contract. There was one dominant proximity-connected particle component after each test at several radii; no detached slice proved. Proximity connectivity is not a fracture criterion and nearby disconnected material can still count as connected.
The upstream force field accumulates SUMS OF CONTACT IMPULSE MAGNITUDES. Divide by dt only to obtain the sum of force magnitudes under these model units; it is not a net force or six-axis reaction. Material density/mass conventions differ from the tomato, and knife friction is zero in the supplied material table. A robot reaction adapter and calibration are required.
The curved and size-changed runs demonstrate limited path/geometry flexibility without pre-inserting a cutting plane. The supplied action interface remains planar; unrestricted six-dimensional blade motion was not tested. MPM topology flexibility is not equivalent to a calibrated skin/pulp fracture law or durable separation.
Compatibility changes: removed obsolete Taichi packed flag, explicit structure-member resets for current Taichi, static None comparison update, forward-only grid allocation. Patches recorded. No changes to our production model.

RECOMMENDED NEXT ACTION
Prefer a bounded DiSECt hardening and same-tomato feasibility test for planar learned slicing: resolve native meshing/exit faults, inspect repeatability, then compare force, geometry and separation on an explicitly specified tomato mesh. Do not couple it to the robot yet. Keep MPM as the candidate for broader path freedom if willing to develop a tomato-appropriate material/contact model and manage resolution/memory. Optimizing host transfers alone is not a demonstrated route to practical RL throughput for the current solver.
The benchmark does not authorize replacing the research tomato with either of these test objects. No learning, full-cut claim or physics adoption occurred.

Evidence: comparison.json; current_profile*/steady_profile.pstats; current_profile3/timings.json; disect*_result.json; disect_stability_assessment.json; robo_*_result.json; robo_separation_assessment.json; memory_samples*.json; *_compatibility.patch; manifest.json; benchmark_scope.json.
Sources: https://github.com/NVlabs/DiSECt ; https://diff-cutting-sim.github.io/ ; https://github.com/real-stanford/roboninja ; https://arxiv.org/html/2302.11553 ; https://arxiv.org/html/2404.02569v2 .
'''
(w/'REPORT.txt').write_text(text)
