from pathlib import Path
import json,datetime,re,shutil
import numpy as np
W=Path(__file__).resolve().parents[1];OUT=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs');S=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm/docs/rl/ASTRA_HIGH_TOMATO_MODEL_EXECUTION_STATUS_20261110.json')
read=lambda p:json.loads((W/p).read_text())
files=['native_validation','geometry_holdout','persistent_validation','pipeline_validation','combined_loop','invariants','final_performance','steady_performance'];results={f:read(f+'.json') for f in files}
assert all(r['status']=='pass' for r in results.values());assert read('preservation.json')['passed']
steady=results['steady_performance'];fresh=results['final_performance'];combo=results['combined_loop'];runs=[r for r in steady['rows'] if r.get('reused_GPU')];rates=[r['diagnostic_transitions_s'] for r in runs];cold=[r['diagnostic_transitions_s'] for r in fresh['rows'] if r['overlap']]
single_old=next(r for r in combo['timings'] if not r['new'] and r['n']==10);single_new=next(r for r in combo['timings'] if r['new'] and r['n']==10 and r['batch']==1);eight=next(r for r in combo['timings'] if r['batch']==8 and r['workers']==4)
old=json.loads(Path('/home/omen/Documents/Codex/experiments/tomato_compiled_events_20261112_v21/qualification.json').read_text())['independent_batch']['aggregate_diagnostic_transitions_s']
now=datetime.datetime.now().astimezone().isoformat()
q={'version':'v22','updated':now,'decision':'cut_update_redesign_verified_repeated_geometric_speed_screen_passes_actual_RL_pending','candidate_directory':str(W),'simulation_running':False,'current_setup_changed':False,'production_adopted':False,'physics_or_timestep_changed':False,'accuracy_criteria_changed':False,'physical_cut':False,'physical_tomato_model_completed':False,'rl_ready':False,'actual_RL_speed_qualified':False,'experimental_validation':'pending','passed_check_sets':{f:len(r['checks']) for f,r in results.items()},'repeated_geometric_speed_screen':{'passed':min(rates)>=100,'minimum_transitions_s':min(rates),'median_transitions_s':float(np.median(rates)),'maximum_transitions_s':max(rates),'repeats':len(rates),'independent_environments':16,'groups':2,'CPU_workers':4,'controls_per_environment_episode':10,'geometric_events_per_environment_episode':4,'reset_cost_included':True,'GPU_objects_reused':True,'template_preparation_separate_s':steady['template_preparation_s'],'no_shared_future_cut_path':True,'scope':steady['scope']},'fresh_instance_screen':{'minimum_transitions_s':min(cold),'median_transitions_s':float(np.median(cold)),'maximum_transitions_s':max(cold),'all_runs_above_100':min(cold)>=100},'eight_environment_no_overlap_transitions_s':eight['diagnostic_transitions_per_s'],'prior_v21_eight_environment_transitions_s':old,'matched_one_body_new_instance_s':{'v21':single_old['wall_s'],'v22':single_new['wall_s'],'simulated_duration_s':.2,'compilation_warmed':True},'minimum_actual_RL_steps_s':100,'preferred_actual_RL_steps_s':500,'model':{'shape':'60 mm synthetic cubic block','grid_m':.006,'initial_tetrahedra':6000,'E_Pa':100000,'nu':.4,'rho':1000,'substep_s':12.5e-6,'support_selector':1e-8,'maximum_cut_slots':4},'maximum_mass_relative':max(r['mass_error_relative'] for r in runs),'maximum_numerical_energy_residual_relative':max(r['energy_residual_relative'] for r in runs),'GPU_arrays_and_rollback_bytes':runs[0]['gpu_arrays_and_rollback_bytes'],'memory_scope':'Array accounting only; excludes CUDA context, CPU/native geometry, pinned staging, robot and policy.','preservation':read('preservation.json'),'report':str(W/'REPORT.txt'),'next_action':str(W/'NEXT_STEPS.txt')}
(W/'qualification.json').write_text(json.dumps(q,indent=2));(W/'status.json').write_text(json.dumps(q,indent=2))
report=f'''V22 — CUT-UPDATE REDESIGN: VERIFIED COMPONENT SPEED RESULT
Completed: {now}

OUTCOME
Repeated episodes now achieve {min(rates):.2f}–{max(rates):.2f} aggregate geometric diagnostic transitions/s, median {np.median(rates):.2f}, across eight timed repeats and two sets of independent cut directions. All eight exceed the preliminary 100/s speed screen. Sixteen environments run in two independent groups of eight, with four CPU workers. Resets, cut events, material advancement, transfers, observations and conservation checks are included. GPU storage/graphs persist between episodes as an environment normally would; each reset clears previous state/history and is checked against a fresh episode.
Fresh-instance runs are less consistent: {min(cold):.2f}–{max(cold):.2f}/s. That screen does NOT pass in every run. One-time pristine-template preparation takes {steady['template_preparation_s']:.3f} s separately; compilation is warmed. The tested bodies have fixed size and resolution and do not share a future cut path. New shape/size preparation is not qualified at this rate.

THIS IS NOT ACTUAL RL QUALIFICATION
These are synthetic bulk/geometric updates, without physical blade contact, paid fracture, recontact, board support, robot stepping or policy inference. The actual RL environment target remains 100/s, preferred 500/s, and is still untested. At the median measured rate there is little headroom for those missing parts. No anatomical tomato, physical slice or learned controller is claimed. Experimental validation remains pending.

WHAT CHANGED
1. Reusable convex boundary faces replace repeated hull construction. Packed immutable geometry and compiled compatibility bookkeeping remove per-region Python reconstruction.
2. Unchanged operators, exact mass blocks and graph storage are reused. Geometry and selector changes invalidate cached data. State and cut history stay independent.
3. Pinned transfers, retained rollback buffers and CUDA graph grid updates cover active work without recreating execution graphs.
4. Independent environments overlap CPU preparation with GPU material stepping on separate streams. Each event uses its own latest completed state; unfinished mutation/read requests are rejected.
5. Scalar compiled accounting retains the same volume, energy, mass and momentum checks, and repeated resets retain the same material model and timestep.
See FORMULATION.txt for equations, unchanged limits and implementation details. No package was installed or upgraded.

MEASURED COMPARISONS
- Saved v21 eight-environment/four-worker changing-loop result: {old:.2f}/s.
- V22 same eight-environment/four-worker layout without overlap: {eight['diagnostic_transitions_per_s']:.2f}/s. Same 60 mm size, 6 mm grid, 50 Hz controls and four events in ten controls.
- V22 sixteen-environment overlapped repeated episodes: median {np.median(rates):.2f}/s, range {min(rates):.2f}–{max(rates):.2f}/s. This changes execution batch/layout, not physical size, resolution or equations; it is not a matched single-variable timing ratio against the eight-environment result.
- Matched new-instance one-body episode, 0.2 simulated seconds: v21 {single_old['wall_s']:.3f} s -> v22 {single_new['wall_s']:.3f} s. Compilation is warmed; geometry/template preparation for that new body is included.
- Warm large-block geometry updates in native_validation.json: about 11 ms for oblique and 14 ms for near-corner cuts, compared with v21's saved 100–130 ms. Initial geometry preparation is separate from these warm-event timings.
- Selected sixteen-environment GPU arrays and rollback storage total {q['GPU_arrays_and_rollback_bytes']/1e6:.2f} MB. This is not total process/VRAM use; CPU geometry, pinned staging, driver/context, robot and policy are excluded.

REFERENCE AND FAILURE CHECKS
{sum(q['passed_check_sets'].values())} recorded checks pass across the selected suites: {json.dumps(q['passed_check_sets'])}.
The matched v21/v22 dynamic checkpoints have maximum position and velocity differences of zero and deformation-gradient difference {max(d.get('F',0) for d in combo['differences']):.3g}. Additional tests cover held-out directions, small regions, world/reference cuts, four-slot histories, operators, CPU/GPU precision, continued restart, cache invalidation, independent streams and rollback after a deliberately invalid step.
A failed asynchronous environment restores its prior state without changing another environment. Fresh and reused episodes agree at sampled checkpoints through prior cut histories. In the selected repeated episodes, maximum mass relative error is {q['maximum_mass_relative']:.3g}; maximum numerical energy residual is {q['maximum_numerical_energy_residual_relative']*100:.5f}%.

REJECTED EXPERIMENTS PRESERVED
The fused four-row kernel and edge-force cache passed their numerical comparisons but were slower. The one-warp alternative was slower and exceeded the strict velocity comparison: about 0.343 mm/s against 0.1 mm/s. None is used by the selected runtime. Compiler/API-integration errors and their fixes remain in runs/. No failing limit was relaxed to obtain the selected result.

PRESERVATION
All {q['preservation']['protected_files']} protected source/evidence files match their starting hashes. Existing Isaac/DiSECt scenes, robot, kitchen, grip and production scripts remain unchanged. This is an isolated candidate, not a production replacement. No simulation job is left running when this report is delivered.

NEXT
Keep this candidate as the verified geometry/runtime baseline. Before training, qualify an isolated integration with the intended physical blade/contact/fracture model and measure the actual complete loop. The 103–109/s component result provides a basis for that measurement, not permission to skip it or a promise that the added physics will remain above 100/s. See NEXT_STEPS.txt.
'''
(W/'REPORT.txt').write_text(report)
(W/'NEXT_STEPS.txt').write_text('''NEXT AFTER V22 — COMPLETE-LOOP INTEGRATION, NOT TRAINING YET

1. Preserve this frozen numerical/runtime baseline. The selected implementation is pipeline_gpu -> active_gpu -> cached_gpu plus compiled_body/fast_aggregation/fast_data. Keep the production Isaac/DiSECt setup separate.
2. Identify the existing physical blade-contact and fracture implementation to integrate. Preserve its approved constitutive, failure/work, contact, support and stop rules; do not treat geometric splitting as paid fracture. If a required physical law is missing, explicitly define that scope before adding a new law or relaxing its criteria.
3. Connect only one isolated environment first. Validate actual state-driven blade contact, fracture work, force feedback, recontact, board/support, stopping and reset. Retain the 2 N and 0.1 mm limits. Compare observations and complete physical trajectories against the existing reference.
4. Measure that complete environment with independent histories, realistic action updates, reset, robot/policy and output costs. Report fixed-size and changed-size preparation separately. Retain the 100 actual transitions/s entry gate and 500/s preferred target.
5. Start a small learning-interface pilot only after physical and complete-loop speed gates pass. The present component benchmark has limited headroom and cannot establish how much contact/fracture overhead is affordable.

Current result: repeated geometric updates pass the preliminary speed screen; actual RL and physical tomato/cutting qualification remain pending. No future cut path is baked into resets. General curved cutting, unlimited slicing/dicing, changed sizes, tomato skin/anatomy and experimental realism are not established by this trial.
''')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
values=[old,eight['diagnostic_transitions_per_s'],np.median(cold),np.median(rates)];lo=[0,0,np.median(cold)-min(cold),np.median(rates)-min(rates)];hi=[0,0,max(cold)-np.median(cold),max(rates)-np.median(rates)]
fig,ax=plt.subplots(figsize=(10,5.7));bars=ax.bar(range(4),values,width=.57,color=['#99a9bc','#5887ac','#6d9ba8','#147d79'],yerr=[lo,hi],capsize=5)
for b,v,h in zip(bars,values,hi):ax.text(b.get_x()+b.get_width()/2,v+h+2,f'{v:.1f}/s',ha='center',fontsize=11)
ax.axhline(100,color='#a45d25',ls='--',lw=1.2);ax.text(-.4,101.5,'100/s diagnostic screen',color='#a45d25',fontsize=9)
ax.set_xticks(range(4),['V21\n8 environments','V22\n8 environments','V22 pipeline\n16, fresh instances','V22 pipeline\n16, repeated episodes']);ax.set_ylim(0,127);ax.set_ylabel('Aggregate geometric diagnostic transitions / second');ax.spines[['right','top']].set_visible(False);ax.set_title('Cut-update redesign: repeated episodes pass the preliminary speed screen',fontsize=13,pad=16)
fig.text(.09,.035,'Same 60 mm cube, 6 mm grid, material laws and timestep. Reset, events, transfer, observations and checks included.\nTemplate preparation and compilation reported separately. Physical blade/contact/fracture, robot and policy excluded.',fontsize=9,color='#384d61');fig.subplots_adjust(left=.09,right=.98,bottom=.22,top=.86);fig.savefig(W/'reports/performance.png',dpi=160);plt.close(fig)
backup=W/'reports/checklist_backups';backup.mkdir(exist_ok=True)
banner=f'''<aside id="mpm-gate3-status" style="margin:16px auto;padding:16px 20px;max-width:1150px;border:1px solid #a8d5c5;border-left:5px solid #147d79;border-radius:12px;background:#f0faf7;color:#173e36;font:15px/1.55 system-ui,sans-serif"><strong>Cut-update redesign verified · preliminary speed screen passed</strong><br><strong>Measured repeated episodes:</strong> {min(rates):.0f}–{max(rates):.0f} steps/second; median {np.median(rates):.0f}, across 16 independent environments. All eight repeats exceed 100/s. Resets, current cut updates, transfers, observations and conservation checks are included.<br><strong>Same eight-environment layout:</strong> about 17 → {eight['diagnostic_transitions_per_s']:.0f} steps/second. Reusable geometry, connections, GPU data and overlapping preparation provide the improvement.<br><strong>Physics checks:</strong> reference motion, geometry, operators, restart, independent histories and failure rollback pass. Material laws, timestep and accuracy limits are preserved.<br><strong>Still pending:</strong> actual blade contact, paid fracture, tomato/robot integration and the complete RL speed test. These results use a synthetic material block; they do not establish a physical tomato slice. Fresh-instance rates sometimes fall below 100/s, and shape/size changes are not speed-qualified.<br><strong>Current state:</strong> trial complete; no simulation running. Current Isaac/DiSECt setup and prior evidence unchanged.<br><a href="cut-update-redesign-20261112.txt">Read verified results</a> · <a href="cut-update-redesign-performance-20261112.png">View measurements</a><br><small>Updated 12 November 2026 · isolated v22 · actual RL qualification pending</small></aside>'''
for name in ['disect-checklist.html','learning-roadmap.html']:
 p=OUT/name;shutil.copy2(p,backup/name);s,n=re.subn(r'<aside id="mpm-gate3-status".*?</aside>',lambda m:banner,p.read_text(),flags=re.S);assert n==1;p.write_text(s)
shutil.copy2(W/'REPORT.txt',OUT/'cut-update-redesign-20261112.txt');shutil.copy2(W/'reports/performance.png',OUT/'cut-update-redesign-performance-20261112.png');shutil.copy2(S,backup/S.name)
s=json.loads(S.read_text());s['previous_active_candidate_v21']=s['active_candidate_qualification'];s.update(updated=now,status=q['decision'],candidate_directory=str(W),execution_status_path=str(W/'status.json'),simulation_running=False,active_candidate_qualification=q,runtime_qualification=f'V22 repeated geometric episodes {min(rates):.1f}–{max(rates):.1f}/s (16 independent environments); synthetic component screen only. Physical blade/fracture/robot/policy and actual RL rate remain pending.',next_action=str(W/'NEXT_STEPS.txt'))
for gate in s['gates']:
 if gate['id'] in [1,2,6]:gate['evidence'].append(str(W/'qualification.json'));gate['scope_note']+=' V22 cached surfaces/operators and independent pipelining preserve the tested numerical model; component speed only, no new physical-cut qualification.'
 if gate['id']==6:gate['status']='v22_repeated_geometric_speed_screen_pass_actual_RL_pending';gate['scope_note']+=' Eight repeated 16-environment episodes exceed 100/s with resets and current geometry updates; physical blade/fracture/robot/policy are excluded, so actual RL gate stays pending.'
S.write_text(json.dumps(s,indent=2));print(json.dumps({'checks':sum(q['passed_check_sets'].values()),'steady_min':min(rates),'steady_median':float(np.median(rates)),'steady_max':max(rates),'actual_RL_qualified':False,'preserved':q['preservation']['protected_files']},indent=2))
