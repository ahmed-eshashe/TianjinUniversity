"""Read-only accepted-checkpoint gate for finishing-stroke planning."""
from pathlib import Path
import argparse,json,sys,hashlib
import numpy as np
from scipy.spatial.transform import Rotation
w=Path(__file__).parent;r=w.parents[1];sys.path.insert(0,str(r/'rl'))
from tomato_native_full_model import registry
from tomato_research_separation import measure
from tomato_exact_blade_coverage import coverage
p=argparse.ArgumentParser();p.add_argument('checkpoint',type=Path);a=p.parse_args();cp=a.checkpoint
meta=json.loads(cp.with_suffix('.json').read_text());z=np.load(cp);data=registry();x=z['x']+[-.0225,0,.0295];pose=z['blade_translation']+[-.0225,0,.0295];rot=z['blade_rotation'];route=json.loads((w/'bodyward_withdrawal_plan_v1.json').read_text());F=np.array(route['target_rotation']);t=np.array(route['target_translation']);world=x@F.T+t
board=json.loads((w/'board_footprint_v02.json').read_text());planes=np.array(board['halfspaces']);margin=-(world[:,:2]@planes[:,:2].T+planes[:,2]).max();sep=measure(data,x,z['v'],z['history']);reaction=np.array(meta['reaction']);applied=np.array(meta['applied_wrench']);unloaded=all(np.linalg.norm(v)<1e-5 for v in [reaction[:3],reaction[3:],applied[:3],applied[3:]])
solid=json.loads((r/'work/exact_blade_cells.json').read_text());triangles=np.array([tri for piece in data['design']['pieces'] for tri in piece['triangles']]);local=(x-pose)@rot
covered=coverage(np.array(solid['vertices']),np.array(solid['cells']),local,triangles,capacity=131072);area=float(sum(row['covered_area_m2'] for row in covered['triangles']));finished=bool(meta['progress']>=1);clear=bool(unloaded and area<=1e-16)
report=dict(scope=__doc__,checkpoint=str(cp),sha256=hashlib.sha256(cp.read_bytes()).hexdigest(),route_finished=finished,blade_surface_overlap_area_m2=area,force_norm_N=float(np.linalg.norm(reaction[:3])),unloaded=unloaded,blade_clear=clear,all_target_nodes_inside_board_with_1mm_margin=bool(margin>=.001),minimum_board_edge_margin_m=float(margin),separation=sep,remaining_patch_ids=np.flatnonzero(z['history'][:,1]<1).tolist(),unreached_patch_ids=np.flatnonzero(~z['seen']).tolist(),ready_for_unloaded_finishing_path_planning=bool(finished and clear and margin>=.001),full_slice_qualified=False,note='This single-frame assessment does not prove sustained support or a successful cut; no simulation state was modified.')
out=cp.parent.parent/('withdrawal_gate_'+cp.stem+'.json');out.write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['separation','remaining_patch_ids','unreached_patch_ids']},indent=2))
