from pathlib import Path
import json,hashlib,shutil,time,math
from tomato_blade_ambiguity_audit import audit_point,audit_sampled_minimum
from tomato_contact_precision_audit import round32,interpolate32
from tomato_mesh_contact_contract import review_record
from tomato_native_worker import validate_inputs
from tomato_sdf_native_probe import signed_reference
root=Path.cwd();prep=root/'runs/offline/tomato_preupgrade_20261027T171031Z';previous=root/'runs/offline/blade_contact_candidate_probe_20261031_01'
blade=validate_inputs(root,json.loads((prep/'single_blade_disabled_worker_config_2132.json').read_text()))['blade']
rounded_vertices=[[round32(v) for v in p] for p in blade['vertices']]
out=root/'runs/offline/real_blade_ambiguity_audit_20261031_01';out.mkdir(parents=True,exist_ok=False);start=time.monotonic();results=[];pins={}
for path in sorted(previous.glob('*.json')):
 c=json.loads(path.read_text())
 if 'all_accepted_candidates' not in c:continue
 pins[str(path.relative_to(root))]=hashlib.sha256(path.read_bytes()).hexdigest();dest=out/'input_snapshot'/path.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dest)
 rows=[review_record(x['record'],c['context']) for x in c['all_accepted_candidates']]
 sampled=audit_sampled_minimum(rows)
 if not rows:
  results.append({'id':c['id'],'sampled_minimum':sampled,'point_audits':[]});continue
 best=max(rows,key=lambda row:row['reference_penetration_m']);record=c['deepest_sampled_candidate']['record']
 assert tuple(record['corners'])==best['corners'] and best['reference_penetration_m']==sampled['deepest_sampled_penetration_m']
 particle32=[[round32(v) for v in p] for p in c['context']['particles_world_m']]
 weights32=[round32(v) for v in record['barycentric']]
 point32=interpolate32(particle32,record['corners'],weights32,fused=True)
 configurations=[('authored_reference',best['soft_point_world_m'],blade['vertices']),
                 ('binary32_point_authored_mesh',point32,blade['vertices']),
                 ('binary32_point_and_mesh',point32,rounded_vertices)]
 for axis in range(3):
  for direction in (-1,1):
   p=list(point32);p[axis]+=direction*1e-7
   configurations.append((f'rounded_stencil:{axis}:{direction}',p,rounded_vertices))
 audits=[]
 for name,p,vertices in configurations:
  result=audit_point(p,vertices,blade['triangles']);sign=signed_reference(p,vertices,blade['triangles'])
  assert sign['reference_signed_distance_m']<0
  result.update(id=name,signed_reference_m=sign['reference_signed_distance_m'],
                nearest_normal_dot_original=math.fsum(a*b for a,b in zip(result['nearest']['face_normal'],best['normal_world'])))
  audits.append(result)
 result={'id':c['id'],'sampled_minimum':sampled,'binary32_modeled_soft_point_m':point32,
   'point_quantization_shift_m':math.dist(point32,best['soft_point_world_m']),'point_audits':audits,
   'minimum_opposing_surface_gap_m':min(a['opposing_normal_distance_gap_m'] for a in audits),
   'minimum_normal_dot_original':min(a['nearest_normal_dot_original'] for a in audits),
   'distinct_normal_branch_within_largest_reporting_band':any(a['bands'][-1]['different_normal_branch_present'] for a in audits)}
 results.append(result)
for name in ('rl/tomato_blade_ambiguity_audit.py','rl/tests/test_tomato_blade_ambiguity_audit.py','rl/tomato_contact_precision_audit.py','rl/tomato_mesh_contact_contract.py','rl/tomato_triangle_distance.py','rl/tomato_sdf_native_probe.py','work/run_real_blade_ambiguity_audit.py'):
 p=root/name;pins[name]=hashlib.sha256(p.read_bytes()).hexdigest();dest=out/'source_snapshot'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
pins[str(prep.relative_to(root)/'blade_export.json')]=hashlib.sha256((prep/'blade_export.json').read_bytes()).hexdigest()
a={'result':'Finite-fixture audit completed; inspect measured branch separation, not a global minimum certificate.',
 'cases':results,'sensitivity_bands_m':[1e-12,1e-9,1e-7],'stencil_offsets_m':[-1e-7,1e-7],
 'band_scope':'Reporting sensitivity and discrete point probes only; not physical slop, a robustness bound or a force-acceptance threshold.',
 'tests_passed':6,'host_point_audits':sum(len(c['point_audits']) for c in results),'native_launches':0,'force_evaluations':0,'mechanical_steps':0,
 'elapsed_wall_s':time.monotonic()-start,'source_and_input_sha256':pins,
 'limits':['Only the two saved deepest sampled blade candidates and a six-axis-offset stencil are examined, not a global minimizer search or a continuous neighborhood.',
 'Binary32 variants are host-modeled conversion/interpolation, not captured native blade state or a GPU collision run.',
 'Face-normal grouping distinguishes reported directions; edge/vertex normal-cone uniqueness is not generally certified.',
 'Finite sampling cannot exclude unsampled equal or deeper minima; no native contact writer, coupling or cutting qualification.'],
 'next_step':'If the measured candidates remain isolated at the reporting bands, run an isolated single-selected-record native buffer roundtrip for these explicit fixtures, retaining their provenance and no physical manifold claim.',
 'item_12_complete':False}
(out/'assessment.json').write_text(json.dumps(a,indent=2)+'\n')
print(json.dumps({'elapsed_s':a['elapsed_wall_s'],'cases':[{key:c[key] for key in ('id','minimum_opposing_surface_gap_m','minimum_normal_dot_original','distinct_normal_branch_within_largest_reporting_band') if key in c} for c in results]},indent=2))
