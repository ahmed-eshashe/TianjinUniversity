"""Archive reviewed qualification evidence after all required final runs pass."""
from pathlib import Path
import json,hashlib,shutil,ast
R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');O=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs');name='physics-materials-integration-20261101';E=O/(name+'-evidence')
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
runs=[('full_model_20261101_07','full_model_measurements.json'),('full_damage_20261101_06','full_damage_measurements.json'),('full_coupling_20261101_03','full_coupling_measurements.json'),('full_blade_20261101_08','full_blade_measurements.json'),('exact_blade_geometry_20261101_02','exact_blade_geometry_measurements.json'),('group_material_20261101_03','group_material_measurements.json')]
results={};metrics={}
for run_id,measurement in runs:
 p=R/'runs/native'/run_id;s=read(p/'supervisor_result.json');assert s['passed'] and s['child_exit_code']==0 and not s['remaining_live_group_members'],run_id
 m=read(p/measurement);results[run_id]=dict(supervisor=s,measurement_path=str(p/measurement),launch_manifest=read(p/'launch_manifest.json'))
 E.mkdir(exist_ok=True)
 target=E/run_id;target.mkdir(exist_ok=True)
 for f in ['supervisor_result.json','worker_result.json','launch_manifest.json']:
  shutil.copy2(p/f,target/f)
 if run_id.startswith('full_model'):
  metrics['full_model_cases']=m['cases'];metrics['topology']=read(p/'topology.json')
 if run_id.startswith('full_damage'):
  metrics['material_loading']={k:m[k] for k in ['nodes','patches','controlled_surface_nodes','free_bulk_nodes','patches_increased','dt_s','volume_trial_clips','records','scope']}
  residuals=[abs(r['energy_gain_above_driver_work_j'])/max(abs(m['initial_energy']['total_j']),abs(r['energy']['total_j']),abs(r['cumulative_driver_work_j']),1e-12) for r in m['records']]
  assert all(v<=.01+1e-12 for v in residuals)
  metrics['material_loading']['independent_absolute_energy_gate_passed']=True
  metrics['material_loading']['max_absolute_relative_energy_residual']=max(residuals)
 if run_id.startswith('full_coupling'):
  metrics['probe_coupling']=m
 if run_id.startswith('full_blade'):
  metrics['blade']={k:v for k,v in m.items() if k!='episodes'}
  metrics['blade']['intervals']=[{k:v for k,v in record.items() if k not in ['positions','velocities']} for episode in m['episodes'] for record in episode]
 if run_id.startswith('exact_blade_geometry'):
  metrics['geometry']={k:v for k,v in m.items() if k!='cases'};metrics['geometry']['cases']=[dict(id=c['id'],reversed=c['reversed'],generated_candidates=c['generated_candidates']) for c in m['cases']]
frozen=read(R/'runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json')['source_sha256'];assert all(sha(R/n)==h for n,h in frozen.items())
installed={n:h for n,h in read(R/'runs/native/bent_replay_20261101_01/source_integrity.json')['sha256'].items() if not n.startswith(str(R))};assert all(sha(Path(n))==h for n,h in installed.items())
# Preserve all direct and transitive local Python imports of final entry points.
queue=[R/'rl'/n for n in ['tomato_full_model_worker.py','tomato_full_damage_worker.py','tomato_full_coupling_worker.py','tomato_full_blade_worker.py','tomato_exact_blade_worker.py','tomato_group_material_worker.py','tomato_isaac_startup_guard.py']];files=set()
while queue:
 p=queue.pop()
 if p in files:continue
 files.add(p)
 for node in ast.walk(ast.parse(p.read_text())):
  modules=[]
  if isinstance(node,ast.ImportFrom) and node.module:modules=[node.module]
  elif isinstance(node,ast.Import):modules=[x.name for x in node.names]
  for module in modules:
   dependency=R/'rl'/(module.split('.')[0]+'.py')
   if dependency.exists():queue.append(dependency)
files.update([R/'work/exact_blade_cells.json',R/'work/build_exact_blade_cells.py',R/'rl/tomato_volume_step_reference.py'])
files.update((R/'rl/tests').glob('test_tomato_cohesive*.py'))
files.update(R/'rl/tests'/n for n in ['test_tomato_material_contract.py','test_tomato_isaac_startup_guard.py','test_tomato_exact_blade_coverage.py','test_tomato_volume_steps.py'])
source_sha={}
for p in sorted(files):
 relative=p.relative_to(R);dest=E/'source'/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);source_sha[str(p)]=sha(p)
# This newly used installed helper was read only. Add its current hash alongside prior pins.
extra=Path('/home/omen/miniconda3/envs/isaaclab_6/lib/python3.12/site-packages/newton/_src/solvers/vbd/particle_vbd_kernels.py');source_sha[str(extra)]=sha(extra)
launch_matches={run_id:{n:sha(R/n)==h for n,h in record['launch_manifest']['source_sha256'].items()} for run_id,record in results.items()}
assert all(all(values.values()) for values in launch_matches.values()),'A final run source changed after launch'
tests=read(R/'work/physics_integration_host_tests.json');assert tests['passed'] and tests['total']==50
shutil.copy2(R/'work/physics_integration_host_tests.json',E/'focused_host_tests.json')
summary=dict(date='2026-11-01',numerical_component_milestones_complete=[12,15,16,18],experimental_validation='pending at user request',production_full_cut_validated=False,interactive_performance_validated=False,qualification_scope='Current saved mesh and fixed-world-frame, predominantly tensile diagnostic setup. Explicit displacement controls in the material-loading test; frozen damage during actual blade exchanges.',metrics=metrics,runs=results,source_sha256=source_sha,launch_sources_match_current=launch_matches,original_frozen_sources_unchanged=True,previously_pinned_installed_dependencies_unchanged=True,pinned_dependency_sha256=installed,focused_tests=tests,known_limits=['Coefficients, blade mass/inertia and pressure stiffness remain synthetic.','Arbitrary material rotation and compression-plus-shear fracture remain unsupported.','Free preloaded opening/reclosure stress attempts are preserved as failures; full free-fragment self-contact and full cuts remain unqualified.','The artificial 0.7-metre soft-facet integration case retains its precision failure. Qualification uses the actual mesh, whose largest tested boundary edge is about 6.19 mm.','Swept/fast contact, long-run behavior, robot drives and interactive performance are later checks.'])
(O/(name+'.json')).write_text(json.dumps(summary,indent=2)+'\n');(E/'source_integrity.json').write_text(json.dumps(dict(source_sha256=source_sha,pinned_dependencies=installed,launch_matches=launch_matches),indent=2)+'\n')
b=metrics['blade'];replay={k:max(c[k] for c in b['replay_comparisons']) for k in b['replay_comparisons'][0] if k!='interval'}
text='''Physics/materials integration — 1 November 2026

The numerical component milestones for the current diagnostic setup are complete. Experimental tomato validation is PENDING at the user's request. This is not a validated complete cut, general free-fragment simulation or interactive robot environment.

1. Actual model integration
The saved 4,032-node tomato now builds as a native spring/barrier/cohesive model: 33,996 bulk springs, 16,291 original volume cells, 5,504 boundary triangles and 47 shared-history interface patches. Saved masses, stiffness assignments, original volume law and geometry are retained. No Neo-Hookean bulk material is substituted for the saved spring model. Input hashes bind the exact mesh/assignment files.

Native tests compare the volume barrier and full assembled nodal forces/diagonal Hessians with independent offline calculations. All actual patches are checked at elastic, softening and failed openings. A four-interval free elastic sequence resets and replays exactly. The existing scalar position, velocity, force and Hessian gates remain unchanged.

The native volume barrier now includes feasible numerical steps. Colored updates use the determinant's affine dependence on one node, with a fraction-to-boundary step. The initial predictor uses a conservative cubic-polynomial bound over its entire proposed path. The original activation J=0.5, floor J=0.1 and modulus 10,000 Pa are unchanged. Unsupported final material states are checked before history is committed; intermediate trial history never accumulates.

2. Full-registry material loading
A disclosed tensile fixture prescribes the 514 paired-interface nodes while 3,518 bulk nodes retain their actual masses and evolve natively. Eight controlled opening increments advance damage in all 47 patches. Native history matches the independent bilinear law. Driver work, kinetic/stored energy, fracture dissipation and support impulse are recorded. An independent saved-data audit also passes the absolute 1% energy-residual gate; the largest measured residual is about 0.0392%. No excess-energy gate is relaxed. This is a controlled-loading qualification, not an unconstrained fracture/reclosure experiment or an actual knife eligibility test.

3. Actual authored-blade contact generation
A constrained TetGen decomposition gives 137 positive solid cells with all 74 original vertices and the exact original 144-triangle oriented exterior. A signed boundary-chain check independently verifies the cell boundary. An unconstrained decomposition failed and was rejected. The mesh is not thickened or replaced by its convex hull. The one-time MeshPy/TetGen tool was unpacked into the workspace; the generated cell file is sufficient at runtime.

Soft triangles are clipped against every overlapping solid cell. This finds intersections inside a soft triangle even when all its vertices are outside. Internal coplanar cell ownership avoids duplicate area. Contact normals and distances come from all original exterior facets using native float64 closest points and solid-angle winding signs. Six crossing/clear/reversed-order geometry cases and 128 off-surface field probes pass. Surface zero-distance normals are outside this field comparison.

Contact forces use reference-material area weights and a degree-two Gaussian rule, refined until consecutive assembled nodal forces agree within 1% plus 1e-5 N. The synthetic pressure stiffness is 1.75e9 N/m³. It is not an experimentally fitted tomato constant. Contacts remain frozen within each implicit soft step and regenerate between exchanges; this is not a swept collision certificate.

4. Two-way exchange, reset and clearing
The full tomato first passes eight exchanges with a synthetic dynamic PhysX probe. A separate authored-blade run uses the complete tomato boundary and original blade geometry. PhysX owns the blade pose and velocity; Newton receives exact state echoes and returns the actual contact wrench. Linear/angular momentum, cumulative impulse and volume admissibility pass.

The final blade run includes eight baseline intervals, a reset and eight replay intervals, then a reset and a clear-space control. All compared particle positions/velocities, blade poses/velocities and contact forces replay exactly. Both instantaneous and permanent dirty wrench queues clear. The clear case has no generated contacts and zero blade velocity. Exactly 17 Newton steps, 17 PhysX steps, 20 state echoes and two resets are counted.

Stable node-owned force accumulation removes GPU summation-order differences. Contact reduction uses fixed 128-row chunks before its final node reduction. This reduced the same final diagnostic from about 204 seconds to about 101 seconds. The result is still a slow diagnostic path; interactive performance is unqualified.

5. Experimental status and remaining scope
The published tomato curve remains a provisional benchmark. No native parameters were fitted to it, and independent numeric measurements/specimen matching were not obtained. The user explicitly chose to keep experimental validation pending. The separate data-requirements file includes an unsent author-request draft.

The current cohesive law uses a fixed world material frame and predominantly tensile supported loading. Compression-plus-shear fracture and arbitrary material rotation remain unsupported. Freely released preloaded full-mesh attempts reached unsupported compressed/shearing interface states and remain preserved as failed stress tests. Full free-fragment self-contact, whole cuts, fast swept motion, robot drives and long-run behavior are not established by these component milestones. The artificial 0.7-metre-wide soft-triangle dynamic test retains its binary32 precision failure; the actual tested tomato boundary has a largest edge of about 6.19 mm. These limitations remain explicit before later full-cut work.

Verification and provenance
Fifty focused host tests pass. Six final native runs pass with exit code zero, no owned live processes and no monitor errors. All final launch source hashes match the archived current code. Frozen original production sources and previously pinned installed dependencies are unchanged. The original three-minute bound remains for other diagnostics; the full-blade replay has a five-minute watchdog. Memory reserves, live monitors, locks and cleanup remain active. The earlier timeout is preserved; no mechanical acceptance threshold was increased.

The companion JSON contains metrics, resource summaries, source hashes and absolute raw-measurement paths. The evidence directory contains the runtime source closure, generated blade cells, final launch/results and host-test log.

Final native runs:
'''
text+=''.join('  '+str(R/'runs/native'/run_id)+'\n' for run_id,_ in runs)
text+='\nMaximum actual-blade replay differences:\n'+''.join(f'  {k}: {v:.12g}\n' for k,v in replay.items())
text+='\nNext roadmap section: Robot & scene. First-cut and experimental claims remain subject to their own later checks.\n'
(O/(name+'.txt')).write_text(text)
print(json.dumps(dict(report=str(O/(name+'.txt')),tests=tests['total'],source_files=len(files),replay=replay)))
