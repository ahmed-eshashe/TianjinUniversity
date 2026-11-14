"""Resume an actual work-paid patch; retain state and full energy accounts."""
from pathlib import Path
import sys,os,json,numpy as np,time,traceback,argparse
from scipy.spatial import ConvexHull
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'));os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba')
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
from compiled_body import Body
from local_continuity import Aggregate
from poly_surface import Surface
from paid_contact_gpu import ContactGPU
from blade_geometry import CAD,certify
from sharp_front import blade_edge,line_resistance,current_sections,novel_area
p=argparse.ArgumentParser();p.add_argument('--hierarchical',action='store_true');p.add_argument('--grid-query',action='store_true');p.add_argument('--geometry-first',action='store_true');p.add_argument('--runtime-mode',action='store_true');p.add_argument('--sparse-contact',action='store_true');p.add_argument('--reduced-quadrature',action='store_true');p.add_argument('--convex-proof',action='store_true');p.add_argument('--gpu-proof',action='store_true');p.add_argument('--hold-pose',action='store_true');p.add_argument('--resolution',type=int,default=4);p.add_argument('--proof-depth',type=int,default=24);p.add_argument('--chunk',type=float,default=.000025);p.add_argument('--resume',type=Path);p.add_argument('--event-period',type=float,default=0.);p.add_argument('--name',default='continue_paid_r1');p.add_argument('--dt',type=float,default=6.25e-6);p.add_argument('--duration',type=float,default=.001);p.add_argument('--events',type=int,default=12);opt=p.parse_args();
if opt.sparse_contact:
 from sparse_contact_gpu import ContactGPU
 if opt.hierarchical:
  from hierarchical_contact_gpu import ContactGPU
out=W/'runs'/opt.name;out.mkdir(exist_ok=False);source=Path('/home/omen/Documents/Codex/experiments/tomato_local_continuity_20261113_v26/runs/paid_opening_r1');report=json.loads((source/'result.json').read_text());a=Aggregate(Body.restore(source/'event_candidate.npz'));cad=CAD();s=Surface(a);ang=np.pi/6;R=np.array([[1.,0,0],[0,np.cos(ang),-np.sin(ang)],[0,np.sin(ang),np.cos(ang)]])@cad.R;edge0=blade_edge(cad,np.zeros(3),R);T0=np.array([.00013,.00304+.003*abs((edge0[1,1]-edge0[0,1])/(edge0[1,2]-edge0[0,2])),0.])-edge0.mean(0);travel=np.array([0.,-.0012,0.]);direction=np.array([0.,-1.,0.]);tangent=edge0[1]-edge0[0];tangent/=np.linalg.norm(tangent);direction-=tangent*(direction@tangent);direction/=np.linalg.norm(direction);t=report['event']['time'];tstart=t;dt=opt.dt;chunk=opt.chunk;pending=report['event']['work_remaining_J'];paid=report['event']['fracture_work_J'];birth=report['event']['contact_birth_energy_J'];accum={k:report['rows'][-1][k] for k in ['tool_work_J','cutting_tool_work_J','friction_J','cutting_numerical_loss_J']};events=[];rows=[];start=time.perf_counter();status='running';last_event_time=tstart
def make(a,s,t):
 fixed=np.isclose(a.body.grid[a.masters,1],-.003);physical=np.isclose(a.body.grid[:,1],-.003)
 if abs(a.E[physical][:,~fixed]).max()>1e-12:raise ValueError('physical support not represented by fixed masters')
 pose0=T0+travel*.5*(1-np.cos(np.pi*tstart/.03)) if opt.hold_pose else T0
 travel0=np.zeros(3) if opt.hold_pose else travel
 g=ContactGPU(a,s,cad,pose0,travel0,dt=dt,fixed=fixed,load=.03,hold=.003,R=R,exact_interior=True,**({'grid_query':opt.grid_query} if opt.sparse_contact else {}),reduced_quadrature=opt.reduced_quadrature,resolution=opt.resolution,capacity=4096,face_capacity=max(256,len(s.triangles)),candidate_capacity=max(4096,min(65536,131*len(s.triangles))));g.steps=round(t/dt);g.base=[(0.,0)];g.certificate_depth=opt.proof_depth
 if opt.convex_proof or opt.gpu_proof:
  from convex_guard import ConvexGuard
  if opt.gpu_proof:
   from convex_guard_gpu import GPUConvexGuard as ConvexGuard
  from compact_proof import CompactProof
  g.volume_certificate=CompactProof(a,s,ConvexGuard(cad))
 with wp.ScopedStream(g.stream):g.clock.assign(np.array([t]))
 return g

def opening(a):
 b=a.body;direction0=np.array([1.,0,0]);best=0.;rankrows=[]
 for r in np.flatnonzero(b.codes%3==1):
  for q in np.flatnonzero(b.codes%3==2):
   if not np.array_equal(b.inv[r],b.inv[q]):continue
   hull=ConvexHull(b.polys[q]);inside=np.max(b.polys[r]@hull.equations[:,:3].T+hull.equations[:,3],axis=1)<1e-12
   for X in b.polys[r][inside]:
    N=np.r_[1.,X]@b.inv[r];jump=N@a.E[b.ids[r]].toarray()-N@a.E[b.ids[q]].toarray();best=max(best,float(np.linalg.norm(jump@a.q)));rankrows.append(jump)
 return best,int(np.linalg.matrix_rank(np.asarray(rankrows),tol=1e-10)) if rankrows else 0

if opt.resume:
 checkpoint=json.loads((opt.resume/'ledger.json').read_text());a=Aggregate(Body.restore(opt.resume/'last_accepted.npz'));s=Surface(a);t=tstart=last_event_time=checkpoint['time'];pending=checkpoint['pending_fracture_J'];paid=checkpoint['paid_fracture_J'];birth=checkpoint['contact_birth_J'];accum=checkpoint['prefix_work']
g=make(a,s,t)
try:
 while t<tstart+opt.duration-1e-12:
  T,tv=g.pose(t);front=line_resistance(a,blade_edge(cad,T,R),direction)
  if front is None:g.configure_resistance(np.ones(len(a.q))/len(a.q),direction,.006,False)
  else:g.configure_vectors(front['B'],front['c'],front['width'],True)
  g.checked_step(round(chunk/dt));a=g.aggregates[0];t=g.steps*dt;obs=g.observe(recompute=not opt.runtime_mode);m=a.metrics();T,tv=g.pose(t);edge=blade_edge(cad,T,R);normal,offset,sections=current_sections(a,edge,direction);front_offset=float(direction@edge[0]);available=pending+obs['earned_fracture_J'];all_area=novel_area(a,sections,direction,front_offset);balance=m['U']+m['T']+obs['contact_energy']-birth-(accum['tool_work_J']+obs['tool_work_J'])-(accum['cutting_tool_work_J']+obs['cutting_tool_work_J'])+accum['friction_J']+obs['friction_J']+accum['cutting_numerical_loss_J']+obs['cutting_numerical_loss_J']+paid+available;scale=max(abs(accum['tool_work_J']+obs['tool_work_J'])+abs(accum['cutting_tool_work_J']+obs['cutting_tool_work_J']),1e-8);gap,rank=opening(a) if not opt.runtime_mode or t>=tstart+opt.duration-1e-12 else (None,None);row=dict(t=t,energy_relative=abs(balance)/scale,gap_m=gap,opening_rank=rank,available_J=available,blade_reached_area_m2=all_area,contact_N=obs['sum_force_N'],cutting_N=float(np.linalg.norm(obs['cutting_force'])),Jmin=float(np.linalg.det(a.body.fields()[2]).min()),nodes=len(a.q));rows.append(row);(out/'progress.json').write_text(json.dumps(row,indent=2));print(json.dumps(row),flush=True)
  if abs(balance)>.05*scale:raise ValueError(('energy balance',balance,scale))
  if available>1e-9 and all_area>1e-11 and (opt.event_period==0 or t-last_event_time>=opt.event_period-1e-12 or t>=tstart+opt.duration-1e-12):
   target=min(all_area,available/80)*(1-1e-7);low=float(np.min(s.positions(a.q)@direction));high=front_offset
   for _ in range(32):
    mid=(low+high)/2
    if novel_area(a,sections,direction,mid)<=target:low=mid
    else:high=mid
   selected=low
   # A moving, deforming crack can also expose a small connecting facet at
   # its previous front. Pay ALL new surface, not only the projected plane.
   geometry_attempts=[]
   for correction in range(8):
    candidate=a.body.clone();candidate.split(normal,offset,cut_id=0,front=(direction,selected),world=True);
    if not opt.runtime_mode:candidate.save(out/'pending_candidate.npz')
    if opt.geometry_first:
     from types import SimpleNamespace
     from scipy.sparse import eye
     trial=Surface(SimpleNamespace(body=candidate,E=eye(len(candidate.u),format='csr'),masters=np.arange(len(candidate.u))))
     area=(trial.tri_area.sum()-s.tri_area.sum())/2
    else:
     a2=Aggregate(candidate);s2=Surface(a2);area=(s2.tri_area.sum()-s.tri_area.sum())/2
    geometry_attempts.append(dict(projected_target=target,actual_area=float(area)))
    if 80*area<=available+1e-15:break
    target*=min(.95,available/(80*area)*.99);low=float(np.min(s.positions(a.q)@direction));high=selected
    for _ in range(32):
     mid=(low+high)/2
     if novel_area(a,sections,direction,mid)<=target:low=mid
     else:high=mid
    selected=low
   if opt.geometry_first:
    a2=Aggregate(candidate);s2=Surface(a2)
    if abs((s2.tri_area.sum()-s.tri_area.sum())/2-area)>1e-15:raise ValueError('geometry-only area disagrees with mechanical representation')
   g2=make(a2,s2,t);cert=g2.volume_certificate(a2.q,T,R,maxdepth=opt.proof_depth) if (opt.convex_proof or opt.gpu_proof) else certify(s2.tets(a2.q),cad,T,R,maxdepth=opt.proof_depth);obs2=g2.observe();dU=obs2['contact_energy']-obs['contact_energy'];checks=dict(positive_area=area>0,paid=80*area<=available+1e-15,projected_area_not_overclaimed=area>=target-1e-15,certificate=cert['passed'],transfer_position=a2.transfer['position_m']<.0001,transfer_weighted_velocity=a2.transfer['weighted_velocity_bound_m_s']<.005,transfer_projection_energy=a2.transfer['energy_relative']<.05,transfer_angular=a2.transfer['angular_relative']<.01,transfer_energy=abs(a2.transfer['elastic_change_J']+a2.transfer['kinetic_change_J'])<.05*scale,birth=abs(dU)<.05*scale,lag=front_offset-selected<.0001,force=obs2['sum_force_N']+np.linalg.norm(obs['cutting_force'])<2);entry=dict(geometry_attempts=geometry_attempts,time=t,checks={k:bool(v) for k,v in checks.items()},area_m2=area,lag_m=front_offset-selected,transfer=a2.transfer,contact_birth_J=dU);events.append(entry)
   if not all(checks.values()):raise ValueError(('event rejected',entry))
   for k in accum:accum[k]+=obs[k]
   pending=available-80*area;paid+=80*area;birth+=dU;a2.body.history[-1]['geometry_only']=False;a2.body.history[-1]['authorization']=entry;a,s,g=a2,s2,g2;last_event_time=t
   if not opt.runtime_mode:a.body.save(out/f'accepted_event_{len(events)}.npz')
   if len(events)>=opt.events:status='bounded_events_complete';break
 else:status='bounded_duration_complete'
except Exception as e:
 status='stopped';traceback.print_exc();(out/'exception.txt').write_text(repr(e));(out/'certificate.json').write_text(json.dumps(getattr(g,'last_certificate',{}),indent=2))
g.state();final=g.observe();prefix={k:accum[k]+final[k] for k in accum};(out/'ledger.json').write_text(json.dumps(dict(time=g.steps*dt,pending_fracture_J=pending+final['earned_fracture_J'],paid_fracture_J=paid,contact_birth_J=birth,prefix_work=prefix),indent=2));g.aggregates[0].body.save(out/'last_accepted.npz');result=dict(status=status,geometry_first=opt.geometry_first,runtime_mode=opt.runtime_mode,resolution=opt.resolution,dt=dt,hold_pose=opt.hold_pose,wall_s=time.perf_counter()-start,simulation_advanced_s=t-tstart,rows=rows,events=events,event_period_s=opt.event_period,paid_fracture_work_J=paid,physical_slice=False,rl_ready=False);(out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k not in ['rows','events']},indent=2))
