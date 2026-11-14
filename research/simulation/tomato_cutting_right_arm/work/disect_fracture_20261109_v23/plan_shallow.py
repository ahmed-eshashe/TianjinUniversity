from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parent;sys.path.insert(0,str(W.parent/'disect_precontact_20261108_v06'));sys.path.insert(0,str(W.parent/'disect_completion_20261108_v18'))
from blade_contact import CADBlade
from full_surface import FullSurface
from interface_contact import InterfaceSampling
s=FullSurface();sam=InterfaceSampling(s.mesh,s);cad=CADBlade();saved=np.load(W.parent/'disect_physical_20261109_v22/settle_contact_final.npz');q=saved['x'];old=json.loads((W.parent/'disect_physical_20261109_v22/indent_plan.json').read_text());T0=np.array(old['initial_translation_m']);candidates=[]
for tx in np.linspace(-.030,-.018,25):
 T=T0.copy();T[0]=tx;hi=.085;lo=.035
 for _ in range(27):
  T[1]=(hi+lo)/2;phi=cad.query(q[sam.ids],T)['phi'].min()
  if phi>5e-6:hi=T[1]
  else:lo=T[1]
 T[1]=(hi+lo)/2;phi=cad.query(q[sam.cut],T)['phi'];candidates.append(dict(translation_m=T.tolist(),minimum_interface_clearance_m=float(phi.min())))
best=min(candidates,key=lambda r:r['minimum_interface_clearance_m']);out=dict(scope='Frozen shallow trajectory using unchanged CAD orientation; geometry-selected lateral placement',candidates=candidates,selected=best,downward_stroke_m=.002,durations_s=[.04,.08,.02],horizontal_withdrawal_m=.006,bodyward_direction_sim=old['bodyward_direction_sim'],total_s=.14,dt_s=3.125e-6,refined_dt_s=1.5625e-6,sample_interval_s=.0005,wall_cap_s=3600,physical_limits=dict(min_volume_ratio=.1,board_penetration_m=.0001,support_error_m=1e-7,board_edge_margin_m=.001,blade_force_N=2.,blade_sum_force_N=2.,CAD_penetration_m=.0001,discrete_force_balance_N=1e-6,solver_residual=1e-9),refinement_limits=dict(position_m=.0001,velocity_m_s=.005,force_relative=.05,moment_relative=.05,force_floor_N=1e-6,moment_floor_Nm=1e-8,damage_absolute=.01,dissipation_relative=.05,dissipation_floor_J=1e-8,event_time_s=.0005,final_failed_group_set_equal=True),pass_requires_nonzero_damage=True)
(W/'shallow_plan.json').write_text(json.dumps(out,indent=2));print(json.dumps({'selected':best,'scope':out['scope']},indent=2))
