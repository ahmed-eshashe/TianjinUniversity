from pathlib import Path
import json,hashlib,shutil,ast,time
from tomato_thin_slab_reference import point_penalty,sample_slab,normalized_integral_reference
root=Path.cwd();out=root/'runs/offline/thin_slab_reference_20261031_02';out.mkdir(exist_ok=False,parents=True);start=time.monotonic()
h=.002;L=.01;k=1750.
reference=normalized_integral_reference(h,L,k);density=[]
for n in (1,2,4,8,16):
 result=sample_slab(h,L,k,subdivisions_per_side=n)
 assert max(abs(a-b) for a,b in zip(result['weighted_endpoint_forces_n'],reference['endpoint_forces_n']))<1e-13
 density.append({key:value for key,value in result.items() if key!='nodes'})
side_limits=[dict(z_m=z,**point_penalty(z,h,k)) for z in (-1e-6,-1e-9,0.,1e-9,1e-6)]
installed=Path('/home/omen/miniconda3/envs/isaaclab_6/lib/python3.12/site-packages/newton/_src/geometry/soft_contacts_sdf.py');source=installed.read_text();tree=ast.parse(source);source_evidence={}
for name in ('optimize_edge_sdf','optimize_face_sdf','create_soft_edge_contacts','create_soft_face_contacts','_emit_soft_ef_contact'):
 node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
 text=ast.get_source_segment(source,node);source_evidence[name]={'line':node.lineno,'excerpt':text}
 if name.startswith('create_soft_'):
  calls=[n for n in ast.walk(node) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='_emit_soft_ef_contact'];assert len(calls)==1
pins={}
for p in (root/'rl/tomato_thin_slab_reference.py',root/'rl/tests/test_tomato_thin_slab_reference.py',root/'work/run_thin_slab_reference.py',installed):
 pins[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest();dest=out/'source_snapshot'/p.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
frozen=json.loads((root/'runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json').read_text())['source_sha256'];assert all(hashlib.sha256((root/n).read_bytes()).hexdigest()==hsh for n,hsh in frozen.items())
a={'result':'PASS: analytic slab comparisons; medial-plane normal remains intrinsically non-unique.',
 'parameters':{'half_thickness_m':h,'endpoint_halfspan_m':L,'stiffness_n_m':k,'gravity':0,'radius_and_margin_m':0},
 'analytic_normalized_integral_reference':reference,'sampling_density_comparisons':density,'one_sided_limits':side_limits,
 'independent_integral_formula':'E=k*h^3/(6L); endpoint F=(-k*h^3/(12L^2), +k*h^3/(12L^2)), for dt=dz/(2L). Alternate mathematical model only.',
 'source_findings':'Installed edge/face pair kernels optimize signed distance and each emit at most one record per candidate pair. Particle, edge and face passes are separate, so this does not mean one total contact per body.',
 'decision':'Preserve installed per-feature minimizer and per-contact material semantics. Do not adopt all-seed summation or normalized-integral coefficients. Check ambiguity at the selected minimum; do not reject solely because normals differ elsewhere in the candidate set.',
 'previous_policy_scope':'The prior aligned-normal selection preview is a conservative diagnostic refusal filter. It is not the general Newton minimizer policy and must not be used to require a new two-sided force formulation.',
 'tests_passed':8,'native_launches':0,'native_force_evaluations':0,'mechanical_steps':0,'elapsed_wall_s':time.monotonic()-start,
 'limits':['Host analytic calculations only; native optimizer behavior at ties has not been measured.',
 'Opposite-normal ambiguity at the medial plane is geometric; it cannot be resolved by adding more point samples.',
 'The normalized integral is not a calibrated material or adopted contact law; it only demonstrates count-independent integration.',
 'No general contact manifold, reliable global minimum, blade integration, dynamic coupling or cutting qualification.'],
 'next_step':'Run a bounded native analytic-slab minimizer query comparing edge order and small offsets; record chosen points, distances and normals with zero forces and integration.',
 'source_sha256':pins,'original_pinned_sources_unchanged':True}
(out/'installed_source_evidence.json').write_text(json.dumps(source_evidence,indent=2)+'\n');(out/'assessment.json').write_text(json.dumps(a,indent=2)+'\n')
deliver=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs');(deliver/'thin-slab-contact-reference-20261031.json').write_text(json.dumps(a,indent=2)+'\n')
(deliver/'thin-slab-contact-reference-20261031.txt').write_text('''Thin-slab contact reference — 31 October 2026

Eight analytic tests passed. No native simulation, force evaluation or motion was run.

A symmetric slab 4 mm thick and an edge with endpoints at z = +/-10 mm were examined with a reference stiffness of 1750 N/m. At the centre, signed distance is -2 mm but the nearest outward normal has two opposite limiting directions. The point-penalty forces approach -3.5 N and +3.5 N from opposite sides. Assigning a unique normal there requires an explicit rule; more samples do not remove this ambiguity.

Raw-sample comparison
Using 4, 8, 16, 32 and 64 samples kept net force approximately zero through symmetry, while individual endpoint loads increased with sample count. Increasing samples from 4 to 32 multiplied each raw endpoint load by eight. Net balance alone therefore cannot validate the contact rule.

Weighted mathematical comparison
An independently integrated penalty over normalized edge parameter gave endpoint forces of +/-0.0116666667 N and energy 0.000233333333 J. Split Gaussian quadrature reproduced those results at every tested density. Its weights define a different model from the native per-contact law; they were not adopted or used to rescale production stiffness.

Installed source clarification and decision
The installed Newton edge/face kernels each optimize signed distance and emit at most one record per feature-shape candidate pair. Different particle/edge/face passes can still emit multiple contacts. We will preserve those per-feature and material semantics. The previous aligned-normal preview remains a restricted refusal diagnostic; different normals elsewhere in a candidate set do not by themselves invalidate a single-minimum policy.

The relevant next question is whether the selected minimum has an ambiguous nearest normal, and how the native optimizer behaves at that tie. Next: a bounded analytic-slab native query with reversed edge order and small offsets, recording geometry only. No alternate force model, native writer, robot motion or cutting is qualified. Checklist item 12 remains open.
''')
print(json.dumps({'reference':reference,'density':[{key:r[key] for key in ('sample_count','raw_endpoint_forces_n','weighted_endpoint_forces_n')} for r in density]},indent=2))
