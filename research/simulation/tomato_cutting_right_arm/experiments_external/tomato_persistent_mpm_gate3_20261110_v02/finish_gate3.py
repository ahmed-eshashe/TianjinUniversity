from pathlib import Path
import json,datetime,hashlib,shutil,os
W=Path(__file__).resolve().parent;now=datetime.datetime.now().astimezone()
def read(p):return json.loads((W/p).read_text())
def save(p,obj): (W/p).write_text(json.dumps(obj,indent=2))
manifest=read('manifest.json');changed=[];missing=[]
for p,h in manifest['protected_sha256'].items():
 f=Path(p)
 if not f.exists():missing.append(p)
 elif hashlib.sha256(f.read_bytes()).hexdigest()!=h:changed.append(p)
preservation={'at':now.isoformat(),'pass':not changed and not missing,'protected_files':len(manifest['protected_sha256']),'changed':changed,'missing':missing,'scope':'All frozen production/CRESSim and previous phase evidence files. Only plan/checklist tracking metadata is updated outside the new candidate.'};save('preservation_check.json',preservation);assert preservation['pass']
cut=read('runs/paid_cut_refined_guard/result.json');oldcut=read('runs/paid_cut/result.json');rec=read('recontact_comparison.json');contact=read('contact_comparison.json');null=read('reports/null_mode_diagnosis.json')
checks=[
 {'id':'law','status':'documented_new_candidate','description':'Bulk, normal contact, friction, ideal cutting work and numerical loss are explicit; synthetic parameters and limits disclosed.','evidence':'physical_model.md'},
 {'id':'area_and_transaction','status':'pass_unit_scope','description':'Reference-area budget, partitioning, no unpaid commit, rejection, repeat query, pause/reversal/re-entry and checkpoint controls. Not a coupled physical cut.','evidence':'cutting_work_controls.json'},
 {'id':'CAD_geometry','status':'pass_component_scope','description':'Independent signed-distance check, force/moment/power adjoint, conservative whole declared-volume intrusion bound and exposed-face reconstruction.','evidence':'geometry_controls.json'},
 {'id':'shallow_contact_refinement','status':'pass_numerical_component_only','description':'Edge and broad-face load/unload force/impulse/work/position comparisons pass, but subsequently discovered strain/geometry discrepancy prevents coupled physical qualification.','evidence':'contact_comparison.json'},
 {'id':'reaction_balance','status':'pass_component_scope','description':'Newton units, reaction sign and moment origin specified; blade/support impulse balance independently checked. Conservation does not cure null-mode motion.','evidence':'force_work_ledger.json'},
 {'id':'blunt_and_miss','status':'partial','description':'Finite broad-face and near-miss contact controls plus decision-law negative tests pass; loaded integrated tip/spine and new physical cut-face tests remain pending.','evidence':'runs/miss_certified/result.json'},
 {'id':'fragment_recontact','status':'failed_refinement_unqualified','description':'Pre-separated pieces collide, slide and separate without healing. Original dt/half-dt forces and friction work fail comparison. Smaller-step run completes, but matched half-step was not launched after structural failure.','evidence':'recontact_comparison.json'},
 {'id':'material_volume','status':'failed_candidate_guard_corrected','description':'Independent guard detects reconstructed-volume collapse missed by stored F. The corrected bounded pilot rejects the next trial at J=0.09943; no state clipping.','evidence':'runs/paid_cut_refined_guard/result.json'},
 {'id':'physical_paid_cut','status':'failed','description':'Zero paid fracture area; no physical topology event. Unit ledger tests do not qualify cutting.','evidence':'runs/paid_cut_refined_guard/result.json'},
 {'id':'bulk_contact_consistency','status':'failed','description':'Independent reference reproduces nonrigid particle motion invisible to stored constitutive strain; repair and mechanics requalification required.','evidence':'reports/null_mode_diagnosis.json'},
 {'id':'preservation','status':'pass','description':'All 547 protected files unchanged; no new candidate adoption.','evidence':'preservation_check.json'}]
out={'updated':now.isoformat(),'gate':3,'status':'failed_physical_qualification','gate_complete':False,'physical_cut_achieved':False,'new_candidate_adopted':False,'existing_setup_changed':False,'experimental_validation':'pending','checks':checks,'primary_blocker':'Nonrigid particle motion and material geometry can evolve without corresponding constitutive strain; loaded contact causes local reconstructed-volume collapse.','concrete_failure':{'last_accepted_sim_time_s':cut['sim_time'],'rejected_trial_volume_J':cut['last_volume_certificate']['observed_minJ'],'peak_force_N':cut['peak_total_force_N'],'paid_fracture_area_m2':cut['cut_ledger']['area_m2'],'physical_topology_event':cut['physical_topology_event']},'next_action':'Scope review of RECOVERY_PROPOSAL.md; do not start Gate 4 or another cutting branch.','supplementary_unfinished':['Integrated tip/spine controls','Physically created cut-face contact','Matched refined recontact comparison','Positive coupled work-gated topology event','Matched refinement of a positive physical cut'],'component_passes_do_not_imply_cutting_qualification':True}
save('contact_fracture_controls.json',out)
ledger={'units':{'force':'N','moment':'N m','impulse':'N s','energy':'J'},'tool_reaction':'Negative of applied material force; moment about instantaneous tool origin T. Interval impulse and endpoint force samples are distinct.','blade_contact':{},'recontact':{},'cutting_pilots':{}}
for name in ['edge_clock','edge_clock_half','broad_clock','broad_clock_half','miss_certified']:
 r=read(f'runs/{name}/result.json');ledger['blade_contact'][name]={k:r[k] for k in ['status','dt','sim_time','wall_s','max_force_N','max_impulse_balance_error_Ns','reaction_impulse_Ns','support_impulse_Ns','work_J','friction_J']};ledger['blade_contact'][name]['trace']=f'runs/{name}/result.json#rows';ledger['blade_contact'][name]['numerical_energy_residual_max_J']=max(abs(v['energy_residual']) for v in r['rows'])
for name in ['recontact_rhs_fixed','recontact_rhs_fixed_half','recontact_spectral']:
 r=read(f'runs/{name}/result.json');ledger['recontact'][name]={k:r[k] for k in ['dt','sim_time','wall_s','peak_force_N','initial_energy_J','friction_dissipated_J','total_momentum_error_Ns','max_net_force_N','max_net_moment_Nm']};ledger['recontact'][name]['sampled_force_integral_note']='Original comparison integrates sparse logged forces; this is a quadrature estimate, not the unavailable substep force integral. No fully qualified reaction-impulse channel claimed for recontact.';ledger['recontact'][name]['trace']=f'runs/{name}/result.json#rows'
for name in ['paid_cut','paid_cut_refined_guard']:
 r=read(f'runs/{name}/result.json');last=r['rows'][-1];ledger['cutting_pilots'][name]={'status':r['status'],'last_accepted_state_s':r['sim_time'],'last_logged_sample_s':last['t'],'last_logged_tool_work_J':last['tool_work_J'],'last_logged_friction_J':last['friction_J'],'last_logged_cut_projection_numerical_loss_J':last['cut_projection_loss_J'],'last_logged_bulk_kinetic_J':last['bulk_kinetic_J'],'final_paid_area_m2':r['cut_ledger']['area_m2'],'final_fracture_work_J':r['cut_ledger']['work_J'],'cut_created':r['physical_topology_event'],'max_impulse_balance_Ns':r['max_impulse_balance_Ns'],'trace':f'runs/{name}/result.json#rows','energy_closure_qualified':False,'reason':'No successful physical cut; cumulative last logged work is not mislabeled as an exact final-step closure. Geometry/strain inconsistency invalidates coupled qualification.'}
save('force_work_ledger.json',ledger)
runtime=[]
for name in ['edge_clock','edge_clock_half','broad_clock','broad_clock_half','recontact_rhs_fixed','recontact_rhs_fixed_half','recontact_spectral','paid_cut_refined_guard']:
 r=read(f'runs/{name}/result.json');runtime.append({'case':name,'particles':512,'dt_s':r['dt'],'sim_s':r['sim_time'],'wall_s':r['wall_s'],'wall_s_per_sim_s':r['wall_s']/r['sim_time'],'status':r['status'],'includes':'Bulk, actual contact queries, CPU geometry checks and sparse evidence writing; excludes scene rendering and initial reconstruction setup.'})
save('runtime_forecast.json',{'results':runtime,'RL_ready':False,'interactive':False,'tomato_scaling_forecast':'Not justified from these 512-particle coupons. No 64k or batched throughput claim.','control_period_s':.02,'optimistic_contact_coupon_wall_s_per_20ms':min(v['wall_s_per_sim_s'] for v in runtime)*.02,'finest_recontact_wall_s_per_20ms':next(v['wall_s_per_sim_s'] for v in runtime if v['case']=='recontact_spectral')*.02,'decision':'Correct the discretization first; do not use an unphysical fast run as an RL benchmark.'})
# Ensure no worker owned by this candidate remains active.
workers=[]
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:cmd=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace')
 except (FileNotFoundError,PermissionError,ProcessLookupError):continue
 if str(W/'tests') in cmd and int(p.name)!=os.getpid():workers.append({'pid':int(p.name),'command':cmd})
# Relative CLI script paths need a cwd and argv check as well.
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:argv=(p/'cmdline').read_bytes().split(b'\0');cwd=(p/'cwd').resolve()
 except (FileNotFoundError,PermissionError,ProcessLookupError):continue
 if cwd==W and len(argv)>1 and b'python' in argv[0] and any(z.startswith(b'tests/') for z in argv[1:]):
  item={'pid':int(p.name),'command':' '.join(z.decode(errors='replace') for z in argv)}
  if not any(q['pid']==item['pid'] for q in workers):workers.append(item)
assert not workers,workers
status={'updated':now.isoformat(),'status':'gate3_failed_scope_review_needed','gate3':'failed_physical_qualification','simulation_running':False,'worker_pid':None,'started':'2026-11-10T18:56:00+08:00','elapsed_wall_minutes':(now-datetime.datetime.fromisoformat('2026-11-10T18:56:00+08:00')).total_seconds()/60,'current_hypothesis':out['primary_blocker'],'next_action':out['next_action'],'evidence':'contact_fracture_controls.json','recovery_proposal':'RECOVERY_PROPOSAL.md','new_candidate_adopted':False,'existing_setup_changed':False,'physical_tomato_qualified':False,'RL_ready':False,'experimental_validation':'pending','gates':{str(i):('historical_component_pass' if i<3 else 'failed_physical_qualification' if i==3 else 'pending') for i in range(9)}};save('status.json',status)
P=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm/docs/rl/ASTRA_HIGH_TOMATO_MODEL_EXECUTION_STATUS_20261110.json');p=json.loads(P.read_text());p.update(status=status['status'],updated=now.isoformat(),candidate_directory=str(W),execution_status_path=str(W/'status.json'),simulation_running=False,new_candidate_adopted=False,existing_solver_modified=False,runtime_qualification='Not qualified for RL; full-contact coupon timings saved in isolated runtime_forecast.json',next_action=str(W/'RECOVERY_PROPOSAL.md'))
for g in p['gates']:
 if g['id']==3:g.update(status='failed_physical_qualification',evidence=[str(W/f) for f in ['contact_fracture_controls.json','REPORT.txt','RECOVERY_PROPOSAL.md']])
 if g['id']<3:g['scope_note']='Historical v01 component pass preserved. A revised numerical update must repeat applicable mechanics and topology controls; not inherited physical cutting qualification.'
P.write_text(json.dumps(p,indent=2))
print(json.dumps({'status':status['status'],'preserved':len(manifest['protected_sha256']),'active_workers':workers,'elapsed_minutes':status['elapsed_wall_minutes']},indent=2))
