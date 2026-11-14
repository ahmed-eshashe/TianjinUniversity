"""Isolated selected blade-reference Contacts transfer, zero forces/steps."""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import signal
import traceback
from tomato_contact_snapshot import preview_buffers,collect_snapshot_contacts,ARRAY_FIELDS
from tomato_owned_contact_capture import capture_owned_prefix
from tomato_isaac_startup_worker import write

ROOT=Path(__file__).resolve().parents[1]
PREP=ROOT/'runs/offline/tomato_preupgrade_20261027T171031Z'
AUDIT=ROOT/'runs/offline/real_blade_ambiguity_audit_20261031_01/assessment.json'
INPUT=ROOT/'runs/offline/blade_contact_candidate_probe_20261031_01'
FILES=('wide_edge_through_authored_blade_face.json','authored_blade_edge_through_soft_interior.json',
       'wide_translated_clear_negative_control.json')


def selected_fixtures():
    audit=json.loads(AUDIT.read_text());cases=[]
    for name in FILES:
        path=INPUT/name;relative=str(path.relative_to(ROOT))
        if hashlib.sha256(path.read_bytes()).hexdigest()!=audit['source_and_input_sha256'][relative]:
            raise ValueError('Candidate source differs from audited fixture')
        case=json.loads(path.read_text());summary=next(c for c in audit['cases'] if c['id']==case['id'])
        if case['expected_crossing']:
            if summary['distinct_normal_branch_within_largest_reporting_band']:
                raise ValueError('Selected fixture has reported competing normal')
            if any(b['near_best_sample_count']!=1 for b in summary['sampled_minimum']['bands']):
                raise ValueError('Selected fixture has sampled minimum tie')
        context=copy.deepcopy(case['context']);context.update(body_motion_type='kinematic',body_inv_mass_effective=0.)
        records=[copy.deepcopy(case['deepest_sampled_candidate']['record'])] if case['expected_crossing'] else []
        cases.append({'id':case['id'],'records':records,'context':context,'path':path,
                      'source_sha256':audit['source_and_input_sha256'][relative]})
    return cases


def publish_owned(contacts, template, *, inject_failure=False):
    """Count-last transfer under exclusive ownership; clear/invalidate on error."""
    import warp as wp
    contacts.clear();wp.synchronize()
    try:
        for index,field in enumerate(ARRAY_FIELDS):
            if int(contacts.soft_contact_count.numpy()[0])!=0:
                raise ValueError('Count became visible during field transfer')
            native=getattr(contacts,field);host=native.numpy().copy();count=template['soft_contact_count'][0]
            if count:host[:count]=template['arrays'][field]
            native.assign(wp.array(host,dtype=native.dtype,device=native.device))
            if inject_failure and index==1:raise RuntimeError('Deliberate partial-transfer fixture')
        wp.synchronize()
        contacts.soft_contact_count.assign(wp.array(template['soft_contact_count'],dtype=int,device=contacts.soft_contact_count.device))
        wp.synchronize()
    except BaseException:
        contacts.clear();wp.synchronize()
        raise
    return int(contacts.contact_generation.numpy()[0])


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    out=parser.parse_args().output
    def stop(signum,frame):raise InterruptedError('Blade record transfer stopped')
    signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
    try:
        from tomato_native_worker import validate_inputs
        from tomato_triangle_distance import point_mesh
        from tomato_sdf_native_probe import signed_reference
        blade=validate_inputs(ROOT,json.loads((PREP/'single_blade_disabled_worker_config_2132.json').read_text()))['blade']
        cases=selected_fixtures();pins={}
        for path in [Path(__file__),AUDIT,*[c['path'] for c in cases],*[ROOT/'rl'/n for n in
            ('tomato_owned_contact_capture.py','tomato_contact_snapshot.py','tomato_mesh_contact_contract.py',
             'tomato_reaction_metadata.py','tomato_wrench_contract.py','tomato_isaac_startup_guard.py',
             'tomato_triangle_distance.py','tomato_sdf_native_probe.py','tomato_native_worker.py')]]:
            pins[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
        write(out,'input_manifest.json',{'source_sha256':pins,'selection':'One explicitly whitelisted deepest sampled record per positive fixture; no automated general manifold.',
            'collision_generated':False,'solver_connected':False})
        import warp as wp
        import newton
        wp.init();wp.set_device('cuda:0');results=[];refusals=[]
        for case in cases:
            if (out/'stop.request').exists():raise InterruptedError('Stopped between selected records')
            write(out,'worker_status.json',{'stage':'selected_blade_record_transfer','case':case['id']})
            context=case['context'];identity=dict(run_id=out.name,episode_id=case['id'],step=0,start_s=0.,dt_s=context['dt_s'],source_sha256=pins)
            template=preview_buffers(case['records'],context,identity,global_capacity=8,body_capacity=8,observed_dynamic_adjacency=[])['payload']
            contacts=newton.Contacts(rigid_contact_max=1,soft_contact_max=8,requires_grad=False,clear_buffers=False,device='cuda:0')
            contacts._enable_rigid_soft_full_surface_contact=True
            try:contacts._assert_particle_only_soft_contacts('diagnostic unsupported consumer')
            except NotImplementedError:refusals.append(case['id']+':particle_only_consumer')
            count=len(case['records'])
            if count:
                before=int(contacts.contact_generation.numpy()[0])
                try:publish_owned(contacts,template,inject_failure=True)
                except RuntimeError as exc:
                    if str(exc)!='Deliberate partial-transfer fixture':raise
                    if int(contacts.soft_contact_count.numpy()[0])!=0 or int(contacts.contact_generation.numpy()[0])<=before:
                        raise ValueError('Partial transfer exposed data or failed to invalidate')
                    refusals.append(case['id']+':partial_transfer_invalidated')
            generation=publish_owned(contacts,template)
            # Stale inactive storage must never be mistaken for published data.
            host=contacts.soft_contact_indices.numpy().copy();host[7]=[999,999,999]
            contacts.soft_contact_indices.assign(wp.array(host,dtype=wp.vec3i,device='cuda:0'))
            particles=wp.array(template['particle_q_world_m'],dtype=wp.vec3)
            mapping=wp.array(template['shape_body'],dtype=int)
            poses=wp.array([wp.transform_identity()],dtype=wp.transform);wp.synchronize()
            def capture(expected=generation,ident=identity):
                return capture_owned_prefix(contacts,particles,mapping,poses,ident,context,
                    expected_generation=expected,native_capture_authorized=True,
                    capture_origin='owned_selected_blade_reference_diagnostic')
            captured,native_context=capture()
            for field in ARRAY_FIELDS:
                if captured['payload']['arrays'][field]!=template['arrays'][field]:raise ValueError('Native field mismatch: '+field)
            observed=collect_snapshot_contacts(captured,identity,native_context,target_body=0,collector_capacity=8)
            if observed['target_count']!=count:raise ValueError('Published count differs')
            geometry=[]
            for row in observed['target_records']:
                surface=point_mesh(row['raw_rigid_surface_world_m'],blade['vertices'],blade['triangles'])['distance_m']
                signed=signed_reference(row['soft_point_world_m'],blade['vertices'],blade['triangles'])
                gap_error=abs(row['projected_gap_from_rounded_snapshot_m']-signed['reference_signed_distance_m'])
                normal_error=math.dist(row['normal_world'],case['records'][0]['normal_world'])
                if surface>1e-7 or gap_error>1e-7 or normal_error>1e-6 or signed['reference_signed_distance_m']>=0:
                    raise ValueError('Converted record geometry mismatch')
                geometry.append({'surface_error_m':surface,'projected_gap_error_m':gap_error,'normal_conversion_error':normal_error})
            if count:
                try:collect_snapshot_contacts(captured,identity,native_context,target_body=0,collector_capacity=1)
                except ValueError:refusals.append(case['id']+':saturated_collector')
            contacts.soft_contact_count.assign(wp.array([8],dtype=int));wp.synchronize()
            try:capture()
            except ValueError:refusals.append(case['id']+':saturated_native_count')
            contacts.soft_contact_count.assign(wp.array([count],dtype=int));wp.synchronize()
            storage=contacts.soft_contact_indices.numpy().tolist();contacts.clear();wp.synchronize()
            reset_generation=int(contacts.contact_generation.numpy()[0])
            if reset_generation==generation or storage!=contacts.soft_contact_indices.numpy().tolist():raise ValueError('Clear generation/storage mismatch')
            try:capture()
            except ValueError:refusals.append(case['id']+':stale_generation')
            reset_identity=dict(identity,episode_id=case['id']+':after_clear')
            cleared,cleared_context=capture(reset_generation,reset_identity)
            if collect_snapshot_contacts(cleared,reset_identity,cleared_context,target_body=0,collector_capacity=8)['target_count']!=0:
                raise ValueError('Cleared prefix read stale storage')
            try:collect_snapshot_contacts(captured,reset_identity,native_context,target_body=0,collector_capacity=8)
            except ValueError:refusals.append(case['id']+':stale_episode_snapshot')
            filename=case['id'].replace(':','_')
            write(out,filename+'_capture.json',captured);write(out,filename+'_cleared_capture.json',cleared)
            write(out,filename+'_reference.json',{'records':case['records'],'context':context,'float32_preview':template})
            results.append({'id':case['id'],'native_count':count,'seven_fields_equal':True,'geometry':geometry,
                'generation_published':generation,'generation_cleared':reset_generation,'inactive_tail_ignored':True,
                'clear_does_not_prove_complete_physics_reset':True})
        if len(refusals)!=16:raise ValueError('Expected refusal control did not reject')
        write(out,'blade_record_roundtrip_measurements.json',{'cases':results,'refusal_controls':refusals,
            'mechanical_steps':0,'force_evaluations':0,'collision_generated':False,'solver_connected':False,
            'full_blade_contact_path_validated':False,'conversion_scope':'Selected identity-frame fixtures only: surface/gap 1e-7 m; normal conversion 1e-6. Not a global force/contact acceptance threshold.'})
        write(out,'worker_result.json',{'diagnostic_passed':True,'shutdown_requested':True,
            'blade_record_cases_completed':3,'published_selected_records':2,'refusal_controls_passed':16,
            'mechanical_steps':0,'force_evaluations':0,'training':False,'full_surface_contact_validated':False})
        return 0
    except BaseException:
        write(out,'worker_failure.json',{'traceback':traceback.format_exc()})
        write(out,'worker_result.json',{'diagnostic_passed':False,'shutdown_requested':True})
        traceback.print_exc();return 1


if __name__=='__main__':raise SystemExit(main())
