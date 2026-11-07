"""Pure host stiffness/velocity-error localization; not a modal qualification."""
from pathlib import Path
import numpy as np,json,hashlib
from tomato_surface_cohesion import SurfaceCohesion
from tomato_coupled_contact import cut_pairs
r=Path('.').resolve();folder=r/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5';paths=[folder/'surface_design.json',folder/'mass_stiffness_assignments.json',Path(__file__).resolve(),r/'rl/tomato_surface_cohesion.py',r/'rl/tomato_coupled_contact.py'];d=json.loads(paths[0].read_text());a=json.loads(paths[1].read_text());mass=np.zeros(len(d['nodes']))
for part in a:mass[part['global_node_ids']]=part['node_mass_kg']
pairs=cut_pairs(d);coh=SurfaceCohesion(d,pairs,0.);K=np.zeros((len(pairs),3,3));membership=[[]for _ in pairs]
for patch in coh.patches:
 for index,weight in zip(patch['indices'],patch['weights']):K[index]+=weight*patch['stiffness'];membership[index].append(patch['id'])
# Opposite perturbation of one cut pair leaves all pair midpoints fixed;
# the reference normal/shear stiffness gives a disclosed coefficient screen.
values=4*np.linalg.eigvalsh(K)/mass[pairs].sum(1)[:,None];frequencies=np.sqrt(np.maximum(values,0))/(2*np.pi);rank=np.argsort(frequencies.max(1))[::-1];records=[]
for index in rank[:10]:records.append(dict(pair_index=int(index),node_ids=pairs[index].tolist(),mass_kg=mass[pairs[index]].tolist(),weighted_patch_stiffness_n_m=K[index].tolist(),reference_pair_frequency_hz=frequencies[index].tolist(),patches=membership[index]))
left=r/'runs/native/mounted_target_v06_r8_20261102_01/feedback_interval63.npz';right=r/'runs/native/mounted_target_v06_r16_20261102_01/feedback_interval127.npz';z0=np.load(left);z1=np.load(right);difference=abs(z0['v']-z1['v']);node,axis=np.unravel_index(difference.argmax(),difference.shape);match=np.flatnonzero(np.any(pairs==node,axis=1));local=[]
for index in match:local.append(dict(pair_index=int(index),node_ids=pairs[index].tolist(),actual_registry_mass_kg=mass[pairs[index]].tolist(),weighted_patch_stiffness_n_m=K[index].tolist(),reference_pair_frequency_hz=frequencies[index].tolist(),patches=membership[index]))
for path in [left,right]:paths.append(path)
report=dict(worst_saved_final_velocity_error=dict(node_id=int(node),component=int(axis),error_m_s=float(difference[node,axis]),world_position_m=(z1['x_after'][node]+z1['origin']).tolist(),native_registry_mass_kg=float(mass[node]),coarse_velocity_m_s=z0['v'][node].tolist(),fine_velocity_m_s=z1['v'][node].tolist(),actual_pressure_force_n=z1['accepted_particle_force'][node].tolist(),paired_coefficients=local),highest_reference_cohesive_pair_screens=records,maximum_reference_pair_frequency_hz=float(frequencies.max()),source_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths},scope='DIAGNOSTIC only: pure unchanged source mass/cohesive coefficients, tensile-side reference material axes, single-pair opposite perturbation leaves pair midpoints fixed. Not the full prepared moving-frame/contact/barrier Hessian, exact natural frequencies, a stable timestep certificate, or permission to change law/masses/damping. Correlates actual saved contact velocity error with existing stiff pair coefficients.');out=r/'runs/offline/contact_velocity_mode_diagnostic_20261102_01';out.mkdir(exist_ok=False);(out/'measurements.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['worst_saved_final_velocity_error'],indent=2));print('Largest reference cohesive pair screen Hz',frequencies.max())
