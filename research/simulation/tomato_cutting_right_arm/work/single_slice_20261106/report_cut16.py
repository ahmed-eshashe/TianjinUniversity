from pathlib import Path
import json,numpy as np
w=Path(__file__).parent/'robot_cut16'
if (w/'supervisor_result.json').exists() and (w/'cutting_trace.json').exists():
 s=json.loads((w/'cutting_trace.json').read_text())[-1];z=np.load(w/'checkpoints'/f"step_{s['step']:06d}.npz");source='complete accepted checkpoint'
elif (w/'cutting_status.json').exists():
 s=json.loads((w/'cutting_status.json').read_text());z=np.load(w/'latest_material.npz');source='published accepted state'
else:
 print('Starting robot and restoring accepted checkpoint');raise SystemExit
print(dict(source=source,step=s['step'],stage=s.get('motion_stage'),phase=s['phase'],simulation_time_s=s['time_s'],failed=s['failed_patches'],components=s['component_count'],force_N=float(np.linalg.norm(s['current_reaction_canonical'][:3])),wall_s=s['wall_s'],history_max=float(z['history'].max()),stopped=(w/'supervisor_result.json').exists()))
