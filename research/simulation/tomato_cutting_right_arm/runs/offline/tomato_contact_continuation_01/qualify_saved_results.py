"""Serial finite-data, source/state-hash and saved-audit qualification."""
import resource,signal,fcntl,json,hashlib,math,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];F=Path(__file__).resolve().parent
resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55)
with (R/'logs/right_arm_control.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 import numpy as np
 sys.path.insert(0,str(R/'rl'))
 from tomato_coupled_contact import cut_pairs
 from tomato_triangle_contact import triangle_geometry,blade_resistance
 read=lambda p:json.loads(p.read_text())
 def finite(v):
  if isinstance(v,dict):return all(finite(x) for x in v.values())
  if isinstance(v,list):return all(finite(x) for x in v)
  return not isinstance(v,float) or math.isfinite(v)
 def verify(folder):
  s=read(folder/'summary.json');assert s['passed'] and finite(s)
  for n,h in s['source_hashes'].items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h
  for n,h in s['state_hashes'].items():
   assert hashlib.sha256((folder/n).read_bytes()).hexdigest()==h
   assert np.isfinite(np.load(folder/n)).all()
  assert s['limits']=={'address_space_bytes':512*1024**2,'cpu_s':45,'wall_s':55,'shared_lock':True,'blas_threads':1}
  assert not s['forbidden_imports'] and not s['simulator'] and not s['training']
  return s
 report=read(R/'docs/rl/tomato_contact_continuation_results.json');static=[];dynamic=[]
 for s in report['static_probes']:
  folder=R/s['checkpoint'];verify(folder);audit=read(F/(folder.name+'_audit.json'));assert audit['passed'] and finite(audit);static.append(str(folder.relative_to(R)))
 for path in sorted(F.glob('evolving*/status.json')):
  for rec in read(path)['records']:
   if not rec.get('passed'):continue
   folder=R/rec['output'];verify(folder);audit=read(folder.parent/(folder.name+'_audit.json'));assert audit['passed'] and finite(audit);dynamic.append(str(folder.relative_to(R)))
 latest=F/'evolving_cap_extension/attempt045_01';s=verify(latest)
 design=read(R/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5/surface_design.json');points=np.array([n['position_m'] for n in design['nodes']]);pairs=cut_pairs(design)
 g=triangle_geometry(design,points,pairs,s['tip_z_m']);x=np.load(latest/'positions.npy');lam=np.load(latest/'multipliers.npy');n=g['base_rows']
 loaded={kind:int(sum(m['kind']==kind and lam[n+j]>1e-9 for j,m in enumerate(g['cap_rows']))) for kind in ['entry_edge','cap_edge']}
 forbidden=[n for n in sys.modules if n.split('.')[0] in {'newton','warp','torch','isaaclab','isaacsim','omni','pxr'}];assert not forbidden
 result={'passed':True,'static_saved_endpoints_checked':len(static),'evolving_saved_endpoints_checked_including_branches':len(dynamic),'all_source_and_state_hashes_match':True,'all_saved_arrays_and_metrics_finite':True,'all_independent_audits_passed':True,'worker_caps_verified':True,
  'latest_checkpoint':str(latest.relative_to(R)),'latest_depth_mm':s['depth_mm'],'latest_loaded_finite_edge_constraints':loaded,'latest_blade_resistance_n':blade_resistance(g,x,lam),'forbidden_imports':forbidden,'full_cut_validated':False,'independent_release_validated':False}
 (F/'qualification.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
