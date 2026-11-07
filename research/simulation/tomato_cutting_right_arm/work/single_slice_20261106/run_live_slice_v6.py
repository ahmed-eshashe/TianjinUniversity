"""Short live-CAD mechanics entry control. No robot or cutting claim."""
from pathlib import Path
import sys,json,time,traceback
import numpy as np
import argparse,hashlib
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);parser.add_argument('--resume',type=Path);parser.add_argument('--dt',type=float,default=1/2400);parser.add_argument('--padding',type=float,default=8e-5);parser.add_argument('--steps',type=int,default=4800);args=parser.parse_args()
r=Path(__file__).resolve().parents[2];w=Path(__file__).parent;sys.path.insert(0,str(r/'rl'));w=args.output;w.mkdir(parents=True,exist_ok=True)
(w/'sources.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__)]+list((r/'rl').glob('tomato_*.py'))},indent=2))
import warp as wp
from tomato_native_full_model import registry,configure_solver
from tomato_relative_full_model import RelativeObjectiveVBD,build_relative_model,configure_relative
from tomato_relative_contact import RelativeSurfaceContact
from tomato_local_frame import translated_registry,retain_canonical_material
from tomato_board_support import nodal_plane_stiffness
from tomato_live_cad_candidate import LiveCADCandidate
wp.init();wp.set_device('cuda:0');world=registry();world['x']+=[0,0,.002];origin=np.array([world['design']['cut_x_m'],0,.0295]);data,source_rest=translated_registry(world,origin);fixed=np.array(data['design']['fixture']['node_ids']);k=nodal_plane_stiffness(world);model=build_relative_model(data,fixed_nodes=fixed);h=configure_relative(configure_solver(model,data,iterations=1,solver_class=RelativeObjectiveVBD),data,board_stiffness=k,board_height=-origin[2]);retain_canonical_material(h,world,source_rest);h.surface_contact=RelativeSurfaceContact(data,h.spatial_reference,margin=.0001,capacity=256);h.surface_contact.physical_colors=model.particle_colors
s=LiveCADCandidate(h,data,fixed,maximum_outer=256,velocity_defect_budget_m_s=1e-6,declared_duration_s=.1)
from tomato_cached_cad_pressure import CachedCADPressurePacket as ExtendedCADPressurePacket
from tomato_grouped_pressure_assembly import GroupedPressureAssembly
s.pressure=ExtendedCADPressurePacket(s.n);s.assembly=GroupedPressureAssembly(s.assembly.base,s.pressure)
a,b=s.state(),s.state();prepared=np.load(r/'runs/native/static_preparation_cached_20261102_01/prepared_equilibrium.npz');a.particle_q.assign(prepared['x_sim']);a.particle_qd.zero_();ref=np.load(r/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz');blade=json.loads((r/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text());R=ref['rotation'];t=ref['translation']-origin;packet={key:ref[key]for key in ['indices','barycentric','areas']};s.pressure.set_cad(vertices=blade['vertices'],triangles=blade['triangles'],**packet,rotation=R,translation=t,com_local=ref['com_local'],source_scope='Existing qualified padded contact packet');s.bind_domain(prepared['x_sim'],blade['vertices'],R,t)

from scipy.spatial.transform import Rotation
sys.path.insert(0,str(r/'.deps/ipctk-1.6.1-local-cp312'))
import ipctk
from tomato_cut_eligibility import CutEligibility
from tomato_swept_front import SweptFrontDetector
ipctk.set_num_threads(1)
reg=np.load(r/'runs/offline/cut_front_registration_20261102_02/cut_footprints.npz');front=json.loads((r/'runs/offline/cut_front_registration_20261102_02/registration.json').read_text())['front']['face_ids'];solid=json.loads((r/'work/exact_blade_cells.json').read_text());pose=np.r_[t+origin+[0,0,.0001],Rotation.from_matrix(R).as_quat()]
elig=CutEligibility(blade,solid,reg,front,SweptFrontDetector(ipctk),prepared['x_sim']+origin,pose)

from tomato_compiled_partition_refresh import refresh_packet
triangles=np.array([tri for piece in world['design']['pieces'] for tri in piece['triangles']])
# Begin at the saved shallow CAD contact, which is clear of the cohesive interface.
pose=np.r_[t+origin,Rotation.from_matrix(R).as_quat()]
elig=CutEligibility(blade,solid,reg,front,SweptFrontDetector(ipctk),prepared['x_sim']+origin,pose)
checkpoint=None
if args.resume:
 from tomato_cut_eligibility import freeze
 checkpoint=np.load(args.resume);a.particle_q.assign(checkpoint['x']);a.particle_qd.assign(checkpoint['v']);h.objective_history.assign(checkpoint['history']);h.history.assign(checkpoint['history'].astype(np.float32));t=checkpoint['blade_translation'].copy();R=checkpoint['blade_rotation'].copy()
 packet={k:checkpoint['packet_'+k] for k in ['indices','barycentric','areas']}
 s.pressure.set_cad(vertices=blade['vertices'],triangles=blade['triangles'],**packet,rotation=R,translation=t,com_local=ref['com_local'],source_scope='Resumed accepted material packet')
 s.bind_domain(checkpoint['domain_x'],blade['vertices'],R,checkpoint['domain_translation']);s.domain_bound_m=args.padding/2
 elig.world=freeze(a.particle_q.numpy()+origin);elig.pose=freeze(np.r_[t+origin,Rotation.from_matrix(R).as_quat()]);elig.seen=freeze(checkpoint['seen']);elig.eligible=freeze(checkpoint['eligible']);pose=elig.pose.copy()
else:
 # Expand the geometrically covered neighbourhood before increasing the motion bound.
 packet,value,report=refresh_packet(blade,np.asarray(solid['cells']),a.particle_q.numpy()+origin,triangles,world['x'],R,t+origin,ref['com_local'],packet,padding_m=args.padding,lookahead=(a.particle_q.numpy()+origin+a.particle_qd.numpy()*args.dt,t+origin+np.array([R[2,2]/R[0,2],0,-1])*.02*args.dt))
 s.pressure.set_cad(vertices=blade['vertices'],triangles=blade['triangles'],**packet,rotation=R,translation=t,com_local=ref['com_local'],source_scope='40 micrometre padded material coverage')
 s.bind_domain(a.particle_q.numpy(),blade['vertices'],R,t);s.domain_bound_m=args.padding/2
rows=[];dt=args.dt;speed=.02;start_wall=time.monotonic();elapsed=0. if checkpoint is None else float(checkpoint['elapsed']);step_base=0 if checkpoint is None else int(checkpoint['step'])+1
def save_checkpoint(step):
 import shutil
 if (w/'checkpoint.npz').exists():shutil.copy2(w/'checkpoint.npz',w/'checkpoint_previous.npz')
 np.savez(w/'checkpoint_pending.npz',x=a.particle_q.numpy(),v=a.particle_qd.numpy(),history=h.objective_history.numpy(),blade_translation=t,blade_rotation=R,elapsed=elapsed,step=step,seen=elig.seen,eligible=elig.eligible,domain_x=s.domain_x,domain_translation=s.domain_blade[0]-np.asarray(blade['vertices'])[0]@R.T,**{'packet_'+k:v for k,v in packet.items()})
 (w/'checkpoint_pending.npz').replace(w/'checkpoint.npz')
class RetryQuadrature(Exception):pass
for_snapshot=Path(__file__).read_text();(w/'driver_snapshot.py').write_text(for_snapshot)
try:
 for i in range(step_base,step_base+args.steps):
  if (w/'stop.request').exists():break
  end_z=.001-(np.asarray(blade['vertices'])@R.T)[:,2].min()
  if t[2]+origin[2]<=end_z+1e-12:break
  step_dt=min(dt,(t[2]+origin[2]-end_z)/speed)
  lookahead=(a.particle_q.numpy()+origin+a.particle_qd.numpy()*step_dt,t+origin+np.array([R[2,2]/R[0,2],0,-1])*speed*step_dt)
  retries=[]
  for attempt in range(8):
   packet,value,pre_report=refresh_packet(blade,np.asarray(solid['cells']),a.particle_q.numpy()+origin,triangles,world['x'],R,t+origin,ref['com_local'],packet,padding_m=args.padding,lookahead=lookahead)
   s.pressure.set_cad(vertices=blade['vertices'],triangles=blade['triangles'],**packet,rotation=R,translation=t,com_local=ref['com_local'],source_scope='Accepted-state adaptive material packet')
   s.bind_domain(a.particle_q.numpy(),blade['vertices'],R,t);s.domain_bound_m=args.padding/2
   proposed=t+np.array([R[2,2]/R[0,2],0,-1])*speed*step_dt;s.pressure.pose(R,proposed);candidate={}
   def audit(start,end,old,new,mask,interval):
    x=end.particle_q.numpy();v=end.particle_qd.numpy();ratios=np.linalg.det(x[data['cells'][:,1:]]-x[data['cells'][:,:1]])/(6*data['volumes'])
    if not (np.isfinite(x).all() and np.isfinite(v).all() and ratios.min()>.1 and np.array_equal(x[fixed],prepared['x_sim'][fixed]) and np.all(new>=old-1e-14) and np.array_equal(new[~mask],old[~mask])):return False
    candidate['lookahead']=(x+origin,proposed+origin)
    candidate['geometry']=elig.trial(x+origin,np.r_[proposed+origin,pose[3:]])
    try:candidate['post']=refresh_packet(blade,np.asarray(solid['cells']),x+origin,triangles,world['x'],R,proposed+origin,ref['com_local'],packet,padding_m=args.padding)
    except ValueError as error:
     if 'differs from old packet' in str(error):raise RetryQuadrature(str(error)) from error
     raise
    return True
   try:s.audited_step(a,b,step_dt,eligibility=elig.eligible.copy(),acceptance_audit=audit)
   except RetryQuadrature as error:
    retries.append(dict(attempt=attempt,reason=str(error)));lookahead=candidate['lookahead'];s.pressure.pose(R,t);continue
   except ValueError as error:
    if ('iteration budget' in str(error) or 'true-residual' in str(error) or 'descending' in str(error) or 'coverage bound' in str(error)) and step_dt>1/1228800:
     retries.append(dict(attempt=attempt,reason=str(error),dt=step_dt));step_dt*=.5;lookahead=(a.particle_q.numpy()+origin+a.particle_qd.numpy()*step_dt,t+origin+np.array([R[2,2]/R[0,2],0,-1])*speed*step_dt);s.pressure.pose(R,t);continue
    raise
   break
  else:raise ValueError(('No accepted coupled quadrature/mechanics candidate',retries))
  elig.commit(candidate['geometry'],accepted=True);a,b=b,a;t=proposed;elapsed+=step_dt
  packet,value,post_report=candidate['post'];s.pressure.set_cad(vertices=blade['vertices'],triangles=blade['triangles'],**packet,rotation=R,translation=t,com_local=ref['com_local'],source_scope='Post-audited accepted material packet');s.bind_domain(a.particle_q.numpy(),blade['vertices'],R,t);s.domain_bound_m=args.padding/2;s.pressure.evaluate(a.particle_q)
  damage=h.objective_history.numpy()[:,1]
  if i%10==0:
   from tomato_research_separation import measure
   (w/'separation.json').write_text(json.dumps(measure(data,a.particle_q.numpy()+origin,a.particle_qd.numpy(),h.objective_history.numpy()),indent=2))
  row=dict(step=i,sim_time_s=elapsed,dt=step_dt,wall_s=time.monotonic()-start_wall,stroke_m=speed*elapsed,eligible=int(elig.eligible.sum()),damage_max=float(damage.max()),damage_min=float(damage.min()),failed_patches=int(np.sum(damage>=1)),pressure_samples=len(packet['areas']),solver_iterations=len(s.last_trace),retries=len(retries),retry_details=retries,wrench=s.pressure.reaction().tolist())
  rows.append(row)
  if i%10==0:print(row,flush=True);save_checkpoint(i);(w/'status.json').write_text(json.dumps(dict(status='running',last=row,robot_coupled=False,full_slice=False),indent=2))

except BaseException:
 (w/'failure.json').write_text(json.dumps(dict(step=len(rows),traceback=traceback.format_exc(),rows=rows[-20:],trace=s.last_trace),indent=2));raise
finally:
 save_checkpoint(step_base+len(rows)-1)
 (w/'status.json').write_text(json.dumps(dict(status='stopped',accepted_steps=len(rows),elapsed_s=elapsed,full_slice=False,robot_coupled=False),indent=2))
 (w/'rows.json').write_text(json.dumps(rows,indent=2))
