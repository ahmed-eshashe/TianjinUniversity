"""Bounded first work-authorized CAD crack, not a full-slice claim."""
from pathlib import Path
import sys,os,json,numpy as np,time,traceback,argparse
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'));os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba')
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
from compiled_body import Body
from local_continuity import Aggregate
from poly_surface import Surface
from paid_contact_gpu import ContactGPU
from blade_geometry import CAD,certify
from sharp_front import blade_edge,line_resistance,current_sections,novel_area
p=argparse.ArgumentParser();p.add_argument('--tilt',type=float,default=0.);p.add_argument('--proof-depth',type=int,default=24);p.add_argument('--half',action='store_true');p.add_argument('--stroke',type=float,default=.0002);p.add_argument('--load',type=float,default=.005);p.add_argument('--frames',type=int,default=120);p.add_argument('--name',default='first_paid_surface');opt=p.parse_args();dt=3.125e-6 if opt.half else 6.25e-6;chunk=.00005
out=W/'runs'/(opt.name+('_half' if opt.half else ''));out.mkdir(exist_ok=False);a=Aggregate(Body(n=2,h=.003));s=Surface(a);cad=CAD();ang=np.deg2rad(opt.tilt);R=np.array([[1.,0,0],[0,np.cos(ang),-np.sin(ang)],[0,np.sin(ang),np.cos(ang)]])@cad.R;edge0=blade_edge(cad,np.zeros(3),R);T0=np.array([.00013,.00304+.003*abs((edge0[1,1]-edge0[0,1])/(edge0[1,2]-edge0[0,2])),0.])-edge0.mean(0);travel=np.array([0.,-opt.stroke,0.]);direction=np.array([0.,-1.,0.]);tangent=edge0[1]-edge0[0];tangent/=np.linalg.norm(tangent);direction-=tangent*(direction@tangent);direction/=np.linalg.norm(direction);fixed=np.isclose(a.body.grid[a.masters,1],-.003);g=ContactGPU(a,s,cad,T0,travel,dt=dt,fixed=fixed,load=opt.load,hold=.003,R=R);g.certificate_depth=opt.proof_depth;E0=a.metrics()['U']+a.metrics()['T'];rows=[];event=None;status='no_event';start=time.perf_counter();worstenergy=0.
try:
 for frame in range(opt.frames):
  t=g.steps*dt;T,tv=g.pose(t);a=g.aggregates[0];front=line_resistance(a,blade_edge(cad,T,R),direction)
  if front is None:g.configure_resistance(np.ones(len(a.q))/len(a.q),direction,.006,False)
  else:g.configure_vectors(front['B'],front['c'],front['width'],True)
  g.checked_step(round(chunk/dt));q,v=g.state();a=g.aggregates[0];obs=g.observe();m=a.metrics();T,tv=g.pose(g.steps*dt);edge=blade_edge(cad,T,R);normal,offset,sections=current_sections(a,edge,direction);front_offset=float(direction@edge[0]);available=obs['earned_fracture_J'];all_area=novel_area(a,sections,direction,front_offset);energy=m['U']+m['T']+obs['contact_energy']-E0-obs['tool_work_J']-obs['cutting_tool_work_J']+obs['friction_J']+obs['cutting_numerical_loss_J']+available;scale=max(abs(obs['tool_work_J'])+abs(obs['cutting_tool_work_J']),1e-8);worstenergy=max(worstenergy,abs(energy)/scale);row={k:z.tolist() if isinstance(z,np.ndarray) else z for k,z in obs.items()};row.update(time=g.steps*dt,available_area_m2=available/80,blade_reached_area_m2=all_area,energy_relative=abs(energy)/scale,line_present=front is not None);rows.append(row);(out/'progress.json').write_text(json.dumps(row,indent=2))
  if available>1e-9 and all_area>1e-11:
   # Release only reached AND paid material. Any temporarily deferred crack
   # advance is reported; it is not paid by a virtual spring or energy reset.
   target=min(all_area,available/80)*(1-1e-7);world=s.positions(a.q);low=float(np.min(world@direction));high=front_offset
   for _ in range(24):
    mid=(low+high)/2
    if novel_area(a,sections,direction,mid)<=target:low=mid
    else:high=mid
   selected=low;candidate=a.body.clone();candidate.split(normal,offset,cut_id=0,front=(direction,selected),world=True);b2=Aggregate(candidate);s2=Surface(b2);area=(s2.tri_area.sum()-s.tri_area.sum())/2
   if area<=0:continue
   cert=certify(s2.tets(b2.q),cad,T,R)
   checks={'area_paid':80*area<=available+1e-12,'area_geometry_match':abs(area-target)<max(1e-12,target*1e-5),'positive_fracture':area>0,'whole_material':cert['passed'],'not_full_separation':b2.report['physical_components']==1,'transfer_position':b2.transfer['position_m']<=.0001,'transfer_energy':abs(b2.transfer['elastic_change_J']+b2.transfer['kinetic_change_J'])<=.05*scale,'lag_below_penetration_limit':front_offset-selected<.0001}
   b2.body.time=0.;b2.body.steps=0;f2=np.isclose(b2.body.grid[b2.masters,1],-.003);g2=ContactGPU(b2,s2,cad,T0,travel,dt=dt,fixed=f2,load=opt.load,hold=.003,R=R);g2.steps=g.steps
   with wp.ScopedStream(g2.stream):g2.clock.assign(np.array([g.steps*dt]))
   after=g2.observe();dU=after['contact_energy']-obs['contact_energy'];checks['contact_birth_energy']=abs(dU)<=.05*scale;checks['combined_force']=after['sum_force_N']+np.linalg.norm(obs['cutting_force'])<=2;checks['energy_before_event']=abs(energy)<=.05*scale
   event=dict(time=g.steps*dt,checks={k:bool(v) for k,v in checks.items()},accepted=all(checks.values()),reference_area_m2=float(area),fracture_work_J=float(80*area),measured_reserved_work_J=available,work_remaining_J=float(available-80*area),front_lag_m=float(front_offset-selected),contact_birth_energy_J=float(dU),certificate=cert,transfer=b2.transfer,whole_slice=False)
   b2.body.history[-1]['authorization']=event;b2.body.history[-1]['geometry_only']=not event['accepted'];b2.body.save(out/'event_candidate.npz');a.body.save(out/'before_event.npz');status='first_event_accepted' if event['accepted'] else 'first_event_rejected';break
except Exception as e:
 status='stopped';traceback.print_exc();(out/'exception.txt').write_text(repr(e));(out/'rejected_certificate.json').write_text(json.dumps(getattr(g,'last_certificate',{}),indent=2));np.savez_compressed(out/'rejected_state.npz',q=g.q_view[:g.n].copy(),v=g.v_view[:g.n].copy());g.aggregates[0].body.save(out/'last_accepted_body.npz')
 if 'candidate' in locals():candidate.save(out/'uncommitted_candidate.npz')
result=dict(status=status,physical_topology_event=bool(event and event['accepted']),physical_cut_qualified=False,full_separation=False,rl_ready=False,dt=dt,chunk_s=chunk,wall_s=time.perf_counter()-start,maximum_energy_relative=worstenergy,event=event,rows=rows,scope='One small actual-CAD-reached and work-paid patch with original bulk, resistance, inertia and limits. Temporal refinement, continued cutting and complete-loop speed remain separate gates.');(out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
