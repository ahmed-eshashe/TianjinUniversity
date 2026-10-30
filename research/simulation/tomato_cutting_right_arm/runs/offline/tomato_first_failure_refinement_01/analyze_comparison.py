"""Compare saved independent branches; never modify physical history."""
import argparse,json,hashlib,math,fcntl,resource,signal
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[3];F=Path(__file__).parent
p=argparse.ArgumentParser();p.add_argument('--fine-checkpoints',type=Path,nargs='+',required=True);a=p.parse_args()
resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55)
assert datetime.now(timezone.utc)<datetime(2026,10,26,4,54,40,tzinfo=timezone.utc)
parent=(R/'logs/offline_overnight.lock').open('a');fcntl.flock(parent,fcntl.LOCK_EX|fcntl.LOCK_NB)
lock=(R/'logs/right_arm_control.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def finite(v):
 if isinstance(v,float):assert math.isfinite(v)
 elif isinstance(v,dict):
  for x in v.values():finite(x)
 elif isinstance(v,list):
  for x in v:finite(x)
plan=json.loads((F/'plan.json').read_text());base_path=R/plan['common_baseline']
def read(folder):
 folder=folder.resolve();s=json.loads((folder/'summary.json').read_text());finite(s);assert s['passed'] and not s['flags'] and s['backend']=='triangle_spectral_evolving_v1'
 assert s['source_hashes']==plan['physical_source_hashes']
 for n,h in s['source_hashes'].items():assert digest(R/n)==h
 for n,h in s['state_hashes'].items():assert digest(folder/n)==h
 audit=json.loads((folder.parent/(folder.name+'_audit.json')).read_text());finite(audit);assert audit['passed'] and not audit['flags']
 return s
assert digest(base_path/'summary.json')==plan['common_baseline_summary_sha256'];base=read(base_path)
coarse_paths=[R/n for n in plan['coarse_checkpoints']]
for p,h in zip(coarse_paths,plan['coarse_summary_sha256']):assert digest(p/'summary.json')==h
fine_paths=[p.resolve() for p in a.fine_checkpoints]
def analyze(paths,max_step):
 previous=base;previous_path=base_path;states=[];ledgers=[];brackets=[];maximum_force=base['blade_resistance_n']
 for folder in paths:
  s=read(folder);assert s['previous_checkpoint']==str(previous_path.relative_to(R));assert s['previous_summary_sha256']==digest(previous_path/'summary.json')
  step=s['depth_mm']-previous['depth_mm'];assert 0<step<=max_step+1e-12
  assert all(v['damage']>=u['damage'] and v['kappa_m']>=u['kappa_m'] for u,v in zip(previous['damage_states'],s['damage_states']))
  work=.5*(s['blade_resistance_n']+previous['blade_resistance_n'])*step/1000;assert abs(work-s['increment_blade_work_j'])<=1e-10
  dw=s['cumulative_blade_work_j']-base['cumulative_blade_work_j'];de=s['energy_j']-base['energy_j'];dd=s['fracture_dissipation_j']-base['fracture_dissipation_j'];residual=dw-de-dd
  passed=dd>0 and abs(residual)<=plan['local_fracture_energy_relative_limit']*dd+plan['local_fracture_energy_absolute_allowance_j']
  ledgers.append({'depth_mm':s['depth_mm'],'local_blade_work_j':dw,'local_stored_energy_change_j':de,'local_fracture_dissipation_j':dd,'local_fracture_residual_j':residual,'relative_fracture_error':abs(residual)/dd if dd>0 else None,'positive_fracture_denominator':dd>0,'local_fracture_energy_gate_passed':passed})
  for i,(u,v) in enumerate(zip(previous['damage_states'],s['damage_states'])):
   if u['damage']<1 and v['damage']==1:brackets.append({'patch_index':i,'last_sample_not_fully_failed_mm':previous['depth_mm'],'first_sample_fully_failed_mm':s['depth_mm']})
  maximum_force=max(maximum_force,s['blade_resistance_n']);states.append(s);previous=s;previous_path=folder
 return {'checkpoints':[str(p.relative_to(R)) for p in paths],'summary_sha256':[digest(p/'summary.json') for p in paths],'actual_depths_mm':[s['depth_mm'] for s in states],'ledgers':ledgers,'sampled_peak_blade_force_n':maximum_force,'peak_is_sampling_limited':True,'complete_failure_brackets':brackets},states
coarse,cs=analyze(coarse_paths,plan['coarse_step_mm']);fine,fs=analyze(fine_paths,plan['fine_step_mm'])
comparisons=[]
for c in cs:
 matches=[s for s in fs if s['depth_mm']==c['depth_mm']]
 if not matches:continue
 s=matches[0]
 delta={'depth_mm':c['depth_mm'],'maximum_damage_difference':max(abs(x['damage']-y['damage']) for x,y in zip(c['damage_states'],s['damage_states'])),'maximum_history_difference_m':max(abs(x['kappa_m']-y['kappa_m']) for x,y in zip(c['damage_states'],s['damage_states'])),'coarse_fully_failed_ids':[i for i,x in enumerate(c['damage_states']) if x['damage']==1],'fine_fully_failed_ids':[i for i,x in enumerate(s['damage_states']) if x['damage']==1],'coarse_topology':c['topology'],'fine_topology':s['topology']}
 for key in ['blade_resistance_n','energy_j','fracture_dissipation_j','cumulative_blade_work_j']:delta[key+'_fine_minus_coarse']=s[key]-c[key]
 comparisons.append(delta)
complete=fs[-1]['depth_mm']==plan['fine_targets_mm'][-1] and len(comparisons)==len(cs)
energy_pass=complete and all(d['local_fracture_energy_gate_passed'] for d in coarse['ledgers']+fine['ledgers'])
report={'status':'complete' if complete else 'partial','scope':'local quasistatic insertion-step sensitivity; not native timestep/spatial/material convergence','common_baseline':plan['common_baseline'],'common_baseline_summary_sha256':digest(base_path/'summary.json'),'plan_sha256':digest(F/'plan.json'),'analyzer_source_hash':digest(Path(__file__)),'coarse':coarse,'fine':fine,'common_depth_comparisons':comparisons,'complete_paired_comparison':complete,'local_fracture_energy_gates_passed':energy_pass,'all_supplied_endpoints_independently_qualified':True,'cross_path_damage_tolerance_invented':False,'main_path_advanced':False,'physical_history_modified':False,'full_cut':False,'independent_release_validated':False,'simulator':False,'training':False}
finite(report);(F/'comparison.json').write_text(json.dumps(report,indent=2)+'\n');(R/'docs/rl/tomato_first_failure_step_comparison_results.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
