"""Two tetrahedral pieces with shared cohesive face and native post-failure mesh contact."""
import argparse,signal,traceback,math
from pathlib import Path
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1];DT=1/2400

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=None;passed=False;steps=probes=0;records=[]
 def stop(*args):raise InterruptedError('Volumetric coupon stopped')
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 def result():return dict(shutdown_requested=app is not None,diagnostic_passed=passed,volume_coupon_passed=passed,newton_steps=steps,controlled_steps=steps,volume_coupon_cases=len(records),opening_probes=probes,material_calibrated=False)
 try:
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,warp as wp
  import newton
  import newton.solvers
  from tomato_native_group_cohesion import GroupCohesiveVBD,group_blocks
  wp.init();wp.set_device('cuda:0')
  points=[[-.01,0.,0.],[-.0005,0.,0.],[-.0005,.01,0.],[-.0005,0.,.01],[.0005,0.,0.],[.0005,.01,0.],[.0005,0.,.01],[.01,0.,0.]]
  builder=newton.ModelBuilder(gravity=(0.,0.,0.))
  for i,x in enumerate(points):builder.add_particle(wp.vec3(*x),wp.vec3(0.),0. if i<4 else .001,radius=0.)
  tets=[(0,1,2,3),(4,7,5,6)];volumes=[]
  for tet in tets:
   volume=builder.add_tetrahedron(*tet,k_mu=12000.,k_lambda=12000.,k_damp=0.);volumes.append(float(volume))
   for face in ((0,2,1),(0,1,3),(0,3,2),(1,2,3)):builder.add_triangle(*(tet[j] for j in face),tri_ke=0.,tri_ka=0.,tri_kd=0.)
  if min(volumes)<=0.:raise ValueError('Positive tet volumes required')
  builder.color();builder.set_coloring([[i] for i in range(8)]);model=builder.finalize(device='cuda:0');model.soft_contact_ke=1000.;model.soft_contact_kd=0.;model.soft_contact_mu=0.
  solver=GroupCohesiveVBD(model,iterations=48,particle_enable_self_contact=True,particle_self_contact_margin=.0001,particle_self_contact_gap=.0001,particle_rest_shape_contact_exclusion_radius=0.,particle_topological_contact_filter_threshold=2,particle_vertex_contact_buffer_size=32,particle_edge_contact_buffer_size=64)
  pairs=wp.array([[[1,4],[2,5],[3,6]]],dtype=wp.vec2i);rest=wp.array([[[.001,0.,0.]]*3],dtype=wp.vec3);weights=wp.array([[1/3]*3],dtype=float);counts=wp.array([3],dtype=int);nodes=wp.array([[1,2,3,4,5,6]],dtype=int);node_counts=wp.array([6],dtype=int)
  stiffness=wp.array([[[2000.,0.,0.],[0.,800.,0.],[0.,0.,600.]]],dtype=wp.mat33);law=wp.array([[2000.,.001,.004]],dtype=wp.vec3);history=wp.zeros(1,dtype=wp.vec2);eligible=wp.array([1],dtype=int)
  solver.configure(pairs,rest,weights,counts,nodes,node_counts,stiffness,law,history,eligible);sin=model.state();sout=model.state();original=model.particle_q.numpy().copy();forces=wp.zeros(8,dtype=wp.vec3);hess=wp.zeros(8,dtype=wp.mat33)
  path=[]
  for i in range(401):
   if (out/'stop.request').exists():raise InterruptedError('Stopped during volume coupon opening')
   gap=.0041*i/400;positions=original.copy();positions[:4,0]-=gap/2;positions[4:,0]+=gap/2;sin.particle_q.assign(wp.array(positions,dtype=wp.vec3));forces.zero_();hess.zero_()
   for color in range(8):wp.launch(group_blocks,dim=1,inputs=[color,model.particle_colors,sin.particle_q,pairs,rest,weights,counts,nodes,node_counts,stiffness,law,history,eligible,solver.invalid],outputs=[forces,hess])
   wp.synchronize();solver.commit_cohesion(sin);wp.synchronize();probes+=1
   total=float(sum(forces.numpy()[[1,2,3],0]));path.append(dict(opening_m=gap,force_n=total,damage=float(history.numpy()[0,1])))
  work=sum(.5*(a['force_n']+b['force_n'])*(b['opening_m']-a['opening_m']) for a,b in zip(path,path[1:]));target=.004
  if abs(work-target)>.01*target+1e-12 or history.numpy().tolist()[0][1]!=1.:raise ValueError('Volumetric face fracture budget mismatch')
  records.append(dict(id='shared_face_failure',opening_work_j=work,target_j=target,relative_error=abs(work-target)/target,area_m2=.00005,quadrature_pairs=3,one_fracture_budget=True,controlled_rigid_piece_opening=True,path=path))
  def prepare(right_shift,velocity):
   positions=original.copy();positions[4:,0]+=right_shift;vel=np.zeros((8,3),dtype=np.float32);vel[4:,0]=velocity
   for state in (sin,sout):state.particle_q.assign(wp.array(positions,dtype=wp.vec3));state.particle_qd.assign(wp.array(vel,dtype=wp.vec3));state.clear_forces()
   return positions
  def counts_checked():
   info=solver.trimesh_collision_detector.collision_info;total=0;data={}
   for name in ('vertex_colliding_triangles','triangle_colliding_vertices','edge_colliding_edges'):
    raw=getattr(info,name+'_count');sizes=getattr(info,name+'_buffer_sizes')
    if raw is None or sizes is None:
     data[name]='not_recorded';continue
    number=raw.numpy();capacity=sizes.numpy()
    if np.any(number>capacity) or np.any((capacity>0)&(number>=capacity)):raise ValueError('Self-contact buffer saturation')
    data[name]=int(number.sum());total+=int(number.sum())
   return total,data
  prepare(.0041,.1);solver.step(sin,sout,None,None,DT);wp.synchronize();steps+=1
  release=sout.particle_qd.numpy()[4:];err=float(np.max(np.abs(release-np.array([.1,0.,0.]))));count,cd=counts_checked()
  write(out,'volume_coupon_partial.json',dict(cases=records,release_velocity_error_m_s=err,release_contact_counts=cd))
  if err>2e-5 or count!=0:raise ValueError(f'Independent volumetric release mismatch {err=}, {count=}')
  records.append(dict(id='volumetric_release',velocity_error_m_s=err,contact_counts=cd))
  prepare(-.00095,0.);solver.step(sin,sout,None,None,DT);wp.synchronize();steps+=1
  count,cd=counts_checked();after=sout.particle_q.numpy();mean_v=float(np.mean(sout.particle_qd.numpy()[4:,0]));min_gap=float(np.min(after[4:7,0])-np.max(after[1:4,0]))
  if count<=0 or mean_v<=0. or min_gap< -1e-7 or history.numpy().tolist()[0][1]!=1.:raise ValueError(f'Native volumetric reclosure failed {count=}, {mean_v=}, {min_gap=}')
  jacobians=[]
  for tet in tets:
   x=after[list(tet)];q=original[list(tet)];jacobians.append(float(np.linalg.det(np.column_stack([x[j]-x[0] for j in (1,2,3)]))/np.linalg.det(np.column_stack([q[j]-q[0] for j in (1,2,3)]))))
  if min(jacobians)<.1:raise ValueError('Volumetric collapse/inversion')
  records.append(dict(id='post_failure_mesh_contact',contact_counts=cd,right_piece_mean_velocity_x_m_s=mean_v,minimum_face_gap_m=min_gap,volume_ratios=jacobians,no_healing=True,explicit_reclosure_control=True))
  prepare(.0041,0.);solver.step(sin,sout,None,None,DT);wp.synchronize();steps+=1;count,cd=counts_checked();drift=float(np.max(np.abs(sout.particle_qd.numpy()[4:])))
  if count or drift>2e-5:raise ValueError(f'Stale volumetric contact {count=}, {drift=}')
  records.append(dict(id='clear_control',contact_counts=cd,velocity_error_m_s=drift))
  if steps!=3 or probes!=401 or len(records)!=4:raise ValueError('Unexpected volumetric counts')
  write(out,'volumetric_coupon_measurements.json',dict(cases=records,newton_steps=steps,opening_probes=probes,volume_m3=volumes,scope='Two single-tetrahedron pieces, controlled opening, fixed material frame and native mesh self-contact. Synthetic and coarse; no real blade.'))
  passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',result())
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
