from pathlib import Path
import json,hashlib,shutil,time
from tomato_contact_selection_preview import selection_preview
root=Path.cwd();previous=root/'runs/offline/blade_contact_candidate_probe_20261031_01';out=root/'runs/source_review/blade_contact_writer_design_20261031';out.mkdir(parents=True,exist_ok=False)
start=time.monotonic();results=[];pins={}
for path in sorted(previous.glob('*.json')):
 data=json.loads(path.read_text())
 if 'all_accepted_candidates' not in data:continue
 records=[x['record'] for x in data['all_accepted_candidates']]
 selected=selection_preview(records,data['context'],raw_capacity=2048)
 if data['expected_crossing']:assert selected['status']=='blocked' and not selected['selected_records']
 else:assert selected['status']=='empty'
 results.append({'id':data['id'],'selection':selected})
 pins[str(path.relative_to(root))]=hashlib.sha256(path.read_bytes()).hexdigest()
 dest=out/'input_snapshot'/path.relative_to(root);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dest)
for name in ('rl/tomato_contact_selection_preview.py','rl/tests/test_tomato_contact_selection_preview.py','rl/tomato_mesh_contact_contract.py','work/run_contact_selection_preview.py'):
 p=root/name;pins[name]=hashlib.sha256(p.read_bytes()).hexdigest();dest=out/'source_snapshot'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
base=Path('/home/omen/miniconda3/envs/isaaclab_6/lib/python3.12/site-packages/newton/_src')
installed={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (base/'sim/contacts.py',base/'solvers/vbd/solver_vbd.py',base/'solvers/vbd/rigid_vbd_kernels.py',base/'solvers/vbd/particle_vbd_kernels.py',base/'geometry/soft_contacts_sdf.py')}
frozen=json.loads((root/'runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json').read_text())['source_sha256'];assert all(hashlib.sha256((root/n).read_bytes()).hexdigest()==h for n,h in frozen.items())
a={'result':'Selection refusal behavior passed; actual blade manifold remains unresolved. No native writer or forces run.',
 'cases':results,'elapsed_wall_s':time.monotonic()-start,'unit_tests_passed':7,
 'selection_policy':'Revalidate every raw record; refuse raw saturation before exact duplicate reduction. Only one support with aligned normals may produce a diagnostic-only deepest representative. Conflicting normal branches and mixed supports are blocked. Native writes always disabled.',
 'alignment_scope':'Pairwise normal dot >= 1-1e-6 is a restricted diagnostic grouping rule, not a physical threshold or manifold qualification.',
 'source_findings':['Contacts has a unified seven-field soft stream and single active count; face/edge records must be marked full-surface-capable so particle-only consumers refuse them.',
 'Contacts.clear bumps contact_generation and zeros counters but can leave stale arrays. It is not a reset of solver contact/material/history state.',
 'SolverVBD accepts full-surface contacts, but an attached collision pipeline may overwrite records at scheduled detection phases.',
 'VBD material cache refresh mixes soft/shape properties across the whole stream; kinematic bodies are omitted from dynamic-body adjacency, so reaction observation must scan the global stream.'],
 'writer_design':{'scope':'Future exclusive, detached Contacts diagnostic only; no production pipeline patch.',
 'preflight':['Verify installed/source pins, run/episode/state generation, valid mappings and supported reference records.','Validate raw count/capacity before reduction; independently validate represented geometry after float32 conversion.','Require a validated manifold/selection policy for the requested fixture. Both current blade crossing fixtures are refused.','Use non-differentiable execution only; replay tids and gradient backpropagation are not supported.'],
 'publish_order':['Allocate a fresh owned Contacts with headroom; declare full-surface capability using pinned private API only in the isolated worker.','Confirm no concurrent producer or solver; clear/bump generation and synchronize.','Write all seven fields for the exact active prefix while counts remain zero.','Synchronize; publish the count last; synchronize; capture and compare all fields and generation before consumption.','Use a separate owned contact object; do not attach a collision pipeline that can overwrite the stream.'],
 'failure_behavior':'Keep count zero, invalidate generation and stop the isolated worker on validation/transfer failure; never let a solver consume partially filled fields.',
 'observation':'Read all active global contacts, not only dynamic-body adjacency; reconstruct reaction only until independent dynamic verification exists.',
 'reset':'Discard/rebuild isolated objects for initial diagnostics. Clearing counts alone is not proof of complete physics reset.',
 'initial_native_test':'One explicit single-normal reference fixture, no integration or forces; verify exact float32 buffer roundtrip, stale generation and capacity refusal. Real-blade multi-normal cases remain blocked.'},
 'source_sha256':pins,'installed_source_sha256':installed,'original_pinned_sources_unchanged':True,
 'native_contact_writes':0,'mechanical_steps':0,'force_evaluations':0,'item_12_complete':False,
 'next_step':'Specify and test two-sided contact behavior on a simple thin slab, including opposite-normal balance and sampling-density independence, before choosing a real-blade manifold.'}
(out/'assessment.json').write_text(json.dumps(a,indent=2)+'\n')
print(json.dumps({'cases':results,'elapsed_s':a['elapsed_wall_s']},indent=2))
