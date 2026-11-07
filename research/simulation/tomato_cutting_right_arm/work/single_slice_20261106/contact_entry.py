"""Short live-CAD mechanics entry control. No robot or cutting claim."""
from pathlib import Path
import sys,json,time,traceback
import numpy as np
r=Path(__file__).resolve().parents[2];w=Path(__file__).parent;sys.path.insert(0,str(r/'rl'))
import warp as wp
from tomato_native_full_model import registry,configure_solver
from tomato_relative_full_model import RelativeObjectiveVBD,build_relative_model,configure_relative
from tomato_relative_contact import RelativeSurfaceContact
from tomato_local_frame import translated_registry,retain_canonical_material
from tomato_board_support import nodal_plane_stiffness
from tomato_live_cad_candidate import LiveCADCandidate
wp.init();wp.set_device('cuda:0');world=registry();world['x']+=[0,0,.002];origin=np.array([world['design']['cut_x_m'],0,.0295]);data,source_rest=translated_registry(world,origin);fixed=np.array(data['design']['fixture']['node_ids']);k=nodal_plane_stiffness(world);model=build_relative_model(data,fixed_nodes=fixed);h=configure_relative(configure_solver(model,data,iterations=1,solver_class=RelativeObjectiveVBD),data,board_stiffness=k,board_height=-origin[2]);retain_canonical_material(h,world,source_rest);h.surface_contact=RelativeSurfaceContact(data,h.spatial_reference,margin=.0001,capacity=256);h.surface_contact.physical_colors=model.particle_colors
s=LiveCADCandidate(h,data,fixed,maximum_outer=256,velocity_defect_budget_m_s=1e-6,declared_duration_s=.1);a,b=s.state(),s.state();prepared=np.load(r/'runs/native/static_preparation_cached_20261102_01/prepared_equilibrium.npz');a.particle_q.assign(prepared['x_sim']);a.particle_qd.zero_();ref=np.load(r/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz');blade=json.loads((r/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text());R=ref['rotation'];t=ref['translation']-origin;packet={key:ref[key]for key in ['indices','barycentric','areas']};s.pressure.set_cad(vertices=blade['vertices'],triangles=blade['triangles'],**packet,rotation=R,translation=t,com_local=ref['com_local'],source_scope='Existing qualified padded contact packet');s.bind_domain(prepared['x_sim'],blade['vertices'],R,t)
rows=[];dt=1/38400
for i in range(4):
 def audit(start,end,old,new,eligible,interval):
  x=end.particle_q.numpy();v=end.particle_qd.numpy();ratios=np.linalg.det(x[data['cells'][:,1:]]-x[data['cells'][:,:1]])/(6*data['volumes']);ok=bool(np.isfinite(x).all()and np.isfinite(v).all()and ratios.min()>.1 and np.array_equal(x[fixed],prepared['x_sim'][fixed])and np.array_equal(old,new)and not eligible.any());return ok
 start=time.monotonic()
 try:s.audited_step(a,b,dt,eligibility=np.zeros(h.pairs.shape[0],dtype=bool),acceptance_audit=audit)
 except BaseException:
  (w/'entry_failure.json').write_text(json.dumps(dict(step=i,traceback=traceback.format_exc(),iterations=s.last_trace,rows=rows),indent=2));raise
 s.pressure.evaluate(b.particle_q);rows.append(dict(step=i,wall_s=time.monotonic()-start,force=s.pressure.reaction().tolist(),domain_motion=s.domain_motion(b.particle_q),iterations=len(s.last_trace),history_max=float(h.objective_history.numpy()[:,1].max())));a,b=b,a
(w/'entry_result.json').write_text(json.dumps(dict(passed=True,dt=dt,rows=rows,cutting=False,robot_coupling=False,work_qualified=False),indent=2));print(rows)
