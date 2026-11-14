from pathlib import Path
import json,hashlib,time,shutil
from tomato_blade_contact_candidates import search_reference_records
from tomato_native_worker import validate_inputs
from tomato_coupon_trajectory import audit_closed_surface
from tomato_sdf_native_probe import signed_reference
root=Path.cwd();prep=root/'runs/offline/tomato_preupgrade_20261027T171031Z'
blade=validate_inputs(root,json.loads((prep/'single_blade_disabled_worker_config_2132.json').read_text()))['blade'];audit_closed_surface(blade['vertices'],blade['triangles'])
registry=root/'runs/native/blade_mesh_crossings_20261031_01/fixture_registry.json';data=json.loads(registry.read_text())
assert data['blade_export_sha256']==hashlib.sha256((prep/'blade_export.json').read_bytes()).hexdigest()
selected=[c for c in data['cases'] if c['id'].startswith('wide:') or c['id']=='authored_blade_edge_through_soft_interior'];assert len(selected)==3
out=root/'runs/offline/blade_contact_candidate_probe_20261031_01';out.mkdir(parents=True,exist_ok=False)
pins={}
for path in [prep/'blade_export.json',registry,root/'rl/tomato_blade_contact_candidates.py',root/'rl/tomato_triangle_distance.py',root/'rl/tomato_sdf_native_probe.py',root/'rl/tomato_mesh_contact_contract.py',root/'rl/tomato_wrench_contract.py',root/'work/run_blade_candidate_probe.py']:
 pins[str(path.relative_to(root))]=hashlib.sha256(path.read_bytes()).hexdigest();dest=out/'source_snapshot'/path.relative_to(root);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dest)
(out/'manifest.json').write_text(json.dumps({'source_sha256':pins,'scope':'Host-only finite candidate prototype; no native imports or force evaluations.','wall_bound_s':45},indent=2)+'\n')
start=time.monotonic();results=[]
for case in selected:
 vertex_signed=[signed_reference(p,blade['vertices'],blade['triangles'])['reference_signed_distance_m'] for p in case['facet']]
 assert all(v>0 for v in vertex_signed)
 result=search_reference_records(blade,case['facet']);result.update(id=case['id'],all_soft_vertices_outside=True,vertex_signed_distances_m=vertex_signed,expected_crossing=case['expected_crossing'])
 (out/(case['id'].replace(':','_')+'.json')).write_text(json.dumps(result,indent=2)+'\n')
 assert bool(result['accepted_count'])==case['expected_crossing']
 results.append({k:result[k] for k in ('id','expected_crossing','all_soft_vertices_outside','vertex_signed_distances_m','witness_count','seed_count','accepted_count','exclusions','deepest_sampled_candidate')})
 print(case['id'], 'seeds',result['seed_count'],'admissible',result['accepted_count'],flush=True)
assessment={'result':'PASS: two all-vertices-outside blade crossing fixtures yield signed face-projection reference records; clear fixture yields none.',
 'cases':results,'elapsed_wall_s':time.monotonic()-start,'mechanical_steps':0,'native_contact_writes':0,'force_evaluations':0,'focused_unit_tests_passed':4,
 'method':'All disclosed blade facets are scanned for noncoplanar surface intersections. Pairwise witness midpoints and centroid seed a bounded finite search. Seeds are checked by full authored-mesh winding sign, closest surface, barycentric support and existing record contract. No SDF is used.',
 'limitations':['Finite heuristic seed search, not a complete collision backend, global SDF minimum or force manifold.',
 'Coplanar intersections do not generate witnesses; exact/adaptive predicates, degeneracies and CCD remain unresolved.',
 'Nearest-edge/vertex normals are rejected unless an unambiguous outward-face projection is demonstrated.',
 'Sampled penetration is a local signed point-to-surface distance, not a minimum translation depth for an entire soft triangle.',
 'No deduplication/manifold/force scaling policy, engine writer, runtime resets, coupling or motion qualification.',
 'Identity frames and zero diagnostic radii/margins only; authored blade geometry unchanged.'],
 'next_step':'Read-only solver-integration design for an isolated complete-stream contact writer, including manifold policy and unsupported-case handling; do not emit all seeds as forces.',
 'item_12_complete':False}
(out/'assessment.json').write_text(json.dumps(assessment,indent=2)+'\n')
