"""Independent prospective audit of an actual recorded robot cut.

Horizontal sliding is allowed by the original frictionless board. The slice
must stay inside the finite board footprint, with quiet vertical motion.
Raw simulator results are never overwritten.
"""
from pathlib import Path
import argparse,json,sys
import numpy as np
from scipy.spatial.transform import Rotation

w=Path(__file__).parent;r=w.parents[1];sys.path.insert(0,str(r/'rl'))
from tomato_native_full_model import registry
from tomato_research_separation import measure
from tomato_exact_blade_coverage import coverage
parser=argparse.ArgumentParser();parser.add_argument('run',type=Path);args=parser.parse_args()
spec=json.loads((w/'full_slice_acceptance.json').read_text())
board=json.loads((w/'board_footprint.json').read_text())
route=json.loads((w/'clear_entry_robot_plan_v8.json').read_text())
F=np.array(route['target_rotation']);translation=np.array(route['target_translation'])
planes=np.array(board['halfspaces']);data=registry()
slice_ids=np.flatnonzero(np.array([n['side'] for n in data['design']['nodes']])=='slice')
assert not(set(slice_ids)&set(data['design']['fixture']['node_ids']))
triangles=np.array([t for piece in data['design']['pieces'] for t in piece['triangles']])
solid=json.loads((r/'work/exact_blade_cells.json').read_text())
vertices=np.array(solid['vertices']);cells=np.array(solid['cells'])
records=[];begin=None;previous=None;passed=False
for filename in sorted((args.run/'material_states').glob('step_*.npz')):
    status=json.loads(filename.with_suffix('.json').read_text())
    if status['phase']!='settle':continue
    with np.load(filename) as saved:
        x=saved['x'];v=saved['v'];history=saved['history'];pose=saved['actual_tool_pose']
        separated=measure(data,x,v,history)
        world=x@F.T+translation
        inside=bool(np.all(world[slice_ids,:2]@planes[:,:2].T+planes[:,2]<=-.001))
        vertical_speed=float(abs(v[slice_ids,2]).max())
        bottom=float(x[slice_ids,2].min())
        reaction=np.array(status['current_reaction_canonical'])
        applied=np.array(status['applied_previous_wrench_world'])
        unloaded=all(np.linalg.norm(a)<1e-5 for a in [reaction[:3],reaction[3:],applied[:3],applied[3:]])
        overlap=None
        if separated['topological_separation'] and unloaded and inside:
            local=(x-pose[:3])@Rotation.from_quat(pose[3:]).as_matrix()
            c=coverage(vertices,cells,local,triangles,capacity=131072)
            overlap=float(sum(row['covered_area_m2'] for row in c['triangles']))
        good=bool(separated['topological_separation'] and separated['failed_patches']==47
            and separated['remaining_material_patches']==0 and inside
            and abs(bottom)<.0002 and vertical_speed<.01 and unloaded
            and overlap is not None and overlap<=1e-16)
        now=status['time_s']
        # Ten-step output interval is 4.167ms. Reject missing frame gaps.
        if previous is not None and now-previous>.004167+1e-8:begin=None
        if not good:begin=None
        elif begin is None:begin=now
        duration=0. if begin is None else now-begin
        records.append(dict(step=status['step'],time_s=now,passed_frame=good,
            supported_duration_s=duration,inside_finite_board=inside,
            bottom_m=bottom,maximum_vertical_speed_m_s=vertical_speed,
            force_norm_N=float(np.linalg.norm(reaction[:3])),blade_overlap_area_m2=overlap,
            separation=separated))
        previous=now
        if duration>=.1:passed=True;break
result=dict(full_supported_slice_success=passed,criteria=spec,frames=records,
    raw_driver_result_preserved=True,actual_robot_run=str(args.run),
    experimental_validation='pending',motor_work_qualified=False,
    horizontal_motion_allowed_on_frictionless_board=True)
(args.run/'independent_slice_audit.json').write_text(json.dumps(result,indent=2))
print(dict(full_supported_slice_success=passed,settle_frames_checked=len(records)))
