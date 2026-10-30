import fcntl,resource,signal,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[3];F=Path(__file__).resolve().parent
resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55)
with (R/'logs/right_arm_control.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 import numpy as np
 sys.path.insert(0,str(R/'rl'))
 from tomato_coupled_contact import cut_pairs
 from tomato_triangle_contact import triangle_geometry
 design=json.loads((R/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5/surface_design.json').read_text());points=np.array([n['position_m'] for n in design['nodes']]);pairs=cut_pairs(design)
 folder=F/'reclosure_batch01/phase02_00';s=json.loads((folder/'summary.json').read_text());lam=np.load(folder/'multipliers.npy');x=np.load(folder/'positions.npy');n=len(pairs);g=triangle_geometry(design,points,pairs,s['tip_z_m'])
 blade=np.asarray(g['matrix'][n:].T@lam[n:]).reshape(-1,3)
 report={'zero_depth_blade_active_rows':int(g['active'][n:].sum()),'loaded_blade_rows':int((lam[n:]>1e-9).sum()),'maximum_blade_multiplier_n':float(lam[n:].max()),'blade_force_on_slice_cut_nodes_x_n':float(blade[pairs[:,0],0].sum()),'blade_force_on_remainder_cut_nodes_x_n':float(blade[pairs[:,1],0].sum()),'maximum_cut_gap_m':float(np.max(x[pairs[:,1],0]-x[pairs[:,0],0])),'conclusion':'At zero insertion, the edge remains an active load-bearing obstacle. This is not a blade-clear supported reclosure test.','simulator':False,'training':False}
 (F/'zero_depth_contact_diagnostic.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
