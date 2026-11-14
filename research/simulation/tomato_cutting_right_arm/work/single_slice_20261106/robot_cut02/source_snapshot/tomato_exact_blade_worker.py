"""Generated actual blade cell coverage, native contacts and implicit references."""
import argparse,json,signal,traceback,hashlib
from pathlib import Path
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1];DT=1/2400

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--geometry-only',action='store_true');args=p.parse_args();out=args.output;app=None;passed=False;steps=0;cases=[];queries=0
 def stop(*args):raise InterruptedError('Exact blade check stopped')
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 try:
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,warp as wp,newton
  from tomato_native_worker import validate_inputs
  from tomato_exact_blade_coverage import coverage,verify_cells
  from tomato_exact_blade_queries import sample
  from tomato_mesh_weighted_contact import MeshContactVBD,publish,implicit_reference
  from tomato_blade_record_roundtrip_worker import selected_fixtures
  from tomato_sdf_native_probe import make_queries
  from tomato_half_step_reaction import collect_reaction
  wp.init();wp.set_device('cuda:0');config=json.loads((ROOT/'runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json').read_text());blade=validate_inputs(ROOT,config)['blade'];cells=json.loads((ROOT/'work/exact_blade_cells.json').read_text())
  if cells['source_blade_sha256']!=config['blade']['sha256'] or not cells['boundary_matches_original_facets']:raise ValueError('Unbound solid blade cells')
  certificate=verify_cells(blade,cells)
  center=(np.min(blade['vertices'],axis=0)+np.max(blade['vertices'],axis=0))/2;vertices=np.asarray(blade['vertices'])-center;faces=blade['triangles'];tet=cells['cells']
  points=make_queries(blade,targeted=True);off=[p for p in points if p['kind']=='signed_offset'];r=sample(vertices,faces,np.array([p['point_m'] for p in off])-center);queries=len(off)
  distance_error=float(max(abs(r['phi']-np.array([p['reference_signed_distance_m'] for p in off]))));normal_error=float(np.max(np.linalg.norm(r['normal']-np.array([p['reference_normal'] for p in off]),axis=1)))
  if distance_error>1e-9 or normal_error>1e-6:raise ValueError('Native float64 authored-field reference mismatch')
  for fixture in selected_fixtures():
   for reverse in (False,True):
    pos=np.asarray(fixture['context']['particles_world_m'])-center;tri=[[2,1,0] if reverse else [0,1,2]];c=coverage(vertices,np.asarray(tet),pos,tri,capacity=2048);s=c['samples'];q=sample(vertices,faces,[x['point_m'] for x in s]) if s else dict(phi=[],normal=[],closest=[])
    if args.geometry_only:
     count=int(sum(p<-1e-12 for p in q['phi']))
     if bool(count)!=bool(fixture['records']):raise ValueError('Geometric crossing/clear result differs')
     cases.append(dict(id=fixture['id'],reversed=reverse,generated_candidates=count,coverage=c));continue
    b=newton.ModelBuilder(gravity=(0.,0.,0.))
    for point in pos:b.add_particle(wp.vec3(*point),wp.vec3(0.),.01,radius=0.)
    proxy=b.add_body(is_kinematic=True);b.add_shape_box(proxy,hx=.001,hy=.001,hz=.001,cfg=newton.ModelBuilder.ShapeConfig(density=0.,ke=2500.,kd=0.,mu=0.,margin=0.,gap=0.));b.color();b.set_coloring([[0],[1],[2]]);model=b.finalize(device='cuda:0');model.soft_contact_ke=1000.;model.soft_contact_kd=0.;model.soft_contact_mu=0.
    contacts=newton.Contacts(rigid_contact_max=8,soft_contact_max=2048,requires_grad=False,clear_buffers=False,device='cuda:0');contacts._enable_rigid_soft_full_surface_contact=True;weights,payload=publish(contacts,s,q);count=len(weights)
    if bool(count)!=bool(fixture['records']):raise ValueError('Generated positive/clear candidate coverage mismatch')
    solver=MeshContactVBD(model,iterations=64,rigid_avbd_beta=0.);solver.contact_weights=wp.array(weights,dtype=float);sin=model.state();sout=model.state();before=sin.particle_q.numpy().copy();expected,velocity=implicit_reference(before,model.particle_mass.numpy(),payload,weights,DT)
    solver.step(sin,sout,None,contacts,DT);wp.synchronize();steps+=1;after=sout.particle_q.numpy();vel=sout.particle_qd.numpy();pe=float(np.max(abs(after-expected)));ve=float(np.max(abs(vel-velocity)))
    reaction=collect_reaction(model,sout,sin,contacts,solver) if count else dict(force=[],wrench=[])
    force=np.asarray(reaction['force']).reshape(-1,3).sum(axis=0);wrench=np.asarray(reaction['wrench']).reshape(-1,6).sum(axis=0);momentum=(model.particle_mass.numpy()[:,None]*vel).sum(axis=0);ie=float(np.linalg.norm(momentum-DT*force))
    if pe>1e-7 or ve>2e-5 or ie>2e-7 or np.linalg.norm(force+wrench[:3])>1e-7:raise ValueError(f'Generated blade contact mechanics mismatch {pe=}, {ve=}, {ie=}')
    cases.append(dict(id=fixture['id'],reversed=reverse,generated_contacts=count,covered_area_m2=sum(x['area_m2'] for x in s),position_error_m=pe,velocity_error_m_s=ve,impulse_error_ns=ie,force_n=force.tolist(),wrench=wrench.tolist(),coverage=c))
    write(out,'exact_blade_partial.json',dict(cases=cases,query_count=queries,distance_error_m=distance_error,normal_error=normal_error))
  if len(cases)!=6 or steps!=(0 if args.geometry_only else 6) or queries!=128:raise ValueError(f'Unexpected blade check counts {queries=}')
  write(out,'exact_blade_geometry_measurements.json' if args.geometry_only else 'exact_blade_measurements.json',dict(geometry_only=args.geometry_only,solid_cell_certificate=certificate,cases=cases,query_count=queries,distance_error_m=distance_error,normal_error=normal_error,cell_file_sha256=hashlib.sha256((ROOT/'work/exact_blade_cells.json').read_bytes()).hexdigest(),newton_steps=steps,quadrature_reference_area_m2=1e-6,contact_stiffness_density_n_m3=1750./1e-6,scope='Six generated soft-triangle/blade intersection cases, 128 native field queries; no solver steps or force qualification.' if args.geometry_only else 'Generated full soft-triangle/actual blade solid intersections; synthetic area-weighted penalty, six native one-step cases. No long cut or calibrated tomato force claim.'))
  passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,exact_blade_passed=passed and not args.geometry_only,exact_blade_geometry_passed=passed and args.geometry_only,newton_steps=steps,controlled_steps=steps,exact_blade_cases=len(cases),blade_field_queries=queries))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
