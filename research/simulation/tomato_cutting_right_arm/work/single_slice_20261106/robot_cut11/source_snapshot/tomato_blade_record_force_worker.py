"""Stationary native helper checks on explicit blade-reference records only."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import signal
import traceback
from types import SimpleNamespace
from tomato_analytic_force_worker import evaluate_native,stationary_reference
from tomato_blade_record_roundtrip_worker import selected_fixtures,publish_owned,ROOT,PREP,AUDIT
from tomato_contact_snapshot import preview_buffers,collect_snapshot_contacts
from tomato_owned_contact_capture import capture_owned_prefix
from tomato_contact_precision_audit import interpolate32
from tomato_isaac_startup_worker import write

PARAMETERS={'soft_ke':1000.,'soft_kd':10.,'soft_mu':.5,'shape_ke':2500.,'shape_kd':100.,
            'shape_mu':0.,'cold_start_k':-1.,'friction_epsilon':.01}


def stationary_checks(payload,raw,*,stiffness=1750.,damping=55.,friction=0.):
    if payload['soft_contact_count']!=[1]:raise ValueError('Single disclosed contact required')
    a=payload['arrays'];normal=a['soft_contact_normal'][0]
    if math.hypot(*normal)==0 or abs(math.hypot(*normal)-1)>1e-6:raise ValueError('Unit normal required')
    if any(a['soft_contact_body_vel'][0]):raise ValueError('Stationary reference required')
    soft=interpolate32(payload['particle_q_world_m'],a['soft_contact_indices'][0],a['soft_contact_barycentric'][0],fused=True)
    rigid=a['soft_contact_body_pos'][0]  # Disclosed identity body/shape frame only.
    penetration=-math.fsum(n*(p-q) for n,p,q in zip(normal,soft,rigid))
    if penetration<=0:raise ValueError('Expected positive penetration')
    expected_f,expected_r,expected_m,expected_h=stationary_reference(penetration,normal,stiffness,rigid,[0.,0.,0.])
    result={'modeled_binary32_soft_point_m':soft,'projected_penetration_m':penetration,
        'expected_force_n':expected_f,'native_force_n':raw['force'][0],
        'expected_reconstructed_reaction_n':expected_r,'expected_reconstructed_moment_nm':expected_m,
        'force_error_n':math.dist(raw['force'][0],expected_f),
        'reaction_error_n':math.dist(raw['wrench'][0][:3],expected_r),
        'moment_error_nm':math.dist(raw['wrench'][0][3:],expected_m),
        'hessian_error_n_m':max(abs(raw['hessian'][0][i][j]-expected_h[i][j]) for i in range(3) for j in range(3))}
    if any(not math.isfinite(v) for field in ('force','hessian','wrench') for row in raw[field]
           for value in row for v in (value if isinstance(value,list) else [value])):
        raise ValueError('Nonfinite native output')
    if (raw['ke']!=[stiffness] or raw['material_ke']!=[stiffness] or raw['kd']!=[damping] or raw['mu']!=[friction]
        or raw['rigid_point']!=[rigid] or result['force_error_n']>1e-5 or result['reaction_error_n']>1e-5
        or result['moment_error_nm']>1e-6 or result['hessian_error_n_m']>1e-4):
        raise ValueError('Stationary native force/reference comparison failed: '+json.dumps(result))
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    out=parser.parse_args().output
    def stop(signum,frame):raise InterruptedError('Stationary blade force diagnostic stopped')
    signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
    try:
        from tomato_native_worker import validate_inputs
        from tomato_sdf_native_probe import signed_reference
        blade=validate_inputs(ROOT,json.loads((PREP/'single_blade_disabled_worker_config_2132.json').read_text()))['blade']
        cases=selected_fixtures();pins={}
        for p in [Path(__file__),AUDIT,*[c['path'] for c in cases],*[ROOT/'rl'/n for n in
            ('tomato_analytic_force_worker.py','tomato_blade_record_roundtrip_worker.py','tomato_contact_precision_audit.py',
             'tomato_owned_contact_capture.py','tomato_contact_snapshot.py','tomato_mesh_contact_contract.py',
             'tomato_reaction_metadata.py','tomato_wrench_contract.py','tomato_isaac_startup_guard.py',
             'tomato_sdf_native_probe.py','tomato_triangle_distance.py','tomato_native_worker.py')]]:
            pins[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
        write(out,'input_manifest.json',{'source_sha256':pins,'parameters':PARAMETERS,
            'parameter_provenance':'Same disclosed synthetic contact scalars as prior analytic box diagnostic. Not a calibrated blade/tomato material or a production setting change.',
            'solver_instantiated':False,'collision_generated':False})
        import warp as wp
        import newton
        wp.init();wp.set_device('cuda:0');results=[];evaluations=0
        for case in cases:
            if (out/'stop.request').exists():raise InterruptedError('Stopped between force records')
            write(out,'worker_status.json',{'stage':'stationary_selected_blade_force','case':case['id']})
            context=case['context'];identity=dict(run_id=out.name,episode_id=case['id'],step=0,start_s=0.,dt_s=context['dt_s'],source_sha256=pins)
            template=preview_buffers(case['records'],context,identity,global_capacity=8,body_capacity=8,observed_dynamic_adjacency=[])['payload']
            contacts=newton.Contacts(rigid_contact_max=1,soft_contact_max=8,requires_grad=False,clear_buffers=False,device='cuda:0')
            contacts._enable_rigid_soft_full_surface_contact=True;generation=publish_owned(contacts,template)
            particles=wp.array(template['particle_q_world_m'],dtype=wp.vec3)
            mapping=wp.array([0],dtype=int);poses=wp.array([wp.transform_identity()],dtype=wp.transform)
            velocity=wp.zeros(1,dtype=wp.spatial_vector);com=wp.zeros(1,dtype=wp.vec3)
            # Array carriers for an existing helper API; no Model or Solver instance.
            model=SimpleNamespace(device=wp.get_device(),soft_contact_ke=PARAMETERS['soft_ke'],
                soft_contact_kd=PARAMETERS['soft_kd'],soft_contact_mu=PARAMETERS['soft_mu'],
                shape_material_ke=wp.array([PARAMETERS['shape_ke']],dtype=float),
                shape_material_kd=wp.array([PARAMETERS['shape_kd']],dtype=float),
                shape_material_mu=wp.array([PARAMETERS['shape_mu']],dtype=float),
                particle_radius=wp.zeros(len(template['particle_q_world_m']),dtype=float),
                shape_margin=wp.zeros(1,dtype=float),body_com=com,shape_body=mapping)
            state=SimpleNamespace(particle_q=particles,body_q=poses,body_qd=velocity)
            settings=SimpleNamespace(rigid_contact_k_start_value=PARAMETERS['cold_start_k'],friction_epsilon=PARAMETERS['friction_epsilon'])
            def capture():
                return capture_owned_prefix(contacts,particles,mapping,poses,identity,context,
                    expected_generation=generation,native_capture_authorized=True,
                    capture_origin='owned_selected_blade_reference_diagnostic')
            before,native_context=capture();before_velocity=velocity.numpy().tolist()
            observed=collect_snapshot_contacts(before,identity,native_context,target_body=0,collector_capacity=8)
            raw=None;comparison=None
            if observed['target_count']:
                raw=evaluate_native(model,state,contacts,settings);evaluations+=1
                write(out,case['id'].replace(':','_')+'_native_arrays.json',raw)
                comparison=stationary_checks(before['payload'],raw)
                signed=signed_reference(comparison['modeled_binary32_soft_point_m'],blade['vertices'],blade['triangles'])
                comparison['independent_mesh_penetration_m']=-signed['reference_signed_distance_m']
                comparison['geometry_penetration_error_m']=abs(comparison['projected_penetration_m']+signed['reference_signed_distance_m'])
                if signed['reference_signed_distance_m']>=0 or comparison['geometry_penetration_error_m']>1e-7:
                    raise ValueError('Independent geometry discrepancy')
            after,_=capture()
            if before!=after or before_velocity!=velocity.numpy().tolist():raise ValueError('Stationary physical/contact state changed')
            write(out,case['id'].replace(':','_')+'_capture.json',before)
            results.append({'id':case['id'],'contact_count':observed['target_count'],'comparison':comparison,
                            'native_arrays':raw,'state_and_contacts_unchanged':True})
        if evaluations!=2:raise ValueError('Unexpected force evaluation count')
        write(out,'blade_stationary_force_measurements.json',{'cases':results,'parameters':PARAMETERS,
            'mixed_ke':1750.,'mixed_kd':55.,'mixed_mu':0.,'force_evaluations':evaluations,'mechanical_steps':0,
            'comparison_scope':'Selected stationary identity-frame references, zero radius/margin/velocity, frictionless mix. Force/reaction 1e-5 N, moment 1e-6 Nm, Hessian 1e-4 N/m; mesh penetration 1e-7 m.',
            'reaction_is_reconstructed_not_measured':True,'solver_instantiated':False,'collision_generated':False,
            'particle_force_distribution_validated':False,'full_blade_contact_path_validated':False})
        write(out,'worker_result.json',{'diagnostic_passed':True,'shutdown_requested':True,'blade_force_cases_completed':3,
            'stationary_force_checks_passed':True,'force_evaluations':2,'mechanical_steps':0,'training':False,
            'full_surface_contact_validated':False})
        return 0
    except BaseException:
        write(out,'worker_failure.json',{'traceback':traceback.format_exc()})
        write(out,'worker_result.json',{'diagnostic_passed':False,'shutdown_requested':True})
        traceback.print_exc();return 1


if __name__=='__main__':raise SystemExit(main())
