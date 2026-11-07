"""Two fresh one-step analytic proxy fixtures; no blade or robot state."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import signal
import traceback
from tomato_dynamic_proxy_reference import assess_step
from tomato_isaac_startup_worker import write

ROOT=Path(__file__).resolve().parents[1]
DT=1/1200
ITERATIONS=16


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    out=parser.parse_args().output
    def stop(signum,frame):raise InterruptedError('Dynamic proxy check stopped')
    signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
    try:
        pins={}
        for name in ('tomato_dynamic_proxy_worker.py','tomato_dynamic_proxy_reference.py','tomato_isaac_startup_guard.py'):
            p=ROOT/'rl'/name;pins[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
        write(out,'input_manifest.json',{'source_sha256':pins,'fixture_count':2,'steps_per_fresh_fixture':1,
            'total_step_cap':2,'dt_s':DT,'solver_iterations_per_step':ITERATIONS,
            'scope':'Isolated analytic particle/free-box contact plus fresh clear control. No real blade, robot, cohesive material or PhysX coupling.'})
        import warp as wp
        import newton
        import newton.solvers
        wp.init();wp.set_device('cuda:0');results=[];steps=0
        for name,z in (('free_contact',.001),('clear_control',.003)):
            if (out/'stop.request').exists():raise InterruptedError('Stopped between dynamic fixtures')
            write(out,'worker_status.json',{'stage':'dynamic_proxy_setup','case':name,'committed_steps':steps})
            builder=newton.ModelBuilder(gravity=(0.,0.,0.))
            builder.add_particle(wp.vec3(0.,0.,z),wp.vec3(0.),.01,radius=0.)
            body=builder.add_body(xform=wp.transform_identity(),label='free_dynamic_proxy')
            shape=builder.add_shape_box(body,hx=.01,hy=.01,hz=.002,
                cfg=newton.ModelBuilder.ShapeConfig(density=12500.,ke=2500.,kd=0.,mu=0.,margin=0.,gap=0.))
            builder.color();model=builder.finalize(device='cuda:0')
            model.soft_contact_ke=1000.;model.soft_contact_kd=0.;model.soft_contact_mu=0.
            state_in=model.state();state_out=model.state()
            solver=newton.solvers.SolverVBD(model,iterations=ITERATIONS,rigid_compliant_alm=True,
                integrate_with_external_rigid_solver=False,rigid_avbd_beta=0.)
            if solver.rigid_contact_k_start_value!=-1.:raise ValueError('Expected fixed contact stiffness')
            pipeline=newton.CollisionPipeline(model,broad_phase='nxn',soft_contact_gap=0.,
                soft_contact_max=8,rigid_contact_max=8,enable_rigid_soft_full_surface_contact=True)
            contacts=pipeline.contacts();pipeline.collide(state_in,contacts);wp.synchronize()
            count=int(contacts.soft_contact_count.numpy()[0])
            if count!=(1 if name=='free_contact' else 0):raise ValueError('Unexpected initial contact count')
            def snapshot(state):
                return {'particle_q':state.particle_q.numpy().tolist(),'particle_qd':state.particle_qd.numpy().tolist(),
                        'body_q':state.body_q.numpy().tolist(),'body_qd':state.body_qd.numpy().tolist()}
            before=snapshot(state_in)
            masses={'particle':float(model.particle_mass.numpy()[0]),'body':float(model.body_mass.numpy()[body])}
            half_height=float(model.shape_scale.numpy()[shape][2]);stiffness=.5*(float(model.soft_contact_ke)+float(model.shape_material_ke.numpy()[shape]))
            if not masses['particle']>0 or not masses['body']>0:raise ValueError('Two freely moving masses required')
            if any(v!=0 for p in state_in.particle_f.numpy().tolist()+state_in.body_f.numpy().tolist() for v in p):
                raise ValueError('Unexpected external forces')
            write(out,name+'_initial.json',{'state':before,'masses_kg':masses,'half_height_m':half_height,
                'stiffness_n_m':stiffness,'contact_count':count,'contact_arrays':{
                    field:getattr(contacts,field).numpy()[:count].tolist() for field in
                    ('soft_contact_indices','soft_contact_barycentric','soft_contact_body_pos','soft_contact_normal')}})
            if (out/'stop.request').exists():raise InterruptedError('Stopped before proxy step')
            solver.step(state_in,state_out,None,contacts,DT);wp.synchronize();steps+=1
            after=snapshot(state_out);write(out,name+'_final.json',{'state':after,'committed_steps':steps})
            def scalar(s):
                return dict(particle_z=s['particle_q'][0][2],body_z=s['body_q'][body][2],
                    particle_vz=s['particle_qd'][0][2],body_vz=s['body_qd'][body][2])
            assessment=assess_step(scalar(before),scalar(after),masses['particle'],masses['body'],stiffness,half_height,DT)
            off_axis=[*after['particle_q'][0][:2],*after['particle_qd'][0][:2],*after['body_q'][body][:2],
                      *after['body_qd'][body][:2],*after['body_qd'][body][3:]]
            if any(not math.isfinite(v) or abs(v)>1e-6 for v in off_axis):raise ValueError('Unexpected off-axis motion')
            if math.dist(after['body_q'][body][3:],[0.,0.,0.,1.])>1e-6:raise ValueError('Unexpected rotation')
            cached_k=solver.body_particle_contact_penalty_k.numpy().tolist()[:count]
            cached_kd=solver.body_particle_contact_material_kd.numpy().tolist()[:count]
            cached_mu=solver.body_particle_contact_material_mu.numpy().tolist()[:count]
            if cached_k!=[1750.]*count or cached_kd!=[0.]*count or cached_mu!=[0.]*count:
                raise ValueError('Unexpected native contact material')
            dynamic_count=int(solver.body_particle_contact_counts.numpy()[body])
            if dynamic_count!=count:raise ValueError('Dynamic-body contact adjacency mismatch')
            results.append({'id':name,'before':before,'after':after,'masses_kg':masses,
                'stiffness_n_m':stiffness,'half_height_m':half_height,'assessment':assessment,
                'dynamic_body_contact_count':dynamic_count,'cached_ke':cached_k,'cached_kd':cached_kd,'cached_mu':cached_mu,
                'steps':1,'fresh_model_and_solver':True})
        if steps!=2:raise ValueError('Unexpected step count')
        write(out,'dynamic_proxy_measurements.json',{'cases':results,'committed_steps':2,'dt_s':DT,
            'iterations_per_step':ITERATIONS,'damping_and_friction':0.,'gravity':[0.,0.,0.],
            'comparison_scope':'One-step analytic free-pair fixtures only: position 1e-7 m, velocity 2e-5 m/s, momentum/impulse 2e-7 kg m/s, discrete work/energy identities 2e-8 J.',
            'physical_energy_conservation_expected':False,'backward_euler_numerical_dissipation_accounted':True,
            'full_blade_contact_path_validated':False,'physx_coupling_validated':False})
        write(out,'worker_result.json',{'diagnostic_passed':True,'shutdown_requested':True,
            'dynamic_proxy_cases_completed':2,'committed_steps':2,'dynamic_proxy_checks_passed':True,
            'training':False,'full_surface_contact_validated':False})
        return 0
    except BaseException:
        write(out,'worker_failure.json',{'traceback':traceback.format_exc()})
        write(out,'worker_result.json',{'diagnostic_passed':False,'shutdown_requested':True})
        traceback.print_exc();return 1


if __name__=='__main__':raise SystemExit(main())
