from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib,re,shutil
W=Path(__file__).resolve().parents[1]
now=datetime.now(timezone(timedelta(hours=8))).isoformat()
read=lambda name:json.loads((W/name).read_text())
names=['algebra_controls','dynamics_controls','transaction_controls','history_checkpoint_controls']
checks={name:read(name+'.json')['status']=='pass_restricted_unit_scope' for name in names}
m=read('manifest.json')['protected_sha256'];mismatches=[name for name,h in m.items() if not Path(name).exists() or hashlib.sha256(Path(name).read_bytes()).hexdigest()!=h]
preservation={'checked_at':now,'count':len(m),'mismatches':mismatches,'passed':not mismatches}
(W/'preservation_check.json').write_text(json.dumps(preservation,indent=2));checks['preservation']=not mismatches
assert all(checks.values()),checks
qualification={'status':'aligned_cut_basis_component_pass_off_grid_sampling_blocked','updated':now,'checks':checks,'evidence':[str(W/(name+'.json')) for name in names]+[str(W/'conditioning_diagnosis.json')],'material_unchanged':{'E_Pa':100000,'nu':.4,'rho_kg_m3':1000,'Gc_J_m2':80},'cut_scope':'One aligned plane; partial and full prescribed topology on a complete 12 mm block. No actual tool or physical fracture.','blocking_result':{'plane_X_m':.0003,'scalar_basis_dimension':324,'sample_rank':288,'missing_modes':36,'mechanism':'Unsampled thin material support region'},'limits':{'production_adopted':False,'arbitrary_shape_supported':False,'freely_positioned_cuts_supported':False,'full_gate2_requalified':False,'blade_contact_requalified':False,'gate3_complete':False,'physical_cut':False,'RL_qualified':False},'next_scope_proposal':str(W/'RECOVERY_PROPOSAL.txt')}
(W/'qualification.json').write_text(json.dumps(qualification,indent=2))
ledger={'scope':'Prescribed topology unit fixtures only','physical_cutting_runs':0,'paid_fracture_area_m2':0,'paid_fracture_work_J':0,'Gc_J_m2':80,'blade_reaction_qualified':False,'fragment_recontact_qualified':False,'note':'Balanced external opening loads are virtual-work unit tests, not measured blade loads. No physical separation qualification.'}
(W/'force_work_scope.json').write_text(json.dumps(ledger,indent=2))
d=read('dynamics_controls.json')['results']
runtime={'scope':'CPU verification harness; monitoring included. No candidate-only full tomato timing or RL forecast.','partial_coarse_wall_s_per_sim_s':d['partial']['wall_s']/d['partial']['sim_s'],'partial_half_wall_s_per_sim_s':d['partial_half']['wall_s']/d['partial_half']['sim_s'],'full_coarse_timing_includes_two_separate_references':True,'peak_memory_measured':False,'note':'Memory and complete cut/contact performance remain unqualified; these short control timings must not be mistaken for RL throughput.'}
(W/'runtime_forecast.json').write_text(json.dumps(runtime,indent=2))
status={'updated':now,'status':qualification['status'],'simulation_running':False,'process_id':None,'last_completed_run':str(W/'runs/history_checkpoint'),'hypothesis':'Fixed-point quadrature cannot resolve the thin support region introduced by off-grid cuts. Cut-aware integration fixes rank algebraically but is not dynamically adopted.','next_action':str(W/'RECOVERY_PROPOSAL.txt'),'adopted':False,'production_changed':False,'scope_review_needed':True,'evidence':str(W/'qualification.json')}
(W/'status.json').write_text(json.dumps(status,indent=2))
# Update only reporting metadata; production/prior artifacts remain frozen.
backup=W/'reports/checklist_backups';backup.mkdir(exist_ok=True)
state=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm/docs/rl/ASTRA_HIGH_TOMATO_MODEL_EXECUTION_STATUS_20261110.json')
assert not (backup/state.name).exists(),'Do not overwrite the pre-update backup'
shutil.copy2(state,backup/state.name);s=json.loads(state.read_text());s.update(status=qualification['status'],updated=now,candidate_directory=str(W),execution_status_path=str(W/'status.json'),simulation_running=False,runtime_qualification='Not RL qualified; small-block CPU partial-cut verification costs about 4546 wall seconds per simulated second, with monitoring. No full candidate throughput established.',next_action=str(W/'RECOVERY_PROPOSAL.txt'))
s['active_candidate_qualification']={'version':'v05','gate0':'freeze_pass','gate1':'intact_v04_reference_retained_untouched_equivalence_checked','gate2':'aligned_partial_full_unit_controls_pass_off_grid_sampling_blocks_completion','gate3':'contact_and_paid_fracture_not_requalified','arbitrary_tomato_shape_supported':False,'physical_cut':False,'evidence':str(W/'qualification.json')}
s['cut_basis_v05']={'decision':'User requested pursue work after v04 next-step proposal','result':'Restricted unit proof completed; off-grid sampling is a demonstrated blocker; proposed integration revision not adopted'}
for gate in s['gates']:
 if gate['id']==2:
  gate['status']='historical_component_pass_active_candidate_incomplete';gate['evidence'].append(str(W/'qualification.json'));gate['scope_note']='Historical v01 unit evidence preserved. v05 passes aligned single-plane partial/full prescribed-cut controls, but off-grid sampling fails; multiple cuts, real tool generation and full Gate 2 are not requalified.'
 if gate['id']==3:
  gate['status']='blocked_by_cut_representation_sampling';gate['evidence'].extend([str(W/'REPORT.txt'),str(W/'conditioning_diagnosis.json')]);gate['scope_note']='Prior failures preserved. v05 aligned topology unit checks pass; off-grid sampling requires a revised numerical scope. CAD contact and paid fracture remain unqualified; no new physical cut.'
state.write_text(json.dumps(s,indent=2)+'\n')
out=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs')
shutil.copy2(W/'REPORT.txt',out/'mpm-v05-cut-basis-status-20261110.txt')
shutil.copy2(W/'RECOVERY_PROPOSAL.txt',out/'mpm-v05-integration-proposal-20261110.txt')
banner=f'''<aside id="mpm-gate3-status" style="margin:16px auto;padding:16px 20px;max-width:1150px;border:1px solid #dbc391;border-left:5px solid #a86c17;border-radius:12px;background:#fff8e9;color:#45351d;font:15px/1.55 system-ui,sans-serif"><strong>Separate material prototype · Aligned cut-state tests passed</strong><br>Verified on a small block: partial cuts retain their intact bridge; fully divided pieces move independently; mass, loaded state and complete cut-history restart checks pass. These are prescribed unit tests, not a physical knife cut.<br><strong>Blocker:</strong> a cut shifted by 0.3 mm creates a region the fixed samples cannot resolve. Cut-aware integration restores rank in an algebra check, but needs fresh validation before use.<br><strong>Gate 3 remains open.</strong> Freely positioned cuts, tomato geometry, blade contact, physical fracture and RL speed are not qualified. No simulation is running. Existing Isaac/DiSECt results and milestone counts remain unchanged.<br><a href="mpm-v05-cut-basis-status-20261110.txt" style="color:#805214;text-decoration:underline">Verified results</a> · <a href="mpm-v05-cut-basis-outcome-20261110.png" style="color:#805214;text-decoration:underline">Test chart</a> · <a href="mpm-v05-integration-proposal-20261110.txt" style="color:#805214;text-decoration:underline">Proposed next repair</a><br><small>Updated {now[:16].replace('T',' ')} (China time)</small></aside>'''
for name in ['disect-checklist.html','learning-roadmap.html']:
 p=out/name;assert not (backup/name).exists();shutil.copy2(p,backup/name);old=p.read_text();new,n=re.subn(r'<aside id="mpm-gate3-status".*?</aside>',lambda match:banner,old,flags=re.S);assert n==1;p.write_text(new)
print(json.dumps({'status':status['status'],'checks':checks,'protected_files':len(m),'updated_checklists':2,'proposal':str(W/'RECOVERY_PROPOSAL.txt')},indent=2))
