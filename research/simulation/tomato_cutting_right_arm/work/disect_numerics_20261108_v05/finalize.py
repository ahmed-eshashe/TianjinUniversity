from pathlib import Path
import json,datetime,hashlib,shutil
from zoneinfo import ZoneInfo
import numpy as np
W=Path(__file__).resolve().parent;O=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs');v04=W.parent/'disect_objective_damping_20261108_v04'
c=json.loads((W/'controls_result.json').read_text());r=json.loads((W/'comparison_result.json').read_text());a=json.loads((W/'candidate_result.json').read_text());f=json.loads((W/'candidate_fused_result.json').read_text());ref=json.loads((W/'reference_result.json').read_text());ref2=json.loads((W/'refined_result.json').read_text());ic=json.loads((W/'implicit_control_result.json').read_text());fc=json.loads((W/'fused_control_result.json').read_text())
assert c['passed'] and ic['passed'] and fc['passed'] and r['reference_refinement']['passed']
best=r['candidates']['candidate'];notes={k:float(np.mean([q[k] for q in a['profiled_steps']])) for k in ['force_wall_s','ground_wall_s','solve_wall_s','integration_wall_s']}
timing={'definition':'Saved end-to-end interval timing includes sampling but excludes final compressed-trajectory serialization. Output wall is sampling plus final serialization. They overlap; do not subtract to claim an exact pure stepping time.','adaptive_profile_synchronized_mean_step_wall_s':notes,'adaptive_pure_stepping_wall_s_per_sim_s_lower_bound':(a['total_wall_s']-a['output_wall_s'])/.02,'adaptive_end_to_end_wall_s_per_sim_s_upper_bound':(a['total_wall_s']+a['output_wall_s'])/.02,'robot_step_wall_s':None,'robot_note':'No robot instantiated; excluded rather than measured as a robot performance result.'}
(W/'timing_audit.json').write_text(json.dumps(timing,indent=2))
report=f'''Section 2 — numerical consistency and speed, 8 November 2026

DECISION
Three of four requested checks PASS within an isolated forward-only intact-bulk adapter. The fourth check, sufficiently fast integration, remains OPEN / COST FAILED. Do not mark the entire section complete. The bounded study is finished with the explicit cost blocker allowed by the saved NEXT_ACTION directive. No contact/cutting/training was started and no parameter, support or geometry was reduced to obtain a pass.

WHAT CHANGED
A separate CUDA numerical adapter uses float64 coordinates, velocities, constitutive forces and rest geometry. It uses the preserved original double mesh coordinates, identical 28,727 tets / 5,762 nodes, 25 fixed indices, physical masses (121.671g), constitutive coefficients, gravity and ground constants. Inverse rest matrices and inverse physical masses are recomputed in double instead of inheriting float32 rounding. Original v04 files and the production solver/checkpoint 6925 are unchanged. This is a versioned numerical implementation, not installation into the robot or evidence of autodifferentiation support.
The bulk law follows the corrected v04 source, including its diagonal-only Ic expression. No new constitutive correction, material calibration, fracture law or original spring/skin equivalence is claimed. The ground force reproduces the inherited infinite-plane proxy (radius .001m, ke1000, kd0, kf1000, mu.2); the finite board is not qualified here.

CHECK 1 — LOST POSITION INCREMENTS: PASS
The SAME double integration kernel used by the adapter preserves 100,000 tiny translation updates at dt1.5e-7s. Position error {c['translation_integration']['position_error_m']:.5g}m against analytic motion (limit1e-10m); velocity error zero. Fixed vertex remains exact. Unlike the old final-state float32 calculation, these are observed accumulated updates, not just representability estimates.

CHECK 2 — INDEPENDENT MOTION / RESET REFERENCES: PASS
Free fall position error {c['freefall_integration']['position_error_m']:.5g}m agrees with the known first-order Euler position bias; velocity error {c['freefall_integration']['velocity_error_m_s']:.5g}m/s. Analytic damped oscillator position/velocity errors {c['analytic_oscillator']['position_error_m']:.5g}m / {c['analytic_oscillator']['velocity_error_m_s']:.5g}m/s. Explicit repeated/reset trajectory maximum difference {c['reset']['repeat_max_error']:.5g}; fresh/reset state exactly matches. Separate controlled FEM fixture compares the implicit solve to an independent NumPy dense solve: position error {ic['position_error_m']:.5g}m, velocity error {ic['velocity_error_m_s']:.5g}m/s. Final fused fixture also matches the dense solve and clears all added solver/graph diagnostic state. Full-mesh graph/adaptive and allocation/reset controls pass. Forward reset support is not a claim of backpropagation support.

CHECK 3 — SMALL-FORCE PRECISION: PASS IN DECLARED RANGE
Independent NumPy float64 constitutive force at a seeded deformed state differs from CUDA by {c['independent_constitutive']['relative_error']:.5g} relative. Uniform translation produces exactly zero damping in the checked kernel. Affine strain-rate controls 1e-6,1e-4,.01,1 per second have force norms approximately 1.10e-8,1.10e-6,1.10e-4,.0110 N and absolute discrepancy near 7.5e-16 N. All pass the prospectively retained .1% relative criterion with a declared absolute floor1e-10N and nonpositive damping power. This establishes tested computational signal range, not experimental sensor accuracy. Prior float32 .01/s failure (.312%) remains FAILED in v04; it has not been relabelled.

CHECK 4 — STABLE AND PRACTICAL INTEGRATION: ACCURACY PASS, COST FAIL
One damping-aware route was implemented: IMEX Euler, nonlinear elasticity explicit and current-geometry corrected viscous forces implicit via constrained mass-scaled PCG. It preserves viscosity10. No frozen rest-J damping, coarsened mesh, changed material or skipped physical intervals is used. The four-node dense reference and symmetric PSD damping checks pass. Full-mesh explicit reference dt1.499925e-7s and refined dt7.499625e-8s both run20ms. Their max position difference {r['reference_refinement']['max_position_error_m']:.5g}m, material-force relative difference {r['reference_refinement']['max_material_force_relative_or_floor_error']:.5g}; independent reference-convergence limits pass.
The adaptive implicit candidate dt1.492537e-5s runs the same20ms in1,340 intervals. At matching1ms sample times versus the refined reference:
  max nodal position difference {best['max_position_error_m']*1000:.6f}mm <=.1mm PASS
  max nodal velocity difference {best['max_velocity_error_m_s']:.6f}m/s <=.005 PASS
  global material-force difference {best['max_material_force_relative_or_floor_error']*100:.5f}% <=5% PASS
  resultant fixed-support reaction difference {best['max_support_reaction_relative_or_floor_error']*100:.5f}% <=5% PASS
  near-zero force floor1e-6N is explicit; raw force errors/norms saved per sample
  true linear residual maximum {a['pcg_max_relative_residual']:.5g} <=1e-9 PASS
  sampled cells finite, min volume ratio {min(q['min_volume_ratio'] for q in a['rows']):.6f} >.1, board penetration0, fixed error0 PASS
The reaction is the resultant assembled material+ground force on fixed DOFs, not a sum of contact-force magnitudes or measured motor effort. Bounds are at saved sample times, not a proof for unsampled extrema. Fracture and separation are NOT TESTED in any comparison, so their equivalence is not inferred.

MEASURED COST AND MEMORY
                                      setup     interval wall   wall s/s
double explicit reference             {ref['setup_wall_s']:.3f}s      {ref['total_wall_s']:.3f}s        {ref['stepping_and_sampling_wall_s_per_sim_s']:.1f}
double explicit refined               {ref2['setup_wall_s']:.3f}s      {ref2['total_wall_s']:.3f}s        {ref2['stepping_and_sampling_wall_s_per_sim_s']:.1f}
adaptive IMEX (fastest valid route)    {a['setup_wall_s']:.3f}s       {a['total_wall_s']:.3f}s        {a['stepping_and_sampling_wall_s_per_sim_s']:.1f}
fused/gathered graph IMEX              {f['setup_wall_s']:.3f}s       {f['total_wall_s']:.3f}s        {f['stepping_and_sampling_wall_s_per_sim_s']:.1f}
Setup values above are warm-cache measurements; first extension compilation is separate and compiler logs are preserved. Output accumulation/serialization wall adaptive {a['output_wall_s']:.3f}s, fused {f['output_wall_s']:.3f}s. Interval wall includes sampling but excludes final compression; these values overlap and must not be added/subtracted as an exact disjoint decomposition. Even subtracting ALL recorded output gives an optimistic pure-stepping lower bound {timing['adaptive_pure_stepping_wall_s_per_sim_s_lower_bound']:.1f} wall s/s, still above the prospective120 target. Conservative adaptive end-to-end upper bound {timing['adaptive_end_to_end_wall_s_per_sim_s_upper_bound']:.1f} wall s/s.
Synchronized adaptive profile means per sampled step (not a new end-to-end benchmark): material force {notes['force_wall_s']*1000:.4f}ms, ground {notes['ground_wall_s']*1000:.4f}ms, damping linear solve {notes['solve_wall_s']*1000:.4f}ms, state integration {notes['integration_wall_s']*1000:.4f}ms. Actual robot stepping is excluded because this is an isolated bulk adapter. With 41.8 mean /64 max CG iterations per interval, repeated small linear-solver work dominates; this is not output saving or robot motion.
CPU peak RSS adaptive {a['peak_rss_kib']/1024**2:.3f}GiB, fused {f['peak_rss_kib']/1024**2:.3f}GiB. Torch GPU peak allocated adaptive {a['peak_torch_allocated_bytes']/1024**2:.2f}MiB /reserved {a['peak_torch_reserved_bytes']/1024**2:.2f}MiB; fused {f['peak_torch_allocated_bytes']/1024**2:.2f}MiB /reserved {f['peak_torch_reserved_bytes']/1024**2:.2f}MiB. GPU figures exclude driver/context and are not process-wide device peaks. Laptop mains was online and battery full during the final audit. The same-model double reference is the correct comparison: about {ref['total_wall_s']/a['total_wall_s']:.2f}x faster for adaptive IMEX. Do not advertise equal-accuracy speedup versus the different original spring/cohesion solver or old inconsistent float32 hold.

REJECTED IMPLEMENTATIONS / EVIDENCE
One early graph attempt failed equivalence because temporary external mass-scaling inputs lacked retained ownership and allocator reuse corrupted them. Its small residual described a corrupted system; it was REJECTED, not accepted as settled/stable physics. Saved under graph_unretained_inputs_failure with a separate failed verdict. Input ownership was fixed; sampling/allocation/reset controls then passed. A single-block fused PCG prototype passed accuracy but failed cost (~615 wall s/s); preserved under fused_single_block_cost_failure. Final parallel updates are accurate but still slower than the adaptive method. These execution variants implement the same single IMEX route; no other engine/physical-model branch was launched.

STOPPING DECISION / NEXT ACTION
Numerical correctness is substantially improved, but the practical integration gate is not achieved. Follow the predeclared stopping rule: stop this feasibility branch with a cost blocker. Do not run another long tomato hold, cut or training job simply because the20ms case is finite. A prospective higher-order or more strongly preconditioned implicit method is the next numerical proposal if the120 wall-s/s development budget is retained. It needs a new bounded contract and independent convergence checks; do not silently widen the speed target or change geometry/material. A coarse mesh/material proxy would change the model and needs the user's decision. No such change is implemented here. The original1mm/s late settling gate remains unchanged and untested by v05. Experimental validation remains pending.

PRIMARY RESEARCH CONTEXT
Implicit treatment of stiff forces and constrained linear solves is established in Baraff & Witkin, Large Steps in Cloth Simulation (1998): https://www.cs.cmu.edu/~baraff/papers/sig98.pdf . This is motivation for the narrower IMEX numerical investigation, not a claim to use their cloth constitutive model or to validate tomato cutting.

REPRODUCTION AND FILES
run.sh controls.py; run.sh implicit_control.py; run.sh compare.py --mode reference /refined /candidate /candidate_fused; run.sh analyze.py. Contract is prospective; results and independent checks are in *_result.json, full trajectories in *_trajectory.npz. Source and evidence hashes are in integrity.json. No run remains active after this report. The section's truthful checklist status is3/4 verified, speed gate open/cost failed, overall11/35 component checks.
'''
(W/'REPORT.txt').write_text(report)
next_text='''Next numerical decision — section 2 remains 3/4, not complete

Keep the higher-precision implementation and three verified controls. Best accurate IMEX route still costs about272 wall seconds per simulated second on the20ms intact-bulk case; even its optimistic output-free bound exceeds120. The final execution optimization is slower, so do not adopt it for its speed.

Do not launch another solver/parameter sweep, long settling, contact, cutting or training in this closed branch. Present one prospective higher-order/preconditioned integration proposal with an independent reference and finite cost exit if continuing numerical work. Any coarsening/material approximation or relaxed scientific contract must be identified as a change for the user's decision, not a successful completion of this failed cost gate.

Original checkpoint6925, robot/kitchen/grip and v04 failures preserved. Experimental validation pending. Full one-second settling remains section3 and has not passed.
'''
(W/'NEXT_ACTION.txt').write_text(next_text)
data=json.loads((v04/'EXECUTION_CHECKLIST.json').read_text());data['updated']=datetime.datetime.now(ZoneInfo('Asia/Shanghai')).isoformat();stage=data['stages'][1];stage['title']='Numerical consistency and speed';stage['note']='3 verified · integration speed gate failed';details=[
'PASS in isolated float64 numerical adapter. 100,000 observed tiny updates match analytic translation within 5.2e-13m; original geometry, masses, material and supports preserved.',
'PASS: independent translation/free-fall/analytic oscillator references; four-node dense implicit solve; full-mesh execution equivalence and reset/allocation controls. Added state clears on reset. Forward-only, not autograd qualification.',
'PASS in tested computational range: independent float64 force checks from ~1.1e-8N to .011N, with declared 1e-10N absolute floor. Old float32 low-signal failure is preserved; no experimental calibration claim.',
'COST FAILED / OPEN: accurate 20ms IMEX result meets 0.1mm/5% limits (0.00518mm, 0.677% material force) but costs ~272 wall s/s; optimistic output-free lower bound ~251 exceeds the prospective120 budget. Final execution optimization is slower. Bounded study stopped; do not mark this check or the full section complete.'
]
for i,item in enumerate(stage['items']):
    item['status']='done' if i<3 else 'planned';item['acceptance_or_limit']=details[i];item['evidence']='disect-numerics-20261108.txt'
    if i==3:item['verdict_label']='Cost failed · open'
data['counts']={k:sum(i['status']==k for s in data['stages'] for i in s['items']) for k in ['done','planned','pending','deferred']};data['latest_numerics']={'section_verified':3,'section_total':4,'cost_gate_passed':False,'report':'disect-numerics-20261108.txt','next_action':'disect-numerics-next-action-20261108.txt'}
(W/'EXECUTION_CHECKLIST.json').write_text(json.dumps(data,indent=2));lines=[data['title'],data['updated'],'11/35 verified component checks. Section2:3/4; speed gate failed/open. Counts are not engineering effort.','']
for stage in data['stages']:
    lines.append(stage['title'])
    for item in stage['items']:lines.extend([f"[{'x' if item['status']=='done' else ' '}] {item['task']} [{item.get('verdict_label',item['status'])}]",'    '+item['acceptance_or_limit']])
    lines.append('')
(W/'EXECUTION_CHECKLIST.txt').write_text('\n'.join(lines))
for src,dst in [('EXECUTION_CHECKLIST.json','disect-execution-checklist.json'),('EXECUTION_CHECKLIST.txt','disect-execution-checklist.txt'),('REPORT.txt','disect-numerics-20261108.txt'),('NEXT_ACTION.txt','disect-numerics-next-action-20261108.txt'),('comparison_result.json','disect-numerics-comparison-20261108.json')]:shutil.copy2(W/src,O/dst)
hashes={str(p.relative_to(W)):hashlib.sha256(p.read_bytes()).hexdigest() for p in W.rglob('*') if p.is_file() and p.name!='integrity.json' and '__pycache__' not in str(p)};hashes['../disect_objective_damping_20261108_v04/initial_audit.npz']=hashlib.sha256((v04/'initial_audit.npz').read_bytes()).hexdigest();(W/'integrity.json').write_text(json.dumps(hashes,indent=2));print(json.dumps(data['counts']));print('Section 2: three passes, cost gate FAILED/OPEN')
