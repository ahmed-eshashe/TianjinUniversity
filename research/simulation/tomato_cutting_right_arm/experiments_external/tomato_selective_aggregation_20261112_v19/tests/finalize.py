"""Assemble measured trial results and update only the candidate status banner."""
from pathlib import Path
import json,datetime,hashlib,re,shutil
W=Path(__file__).resolve().parents[1]
OUT=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs')
STATUS=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm/docs/rl/ASTRA_HIGH_TOMATO_MODEL_EXECUTION_STATUS_20261110.json')
def read(n):return json.loads((W/n).read_text())
now=datetime.datetime.now().astimezone().isoformat()
responses=[r for r in read('weighted_response.json')['rows'] if r['accepted']]
old=read('cost.json');cached=read('cost_cached.json');control=read('cache_control.json')
rates={case:max([r for r in old['rows']+cached['rows'] if r['case']==case],key=lambda x:x['aggregate_50Hz_step_equivalents_s']) for case in ['intact','oblique','corner']}
preservation=read('preservation.json')
assert preservation['passed'] and read('gpu_validation.json')['status']=='pass' and control['status']=='pass'
stats={
 'max_position_mm':max(r['cross_model_at_candidate_dt']['position_m'] for r in responses)*1000,
 'max_weighted_velocity_mm_s':max(r['cross_model_at_candidate_dt']['velocity_mass_weighted_RMS_upper_bound_m_s'] for r in responses)*1000,
 'max_local_velocity_mm_s':max(r['cross_model_at_candidate_dt']['velocity_m_s'] for r in responses)*1000,
 'max_internal_force_RMS_error_percent':100*max(r['cross_model_at_candidate_dt']['force_relative'] for r in responses),
 'max_energy_residual_percent':100*max(r['energy_drift_relative'] for r in responses)}
q={
 'version':'v19','updated':now,'decision':'component_accuracy_pass_material_cost_marginal_full_RL_not_qualified',
 'stage_A':'pass_component_scope_after_explicit_velocity_norm_approval',
 'stage_B':'GPU_equivalence_pass_fixed_topology_cost_screen_complete',
 'stage_C':'report_complete_no_physical_cut_or_engine_expansion',
 'simulation_running':False,'rl_ready':False,'physical_cut':False,'physical_tomato_model_completed':False,
 'current_setup_changed':False,'production_adopted':False,'experimental_validation':'pending',
 'approved_velocity_norm':read('contract.json')['velocity_criterion_approval'],
 'selected_support_threshold':1e-8,'selected_test_timestep_s':12.5e-6,
 'algebra_checks_passed':sum(read('algebra_1e-08.json')['checks'].values()),
 'dynamic_block_cases_passed':len(responses),'history_and_larger_controls_passed':sum(read('weighted_extra.json')['checks'].values()),
 'strict_GPU_checks_passed':sum(read('gpu_validation.json')['checks'].values()),
 'accepted_small_block_metrics':stats,
 'best_fixed_topology_50Hz_equivalents_s':{k:v['aggregate_50Hz_step_equivalents_s'] for k,v in rates.items()},
 'paired_corner_batch8_speedup':control['rows'][1]['paired_speedup_medians'],
 'sustained_corner_batch8_50Hz_equivalents_s':control['sustained']['equivalent_50Hz_steps_s'],
 'minimum_actual_environment_steps_s':100,'preferred_actual_environment_steps_s':500,
 'throughput_scope':'60 mm cube, 6 mm grid, float32 GPU, 12.5 us substeps, 0.1% compression and 0.05% shear; material only. Best rates use eight independent copies. No changing geometry, blade contact, paid fracture, observations, resets, robot, policy or rendering.',
 'remaining_obstacles':['Material-only throughput around 100/s leaves insufficient demonstrated headroom for the complete environment.',
 'Full CPU cut geometry rebuild plus aggregation costs roughly 1.1-1.5 s per body in measured cases; GPU reconstruction adds setup cost.',
 'Small fragments without a compatible full root retain independent nodes and potentially small timesteps.',
 'General crack-front root locality, temporal/spatial convergence under physical cutting, contact/recontact and paid fracture remain unqualified.'],
 'preservation':preservation,'report':str(W/'REPORT.txt'),'next_action':str(W/'NEXT_ACTION.txt')}
(W/'qualification.json').write_text(json.dumps(q,indent=2))
(W/'status.json').write_text(json.dumps(q,indent=2))
table='\n'.join(f"{k:9s} {v['batch']:5d} {v['aggregate_50Hz_step_equivalents_s']:12.2f} {v['median_wall_s']*1000:14.2f}" for k,v in rates.items())
report=f'''V19 SELECTIVE AGGREGATION — COMPLETED ISOLATED TRIAL
Updated: {now}

RESULT
The selective numerical correction passes the tested component accuracy gates under the user's explicitly approved material-weighted velocity norm. Strict CPU/GPU equivalence also passes. A single force-caching optimization improves the difficult corner-cut throughput substantially. The complete RL speed gate is NOT passed: material dynamics alone are approximately 100 equivalent 50 Hz steps/s, excluding every cut update, blade contact, robot and policy. No new physical tomato cut was run. Isaac/DiSECt and all 1800 protected files are unchanged.

WHAT CHANGED
The v18 rule constrained all cut-only nodes and distorted force response. V19 retains substantially supported cut-region nodes, extending only very weakly supported ones (original row-sum nodal mass / rho h^3 < 1e-8, no full-tetrahedron support). Exact reduced inertia A^T diag(m) A is retained, never relumped. Material law remains compressible neo-Hookean E=100 kPa, nu=0.4, rho=1000 kg/m^3. This is an isolated experimental virtual-node FEM adaptation, not official CRESSim or DiSECt and not a calibrated tomato.

APPROVED ACCURACY CONTRACT
The strict original local-velocity failures are preserved. The user then approved a mass-weighted velocity check for cross-representation, projection and timestep comparisons. We use a conservative bound: the maximum vertex error in each convex material polyhedron, squared and weighted by actual material mass, followed by a square root. There is no cancellation of opposing velocities. The bound must be <=5 mm/s. Maximum local velocity remains visible; every-point position at sampled times, force and energy criteria are unchanged. Strict same-operator CPU/GPU tolerances remain position 1 micrometre, velocity 0.1 mm/s, deformation-gradient error 1e-4.
No blade-force or penetration tolerance was relaxed. Those physical checks have NOT yet been exercised by this bulk-material candidate.

VERIFIED COMPONENT RESULTS
- 62 algebra controls at the final 1e-8 selector pass: positive reduced mass, rank, affine reproduction, force/energy gradients, objectivity, force/torque and selected fragment-independence checks.
- Eight 24 mm block response cases pass at 12.5 us, with 6.25 us candidate and 0.25/0.125 us original-reference controls: intact, oblique, partial, additional signed-diagonal direction, and four near-corner offsets (130, 10, 1 and 0.1 micrometres). Comparisons cover 20 ms at 1% compression plus 0.5% shear, sampled every 1 ms. The 25 us trials were rejected and remain recorded.
- Worst accepted cross-representation position error: {stats['max_position_mm']:.6f} mm (limit 0.1 mm).
- Worst material-weighted velocity bound: {stats['max_weighted_velocity_mm_s']:.3f} mm/s (limit 5 mm/s).
- Largest pointwise velocity difference: {stats['max_local_velocity_mm_s']:.3f} mm/s. This would FAIL the original 5 mm/s pointwise contract. The norm approval is material to the result; this is not an every-point velocity pass.
- Worst internal nodal-force RMS error: {stats['max_internal_force_RMS_error_percent']:.3f}% (limit 5%, with the existing 1e-5 N absolute floor). These are INTERNAL material forces, not measured knife forces or cutting work.
- Worst sampled numerical energy residual: {stats['max_energy_residual_percent']:.4f}% (limit 5%). No damping or energy correction is added.
- Loaded projection through partial/completed cuts and four geometric cut slots, restart, and short 60 mm block comparisons at 6/3 mm grids pass their recorded checks. Larger-block windows are 5/2 ms, not a full episode. After the third/fourth geometric cuts, 10/18 weak nodes lack a suitable root and remain independent; their later dynamic timestep is not qualified.
- Eight strict CPU/GPU checks pass, including external-force direction change, three-environment independence and loaded restart. Maximum field discrepancies in the five trajectory cases are about 1.83 nm position, 0.0128 mm/s velocity and 1.21e-6 deformation gradient.

GPU COST AND EQUIVALENT OPTIMIZATION
GPU: RTX 5060 Laptop, 8 GiB, mains power, headless. Fixed-topology timing uses a 60 mm cubic block at 6 mm grid spacing, 12.5 us substeps and 0.1% compression + 0.05% shear. This timing load is lower than the 1% accuracy fixtures. Resolution, shape and physics differ from a full tomato/knife scene; do not claim an apples-to-apples speedup over the research cutting solver.
One 50 Hz equivalent step means advancing ONE body's material state by 20 ms (1600 substeps). Batch throughput counts all bodies. It is not rendering FPS or full environment transitions.

Case      Batch   Equiv steps/s  Batch wall ms / 20 ms sim
{table}

Intact: 6000 regions / 1331 nodes. Oblique: 6840 regions / 1661 original nodes / 1659 reduced nodes. Corner: 7338 regions / 1837 original / 1752 reduced nodes, 85 extended nodes, largest mass block 24. Three identical-state timing repeats; setup/reset/export excluded, state backup and validity synchronization included.
The original fused kernel regathered force repeatedly within coupled mass blocks. Caching each force once changes no equation. A matched alternating-order comparison over five repeats at batch eight improved corner throughput from {control['rows'][1]['fused_equivalent_steps_s']:.2f} to {control['rows'][1]['cached_equivalent_steps_s']:.2f} equivalents/s, a {control['rows'][1]['paired_speedup_medians']:.2f}x speedup. Exported position, velocity and deformation gradient were identical in this comparison. Single-body speedup was {control['rows'][0]['paired_speedup_medians']:.2f}x. A ten-control-step continuous run at batch eight reached {control['sustained']['equivalent_50Hz_steps_s']:.2f}/s over 0.2 simulated seconds/body, with {100*control['sustained']['energy_residual_relative']:.4f}% energy residual; this is an energy screen, not a long-horizon response validation.
Array memory for the cached corner case is 12.36 MB at batch eight and 98.85 MB at batch 64, including backups and benchmark reset copies. CUDA context/graphs, other applications and robot/policy memory are excluded.
CPU geometry rebuild alone takes about 0.76 s (oblique) / 0.91 s (corner); aggregation adds 0.34 / 0.61 s. GPU data/graph setup adds roughly 0.77-1.11 s per measured batch. These costs are excluded from the steady material rates and are not amortized into a claimed complete-environment rate.

DECISION AND NEXT STEP
This trial solves the tested representation mismatch under the approved norm and accelerates the coupled GPU mass solve. It does not establish an RL-ready model. The project entry target is >=100 ACTUAL environment transitions/s; preferred is >=500. Material-only rates around 99-111/s have little headroom and miss the 200-300/s planning allowance for material/history/contact.
Stop this bounded performance branch after its one equivalent optimization. Preserve this implementation as a component reference. The next scoped performance effort should address local cut-geometry updates and the remaining material-kernel cost before long physical cutting or robot integration; see NEXT_ACTION.txt. Do not spend days on cuts using the global CPU rebuild, or silently coarsen/soften/change timesteps to claim speed.

LIMITS
Prescribed geometric plane cuts only; no work-driven fracture, physical blade reaction, collision/recontact, board/support or full slice in v19. Current block tests do not prove arbitrary paths, tiny-fragment robustness, spatial convergence or anatomical tomato behavior. Mass-weighted agreement does not guarantee local contact behavior near a rapidly moving tiny region. Source-root selection is history/component compatible but not a general proof of face-adjacent material connectivity around curved or partial cracks. No experimental validation, policy training, current demo changes or production adoption.

EVIDENCE
contract.json / VELOCITY_CRITERION_PROPOSAL.txt: explicit approval and criteria.
response.json, final_selector.json, history_and_holdout.json, heldout_reference_audit.json, velocity_metric_audit.json: retained strict-contract failures and diagnosis.
weighted_response.json, weighted_extra.json, stage_A.json: approved component qualification.
gpu_validation.json, cache_control.json: final GPU precision, cache equivalence, phase/restart and short continuous energy screen.
cost.json, cost_cached.json: synchronized timings and preparation costs.
preservation.json: 1800 protected files unchanged.
FORMULATION.txt / src / tests: representation, implementation, reproducible controls.
'''
(W/'REPORT.txt').write_text(report)
(W/'NEXT_ACTION.txt').write_text('''PROPOSED NEXT SCOPE — COST-FIRST, SAME MATERIAL MODEL

Do not launch a long cut, robot integration or RL training from this result. The current ~100 material-only equivalents/s does not meet the complete-environment requirement.

A focused successor can retain the accepted selective representation and approved norm, then profile the GPU material path once to identify a concrete remaining bandwidth/launch or assembly bottleneck. Target at least 200 material equivalents/s (eight bodies advanced 20 ms in <=40 ms wall time), leaving measured room for changing cuts/contact. This is a planning target, not a promised result. Validate any equivalent implementation change against the frozen v19 fields and energy before timing.

The separate major cost is global CPU geometry reconstruction. A local update should touch only blade-intersected tetrahedra and affected neighboring history/mass blocks; preserve all untouched state, all material volume, cut history and exact reduced inertia. Do not approximate by removing material or treating unsupported small fragments as frozen. Compare incremental and full-rebuild outputs before claiming an improvement. This is future implementation work, not completed by v19.

First measure a complete material-plus-geometry-changing loop on the small block, including uploads, graph rebuilding, observations and resets. Retest history, partial bridges, independent fragments, root connectivity and unresolved small-region timesteps. Count all costs, including new-cut events, in the reported throughput.

If those costs cannot leave credible room above 100 aggregate actual environment transitions/s, stop this route for online RL and report the limitation. Offline demonstrations or a separately validated surrogate would be different scopes; neither is silently adopted here. If the cost gate passes, proceed to the separately gated physical blade contact and paid-fracture tests, preserving 2 N and 0.1 mm limits. A geometric split is not a physical cut.

No current Isaac/DiSECt setup changes, no new material approximation, no further accuracy relaxation, no new engine, and no model training have been implemented in this proposed next scope.
''')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(9,4.7));names=['Intact','Oblique cut','Corner cut\nbefore cache','Corner cut\nwith cache']
values=[rates['intact']['aggregate_50Hz_step_equivalents_s'],rates['oblique']['aggregate_50Hz_step_equivalents_s'],control['rows'][1]['fused_equivalent_steps_s'],control['rows'][1]['cached_equivalent_steps_s']]
bars=ax.bar(names,values,color=['#6988ad','#6988ad','#b8c3d0','#197f79'],width=.58)
for bar,value in zip(bars,values):ax.text(bar.get_x()+bar.get_width()/2,value+3,f'{value:.1f}',ha='center',fontsize=11)
ax.axhline(100,color='#b65d2a',ls='--',lw=1.3,label='100/s full-environment target (more work required)')
ax.set_ylim(0,145);ax.set_ylabel('Material-only 50 Hz step equivalents / wall second');ax.set_title('GPU material speed improved; complete RL speed is unproven',fontsize=13,pad=15)
ax.legend(loc='upper right',frameon=False,fontsize=9);ax.spines[['top','right']].set_visible(False)
fig.text(.08,.035,'60 mm cube · 6 mm grid · 8 copies · 12.5 μs timestep\nExcludes changing cuts, blade contact, fracture, observations, resets, robot and policy.',fontsize=9,color='#45556a')
fig.subplots_adjust(bottom=.23,left=.1,right=.98,top=.86);fig.savefig(W/'reports/performance.png',dpi=160);plt.close(fig)

banner='''<aside id="mpm-gate3-status" style="margin:16px auto;padding:16px 20px;max-width:1150px;border:1px solid #b8d8e6;border-left:5px solid #217b97;border-radius:12px;background:#f0f9fc;color:#163c4c;font:15px/1.55 system-ui,sans-serif"><strong>GPU trial complete · Accuracy components pass · RL speed still unqualified</strong><br><strong>Verified:</strong> 8/8 block response cases and 8/8 GPU checks pass under the approved material-weighted velocity measure. Local velocity differences remain reported; position, force and energy criteria stay unchanged.<br><strong>Measured:</strong> about 99–111 material-step equivalents/s across the three geometries; the matched corner test improved 3.2× to about 103/s. These rates exclude changing cuts, blade contact, robot and policy.<br><strong>Remaining bottleneck:</strong> cut-geometry rebuilding plus aggregation costs about 1.1–1.5 seconds/body. Full cutting and RL qualification remain pending.<br><strong>Current state:</strong> trial finished; no simulation running. Isaac/DiSECt and prior evidence preserved.<br><a href="selective-trial-20261112.txt">Read verified results</a> · <a href="selective-performance-20261112.png">View speed comparison</a><br><small>Updated 12 November 2026 · Isolated v19 component trial; no new physical tomato slice or training</small></aside>'''
for name in ['disect-checklist.html','learning-roadmap.html']:
 p=OUT/name;html=p.read_text();html,n=re.subn(r'<aside id="mpm-gate3-status".*?</aside>',lambda m:banner,html,flags=re.S);assert n==1;p.write_text(html)
shutil.copy2(W/'REPORT.txt',OUT/'selective-trial-20261112.txt');shutil.copy2(W/'reports/performance.png',OUT/'selective-performance-20261112.png')
s=json.loads(STATUS.read_text());s.update({'updated':now,'status':q['decision'],'simulation_running':False,'active_candidate_qualification':q,'runtime_qualification':'Material-only 99-111 equivalent 50 Hz steps/s; complete RL throughput unqualified. Geometry/contact/robot costs excluded.','next_action':str(W/'NEXT_ACTION.txt')})
s['selective_aggregation_v19']={'authorization':'Targeted continuation and explicitly approved material-weighted velocity criterion','report':str(W/'REPORT.txt'),'qualification':str(W/'qualification.json'),'decision':q['decision'],'existing_setup_changed':False,'protected_files_verified':1800}
for gate in s['gates']:
 if gate['id'] in [1,2,6]:
  gate['evidence'].append(str(W/'qualification.json'))
  gate['scope_note']+=' V19 approved weighted-velocity component checks and strict GPU equivalence pass. This does not qualify physical contact, arbitrary-path cutting or a tomato.'
 if gate['id']==2:gate['status']='v19_restricted_geometric_history_components_pass_general_cutting_pending'
 if gate['id']==6:
  gate['status']='v19_material_cost_marginal_complete_environment_speed_unqualified'
  gate['scope_note']+=' V19 best fixed-topology rates 99-111 equivalent steps/s, with ~1.1-1.5 s CPU geometry/aggregation events excluded; full RL entry target not passed.'
STATUS.write_text(json.dumps(s,indent=2))
print(json.dumps({'decision':q['decision'],'metrics':stats,'best_rates':q['best_fixed_topology_50Hz_equivalents_s'],'updated_checklists':True},indent=2))
