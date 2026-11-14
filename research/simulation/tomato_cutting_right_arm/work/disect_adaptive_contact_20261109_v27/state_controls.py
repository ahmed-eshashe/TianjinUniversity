from pathlib import Path
import json,numpy as np
from adaptive_blade import AdaptiveBlade,m,tensor
from contact_guard import WholeVolumeGuard
from volume_certificate import certify
W=Path(__file__).resolve().parent
b=AdaptiveBlade();state=np.load(W/'moving_probe_fine_final.npz')
T=np.array(json.loads((W/'probe_placement.json').read_text())['loaded_component_hold_translation_m'])+[0,-2e-6,0]
def restore():
 b.x.copy_(tensor(state['x']));b.v.copy_(tensor(state['v']))
 b.fracture.load_state_dict({'history':state['history']})
 b.blade_translation=T.copy();b.blade_velocity=np.zeros(3);b.blade_enabled=True
restore();b.geometry();f=b.blade_sample['force'].copy();energy=b.blade_sample['energy_J']
history=b.fracture.state_dict()['history'].copy();b.geometry()
pure=bool(np.array_equal(history,b.fracture.state_dict()['history']))
repeat_error=float(np.max(abs(f-b.blade_sample['force'])))
b.reset();reset=bool(not b.blade_enabled and b.blade_dashpot is None and b.fracture_trial is None and not b.eligibility.any() and not b.blade_translation.any() and np.all(b.fracture.state_dict()['history']==0))
restore();b.geometry();restart_error=float(np.max(abs(f-b.blade_sample['force'])))
assert pure and reset and repeat_error<1e-12 and restart_error<1e-12
proof=WholeVolumeGuard(b.cad,m['tets']).check(state['x'],T)
assert proof['passed']
coarse=np.load(W/'moving_probe_coarse_final.npz');fine=np.load(W/'moving_probe_fine_final.npz')
com=b.cad.com_local@b.cad.rotation.T+T
reactions=[-z['force'].sum(0) for z in [coarse,fine]]
moments=[-np.cross(z['x']-com,z['force']).sum(0) for z in [coarse,fine]]
force_relative=float(np.linalg.norm(reactions[0]-reactions[1])/max(np.linalg.norm(reactions[1]),1e-6))
moment_relative=float(np.linalg.norm(moments[0]-moments[1])/max(np.linalg.norm(moments[1]),1e-8))
assert force_relative<=.05 and moment_relative<=.05
out=dict(scope='Adaptive contact purity/reset/recomputed checkpoint and moving-component wrench controls',
         repeat_trial_history_pure=pure,reset_clears_contact_and_history=reset,
         repeat_force_error_N=repeat_error,recomputed_checkpoint_force_error_N=restart_error,
         moving_component_reaction_relative=force_relative,moving_component_moment_relative=moment_relative,
         final_whole_volume_certificate=proof,passed=True,
         damaged_cut_restart_qualified=False,gate_b_passed=False)
(W/'state_controls_result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
