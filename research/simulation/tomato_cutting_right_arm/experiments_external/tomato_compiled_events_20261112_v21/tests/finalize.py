from pathlib import Path
import json,datetime,shutil,re
W=Path(__file__).resolve().parents[1];OUT=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs');STATUS=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm/docs/rl/ASTRA_HIGH_TOMATO_MODEL_EXECUTION_STATUS_20261110.json')
def read(n):return json.loads((W/n).read_text())
sets={k:read(f) for k,f in [('native_geometry','native_validation.json'),('heldout_geometry','geometry_holdout.json'),('persistent_GPU','persistent_validation.json'),('combined_loop','combined_loop.json')]}
assert all(d['status']=='pass' for d in sets.values()) and read('preservation.json')['passed']
now=datetime.datetime.now().astimezone().isoformat();loop=sets['combined_loop'];old=next(x for x in loop['timings'] if x['n']==10 and not x['new']);new=next(x for x in loop['timings'] if x['n']==10 and x['new'] and x['batch']==1);serial=next(x for x in loop['timings'] if x['batch']==8 and x['workers']==1);parallel=next(x for x in loop['timings'] if x['batch']==8 and x['workers']==4)
q={'version':'v21','updated':now,'decision':'compiled_geometry_and_persistent_GPU_verified_combined_speed_below_RL_target','simulation_running':False,'current_setup_changed':False,'production_adopted':False,'physical_tomato_model_completed':False,'physical_cut':False,'rl_ready':False,'experimental_validation':'pending','passed_check_sets':{k:len(v['checks']) for k,v in sets.items()},'strict_model_or_accuracy_change':False,'one_body_cold_episode':{'reference_wall_s':old['wall_s'],'optimized_wall_s':new['wall_s'],'speedup':old['wall_s']/new['wall_s'],'simulated_s':.2,'controls':10,'geometric_events':4,'GPU_replacement_speedup':old['phases']['GPU_replace']/new['phases']['GPU_replace']},'independent_batch':{'environments':8,'host_workers':4,'wall_s':parallel['wall_s'],'aggregate_diagnostic_transitions_s':parallel['diagnostic_transitions_per_s'],'template_preparation_excluded_s':loop['warm_template_preparation_s'],'transitions_s_if_template_counted_once':80/(parallel['wall_s']+loop['warm_template_preparation_s']),'scope':parallel['scope'],'no_shared_future_cut_path':True,'graphs_and_storage_reused':parallel['graphs_and_storage_reused']},'minimum_actual_RL_transitions_s':100,'preferred_actual_RL_transitions_s':500,'preservation':read('preservation.json'),'report':str(W/'REPORT.txt'),'next_action':str(W/'NEXT_DECISION.txt')}
(W/'qualification.json').write_text(json.dumps(q,indent=2));(W/'status.json').write_text(json.dumps(q,indent=2))
phases='\n'.join(f"{k:23s} {old['phases'][k]:9.4f} {new['phases'][k]:9.4f} {parallel['phases'][k]:12.4f}" for k in old['phases'])
report=f'''V21 — COMPILED CUT GEOMETRY AND REUSED GPU DATA
Completed: {now}

OUTCOME
The two requested implementation changes are complete and validated in an isolated version. Compiled convex-geometry work reduces warm large-block events to about 0.10-0.13 s; the preceding v20 implementation took about 0.36-0.59 s in the corresponding saved warm-event screen. Reusing GPU buffers and graphs reduces four GPU replacements in the matched episode from {old['phases']['GPU_replace']:.3f} to {new['phases']['GPU_replace']:.3f} s, about {old['phases']['GPU_replace']/new['phases']['GPU_replace']:.1f}x faster.
The full one-body diagnostic improves {old['wall_s']/new['wall_s']:.2f}x: {old['wall_s']:.3f} -> {new['wall_s']:.3f} s wall time for 0.2 simulated seconds. Eight independent geometric event streams with four host workers reach {parallel['diagnostic_transitions_per_s']:.2f} aggregate diagnostic transitions/s. This is BELOW the 100/s RL entry target even before blade contact, physical fracture, robot and policy work. It is not an RL-ready tomato or physical slicing result.

Isaac/DiSECt, the kitchen, robot, knife grip and previous evidence remain unchanged. All {q['preservation']['protected_files']} protected files match their saved hashes. No package was installed/upgraded; compilation uses the existing compiler and Qhull library and writes only inside this experiment.

WHAT WAS IMPLEMENTED
- C++ geometric clipping/moments using installed reentrant Qhull 8.0.2, with unchanged material-region/history semantics. The initial reference-moment cache preserves tied source-root choices. No mass or tiny region is deleted.
- Compiled construction of the same reduced gradient/incidence data; exact coupled inertia remains unchanged.
- Persistent GPU arrays with active counts and 64-substep graph reuse across geometry events. Active data are still repacked/uploaded; this is not a claim of a completely GPU-resident topology algorithm.
- Independent stream packing for different geometry, loading and cut-front parameters. No future cut path is supplied to reset and no common geometry is imposed on the eight environments.
- Explicit capacity rejection, invalid-state rejection/rollback and loaded restart. Stored capacities do not silently erase history or suppress fragments.
- Four-worker host execution of independent current geometry events; serial and parallel outputs agree.

VALIDATION
{q['passed_check_sets']['native_geometry']} native geometry/setup checks pass, including partial-to-complete history, four cut slots, capacity, restart, world-space planes and 60 mm cases.
{q['passed_check_sets']['heldout_geometry']} additional seeded geometry checks pass across different directions, two successive cuts, 3/6 mm grids, rotation/deformation and world/reference coordinates. They compare topology, two-way convex containment, material force, energy, mass and extension operators.
{q['passed_check_sets']['persistent_GPU']} GPU/storage checks pass: compiled operator data, strict trajectories, separate stream topology/loading, unchanged graph and array pointers across replacement, restart, capacity rejection, invalid replacement and deliberate unstable-step rollback.
{q['passed_check_sets']['combined_loop']} combined-loop checks pass, including strict v20/v21 trajectory and serial/parallel equivalence. The recorded combined-loop position, velocity and deformation-gradient differences were zero at the sampled checkpoints; no accuracy tolerance was relaxed.

One initially failing check compared raw convex vertex-array shapes after a fourth cut. Qhull can produce different redundant coplanar vertices while the convex region is the same. The diagnostic is preserved. Independent two-way hull containment (1e-12 m), unchanged topology/mass/forces/extension matrices and dynamic evaluation on the UNION of both vertex sets establish equivalence. Surface errors are not hidden by ignoring unmatched vertices. See reports/native_vertex_array_diagnostic.json, geometry_holdout.json and FORMULATION.txt.

MATCHED ONE-BODY AND INDEPENDENT-BATCH COST
Model: 60 mm CUBIC diagnostic material block, 6 mm grid; compressible neo-Hookean E=100 kPa, nu=0.4, rho=1000 kg/m^3; 12.5 us substeps. Ten 50 Hz controls per episode, four geometric front events per environment, 0.2 simulated seconds/body. Initial compression is 0.1% plus 0.05% shear; independent batch states/planes vary slightly. Geometry is chosen as each event occurs. A two-component geometric result is not paid material fracture or a legitimate physical tomato slice.

Phase                       V20 one   V21 one   V21 eight/4 workers (seconds)
{phases}
Total wall:                 {old['wall_s']:9.4f} {new['wall_s']:9.4f} {parallel['wall_s']:12.4f}

One-body cold episodes include body reset, initial aggregate/GPU setup and reference geometry-cache preparation. All episodes include cut events, mass/projection/aggregate preparation, GPU upload/replacement, material advancement, CPU observations and conservation checks. Native/JIT/kernel compilation is warmed separately; initial Numba compilation is about 3.25 s in persistent_validation.json.
The eight-body runs copy a pristine material template with NO cut history or future cut data. Preparing that template costs {loop['warm_template_preparation_s']:.3f} s separately. With four workers: {parallel['diagnostic_transitions_per_s']:.2f}/s warm-template throughput; {q['independent_batch']['transitions_s_if_template_counted_once']:.2f}/s if template preparation is charged once to this episode. Per-environment state reset remains included in both figures. GPU arrays plus step backups occupy about {parallel['array_memory_bytes']/1e6:.2f} MB; temporary rollback buffers, CPU working data, CUDA context, robot and policy memory are not included in this array count.
The serial eight-body run takes {serial['wall_s']:.3f} s ({serial['diagnostic_transitions_per_s']:.2f}/s), compared with {parallel['wall_s']:.3f} s ({parallel['diagnostic_transitions_per_s']:.2f}/s) using four host workers. This is a host implementation improvement, not a change to equations.
Maximum mass residual across the reported episodes is below 1e-6, and numerical energy residual stays below 0.05. Actual recorded large-block batch energy residual is {parallel['maximum_energy_residual_relative']*100:.5f}%.

WHAT THE MEASUREMENT MEANS
Unlike earlier material-only numbers, this batch measurement includes real changes to geometric history, setup, resets and output. It still excludes physical blade contact, work-dependent fracture, recontact, board/support, robot and policy. Therefore 17/s is not a completed RL benchmark and cannot be presented as a pass. The same project entry target of 100 aggregate ACTUAL environment transitions/s and preferred 500/s remain unchanged.

REMAINING COST AND DECISION
At eight environments/four workers, cut-plus-aggregate work still costs {parallel['phases']['cut_and_aggregation']:.3f} s of {parallel['wall_s']:.3f} s. Global topology/mass rebuilding and CPU-side state/energy inspection remain, and material advancement costs another {parallel['phases']['material']:.3f} s. Removing repeated GPU allocation/graph construction did not close the throughput gap. There is no measured basis to promise that another small patch will make this a near-term RL backend.
Preserve this version as a faster numerical reference. Do not start physical robot cuts or RL from these component results. Further work needs a deliberate choice between a substantial fully GPU-resident implementation of the current model and a separately validated lower-cost training approximation. Neither is implemented or silently authorized by this report. Current physical limits and model assumptions remain intact; see NEXT_DECISION.txt.

UNQUALIFIED
No anatomical tomato, actual blade-driven paid fracture, physical separation/slice, general arbitrary curved cutting, small-fragment timestep proof, general source-root locality, full spatial convergence, experimental calibration, robot contact or RL training. The 2 N force stop and 0.1 mm whole-material penetration limit are unchanged but not exercised by these bulk/geometric tests. All inherited restrictions from v19/v20 remain.

EVIDENCE
native_validation.json / geometry_holdout.json: geometry, mechanics and operator comparisons.
persistent_validation.json: reuse, independent streams, strict precision and rollback checks.
combined_loop.json: matched complete diagnostic loop and independent-batch timing breakdown.
preservation.json: original setup/evidence unchanged.
FORMULATION.txt / src/ / tests/: method, native source, build artifact and reproducible procedures.
'''
(W/'REPORT.txt').write_text(report)
(W/'NEXT_DECISION.txt').write_text('''NEXT SCOPE DECISION — AFTER V21

Verified combined throughput is about 17 diagnostic transitions/s at eight independent environments and four host workers, already excluding blade/contact/fracture/robot/policy. The required actual RL entry rate is 100/s. The compiled geometry and persistent-buffer changes are complete; they do not establish RL readiness.

Two different scopes are now possible:

1. Preserve the current numerical model and accuracy contract. A substantial fully GPU-resident topology/history/mass/observation implementation would be required for the next performance attempt. Its speed and physical qualification are unproven; no completion date or successful outcome is promised. Until then use this as a numerical reference or for slow offline data collection, not efficient online RL.

2. Design and validate a lower-cost training approximation against the retained reference. This changes the modeling/accuracy scope and requires the user's decision before implementation. Define the required slice dimensions, permitted force/deformation discrepancies, cut-path freedom and evaluation cases first. A coarse mesh or learned approximation must not silently sacrifice small slices, remaining bridges, contact stops or truthful separation. No specific approximation is claimed suitable yet, and no material, mesh or fracture law has been changed by v21.

Avoid another chain of small speed patches without a measured route to the complete-loop target. Neither option authorizes production replacement, altered blade-force/penetration limits, fake separation, large training runs or edits to the current Isaac/DiSECt setup.
''')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
fig,axs=plt.subplots(1,2,figsize=(11,5));ax=axs[0];names=['V20\nrebuild GPU','V21\nreuse GPU'];values=[old['wall_s'],new['wall_s']];bars=ax.bar(names,values,color=['#9badc4','#147d79'],width=.52)
for bar,v in zip(bars,values):ax.text(bar.get_x()+bar.get_width()/2,v+.06,f'{v:.2f} s',ha='center')
ax.set_ylim(0,3.2);ax.set_ylabel('Wall seconds per 0.2 simulated seconds');ax.set_title('One-body matched diagnostic')
ax=axs[1];vals=[serial['diagnostic_transitions_per_s'],parallel['diagnostic_transitions_per_s']];bars=ax.bar(['8 bodies\n1 host worker','8 bodies\n4 host workers'],vals,color=['#779bbc','#147d79'],width=.52)
for bar,v in zip(bars,vals):ax.text(bar.get_x()+bar.get_width()/2,v+2,f'{v:.1f}/s',ha='center')
ax.axhline(100,color='#ad5c2b',ls='--');ax.text(.5,104,'100/s actual RL entry target',ha='center',color='#ad5c2b',fontsize=9);ax.set_ylim(0,115);ax.set_ylabel('Aggregate geometric diagnostic transitions / s');ax.set_title('Independent changing-cut streams')
for ax in axs:ax.spines[['top','right']].set_visible(False)
fig.suptitle('Compiled updates improve speed; combined RL target is still unmet',fontsize=14)
fig.text(.08,.025,'Same numerical model and timestep. Reset, events, GPU replacement and CPU output included.\nEight-body runs reuse a pristine template (preparation reported separately). Blade/contact/fracture/robot/policy are excluded.',fontsize=9,color='#41566b');fig.subplots_adjust(left=.08,right=.98,bottom=.22,top=.83,wspace=.3);fig.savefig(W/'reports/performance.png',dpi=160);plt.close(fig)
banner='''<aside id="mpm-gate3-status" style="margin:16px auto;padding:16px 20px;max-width:1150px;border:1px solid #b8d8e6;border-left:5px solid #217b97;border-radius:12px;background:#f0f9fc;color:#163c4c;font:15px/1.55 system-ui,sans-serif"><strong>Compiled updates + GPU reuse verified · RL speed target still unmet</strong><br><strong>Completed:</strong> compiled convex geometry, faster data preparation and reusable GPU arrays/graphs. Independent cut histories, reloads and failure rollback pass the checks.<br><strong>Measured one-body loop:</strong> 2.67 → 1.26 seconds for 0.2 simulated seconds. GPU replacements are about 16× faster.<br><strong>Measured independent batch:</strong> eight environments and four host workers reach about 17 diagnostic transitions/s, including changing geometry, reset and output. The actual RL entry target remains 100/s; blade/contact/fracture/robot/policy are still excluded.<br><strong>Decision:</strong> retain this faster reference. A larger execution redesign or a separately validated training approximation needs to be scoped before more implementation. No RL-ready tomato or physical slice is claimed.<br><strong>Current state:</strong> trial finished; no simulation running. Isaac/DiSECt and prior evidence preserved.<br><a href="compiled-events-trial-20261112.txt">Read verified results</a> · <a href="compiled-events-performance-20261112.png">View comparison</a><br><small>Updated 12 November 2026 · Isolated v21 implementation trial</small></aside>'''
backup=W/'reports/checklist_backups';backup.mkdir(exist_ok=True)
for name in ['disect-checklist.html','learning-roadmap.html']:
 p=OUT/name;shutil.copy2(p,backup/name);html,n=re.subn(r'<aside id="mpm-gate3-status".*?</aside>',lambda m:banner,p.read_text(),flags=re.S);assert n==1;p.write_text(html)
shutil.copy2(W/'REPORT.txt',OUT/'compiled-events-trial-20261112.txt');shutil.copy2(W/'reports/performance.png',OUT/'compiled-events-performance-20261112.png');shutil.copy2(STATUS,backup/STATUS.name)
s=json.loads(STATUS.read_text());s['previous_active_candidate_v20']=s['active_candidate_qualification'];s.update(updated=now,status=q['decision'],candidate_directory=str(W),execution_status_path=str(W/'status.json'),simulation_running=False,active_candidate_qualification=q,runtime_qualification='V21 one-body changing loop 2.12x faster; independent 8-body/4-worker diagnostic ~17/s, below 100/s actual RL target and excluding physical cutting/robot/policy.',next_action=str(W/'NEXT_DECISION.txt'))
for gate in s['gates']:
 if gate['id'] in [1,2,6]:gate['evidence'].append(str(W/'qualification.json'));gate['scope_note']+=' V21 compiled geometry and persistent GPU storage pass restricted component and changing-loop comparisons; no inherited physical-cut qualification.'
 if gate['id']==6:gate['status']='v21_combined_geometric_cost_below_RL_target';gate['scope_note']+=' Eight independent event streams with four host workers achieve ~17 diagnostic transitions/s including geometry/reset/output, but excluding blade/fracture/robot/policy; no RL pass.'
STATUS.write_text(json.dumps(s,indent=2));print(json.dumps({'decision':q['decision'],'passed':q['passed_check_sets'],'one_body_speedup':q['one_body_cold_episode']['speedup'],'batch_rate':parallel['diagnostic_transitions_per_s']},indent=2))
