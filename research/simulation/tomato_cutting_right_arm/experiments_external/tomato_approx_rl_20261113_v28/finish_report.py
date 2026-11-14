from pathlib import Path
import json,datetime,hashlib,re
W=Path(__file__).resolve().parent
load=lambda p:json.loads((W/p).read_text())
bench=load('runs/full_training_benchmark_adaptive/result.json');mechanics=load('reports/mechanics.json');reset=load('reports/contact_and_reset.json');adaptive=load('reports/adaptive_controls.json');second=load('runs/second_intersecting_cut_adaptive/result.json');large=load('runs/large_tomato_adaptive/result.json');oblique=load('runs/small_oblique_adaptive/result.json');preserve=load('reports/parent_preservation.json');timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
pilot_pass=bench['pass'] and mechanics['pass'] and reset['pass'] and adaptive['pass'] and second['pass'] and all(large['success']) and preserve['pass']
qualification={'status':'restricted_approximate_RL_pilot_pass' if pilot_pass else 'not_qualified','updated_utc':timestamp,'approximate_task_ready_for_initial_RL_trial':pilot_pass,'general_tomato_qualification':False,'robot_RL_qualification':False,'learned_policy_trained':False,'experimental_validation':'pending','existing_setup_changed':False,'speed_complete_task_transitions_s':bench['complete_task_transitions_s'],'full_batched_successes':bench['successes'],'full_batched_failures':bench['failures'],'mechanics_components':mechanics['pass'],'reset_and_stops':reset['pass'],'state_retry':adaptive['pass'],'two_intersecting_cuts_four_pieces':second['pass'],'larger_tomato_cut':all(large['success']),'oblique_trial':{'success':False,'stop':'2 N force limit','peak_N':oblique['peak_N'][0]},'numerical_accuracy':'Coarse/fine complete cycles separate the same bonds, but final positions differ up to 1.54 mm and peak forces by about 46%. Not detailed-solver or real-tomato equivalence.','speed_scope':bench['scope'],'source_artifacts':['runs/full_training_benchmark_adaptive/result.json','reports/mechanics.json','reports/contact_and_reset.json','reports/adaptive_controls.json','runs/second_intersecting_cut_adaptive/result.json','runs/large_tomato_adaptive/result.json','runs/small_oblique_adaptive/result.json','reports/timestep_outcomes.json','reports/reference_differences.json','reports/full_cycle_energy.json','reports/parent_preservation.json']}
(W/'qualification.json').write_text(json.dumps(qualification,indent=2));(W/'status.json').write_text(json.dumps({'status':qualification['status'],'stage':'live_view_prepared','rl_ready_scope':'Initial approximate kinematic-blade task only' if pilot_pass else 'not ready','rl_ready':pilot_pass,'production_changed':False,'updated_utc':timestamp},indent=2))
text=f'''V28 RESULT — separate approximate model for initial RL experiments
{timestamp}

The restricted approximate blade-control pilot {'PASSES' if pilot_pass else 'DOES NOT PASS'}.
Final measured rate: {bench['complete_task_transitions_s']:.1f} complete task
transitions per wall second, eight environments, 50 Hz control; minimum target100.
{bench['completed_transitions']} transitions in {bench['wall_s']:.1f} s, including live
physics, actions, observations, connectivity, rewards, termination and selective
resets. All eight bodies complete an actual work-paid cut and horizontal withdrawal.
No policy was trained. Robot dynamics, rendering and policy inference are excluded.
This qualifies an initial approximate-task RL trial, not the full robot project.

Mechanics and functionality
- 2,803 massive particles, 31,950 initial elastic bonds, 3.5 mm spacing, 121.253 g.
- No supplied future fracture plane; blade motion spends irreversible work to
  break existing connections. Partial cuts retain bridges; completed cuts produce
  disconnected components. Particle contact remains active after separation.
- A second perpendicular cut from an already cut state produces FOUR components
  of 817, 697, 697 and 592 particles. It required one time-step refinement.
- A 20% larger tomato also completes a cut and horizontal withdrawal.
- Exact selective resets, untouched parallel states, timeout/invalid-action,
  blade-board and penetration stops pass. Full-state retry matches a fresh small-
  step control. A force stop is not bypassed by retrying at another time step.
- Independent blade distance tests: maximum error about4 nanometres in165cases.
- Intact energy residual below1% at the finer steps; fast-step intact residual
  about4.3%. Nominal complete cutting-cycle energy residual about2.1% of tool work.
  This is a numerical ledger audit, not motor-work or experimental validation.

Important limits / failed trials retained
- 30-degree oblique cut at80%size stops at {oblique['peak_N'][0]:.3f} N; NOT qualified.
- Coarse/fine completed cycles have the same broken bonds but up to1.54mm final
  position difference and about46% peak-force difference. They finish at different
  times. High-fidelity numerical convergence is not established.
- Imposed-strain stress differences versus the old neo-Hookean reference are
  about4–66%. Sampled fracture-area directionality errors are about5–13%.
- Collidable spheres fill only38%of the former continuum volume. The voids and
  massless bonds are an explicit approximation; no whole-continuum penetration
  claim. The skin/pulp/seed structure and measured tomato calibration are absent.
- Blade geometry is a tapered proxy, not original CAD. Numerical settings refine
  automatically for harder states, so speed is case-dependent.
- Reused broad-phase grid optimization was NOT adopted. Earlier failed blunt-
  blade, fast-step, oblique and second-cut attempts remain in runs/reports.

Preservation
All {preserve['files_checked']} frozen v27 files match their saved hashes. Original
Isaac/DiSECt, kitchen, robot and grip are unchanged. Only new isolated experiment
files and authorized progress pages/status are updated.

Next useful step
Use this qualified restricted task for an initial imitation/residual-RL trial,
then evaluate held-out motions and explicit reference comparisons. Do not promise
arbitrary-path success, realistic force transfer or a full-robot RL speedup.

To see the live approximate model, run launch_live.sh in this directory.
It creates a separate Isaac Sim view. The physics runs live, not a saved playback.
The optional post-cut pull-apart button discloses its extra opening impulse.
'''
(W/'RESULT.txt').write_text(text)
root=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs')
block=f'''<section id="v28-live" style="margin:18px;padding:22px;background:#153c35;color:#e9fff7;border-radius:14px;border:1px solid #44bd9c"><b style="font-size:22px">Approximate RL pilot — {"passed" if pilot_pass else "incomplete"}</b><p><strong>{bench['complete_task_transitions_s']:.0f} complete task steps/s · 8/8 cuts + withdrawal + resets</strong></p><p>✓ Separate model preserved &nbsp; ✓ Persistent cutting &nbsp; ✓ Four-piece intersecting cut &nbsp; ✓ Larger tomato &nbsp; ✓ RL interface and reset checks</p><p>Scope: live blade-and-tomato task. Robot simulation and learned-policy training are not included. The 30° smaller-tomato trial reaches the 2 N stop. Material and numerical approximations remain explicit; experimental validation is pending.</p><p>Live Isaac viewer prepared · 13 November 2026 · Existing robot/kitchen/DiSECt unchanged.</p></section>'''
for name in ['learning-roadmap.html','disect-checklist.html','isaac-sim-progress.html']:
 p=root/name;s=p.read_text();s=re.sub(r'<section id="v28-live".*?</section>',block,s,flags=re.S);p.write_text(s)
(root/'approximate-training-status.json').write_text(json.dumps(qualification,indent=2))
p=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm/docs/rl/ASTRA_HIGH_TOMATO_MODEL_EXECUTION_STATUS_20261110.json');d=json.loads(p.read_text());d['status']=qualification['status'];d['latest_candidate_directory']=str(W);d['approximate_training_pilot']=qualification;d['simulation_running']=False;d['next_action']='Inspect live separate model; begin restricted blade-control learning trial when ready. Broad-path qualification and robot coupling remain separate.';p.write_text(json.dumps(d,indent=2))
print(json.dumps(qualification,indent=2))
