"""Read-only local coupled comparison. This does not qualify complete cutting."""
from pathlib import Path
import json,numpy as np
w=Path(__file__).parent;cases=[];stride=4
for run in ('coupling_timestep_stride1','coupling_timestep_stride4'):
 assert not (w/run/'worker_failure.json').exists(),run
 assert (w/run/'cutting_result.json').exists(),run
 assert json.loads((w/run/'restore_audit.json').read_text())['passed'],run
assert json.loads((w/'coupling_timestep_stride1/worker_result.json').read_text())['controlled_steps']==json.loads((w/'coupling_timestep_stride4/worker_result.json').read_text())['controlled_steps'], 'Native substep count changed'
for j in range(1,9):
 base=w/'coupling_timestep_stride1/checkpoints'/f'step_{6400+j*4:06d}.npz';cand=w/'coupling_timestep_stride4/checkpoints'/f'step_{6400+j:06d}.npz';a=np.load(base);b=np.load(cand);ma=json.loads(base.with_suffix('.json').read_text());mb=json.loads(cand.with_suffix('.json').read_text());dx=float(np.linalg.norm(a['x']-b['x'],axis=1).max());tool=float(np.linalg.norm(np.array(ma['robot_state']['tool_pose'][:3])-mb['robot_state']['tool_pose'][:3]));df=float(np.linalg.norm(np.array(ma['reaction'][:3])-mb['reaction'][:3]))/max(float(np.linalg.norm(ma['reaction'][:3])),1e-5);separation=bool(np.array_equal(a['history'][:,1]>=1,b['history'][:,1]>=1));eligible=bool(np.array_equal(a['eligible'],b['eligible']));clock=abs(ma['clock']-mb['clock'])<1e-12
 cases.append(dict(native_steps=j*4,material_position_difference_m=dx,tool_position_difference_m=tool,force_difference_relative=df,separation_identical=separation,eligibility_identical=eligible,clock_equal=clock,passed=bool(max(dx,tool)<=1e-4 and df<=.05 and separation and eligible and clock)))
report=dict(scope=__doc__,passed=all(c['passed'] for c in cases),comparisons=cases,native_dt_s=1/2400,candidate_material_dt_s=1/600,native_collision_checks_every_substep=True,reaction_reapplied_every_native_substep=True,full_slice_success=False,full_cut_accuracy_qualified=False)
(w/'coupled_timestep_comparison.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
