"""Bounded stationary scatter-kernel diagnostic; no solver steps or motion."""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import signal
import traceback
from types import SimpleNamespace
from tomato_blade_record_force_worker import PARAMETERS,stationary_checks
from tomato_analytic_force_worker import evaluate_native
from tomato_blade_record_roundtrip_worker import ROOT,PREP,selected_fixtures,publish_owned
from tomato_contact_snapshot import preview_buffers,collect_snapshot_contacts
from tomato_owned_contact_capture import capture_owned_prefix
from tomato_particle_scatter_reference import scatter_reference
from tomato_isaac_startup_worker import write
from tomato_wrench_contract import cross


def fixture_cases():
    cases=selected_fixtures()
    base=cases[0];original=base['records'][0]
    # Equivalent padded edge support for the first selected blade reference.
    edge=copy.deepcopy(base);edge['id']='control:padded_blade_edge'
    edge['records'][0].update(id='edge',feature='edge',corners=[0,1,-1])
    cases.append(edge)
    # A particle placed at the same represented double-precision contact point.
    particle=copy.deepcopy(base);particle['id']='control:blade_particle'
    weights=original['barycentric'];points=base['context']['particles_world_m']
    p=[math.fsum(w*q[k] for w,q in zip(weights,points)) for k in range(3)]
    particle['context']['particles_world_m'].append(p);particle['context']['particle_radius_m'].append(0.)
    particle['records'][0].update(id='particle',feature='particle',corners=[3,-1,-1],barycentric=[1.,0.,0.])
    cases.append(particle)
    # Explicit synthetic all-three-weight control on an analytic planar facet.
    face=copy.deepcopy(base);face['id']='control:three_weight_face';context=face['context']
    context.update(particles_world_m=[[0.,0.,-.001],[1.,0.,-.001],[0.,1.,-.001]],particle_radius_m=[0.,0.,0.],
        rigid_vertices_shape_m=[[0.,0.,0.],[1.,0.,0.],[0.,1.,0.]],rigid_triangles=[[0,1,2]])
    face['records']=[dict(original,id='face',rigid_triangle_id=0,barycentric=[1/3]*3,rigid_barycentric=[1/3]*3,
        rigid_surface_body_m=[1/3,1/3,0.],normal_world=[0.,0.,1.],projected_signed_gap_m=-.001)]
    cases.append(face)
    for case in cases:
        case['context']['particles_world_m'].append([2.,2.,2.])
        case['context']['particle_radius_m'].append(0.)
    return cases


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    out=parser.parse_args().output
    def stop(signum,frame):raise InterruptedError('Particle scatter check stopped')
    signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
    try:
        from tomato_native_worker import validate_inputs
        validate_inputs(ROOT,json.loads((PREP/'single_blade_disabled_worker_config_2132.json').read_text()))
        cases=fixture_cases();pins={}
        names=('tomato_particle_scatter_worker.py','tomato_particle_scatter_reference.py','tomato_blade_record_force_worker.py',
            'tomato_analytic_force_worker.py','tomato_blade_record_roundtrip_worker.py','tomato_contact_snapshot.py',
            'tomato_owned_contact_capture.py','tomato_mesh_contact_contract.py','tomato_contact_precision_audit.py',
            'tomato_reaction_metadata.py','tomato_wrench_contract.py','tomato_isaac_startup_guard.py')
        for name in names:
            p=ROOT/'rl'/name;pins[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
        for case in cases:
            path=case['path'];pins[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
        write(out,'input_manifest.json',{'source_sha256':pins,'parameters':PARAMETERS,
            'fixture_scope':'Two selected blade faces, empty control, equivalent padded edge, particle, synthetic three-weight face; one spectator each.'})
        import warp as wp
        import newton
        from newton._src.solvers.vbd.particle_vbd_kernels import accumulate_particle_body_contact_force_and_hessian
        wp.init();wp.set_device('cuda:0');results=[];point_evaluations=0;launches=0
        for case in cases:
            if (out/'stop.request').exists():raise InterruptedError('Stopped between scatter fixtures')
            write(out,'worker_status.json',{'stage':'native_particle_scatter','case':case['id']})
            context=case['context'];identity=dict(run_id=out.name,episode_id=case['id'],step=0,start_s=0.,dt_s=context['dt_s'],source_sha256=pins)
            template=preview_buffers(case['records'],context,identity,global_capacity=8,body_capacity=8,observed_dynamic_adjacency=[])['payload']
            contacts=newton.Contacts(rigid_contact_max=1,soft_contact_max=8,requires_grad=False,clear_buffers=False,device='cuda:0')
            contacts._enable_rigid_soft_full_surface_contact=True;generation=publish_owned(contacts,template)
            count=len(template['particle_q_world_m']);particles=wp.array(template['particle_q_world_m'],dtype=wp.vec3)
            mapping=wp.array([0],dtype=int);poses=wp.array([wp.transform_identity()],dtype=wp.transform)
            velocity=wp.zeros(1,dtype=wp.spatial_vector);com=wp.zeros(1,dtype=wp.vec3)
            model=SimpleNamespace(device=wp.get_device(),soft_contact_ke=1000.,soft_contact_kd=10.,soft_contact_mu=.5,
                shape_material_ke=wp.array([2500.],dtype=float),shape_material_kd=wp.array([100.],dtype=float),
                shape_material_mu=wp.array([0.],dtype=float),particle_radius=wp.zeros(count,dtype=float),
                shape_margin=wp.zeros(1,dtype=float),body_com=com,shape_body=mapping)
            state=SimpleNamespace(particle_q=particles,body_q=poses,body_qd=velocity)
            settings=SimpleNamespace(rigid_contact_k_start_value=-1.,friction_epsilon=.01)
            def capture():
                return capture_owned_prefix(contacts,particles,mapping,poses,identity,context,expected_generation=generation,
                    native_capture_authorized=True,capture_origin='owned_selected_blade_reference_diagnostic')
            before,native_context=capture();before_velocity=velocity.numpy().tolist()
            collect_snapshot_contacts(before,identity,native_context,target_body=0,collector_capacity=8)
            point=evaluate_native(model,state,contacts,settings) if case['records'] else None
            reference=stationary_checks(before['payload'],point) if point else None
            point_evaluations+=int(point is not None)
            ke=wp.array([1750.]*8,dtype=float);kd=wp.array([55.]*8,dtype=float);mu=wp.zeros(8,dtype=float)
            colors_host=[i%3 for i in range(count)];colors=wp.array(colors_host,dtype=int)
            previous=wp.clone(particles);previous_body=wp.clone(poses)
            forces=wp.zeros(count,dtype=wp.vec3);matrices=wp.zeros(count,dtype=wp.mat33)
            color_checks=[]
            for color in range(3):
                old_f=forces.numpy().tolist();old_h=matrices.numpy().tolist()
                wp.launch(accumulate_particle_body_contact_force_and_hessian,dim=8,inputs=[1/1200,color,previous,
                    particles,colors,.01,model.particle_radius,contacts.soft_contact_indices,contacts.soft_contact_count,8,
                    ke,ke,kd,mu,mapping,poses,previous_body,velocity,com,contacts.soft_contact_shape,
                    contacts.soft_contact_body_pos,contacts.soft_contact_body_vel,contacts.soft_contact_normal,
                    model.shape_margin,contacts.soft_contact_barycentric],outputs=[forces,matrices])
                wp.synchronize();launches+=1;new_f=forces.numpy().tolist();new_h=matrices.numpy().tolist()
                expected_f=[[0.,0.,0.] for _ in range(count)];expected_h=[[[0.]*3 for _ in range(3)] for _ in range(count)]
                if point:
                    arrays=before['payload']['arrays']
                    expected_f,expected_h=scatter_reference(point['force'][0],point['hessian'][0],
                        arrays['soft_contact_indices'][0],arrays['soft_contact_barycentric'][0],count,
                        colors=colors_host,active_color=color)
                ferr=max(abs(new_f[i][j]-old_f[i][j]-expected_f[i][j]) for i in range(count) for j in range(3))
                herr=max(abs(new_h[i][j][k]-old_h[i][j][k]-expected_h[i][j][k]) for i in range(count) for j in range(3) for k in range(3))
                if ferr>1e-5 or herr>1e-4:raise ValueError('Native per-color scatter mismatch')
                if any(new_f[i]!=old_f[i] or new_h[i]!=old_h[i] for i in range(count) if colors_host[i]!=color):
                    raise ValueError('Nonactive color modified')
                color_checks.append({'color':color,'max_force_error_n':ferr,'max_diagonal_stiffness_error_n_m':herr})
            final_f=forces.numpy().tolist();final_h=matrices.numpy().tolist()
            if final_f[-1]!=[0.,0.,0.] or any(v!=0 for row in final_h[-1] for v in row):raise ValueError('Spectator particle modified')
            balance=None
            if point:
                total=[math.fsum(row[j] for row in final_f) for j in range(3)]
                residual=math.dist(total,point['force'][0]);reaction_residual=math.hypot(*[a+b for a,b in zip(total,point['wrench'][0][:3])])
                torque=[math.fsum(cross(p,f)[j] for p,f in zip(template['particle_q_world_m'],final_f))+point['wrench'][0][j+3] for j in range(3)]
                if residual>1e-5 or reaction_residual>1e-5 or math.hypot(*torque)>1e-6:raise ValueError('Algebraic force/moment balance mismatch')
                balance={'summed_particle_force_n':total,'point_force_residual_n':residual,
                    'reconstructed_reaction_residual_n':reaction_residual,'moment_residual_nm':math.hypot(*torque),
                    'raw_barycentric_sum':math.fsum(before['payload']['arrays']['soft_contact_barycentric'][0])}
            after,_=capture()
            if before!=after or before_velocity!=velocity.numpy().tolist():raise ValueError('Diagnostic state changed')
            filename=case['id'].replace(':','_');write(out,filename+'_capture.json',before)
            results.append({'id':case['id'],'point_reference':reference,'color_checks':color_checks,'balance':balance,
                'particle_forces_n':final_f,'particle_diagonal_stiffness_n_m':final_h,'particle_colors':colors_host,
                'spectator_unchanged':True,'physical_and_contact_state_unchanged':True})
        if len(results)!=6 or point_evaluations!=5 or launches!=18:raise ValueError('Unexpected diagnostic scope')
        write(out,'particle_scatter_measurements.json',{'cases':results,'point_force_evaluations':5,'assembly_kernel_launches':18,
            'force_evaluations':18,'mechanical_steps':0,'weights_renormalized':False,
            'comparison_scope':'Stationary fixture scatter: force 1e-5 N, diagonal stiffness 1e-4 N/m, algebraic moment 1e-6 Nm.',
            'off_diagonal_global_stiffness_validated':False,'dynamic_conservation_validated':False,
            'full_blade_contact_path_validated':False})
        write(out,'worker_result.json',{'diagnostic_passed':True,'shutdown_requested':True,'particle_scatter_cases_completed':6,
            'point_force_evaluations':5,'assembly_kernel_launches':18,'force_evaluations':18,'mechanical_steps':0,
            'particle_scatter_checks_passed':True,'training':False,'full_surface_contact_validated':False})
        return 0
    except BaseException:
        write(out,'worker_failure.json',{'traceback':traceback.format_exc()})
        write(out,'worker_result.json',{'diagnostic_passed':False,'shutdown_requested':True})
        traceback.print_exc();return 1


if __name__=='__main__':raise SystemExit(main())
