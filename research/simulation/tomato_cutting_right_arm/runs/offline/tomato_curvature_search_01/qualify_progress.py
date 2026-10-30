"""Read-only qualification of finite audited states and unchanged provenance."""
from pathlib import Path
import json,hashlib,math
R=Path(__file__).resolve().parents[3];F=Path(__file__).parent;W=R/'runs/offline/tomato_triangle_withdrawal_01';V=R/'runs/offline/tomato_optimizer_release_01';G=R/'runs/offline/tomato_contact_continuation_01'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def finite(value):
 if isinstance(value,float):assert math.isfinite(value),'Nonfinite mechanical metric'
 elif isinstance(value,dict):
  for v in value.values():finite(v)
 elif isinstance(value,list):
  for v in value:finite(v)
counts={}
for p in [G/'baseline_hashes.json',W/'baseline_hashes.json',W/'new_source_snapshot.json',V/'source_snapshot.json',F/'source_snapshot.json']:
 d=json.loads(p.read_text())
 for n,h in d.items():assert digest(R/n)==h,('Preservation',n)
 counts[str(p.relative_to(R))]=len(d)
accepted=[];failed=[];candidates=0;rss=0
for p in sorted(F.glob('*/attempt*/summary.json')):
 s=json.loads(p.read_text());finite(s);assert s['backend']=='triangle_spectral_evolving_v1'
 rss=max(rss,s['peak_rss_bytes'])
 for n,h in s['source_hashes'].items():assert digest(R/n)==h
 for n,h in s['state_hashes'].items():assert digest(p.parent/n)==h
 if not s['passed']:failed.append({'checkpoint':str(p.parent.relative_to(R)),'flags':s['flags'],'depth_mm':s['depth_mm']});continue
 audit_path=p.parent.parent/(p.parent.name+'_audit.json');a=json.loads(audit_path.read_text());finite(a);assert a['passed'] and not a['flags'] and not s['flags']
 assert s['force_residual']<=1e-6 and a['force_residual']<=1e-6
 assert s['minimum_softening_stability_eigenvalue']>=1e-6 and a['minimum_softening_stability_eigenvalue']>=1e-6
 assert s['swept_min_J']>=.1 and s['min_length_ratio']>=.1 and s['minimum_multiplier_n']>=-1e-9 and s['complementarity_n_m']<=1e-10
 assert min(s['minimum_cut_gap_m'],s['independent_polygon_minimum_gap_m'],s['swept_blade_minimum_gap_m'])>=-1e-9
 oldpath=R/s['previous_checkpoint'];assert digest(oldpath/'summary.json')==s['previous_summary_sha256'];old=json.loads((oldpath/'summary.json').read_text());assert old['passed']
 assert 0<=s['depth_mm']-old['depth_mm']<=.25000001
 assert all(s['source_hashes'].get(n)==h for n,h in old['source_hashes'].items())
 assert all(v['damage']>=u['damage'] and v['kappa_m']>=u['kappa_m'] for v,u in zip(s['damage_states'],old['damage_states']))
 if s['depth_mm']==old['depth_mm']:
  for key in ['energy_j','fracture_dissipation_j','damage_states','cumulative_blade_work_j']:assert s[key]==old[key]
 accepted.append({'checkpoint':str(p.parent.relative_to(R)),'depth_mm':s['depth_mm'],'force_residual':s['force_residual'],'physical_stability_eigenvalue':s['minimum_softening_stability_eigenvalue'],'max_damage':s['max_damage'],'completely_failed_patches':s['completely_failed_patches'],'topology':s['topology'],'relative_energy_residual':s['relative_energy_residual']})
for p in F.glob('*/attempt*/candidate.json'):
 s=json.loads(p.read_text());finite(s);assert not s['passed'] and s['optimization_only'];candidates+=1;rss=max(rss,s['peak_rss_bytes'])
 for n,h in s['source_hashes'].items():assert digest(R/n)==h
 assert digest(p.parent/'guess.npy')==s['guess_sha256']
last=max(accepted,key=lambda v:v['depth_mm']) if accepted else None
report={'passed':True,'preservation_checks':counts,'tests':json.loads((F/'tests.json').read_text()),'accepted':accepted,'last_accepted':last,'rejected_physical_endpoints':failed,'uncommitted_candidates':candidates,'peak_worker_rss_bytes':rss,'full_cut':False,'independent_release_validated':False,'simulator':False,'training':False}
(F/'qualification.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
