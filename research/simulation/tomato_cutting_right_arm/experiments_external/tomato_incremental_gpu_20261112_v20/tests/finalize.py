from pathlib import Path
import json,datetime,shutil,re
W=Path(__file__).resolve().parents[1]
OUT=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs')
STATUS=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm/docs/rl/ASTRA_HIGH_TOMATO_MODEL_EXECUTION_STATUS_20261110.json')
def read(n):return json.loads((W/n).read_text())
now=datetime.datetime.now().astimezone().isoformat();local=read('local_validation.json');gpu=read('gpu_validation.json');loop=read('changing_loop.json');matched=read('matched_cost.json');preserve=read('preservation.json')
assert all(x['status']=='pass' for x in [local,gpu,loop,matched]) and preserve['passed']
old=next(r for r in loop['timings'] if r['n']==10 and not r['optimized']);new=next(r for r in loop['timings'] if r['n']==10 and r['optimized'])
old_cpu=old['phase_wall_s']['geometry_update']+old['phase_wall_s']['aggregate'];new_cpu=new['phase_wall_s']['geometry_update']+new['phase_wall_s']['aggregate']
checks={k:len(v['checks']) for k,v in [('local_geometry_setup',local),('GPU_precision',gpu),('changing_loop',loop),('matched_GPU_comparison',matched)]}
qualification={'version':'v20','updated':now,'decision':'equivalent_speed_improvements_verified_RL_cost_gate_not_passed','simulation_running':False,'current_setup_changed':False,'production_adopted':False,'physical_tomato_model_completed':False,'physical_cut':False,'rl_ready':False,'experimental_validation':'pending','scope':'Implementation-only optimization of frozen v19; geometric diagnostic cutting only.','passed_check_sets':checks,'failed_final_checks':[],'historical_failures_preserved':True,'matched_GPU_material_rates':matched['rows'],'changing_geometry_loop':{'extent_m':.06,'controls':10,'simulated_duration_s':.2,'front_events':4,'old_total_wall_s':old['wall_s'],'new_total_wall_s':new['wall_s'],'speedup':old['wall_s']/new['wall_s'],'old_geometry_setup_s':old_cpu,'new_geometry_setup_s':new_cpu,'geometry_setup_speedup':old_cpu/new_cpu,'new_single_environment_diagnostic_transitions_s':new['actual_diagnostic_transitions_per_s'],'complete_batched_RL_rate_measured':False,'remaining_cost_scope':'Includes reset, geometry, setup, observations and checks; excludes blade/contact/fracture/robot/policy.'},'target_material_headroom_s':200,'target_minimum_actual_RL_transitions_s':100,'target_preferred_actual_RL_transitions_s':500,'next_action':str(W/'NEXT_ACTION.txt'),'report':str(W/'REPORT.txt'),'preservation':preserve}
(W/'qualification.json').write_text(json.dumps(qualification,indent=2));(W/'status.json').write_text(json.dumps(qualification,indent=2))
table='\n'.join(f"{r['case']:9s} {r['old_material_equivalents_s']:8.2f} {r['new_material_equivalents_s']:8.2f} {r['matched_speedup']:7.2f}x" for r in matched['rows'])
phases='\n'.join(f"{k:22s} {old['phase_wall_s'][k]:9.4f} {new['phase_wall_s'][k]:9.4f}" for k in old['phase_wall_s'])
report=f'''V20 — CUT-UPDATE AND GPU SPEED IMPROVEMENTS
Completed: {now}

RESULT
Cut geometry plus aggregate setup in the matched 60 mm diagnostic episode is {old_cpu/new_cpu:.2f}x faster: {old_cpu:.3f} -> {new_cpu:.3f} seconds total across its four cut-front changes and initial setup. The complete measured material-plus-changing-geometry loop is {old['wall_s']/new['wall_s']:.2f}x faster: {old['wall_s']:.3f} -> {new['wall_s']:.3f} seconds wall time for 0.2 seconds simulated time. Matched GPU fixed-geometry rates improved by 1.21-1.39x. These are useful, verified implementation improvements, but they do not make this an RL-ready cutting simulator.

The current Isaac/DiSECt kitchen, robot, grip and demo remain unchanged. All {preserve['protected_files']} protected files, including v19, match their saved hashes. No new physical tomato slice, robot run, training, material approximation or validation relaxation occurred.

WORK COMPLETED
1. Profiled the CPU geometry/setup path and three GPU kernel phases separately. The host was recomputing moments for unchanged material and repeatedly solving identical tiny connectivity/mass subproblems. GPU force gathering was the largest measured kernel cost.
2. Added conservative region rejection, cached unchanged convex moments and history-group connectivity, and vectorized root/setup/state evaluation. Exact reduced inertia is preserved. Recomputed moments and convex clipping remain confined to affected material regions after initial geometry-cache construction; global lightweight bookkeeping still remains.
3. Corrected a real implementation pitfall: reusing initialization centroids rather than reference ConvexHull centroids changed some tied root selections. The initial failure is preserved. A one-off exact reference-moment cache restores identical topology, root selections and aggregation matrices. Its cost is not hidden: it is counted in complete episodes and separately listed in warm-event timing.
4. Parallelized the same nodal force sum and refined the GPU layout from one to four node groups per block. The stress law, exact coupled mass and 12.5 us integrator step are unchanged. This is the one profile-directed GPU assembly optimization; no further numerical shortcut was added after its cost result.
5. Ran partial-to-complete geometric cutting loops with reset, GPU reconstruction and observations included. Future geometric events are only supplied as they occur.

VERIFICATION
- {checks['local_geometry_setup']} geometry/setup controls passed: oblique, corner, aligned, partial, current-world plane, tangent, outside and tiny-region fixtures; partial-to-complete history through four cut slots; capacity stop; restart; two 60 mm comparisons. Final geometry arrays, connectivity, labels, nodal fields and exact mass agree with the reference in the reported large-block cases.
- {checks['GPU_precision']} strict GPU checks passed, including external-force change, independent environments and loaded restart.
- {checks['changing_loop']} changing-loop checks passed. Maximum optimized/reference error across the recorded 0.2-second trajectories: position {max(r['position_m'] for r in loop['rows'])*1e6:.5f} micrometres, velocity {max(r['velocity_m_s'] for r in loop['rows'])*1000:.5f} mm/s, deformation gradient {max(r['F'] for r in loop['rows']):.6g}. These pass the unchanged 1 micrometre / 0.1 mm/s / 1e-4 same-operator limits.
- {checks['matched_GPU_comparison']} matched large-block GPU comparisons passed; exported position/velocity/deformation gradient differences were zero at their sampled endpoints.
The approved material-weighted norm remains available for cross-representation comparisons; it was not used to loosen these strict implementation-equivalence limits.

GPU SPEED — MATCHED FIXED GEOMETRY
RTX 5060 Laptop, 8 GiB, headless. 60 mm cube, 6 mm grid, E=100 kPa, nu=0.4, rho=1000 kg/m^3, 0.1% compression + 0.05% shear, 12.5 us substeps. Eight independent copies; 20 ms simulated/body per timed repeat. Five alternating-order repeats, synchronized, reset to identical states outside timing. Rows count material-step equivalents at a 50 Hz control rate, NOT actual RL environment steps or FPS.

Case        V19/s    V20/s  Speedup
{table}

Initial setup, reset, output, changing cuts, contact, fracture, robot and policy are EXCLUDED above. The material-only 200/s headroom target was not reached. Larger batch counts were evaluated for the initial parallel layout; they did not establish the 200/s target. The packed final layout was compared at batches one/eight, not claimed optimal for every GPU or batch.

CHANGING-GEOMETRY LOOP — COSTS INCLUDED
One environment, ten 50 Hz controls, four advancing partial-to-complete front events on a fixed oblique plane. One fresh reset per episode. Total simulated time 0.2 s. Material undergoes the same small initial compression/shear as the timing fixture; there is no physical knife force. Convex geometry is generated during the episode, not pre-cut at reset. A final two-component geometric topology is verified but is NOT a physically fractured slice.

60 mm block phase             V19 s     V20 s
{phases}
Other validation/check time {old['other_checks_wall_s']:.4f} -> {new['other_checks_wall_s']:.4f} s.
TOTAL: {old['wall_s']:.4f} -> {new['wall_s']:.4f} s, {old['wall_s']/new['wall_s']:.2f}x speedup.
Single-environment diagnostic transitions: {old['actual_diagnostic_transitions_per_s']:.2f} -> {new['actual_diagnostic_transitions_per_s']:.2f}/s.
The 24 mm block improves from about 0.591 to 0.310 s for the same control count (about 1.91x). That small-block result must not be substituted for tomato-size cost.

The large optimized episode includes its first geometry-cache build. Subsequent geometry events cost about 0.146, 0.367 and 0.145 s, depending on intersected material; the first costs about 0.671 s including preparation. Aggregate setup totals 0.267 s; GPU data/graph reconstruction still totals 0.805 s. No topology-update or setup cost is silently amortized away in the episode total.
No complete batched RL benchmark was run or passed. Single-environment rates above are not directly equivalent to the project's aggregate 100/s RL threshold. However, the present serial host geometry/setup work alone costs about 1.60 s per ten controls: even free GPU stepping would leave an optimistic ceiling around 6.3 diagnostic transitions/s for this serial update schedule, before other work. A different batched/parallel update architecture would require measurement; it cannot be inferred from material-only batching.

DECISION
Preserve the speed improvements and the validated mechanics reference. The current approach remains below the intended complete-environment RL speed envelope. Do not start robot integration or long physical cuts from these numbers. The remaining cost is concentrated in convex geometry generation and rebuilding/uploading the GPU representation, with only modest material-only headroom. A further small timestep or material relaxation is neither justified nor implemented.

NEXT SCOPE
The next substantial implementation effort would be compiled/local convex geometry plus persistent GPU topology storage and incremental updates, validated against this saved reference. It needs a measured combined-loop cost before more physical cutting work. The present CPU global arrays plus rebuilt GPU graphs should not be promoted as an efficient RL backend. See NEXT_ACTION.txt for the proposed bounded decision. This trial stops after its declared equivalent optimization and combined-cost assessment, not because a background job is still running.

EVIDENCE AND LIMITS
profile.json and reports/profile_*.txt: one profile, kernel and host attribution.
local_validation.json, gpu_validation.json, matched_cost.json, changing_loop.json: final checks and raw timing repeats.
reports/local_before_exact_moment_cache.json: preserved root-selection mismatch before correction.
reports/warp32_*.json, cost_packed.json: layout comparison and timing screen.
FORMULATION.txt, src/, tests/: implementation, equations and reproducible procedures.
preservation.json: original files unchanged.
All v19 physical limits remain: synthetic bulk blocks, up to four geometric cuts, unresolved small-fragment time scales, unqualified general crack-front root locality, no blade contact/recontact, paid fracture, board/support, arbitrary-path tomato or experimental calibration. The 2 N force stop and 0.1 mm whole-material penetration limit are unchanged but were not exercised by this bulk-only trial.
'''
(W/'REPORT.txt').write_text(report)
(W/'NEXT_ACTION.txt').write_text('''NEXT DECISION — KEEP THE REFERENCE; DO NOT START RL

V20 delivered verified implementation improvements, but the 60 mm changing-cut diagnostic is still about 3.7 single-environment transitions/s. Material-only batched rates are about 124-159/s and do not include the expensive geometry updates. Neither is a complete RL pass.

The concrete remaining implementation work is to remove Python/ConvexHull and full GPU reconstruction from recurring cut events:
1. Compile the existing convex-region clipping/moment operation and update only affected connectivity/mass neighborhoods, preserving all material and the exact v20 numerical representation. Compare partial bridges, cut history, root choices, all material vertices, volume, energy and momentum against the saved reference; do not infer accuracy from speed.
2. Keep reusable GPU buffers and execution graphs across events, updating changed data and explicit counts. Handle capacity exhaustion visibly; never drop fragments or erase history. Batch independent event streams, not a shared future cut path.
3. Measure the same 60 mm episode with reset, cut events, output and all setup costs counted. First meet a material/history cost envelope that leaves credible room for physical contact and robot work. The current 100 actual aggregate RL transitions/s requirement and preferred 500/s remain unchanged.

This is a substantial implementation phase, not a finished feature. If a bounded prototype still misses the cost envelope, stop treating this backend as a near-term online-RL solution. A learned surrogate or a changed discretization would be a separate modeling decision with independent validation, not an automatic next patch. No such model change is implemented here. Keep Isaac/DiSECt unchanged and retain experimental validation as pending.
''')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
fig,axes=plt.subplots(1,2,figsize=(11,5.2))
x=np.arange(3);ax=axes[0];width=.36
ax.bar(x-width/2,[r['old_material_equivalents_s'] for r in matched['rows']],width,label='Saved v19',color='#9aaec6')
ax.bar(x+width/2,[r['new_material_equivalents_s'] for r in matched['rows']],width,label='Optimized v20',color='#167b76')
ax.set_xticks(x,['Intact','Oblique','Corner']);ax.set_ylabel('Material-only 50 Hz equivalents / second');ax.set_title('GPU material advance · 8 copies');ax.legend(frameon=False);ax.set_ylim(0,200)
ax=axes[1];bottom=np.zeros(2)
phase_groups=[('Geometry',[old['phase_wall_s']['geometry_update'],new['phase_wall_s']['geometry_update']],'#557da6'),('Material setup',[old['phase_wall_s']['aggregate'],new['phase_wall_s']['aggregate']],'#91aecb'),('GPU setup',[old['phase_wall_s']['GPU_setup_graph'],new['phase_wall_s']['GPU_setup_graph']],'#d9ad65'),('Advance + other',[old['wall_s']-old_cpu-old['phase_wall_s']['GPU_setup_graph'],new['wall_s']-new_cpu-new['phase_wall_s']['GPU_setup_graph']],'#167b76')]
for label,vals,color in phase_groups:ax.bar(['Saved v19','Optimized v20'],vals,bottom=bottom,label=label,color=color,width=.5);bottom+=vals
for i,val in enumerate(bottom):ax.text(i,val+.1,f'{val:.2f} s',ha='center')
ax.set_ylim(0,7.4);ax.set_ylabel('Total wall seconds / 0.2 simulated seconds');ax.set_title('Changing-cut loop · 1 body');ax.legend(frameon=False,fontsize=9,loc='upper right')
for ax in axes:ax.spines[['top','right']].set_visible(False)
fig.suptitle('Verified speed improvements; complete RL qualification still pending',fontsize=14)
fig.text(.08,.025,'60 mm block · 6 mm grid · same material and timestep. Right: reset, four geometric events, setup and output included.\nBoth panels exclude physical blade contact, fracture, robot and policy. Different units and batching; do not compare bar heights across panels.',fontsize=9,color='#40546a')
fig.subplots_adjust(left=.08,right=.98,bottom=.2,top=.84,wspace=.3);fig.savefig(W/'reports/performance.png',dpi=160);plt.close(fig)

banner='''<aside id="mpm-gate3-status" style="margin:16px auto;padding:16px 20px;max-width:1150px;border:1px solid #b8d8e6;border-left:5px solid #217b97;border-radius:12px;background:#f0f9fc;color:#163c4c;font:15px/1.55 system-ui,sans-serif"><strong>Speed improvements verified · Full RL speed remains pending</strong><br><strong>Cut-update + setup work:</strong> about 3× faster in the measured episode. The complete material + changing-geometry loop improved 2.2×, from 6.04 to 2.72 seconds for 0.2 simulated seconds.<br><strong>GPU material only:</strong> matched rates improved to 124–159 equivalent 50 Hz steps/s with eight copies. This excludes changing cuts and contact.<br><strong>Accuracy:</strong> 27 geometry/setup checks, 8 GPU checks and 23 changing-loop checks pass. Same material, timestep and acceptance limits; no physical slice or RL pass claimed.<br><strong>Remaining bottleneck:</strong> convex geometry generation and rebuilding GPU data/graphs. The full changing-cut diagnostic is still only about 3.7 single-environment transitions/s.<br><strong>Current state:</strong> bounded trial complete; no simulation running. Isaac/DiSECt and all prior evidence preserved.<br><a href="incremental-trial-20261112.txt">Read verified results</a> · <a href="incremental-performance-20261112.png">View speed comparison</a><br><small>Updated 12 November 2026 · Isolated v20 implementation trial · Contact, fracture and full RL qualification pending</small></aside>'''
backup=W/'reports/checklist_backups';backup.mkdir(exist_ok=True)
for name in ['disect-checklist.html','learning-roadmap.html']:
 p=OUT/name;shutil.copy2(p,backup/name);html=p.read_text();html,n=re.subn(r'<aside id="mpm-gate3-status".*?</aside>',lambda m:banner,html,flags=re.S);assert n==1;p.write_text(html)
shutil.copy2(W/'REPORT.txt',OUT/'incremental-trial-20261112.txt');shutil.copy2(W/'reports/performance.png',OUT/'incremental-performance-20261112.png');shutil.copy2(STATUS,backup/STATUS.name)
s=json.loads(STATUS.read_text());s['previous_active_candidate_v19']=s['active_candidate_qualification'];s.update(updated=now,status=qualification['decision'],candidate_directory=str(W),execution_status_path=str(W/'status.json'),simulation_running=False,active_candidate_qualification=qualification,runtime_qualification='V20 equivalent implementation improvements verified: changing-geometry loop 2.2x faster; material-only 124-159 equivalents/s. Complete RL rate not qualified.',next_action=str(W/'NEXT_ACTION.txt'))
s['local_update_gpu_v20']={'authorization':'User requested lower cut update costs and improved RL speed, current setup unchanged','report':str(W/'REPORT.txt'),'qualification':str(W/'qualification.json'),'protected_files_verified':preserve['protected_files']}
for gate in s['gates']:
 if gate['id'] in [1,2,6]:
  gate['evidence'].append(str(W/'qualification.json'));gate['scope_note']+=' V20 preserves the tested numerical model while improving local geometric updates, setup and force assembly; strict component and changing-loop comparisons pass, without physical contact/fracture qualification.'
 if gate['id']==6:gate['status']='v20_speed_improved_full_RL_cost_unqualified';gate['scope_note']+=' Full measured geometric diagnostic: 6.04 to 2.72 s wall per 0.2 s sim, one body. Batched material-only rates 124-159/s are not complete environment rates.'
STATUS.write_text(json.dumps(s,indent=2));print(json.dumps({'decision':qualification['decision'],'checks':checks,'loop_speedup':old['wall_s']/new['wall_s'],'geometry_setup_speedup':old_cpu/new_cpu},indent=2))
