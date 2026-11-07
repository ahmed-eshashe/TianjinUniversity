from pathlib import Path
import json,numpy as np
w=Path(__file__).parent;p=w/'robot_cut12'
if (p/'worker_failure.json').exists():print((p/'worker_failure.json').read_text());raise SystemExit
files=sorted((p/'material_states').glob('step_*.npz'))
if not files:print('Preparing robot');raise SystemExit
f=files[-1]
if not f.with_suffix('.json').exists():f=files[-2]
s=json.loads(f.with_suffix('.json').read_text());z=np.load(f);h=z['history'];frame=np.load(w/'master_frame_definition.npz');mid=z['x'][frame['pairs']][:,:,1];uv=np.einsum('pji,pjk->pik',frame['coefficients'],mid);area=np.linalg.norm(np.cross(uv[:,0],uv[:,1]),axis=1);active=h[:,1]<1
print(json.dumps(dict(step=s['step'],phase=s['phase'],travel_mm=round(1000*(.06639190507103552-s['actual_tool_pose_canonical'][2]),3),force_N=round(float(np.linalg.norm(s['current_reaction_canonical'][:3])),4),damaged=int((h[:,1]>0).sum()),fully_failed=int((h[:,1]>=1).sum()),max_damage=round(float(h[:,1].max()),5),max_history_opening_mm=round(float(h[:,0].max()*1000),4),minimum_active_frame_area_ratio=round(float(area[active].min()),5) if active.any() else None,wall_s=round(s['wall_s'])),indent=None))
