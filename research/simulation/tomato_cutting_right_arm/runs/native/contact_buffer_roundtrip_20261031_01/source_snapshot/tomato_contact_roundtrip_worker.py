"""Guarded synthetic Newton Contacts buffer round-trip; zero physics/forces."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import signal
import traceback

from tomato_contact_snapshot import preview_buffers, collect_snapshot_contacts, ARRAY_FIELDS
from tomato_owned_contact_capture import capture_owned_prefix
from tomato_isaac_startup_worker import write

ROOT = Path(__file__).resolve().parents[1]


def fixture():
    path = ROOT/'runs/source_review/mesh_contact_contract_20261031/synthetic_reference_preview.json'
    reference = json.loads(path.read_text()); context = reference['context']; face = reference['input']
    face.update(id='face', barycentric=[1/3]*3, rigid_barycentric=[1/3]*3, rigid_surface_body_m=[1/3, 1/3, 0.])
    particle = dict(face, id='particle', feature='particle', corners=[0, -1, -1], barycentric=[1., 0., 0.],
                    rigid_barycentric=[1., 0., 0.], rigid_surface_body_m=[0., 0., 0.])
    edge = dict(face, id='edge', feature='edge', corners=[0, 1, -1], barycentric=[.5, .5, 0.],
                rigid_barycentric=[.5, .5, 0.], rigid_surface_body_m=[.5, 0., 0.])
    return [particle, edge, face, dict(face, id='face_duplicate')], context, path


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', type=Path, required=True)
    output = parser.parse_args().output
    def stop(signum, frame):
        raise InterruptedError('Native buffer diagnostic stopped')
    signal.signal(signal.SIGINT, stop); signal.signal(signal.SIGTERM, stop)
    try:
        records, context, fixture_path = fixture()
        sources = ['tomato_contact_roundtrip_worker.py', 'tomato_owned_contact_capture.py', 'tomato_contact_snapshot.py',
                   'tomato_mesh_contact_contract.py', 'tomato_isaac_startup_guard.py', 'tomato_reaction_metadata.py']
        pins = {'rl/'+name: hashlib.sha256((ROOT/'rl'/name).read_bytes()).hexdigest() for name in sources}
        pins[str(fixture_path.relative_to(ROOT))] = hashlib.sha256(fixture_path.read_bytes()).hexdigest()
        identity = {'run_id': output.name, 'episode_id': 'synthetic_populated', 'step': 0,
                    'start_s': 0., 'dt_s': context['dt_s'], 'source_sha256': pins}
        envelope = preview_buffers(records, context, identity, global_capacity=8, body_capacity=8, observed_dynamic_adjacency=[])
        template = envelope['payload']; template['shape_body'].append(1)
        # A fifth, foreign-body synthetic record checks filtering without using
        # dynamic-body adjacency. No body or solver exists in this diagnostic.
        for field in ARRAY_FIELDS:
            template['arrays'][field].append(copy.deepcopy(template['arrays'][field][1]))
        template['arrays']['soft_contact_shape'][-1] = 1
        template['soft_contact_count'] = [5]
        write(output, 'synthetic_source.json', {'context': context, 'records': records, 'expected_prefix': template,
              'fixture_sha256': pins[str(fixture_path.relative_to(ROOT))], 'mechanical_steps': 0})
        import warp as wp
        import newton
        wp.init(); wp.set_device('cuda:0')
        contacts = newton.Contacts(rigid_contact_max=1, soft_contact_max=8, device='cuda:0',
                                  requires_grad=False, clear_buffers=False)
        for field in ARRAY_FIELDS:
            native = getattr(contacts, field); host = native.numpy().copy()
            host[:5] = template['arrays'][field]
            native.assign(wp.array(host, dtype=native.dtype, device=native.device))
        # Deliberate stale inactive tail. Active-prefix capture must not read it.
        host = contacts.soft_contact_indices.numpy().copy(); host[7] = [999, 999, 999]
        contacts.soft_contact_indices.assign(wp.array(host, dtype=wp.vec3i, device='cuda:0'))
        contacts.soft_contact_count.assign(wp.array([5], dtype=int, device='cuda:0'))
        particles = wp.array(template['particle_q_world_m'], dtype=wp.vec3, device='cuda:0')
        mapping = wp.array(template['shape_body'], dtype=int, device='cuda:0')
        poses = wp.array([wp.transform_identity(), wp.transform_identity()], dtype=wp.transform, device='cuda:0')
        wp.synchronize()
        generation = int(contacts.contact_generation.numpy()[0])
        if (output/'stop.request').exists(): raise InterruptedError('Stopped before capture')
        captured, native_context = capture_owned_prefix(contacts, particles, mapping, poses, identity, context,
                        expected_generation=generation, native_capture_authorized=True)
        for field in ARRAY_FIELDS:
            if captured['payload']['arrays'][field] != template['arrays'][field]:
                raise ValueError('Native round-trip changed field '+field)
        observed = collect_snapshot_contacts(captured, identity, native_context, target_body=0, collector_capacity=8)
        observed['pose_source'] = 'owned synthetic native transform array'
        if observed['target_count'] != 4 or observed['global_prefix_records_checked'] != 5:
            raise ValueError('Full-stream/foreign filtering mismatch')
        write(output, 'populated_capture.json', captured); write(output, 'populated_collection.json', observed)
        # Refusal controls act on this private synthetic buffer, never a solver.
        refused = []
        contacts.soft_contact_count.assign(wp.array([8], dtype=int, device='cuda:0')); wp.synchronize()
        try:
            capture_owned_prefix(contacts, particles, mapping, poses, identity, context,
                                 expected_generation=generation, native_capture_authorized=True)
        except ValueError: refused.append('saturated_native_count')
        contacts.soft_contact_count.assign(wp.array([5], dtype=int, device='cuda:0')); wp.synchronize()
        try: collect_snapshot_contacts(captured, identity, native_context, target_body=0, collector_capacity=4)
        except ValueError: refused.append('saturated_target_collector')
        stored_before_clear = contacts.soft_contact_indices.numpy().tolist()
        contacts.clear(); wp.synchronize()
        if contacts.soft_contact_indices.numpy().tolist() != stored_before_clear:
            raise ValueError('Fast count-clear unexpectedly changed inactive stored indices')
        reset_generation = int(contacts.contact_generation.numpy()[0])
        if reset_generation == generation: raise ValueError('Native clear did not bump contact generation')
        try:
            capture_owned_prefix(contacts, particles, mapping, poses, identity, context,
                                 expected_generation=generation, native_capture_authorized=True)
        except ValueError: refused.append('stale_native_generation')
        reset_identity = dict(identity, episode_id='synthetic_after_clear')
        reset, reset_context = capture_owned_prefix(contacts, particles, mapping, poses, reset_identity, context,
                                 expected_generation=reset_generation, native_capture_authorized=True)
        reset_observed = collect_snapshot_contacts(reset, reset_identity, reset_context, target_body=0, collector_capacity=8)
        if reset_observed['target_count'] != 0: raise ValueError('Cleared count included stale tail records')
        try: collect_snapshot_contacts(captured, reset_identity, native_context, target_body=0, collector_capacity=8)
        except ValueError: refused.append('stale_episode_snapshot')
        if len(refused) != 4: raise ValueError('A refusal control unexpectedly succeeded')
        write(output, 'cleared_capture.json', reset); write(output, 'cleared_collection.json', reset_observed)
        write(output, 'roundtrip_checks.json', {
            'all_seven_record_fields_equal_float32_preview': True, 'native_global_count': 5, 'target_count': 4,
            'feature_types': ['particle', 'edge', 'face'], 'raw_duplicate_preserved': True,
            'inactive_tail_poisoned_and_ignored': True, 'clear_preserves_stale_storage_but_reads_zero_prefix': True,
            'contact_generation_before': generation, 'contact_generation_after_clear': reset_generation,
            'refusal_controls': refused, 'mechanical_steps': 0, 'force_evaluations': 0,
            'limits': ['synthetic manually populated Contacts, not collision-generated contacts',
                       'exclusive worker ownership only; no concurrent live solver/IPC',
                       'generation/count clear is not full physics history reset',
                       'no force, penetration or physical normal qualification']})
        write(output, 'worker_result.json', {'diagnostic_passed': True, 'shutdown_requested': True,
              'native_buffer_roundtrip_passed': True, 'mechanical_steps': 0, 'force_evaluations': 0,
              'training': False, 'full_surface_contact_validated': False})
        return 0
    except BaseException:
        write(output, 'worker_failure.json', {'traceback': traceback.format_exc()})
        write(output, 'worker_result.json', {'diagnostic_passed': False, 'shutdown_requested': True})
        traceback.print_exc(); return 1


if __name__ == '__main__': raise SystemExit(main())
