"""Fixed Isaac startup worker with real resource monitoring and owned-group cleanup."""
import argparse
from contextlib import ExitStack
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import threading
import time

from tomato_preupgrade_guard import startup_decision, runtime_decision, stop_group, group_members

ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / '.venv-native/bin/python'
WORKER = ROOT / 'rl/tomato_isaac_startup_worker.py'
COUPON_WORKER = ROOT / 'rl/tomato_coupon_initial_worker.py'
DIRECT_MESH_WORKER = ROOT / 'rl/tomato_direct_mesh_worker.py'
CROSSING_WORKER = ROOT / 'rl/tomato_mesh_crossing_worker.py'
ROUNDTRIP_WORKER = ROOT / 'rl/tomato_contact_roundtrip_worker.py'
ANALYTIC_WORKER = ROOT / 'rl/tomato_analytic_contact_worker.py'
FORCE_WORKER = ROOT / 'rl/tomato_analytic_force_worker.py'
SLAB_WORKER = ROOT / 'rl/tomato_native_slab_worker.py'
BLADE_RECORD_WORKER = ROOT / 'rl/tomato_blade_record_roundtrip_worker.py'
BLADE_FORCE_WORKER = ROOT / 'rl/tomato_blade_record_force_worker.py'
SCATTER_WORKER = ROOT / 'rl/tomato_particle_scatter_worker.py'
DYNAMIC_PROXY_WORKER = ROOT / 'rl/tomato_dynamic_proxy_worker.py'
PHYSX_PROXY_WORKER = ROOT / 'rl/tomato_physx_proxy_worker.py'
FEEDBACK_WORKER = ROOT / 'rl/tomato_contact_feedback_worker.py'
SEQUENCE_WORKER = ROOT / 'rl/tomato_feedback_sequence_worker.py'
OFFSET_WORKER = ROOT / 'rl/tomato_offset_contact_worker.py'
TURNING_WORKER = ROOT / 'rl/tomato_turning_sequence_worker.py'
RESET_WORKER = ROOT / 'rl/tomato_reset_replay_worker.py'
ANISOTROPIC_WORKER = ROOT / 'rl/tomato_anisotropic_contact_worker.py'
SPIN_WORKER = ROOT / 'rl/tomato_spin_coast_worker.py'
SPIN_AUDIT_WORKER = ROOT / 'rl/tomato_spin_accuracy_worker.py'
NEAR_ORIGIN_WORKER = ROOT / 'rl/tomato_spin_near_origin_worker.py'
ANISOTROPIC_SEQUENCE_WORKER = ROOT / 'rl/tomato_anisotropic_sequence_worker.py'
BENT_REBASED_WORKER = ROOT / 'rl/tomato_bent_rebased_worker.py'
BENT_ORIGIN_WORKER = ROOT / 'rl/tomato_bent_origin_worker.py'
BENT_SEQUENCE_WORKER = ROOT / 'rl/tomato_bent_sequence_worker.py'
BENT_CONTACT_WORKER = ROOT / 'rl/tomato_bent_contact_worker.py'
TWO_JOINT_REPLAY_WORKER = ROOT / 'rl/tomato_two_joint_replay_worker.py'
TWO_JOINT_SEQUENCE_WORKER = ROOT / 'rl/tomato_two_joint_sequence_worker.py'
TWO_JOINT_CONTACT_WORKER = ROOT / 'rl/tomato_two_joint_contact_worker.py'
TWO_JOINT_WORKER = ROOT / 'rl/tomato_two_joint_interface_worker.py'
HINGE_WORKER = ROOT / 'rl/tomato_hinge_interface_worker.py'
HINGE_CONTACT_WORKER = ROOT / 'rl/tomato_hinge_contact_worker.py'
HINGE_SEQUENCE_WORKER = ROOT / 'rl/tomato_hinge_sequence_worker.py'
HINGE_REPLAY_WORKER = ROOT / 'rl/tomato_hinge_replay_worker.py'
SPIN_AUDIT_MODES = {'spin_audit_1': 1, 'spin_audit_2': 2, 'spin_audit_4': 4}
SDF_EXPERIMENTS = {
    'coupon_tight512': (512, 0.005),
    'coupon_fine1024': (1024, 0.05),
    'coupon_tight1024': (1024, 0.005),
}


def worker_passed(worker, mode):
    if worker.get('shutdown_requested') is not True:
        return False
    if mode == 'startup':
        return worker.get('startup_step_passed') is True and worker.get('steps') == 1
    if mode == 'two_joint_replay':
        return (worker.get('diagnostic_passed') is True and worker.get('two_joint_replay_checks_passed') is True
                and worker.get('two_joint_replay_cases_completed') == 2 and worker.get('controlled_steps') == 66
                and worker.get('newton_steps') == 132 and worker.get('cuda_state_echoes') == 138
                and worker.get('reset_cycles_completed') == 2 and worker.get('dirty_wrench_resets') == 4
                and worker.get('replay_comparisons') == 4)
    if mode == 'hinge_replay':
        return (worker.get('diagnostic_passed') is True and worker.get('hinge_replay_checks_passed') is True
                and worker.get('hinge_replay_cases_completed') == 2 and worker.get('controlled_steps') == 66
                and worker.get('newton_steps') == 132 and worker.get('cuda_state_echoes') == 138
                and worker.get('reset_cycles_completed') == 2 and worker.get('dirty_wrench_resets') == 4
                and worker.get('replay_comparisons') == 4)
    if mode == 'bent_rebased':
        return (worker.get('diagnostic_passed') is True and worker.get('bent_rebased_checks_passed') is True
                and worker.get('bent_rebased_cases_completed') == 2 and worker.get('controlled_steps') == 32
                and worker.get('newton_steps') == 64 and worker.get('cuda_state_echoes') == 66
                and worker.get('min_coast_steps',0) >= 3 and worker.get('natural_separation') is True)
    if mode == 'bent_origin':
        return (worker.get('diagnostic_passed') is True and worker.get('bent_origin_checks_passed') is True
                and worker.get('bent_origin_cases_completed') == 2 and worker.get('controlled_steps') == 32
                and worker.get('newton_steps') == 64 and worker.get('cuda_state_echoes') == 66
                and worker.get('min_coast_steps',0) >= 3 and worker.get('natural_separation') is True)
    if mode == 'bent_sequence':
        return (worker.get('diagnostic_passed') is True and worker.get('bent_sequence_checks_passed') is True
                and worker.get('bent_sequence_cases_completed') == 2 and worker.get('controlled_steps') == 32
                and worker.get('newton_steps') == 64 and worker.get('cuda_state_echoes') == 66
                and worker.get('min_coast_steps',0) >= 3 and worker.get('natural_separation') is True)
    if mode == 'two_joint_sequence':
        return (worker.get('diagnostic_passed') is True and worker.get('two_joint_sequence_checks_passed') is True
                and worker.get('two_joint_sequence_cases_completed') == 2 and worker.get('controlled_steps') == 32
                and worker.get('newton_steps') == 64 and worker.get('cuda_state_echoes') == 66
                and worker.get('min_coast_steps',0) >= 3 and worker.get('natural_separation') is True)
    if mode == 'hinge_sequence':
        return (worker.get('diagnostic_passed') is True and worker.get('hinge_sequence_checks_passed') is True
                and worker.get('hinge_sequence_cases_completed') == 2 and worker.get('controlled_steps') == 32
                and worker.get('newton_steps') == 64 and worker.get('cuda_state_echoes') == 66
                and worker.get('min_coast_steps',0) >= 3 and worker.get('natural_separation') is True)
    if mode == 'bent_contact':
        return (worker.get('diagnostic_passed') is True and worker.get('bent_contact_checks_passed') is True
                and worker.get('bent_contact_cases_completed') == 2 and worker.get('controlled_steps') == 2
                and worker.get('newton_steps') == 4 and worker.get('cuda_state_echoes') == 6
                and worker.get('clear_controls_passed') == 2)
    if mode == 'two_joint_contact':
        return (worker.get('diagnostic_passed') is True and worker.get('two_joint_contact_checks_passed') is True
                and worker.get('two_joint_contact_cases_completed') == 2 and worker.get('controlled_steps') == 2
                and worker.get('newton_steps') == 4 and worker.get('cuda_state_echoes') == 6
                and worker.get('clear_controls_passed') == 2)
    if mode == 'hinge_contact':
        return (worker.get('diagnostic_passed') is True and worker.get('hinge_contact_checks_passed') is True
                and worker.get('hinge_contact_cases_completed') == 2 and worker.get('controlled_steps') == 2
                and worker.get('newton_steps') == 4 and worker.get('cuda_state_echoes') == 6
                and worker.get('clear_controls_passed') == 2)
    if mode == 'two_joint_interface':
        return (worker.get('diagnostic_passed') is True and worker.get('two_joint_checks_passed') is True
                and worker.get('two_joint_cases_completed') == 2 and worker.get('controlled_steps') == 2
                and worker.get('cuda_state_echoes') == 4 and worker.get('newton_steps') == 0)
    if mode == 'hinge_interface':
        return (worker.get('diagnostic_passed') is True and worker.get('hinge_checks_passed') is True
                and worker.get('hinge_cases_completed') == 2 and worker.get('controlled_steps') == 2
                and worker.get('cuda_state_echoes') == 4 and worker.get('newton_steps') == 0)
    if mode == 'anisotropic_sequence':
        return (worker.get('diagnostic_passed') is True and worker.get('anisotropic_sequence_checks_passed') is True
                and worker.get('anisotropic_sequence_cases_completed') == 2 and worker.get('newton_steps') == 64
                and worker.get('physx_steps') == 32 and worker.get('min_coast_steps',0) >= 3
                and worker.get('normals_updated') is True)
    if mode == 'near_origin_spin':
        return (worker.get('diagnostic_passed') is True and worker.get('audit_measurements_completed') is True
                and worker.get('physical_accuracy_passed') is True and worker.get('near_origin_fixture') is True
                and worker.get('audit_cases_completed') == 3 and worker.get('refinement') == 2
                and worker.get('physx_steps') == 32 and worker.get('newton_steps') == 0
                and worker.get('cuda_state_echoes') == 96 and worker.get('gyro_control_distinguished') is True)
    if mode in SPIN_AUDIT_MODES:
        factor=SPIN_AUDIT_MODES[mode]
        return (worker.get('diagnostic_passed') is True and worker.get('audit_measurements_completed') is True
                and worker.get('audit_cases_completed') == 3 and worker.get('refinement') == factor
                and worker.get('physx_steps') == 16*factor and worker.get('newton_steps') == 0
                and worker.get('cuda_state_echoes') == 48*factor)
    if mode == 'spin_coast':
        return (worker.get('diagnostic_passed') is True and worker.get('spin_checks_passed') is True
                and worker.get('spin_cases_completed') == 3 and worker.get('newton_steps') == 0
                and worker.get('physx_steps') == 16 and worker.get('cuda_state_echoes') == 48
                and worker.get('gyro_control_distinguished') is True)
    if mode == 'anisotropic_contact':
        return (worker.get('diagnostic_passed') is True and worker.get('anisotropic_checks_passed') is True
                and worker.get('anisotropic_cases_completed') == 2 and worker.get('newton_steps') == 2
                and worker.get('physx_steps') == 1 and worker.get('world_tensor_exercised') is True)
    if mode == 'reset_replay':
        return (worker.get('diagnostic_passed') is True and worker.get('reset_checks_passed') is True
                and worker.get('reset_cases_completed') == 2 and worker.get('newton_steps') == 68
                and worker.get('physx_steps') == 34 and worker.get('reset_cycles_completed') == 2
                and worker.get('replay_comparisons') == 4 and worker.get('dirty_wrench_resets') == 4)
    if mode == 'turning_sequence':
        return (worker.get('diagnostic_passed') is True and worker.get('turning_sequence_checks_passed') is True
                and worker.get('turning_cases_completed') == 2 and worker.get('newton_steps') == 32
                and worker.get('physx_steps') == 16 and worker.get('min_coast_steps',0) >= 3
                and worker.get('normals_updated') is True)
    if mode == 'offset_contact':
        return (worker.get('diagnostic_passed') is True and worker.get('offset_contact_checks_passed') is True
                and worker.get('offset_contact_cases_completed') == 2 and worker.get('newton_steps') == 2
                and worker.get('physx_steps') == 1)
    if mode == 'feedback_sequence':
        return (worker.get('diagnostic_passed') is True and worker.get('sequence_checks_passed') is True
                and worker.get('sequence_cases_completed') == 2 and worker.get('newton_steps') == 32
                and worker.get('physx_steps') == 16 and worker.get('cleared_contact_coast_steps', 0) >= 3)
    if mode == 'contact_feedback':
        return (worker.get('diagnostic_passed') is True and worker.get('feedback_cases_completed') == 2
                and worker.get('newton_steps') == 2 and worker.get('physx_steps') == 1
                and worker.get('feedback_checks_passed') is True)
    if mode == 'physx_proxy':
        return (worker.get('diagnostic_passed') is True and worker.get('physx_proxy_cases_completed') == 2
                and worker.get('controlled_steps') == 2 and worker.get('cuda_state_echoes_completed') == 2
                and worker.get('physx_proxy_checks_passed') is True)
    if mode == 'dynamic_proxy':
        return (worker.get('diagnostic_passed') is True and worker.get('dynamic_proxy_cases_completed') == 2
                and worker.get('committed_steps') == 2 and worker.get('dynamic_proxy_checks_passed') is True)
    if mode == 'particle_scatter':
        return (worker.get('diagnostic_passed') is True and worker.get('particle_scatter_cases_completed') == 6
                and worker.get('particle_scatter_checks_passed') is True and worker.get('point_force_evaluations') == 5
                and worker.get('assembly_kernel_launches') == 18 and worker.get('force_evaluations') == 18
                and worker.get('mechanical_steps') == 0)
    if mode == 'blade_record_forces':
        return (worker.get('diagnostic_passed') is True and worker.get('blade_force_cases_completed') == 3
                and worker.get('stationary_force_checks_passed') is True and worker.get('mechanical_steps') == 0
                and worker.get('force_evaluations') == 2)
    if mode == 'blade_record_roundtrip':
        return (worker.get('diagnostic_passed') is True and worker.get('blade_record_cases_completed') == 3
                and worker.get('published_selected_records') == 2 and worker.get('refusal_controls_passed') == 16
                and worker.get('mechanical_steps') == 0 and worker.get('force_evaluations') == 0)
    if mode == 'native_slab':
        return (worker.get('diagnostic_passed') is True and worker.get('slab_optimizer_cases_completed') == 16
                and worker.get('slab_queries_completed') == 19 and worker.get('mechanical_steps') == 0
                and worker.get('force_evaluations') == 0)
    if mode == 'analytic_forces':
        return (worker.get('diagnostic_passed') is True and worker.get('analytic_force_cases_completed') == 6
                and worker.get('reference_version') == 2 and worker.get('geometry_checks_passed') is True
                and worker.get('arithmetic_checks_passed') is True
                and worker.get('mechanical_steps') == 0 and worker.get('force_evaluations') == 4)
    if mode == 'analytic_contacts':
        return (worker.get('diagnostic_passed') is True and worker.get('analytic_collision_cases_completed') == 6
                and worker.get('mechanical_steps') == 0 and worker.get('force_evaluations') == 0)
    if mode == 'contact_roundtrip':
        return (worker.get('diagnostic_passed') is True and worker.get('native_buffer_roundtrip_passed') is True
                and worker.get('mechanical_steps') == 0 and worker.get('force_evaluations') == 0)
    if mode == 'mesh_crossings':
        return (worker.get('diagnostic_passed') is True and worker.get('crossing_cases_completed') == 11
                and worker.get('mechanical_steps') == 0)
    if mode == 'direct_mesh_double':
        return (worker.get('diagnostic_passed') is True and worker.get('direct_queries_completed') == 562
                and worker.get('mechanical_steps') == 0 and worker.get('double_precision_all_facets') is True)
    if mode in ('direct_mesh', 'direct_mesh_centered'):
        return (worker.get('diagnostic_passed') is True and worker.get('direct_queries_completed') == 562
                and worker.get('mechanical_steps') == 0 and
                (mode == 'direct_mesh' or worker.get('centered_coordinates') is True))
    if mode in SDF_EXPERIMENTS:
        resolution, padding = SDF_EXPERIMENTS[mode]
        return (worker.get('diagnostic_passed') is True and worker.get('committed_steps') == 12
                and worker.get('targeted_sdf_completed') is True and
                worker.get('sdf_resolution') == resolution and worker.get('sdf_cooking_padding_m') == padding)
    if mode in ('coupon_target256', 'coupon_target512'):
        return (worker.get('diagnostic_passed') is True and worker.get('committed_steps') == 12
                and worker.get('targeted_sdf_completed') is True and
                worker.get('sdf_resolution') == {'coupon_target256': 256, 'coupon_target512': 512}[mode])
    if mode in ('coupon_sdf256', 'coupon_sdf512'):
        return (worker.get('diagnostic_passed') is True and worker.get('committed_steps') == 12
                and worker.get('sdf_queries_completed') is True and
                worker.get('sdf_resolution') == {'coupon_sdf256': 256, 'coupon_sdf512': 512}[mode])
    if mode in ('coupon_initial', 'coupon_stationary_sdf'):
        expected = 1 if mode == 'coupon_initial' else 12
        return (worker.get('diagnostic_passed') is True and worker.get('committed_steps') == expected
                and (mode == 'coupon_initial' or worker.get('sdf_queries_completed') is True))
    raise ValueError('Unknown fixed diagnostic mode')


def hardware_sample():
    available = next(int(line.split()[1]) * 1024 for line in
                     Path('/proc/meminfo').read_text().splitlines() if line.startswith('MemAvailable:'))
    raw = subprocess.check_output(
        ['nvidia-smi', '--query-gpu=memory.used,memory.total', '--format=csv,noheader,nounits'],
        text=True, timeout=1)
    rows = raw.strip().splitlines()
    if len(rows) != 1:
        raise ValueError('This check requires exactly one GPU')
    used, total = [int(value.strip()) * 1024**2 for value in rows[0].split(',')]
    if not 0 <= used <= total:
        raise ValueError('Invalid GPU reading')
    return available, total - used


def supervise(output, *, monitor=hardware_sample, wall_s=180, mode='startup', _fixture_command=None):
    """Only CLI route is the fixed startup worker; fixture injection is for stdlib tests."""
    if not 0 < wall_s <= 180:
        raise ValueError('Worker budget must be at most 180 seconds')
    if mode not in ('startup', 'bent_rebased', 'bent_origin', 'bent_sequence', 'bent_contact', 'two_joint_replay', 'two_joint_sequence', 'two_joint_contact', 'two_joint_interface', 'hinge_replay', 'hinge_sequence', 'hinge_contact', 'hinge_interface', 'anisotropic_sequence', 'near_origin_spin', *SPIN_AUDIT_MODES, 'spin_coast', 'anisotropic_contact', 'reset_replay', 'turning_sequence', 'offset_contact', 'feedback_sequence', 'contact_feedback', 'physx_proxy', 'dynamic_proxy', 'particle_scatter', 'blade_record_forces', 'blade_record_roundtrip', 'native_slab', 'analytic_forces', 'analytic_contacts', 'contact_roundtrip', 'mesh_crossings', 'direct_mesh', 'direct_mesh_centered', 'direct_mesh_double', 'coupon_initial', 'coupon_stationary_sdf', 'coupon_sdf256', 'coupon_sdf512', 'coupon_target256', 'coupon_target512') and mode not in SDF_EXPERIMENTS:
        raise ValueError('Only fixed startup or stationary coupon diagnostic allowed')
    worker_path = WORKER if mode == 'startup' else COUPON_WORKER
    if mode in ('direct_mesh', 'direct_mesh_centered', 'direct_mesh_double'):
        worker_path = DIRECT_MESH_WORKER
    if mode == 'mesh_crossings':
        worker_path = CROSSING_WORKER
    if mode == 'contact_roundtrip':
        worker_path = ROUNDTRIP_WORKER
    if mode == 'two_joint_replay':
        worker_path = TWO_JOINT_REPLAY_WORKER
    if mode == 'hinge_replay':
        worker_path = HINGE_REPLAY_WORKER
    if mode == 'two_joint_sequence':
        worker_path = TWO_JOINT_SEQUENCE_WORKER
    if mode == 'hinge_sequence':
        worker_path = HINGE_SEQUENCE_WORKER
    if mode == 'bent_rebased':
        worker_path = BENT_REBASED_WORKER
    if mode == 'bent_origin':
        worker_path = BENT_ORIGIN_WORKER
    if mode == 'bent_sequence':
        worker_path = BENT_SEQUENCE_WORKER
    if mode == 'bent_contact':
        worker_path = BENT_CONTACT_WORKER
    if mode == 'two_joint_contact':
        worker_path = TWO_JOINT_CONTACT_WORKER
    if mode == 'hinge_contact':
        worker_path = HINGE_CONTACT_WORKER
    if mode == 'two_joint_interface':
        worker_path = TWO_JOINT_WORKER
    if mode == 'hinge_interface':
        worker_path = HINGE_WORKER
    if mode == 'anisotropic_sequence':
        worker_path = ANISOTROPIC_SEQUENCE_WORKER
    if mode == 'near_origin_spin':
        worker_path = NEAR_ORIGIN_WORKER
    if mode in SPIN_AUDIT_MODES:
        worker_path = SPIN_AUDIT_WORKER
    if mode == 'spin_coast':
        worker_path = SPIN_WORKER
    if mode == 'anisotropic_contact':
        worker_path = ANISOTROPIC_WORKER
    if mode == 'reset_replay':
        worker_path = RESET_WORKER
    if mode == 'turning_sequence':
        worker_path = TURNING_WORKER
    if mode == 'offset_contact':
        worker_path = OFFSET_WORKER
    if mode == 'feedback_sequence':
        worker_path = SEQUENCE_WORKER
    if mode == 'contact_feedback':
        worker_path = FEEDBACK_WORKER
    if mode == 'physx_proxy':
        worker_path = PHYSX_PROXY_WORKER
    if mode == 'dynamic_proxy':
        worker_path = DYNAMIC_PROXY_WORKER
    if mode == 'particle_scatter':
        worker_path = SCATTER_WORKER
    if mode == 'blade_record_forces':
        worker_path = BLADE_FORCE_WORKER
    if mode == 'blade_record_roundtrip':
        worker_path = BLADE_RECORD_WORKER
    if mode == 'native_slab':
        worker_path = SLAB_WORKER
    if mode == 'analytic_forces':
        worker_path = FORCE_WORKER
    if mode == 'analytic_contacts':
        worker_path = ANALYTIC_WORKER
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    process = None
    reason = 'exception'
    errors = 0
    warning = False
    samples = []
    started = None
    returncode = None
    remaining = []
    timer = None
    timed_out = threading.Event()
    command = _fixture_command or [str(PYTHON), str(worker_path), '--output', str(output)]
    if mode == 'near_origin_spin' and not _fixture_command:
        command += ['--refinement', '2']
    if mode in SPIN_AUDIT_MODES and not _fixture_command:
        command += ['--refinement', str(SPIN_AUDIT_MODES[mode])]
    if mode == 'direct_mesh_centered' and not _fixture_command:
        command.append('--centered')
    if mode == 'direct_mesh_double' and not _fixture_command:
        command.append('--double')
    if mode in ('coupon_stationary_sdf', 'coupon_sdf256', 'coupon_sdf512') and not _fixture_command:
        command.append('--stationary-sdf')
        command += ['--sdf-resolution', str({'coupon_stationary_sdf': 128, 'coupon_sdf256': 256, 'coupon_sdf512': 512}[mode])]
    if mode in ('coupon_target256', 'coupon_target512') and not _fixture_command:
        command += ['--stationary-sdf', '--targeted-sdf', '--sdf-resolution',
                    str({'coupon_target256': 256, 'coupon_target512': 512}[mode])]
    if mode in SDF_EXPERIMENTS and not _fixture_command:
        resolution, padding = SDF_EXPERIMENTS[mode]
        command += ['--stationary-sdf', '--targeted-sdf', '--sdf-resolution', str(resolution),
                    '--sdf-padding', str(padding)]

    def interrupt(signum, frame):
        raise InterruptedError('Shutdown signal ' + str(signum))

    previous = {}
    with ExitStack() as stack:
        for name in ('offline_overnight.lock', 'right_arm_control.lock'):
            lock = stack.enter_context((ROOT / 'logs' / name).open('a'))
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            ram, vram = monitor()
            if not startup_decision(ram, vram):
                reason = 'startup_refused'
            else:
                for sig in (signal.SIGINT, signal.SIGTERM):
                    previous[sig] = signal.signal(sig, interrupt)
                env = os.environ.copy()
                env.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONUNBUFFERED='1')
                manifest = {
                    'command': command, 'worker_wall_budget_s': wall_s,
                    'cleanup_grace_s': 2, 'startup_available_ram_bytes': ram,
                    'startup_free_vram_bytes': vram,
                    'authorization': 'User approved stepwise protected startup and blade/coupon initial-state diagnostics, 2026-10-31',
                    'mode': mode,
                    'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                      for p in ({Path(__file__), worker_path, WORKER, ROOT/'rl/tomato_preupgrade_guard.py', ROOT/'rl/guard_benchmark.py'} |
                                                ({ROOT/'rl/tomato_coupon_runtime_builder.py', ROOT/'rl/tomato_sdf_native_probe.py'} if mode != 'startup' else set()) |
                                                ({ROOT/'rl/tomato_mesh_double_query.py'} if mode in ('direct_mesh_double', 'mesh_crossings') else set()) |
                                                ({ROOT/'rl/tomato_owned_contact_capture.py', ROOT/'rl/tomato_contact_snapshot.py', ROOT/'rl/tomato_mesh_contact_contract.py', ROOT/'rl/tomato_reaction_metadata.py'} if mode in ('contact_roundtrip', 'analytic_contacts', 'analytic_forces', 'blade_record_roundtrip', 'blade_record_forces', 'particle_scatter') else set()) |
                                                ({ANALYTIC_WORKER, ROOT/'rl/tomato_wrench_contract.py', ROOT/'rl/tomato_contact_precision_audit.py'} if mode == 'analytic_forces' else set()) |
                                                ({BLADE_RECORD_WORKER, FORCE_WORKER, ROOT/'rl/tomato_contact_precision_audit.py', ROOT/'rl/tomato_wrench_contract.py'} if mode in ('blade_record_forces', 'particle_scatter') else set()) |
                                                ({BLADE_FORCE_WORKER, ROOT/'rl/tomato_particle_scatter_reference.py'} if mode == 'particle_scatter' else set()) |
                                                ({ROOT/'rl/tomato_dynamic_proxy_reference.py'} if mode == 'dynamic_proxy' else set()) |
                                                ({ROOT/'rl/tomato_partitioned_reference.py'} if mode == 'contact_feedback' else set()) |
                                                ({FEEDBACK_WORKER, ROOT/'rl/tomato_feedback_sequence_reference.py'} if mode == 'feedback_sequence' else set()) |
                                                ({ROOT/'rl/tomato_two_joint_contact_reference.py', ROOT/'rl/tomato_two_joint_reference.py', ROOT/'rl/tomato_hinge_contact_reference.py', ROOT/'rl/tomato_half_step_reaction.py', ROOT/'rl/tomato_offset_contact_reference.py', ROOT/'rl/tomato_reaction_metadata.py', ROOT/'rl/tomato_wrench_contract.py'} if mode == 'two_joint_contact' else set()) |
                                                ({ROOT/'rl/tomato_two_joint_sequence_reference.py', ROOT/'rl/tomato_half_step_reaction.py', ROOT/'rl/tomato_offset_contact_reference.py', ROOT/'rl/tomato_reaction_metadata.py', ROOT/'rl/tomato_wrench_contract.py'} if mode == 'two_joint_sequence' else set()) |
                                                ({ROOT/'rl/tomato_two_joint_replay_reference.py', ROOT/'rl/tomato_two_joint_sequence_reference.py', ROOT/'rl/tomato_half_step_reaction.py', ROOT/'rl/tomato_offset_contact_reference.py', ROOT/'rl/tomato_reaction_metadata.py', ROOT/'rl/tomato_wrench_contract.py'} if mode == 'two_joint_replay' else set()) |
                                                ({ROOT/'rl/tomato_bent_contact_reference.py', ROOT/'rl/tomato_two_joint_reference.py', ROOT/'rl/tomato_two_joint_sequence_reference.py', ROOT/'rl/tomato_hinge_contact_reference.py', ROOT/'rl/tomato_half_step_reaction.py', ROOT/'rl/tomato_offset_contact_reference.py', ROOT/'rl/tomato_reaction_metadata.py', ROOT/'rl/tomato_wrench_contract.py'} if mode == 'bent_contact' else set()) |
                                                ({ROOT/'rl/tomato_two_joint_sequence_reference.py', ROOT/'rl/tomato_half_step_reaction.py', ROOT/'rl/tomato_offset_contact_reference.py', ROOT/'rl/tomato_reaction_metadata.py', ROOT/'rl/tomato_wrench_contract.py'} if mode == 'bent_sequence' else set()) |
                                                ({ROOT/'rl/tomato_bent_origin_reference.py', ROOT/'rl/tomato_two_joint_sequence_reference.py', ROOT/'rl/tomato_half_step_reaction.py', ROOT/'rl/tomato_offset_contact_reference.py', ROOT/'rl/tomato_reaction_metadata.py', ROOT/'rl/tomato_wrench_contract.py'} if mode == 'bent_origin' else set()) |
                                                ({ROOT/'rl/tomato_bent_rebased_reference.py', ROOT/'rl/tomato_bent_origin_reference.py', ROOT/'rl/tomato_two_joint_sequence_reference.py', ROOT/'rl/tomato_half_step_reaction.py', ROOT/'rl/tomato_offset_contact_reference.py', ROOT/'rl/tomato_reaction_metadata.py', ROOT/'rl/tomato_wrench_contract.py'} if mode == 'bent_rebased' else set()) |
                                                ({ROOT/'rl/tomato_two_joint_reference.py'} if mode == 'two_joint_interface' else set()) |
                                                ({ROOT/'rl/tomato_hinge_reference.py', ROOT/'rl/tomato_wrench_contract.py'} if mode == 'hinge_interface' else set()) |
                                                ({ROOT/'rl/tomato_hinge_sequence_reference.py', ROOT/'rl/tomato_half_step_reaction.py', ROOT/'rl/tomato_offset_contact_reference.py', ROOT/'rl/tomato_reaction_metadata.py', ROOT/'rl/tomato_wrench_contract.py'} if mode == 'hinge_sequence' else set()) |
                                                ({ROOT/'rl/tomato_hinge_replay_reference.py', ROOT/'rl/tomato_hinge_sequence_reference.py', ROOT/'rl/tomato_half_step_reaction.py', ROOT/'rl/tomato_offset_contact_reference.py', ROOT/'rl/tomato_reaction_metadata.py', ROOT/'rl/tomato_wrench_contract.py'} if mode == 'hinge_replay' else set()) |
                                                ({ROOT/'rl/tomato_hinge_reference.py', ROOT/'rl/tomato_hinge_contact_reference.py', ROOT/'rl/tomato_half_step_reaction.py', ROOT/'rl/tomato_offset_contact_reference.py', ROOT/'rl/tomato_reaction_metadata.py', ROOT/'rl/tomato_wrench_contract.py'} if mode == 'hinge_contact' else set()) |
                                                ({ROOT/'rl/tomato_half_step_reaction.py', ROOT/'rl/tomato_anisotropic_sequence_reference.py', ROOT/'rl/tomato_anisotropic_reference.py', ROOT/'rl/tomato_offset_contact_reference.py', ROOT/'rl/tomato_reaction_metadata.py', ROOT/'rl/tomato_wrench_contract.py'} if mode == 'anisotropic_sequence' else set()) |
                                                ({ROOT/'rl/tomato_spin_accuracy_audit.py', ROOT/'rl/tomato_spin_reference.py', ROOT/'rl/tomato_turning_sequence_reference.py', ROOT/'rl/tomato_offset_contact_reference.py', ROOT/'rl/tomato_reaction_metadata.py', ROOT/'rl/tomato_wrench_contract.py'} if mode in SPIN_AUDIT_MODES or mode == 'near_origin_spin' else set()) |
                                                ({ROOT/'rl/tomato_spin_reference.py', ROOT/'rl/tomato_turning_sequence_reference.py', ROOT/'rl/tomato_offset_contact_reference.py', ROOT/'rl/tomato_reaction_metadata.py', ROOT/'rl/tomato_wrench_contract.py'} if mode == 'spin_coast' else set()) |
                                                ({FEEDBACK_WORKER, ROOT/'rl/tomato_anisotropic_reference.py', ROOT/'rl/tomato_offset_contact_reference.py', ROOT/'rl/tomato_reaction_metadata.py', ROOT/'rl/tomato_wrench_contract.py'} if mode == 'anisotropic_contact' else set()) |
                                                ({FEEDBACK_WORKER, ROOT/'rl/tomato_reset_replay_reference.py', ROOT/'rl/tomato_turning_sequence_reference.py', ROOT/'rl/tomato_offset_contact_reference.py', ROOT/'rl/tomato_physx_proxy_reference.py', ROOT/'rl/tomato_reaction_metadata.py', ROOT/'rl/tomato_wrench_contract.py'} if mode == 'reset_replay' else set()) |
                                                ({FEEDBACK_WORKER, ROOT/'rl/tomato_turning_sequence_reference.py', ROOT/'rl/tomato_offset_contact_reference.py', ROOT/'rl/tomato_physx_proxy_reference.py', ROOT/'rl/tomato_reaction_metadata.py', ROOT/'rl/tomato_wrench_contract.py'} if mode == 'turning_sequence' else set()) |
                                                ({FEEDBACK_WORKER, ROOT/'rl/tomato_offset_contact_reference.py', ROOT/'rl/tomato_physx_proxy_reference.py', ROOT/'rl/tomato_reaction_metadata.py', ROOT/'rl/tomato_wrench_contract.py'} if mode == 'offset_contact' else set()) |
                                                ({ROOT/'rl/tomato_physx_proxy_reference.py', ROOT/'rl/tomato_physx_bridge_reference.py', ROOT/'rl/tomato_reaction_metadata.py', ROOT/'rl/tomato_wrench_contract.py'} if mode == 'physx_proxy' else set()))},
                    'training': False, 'checkpoint_resumable': False}
                (output/'launch_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
                log = stack.enter_context((output/'simulation.log').open('w'))
                stream = stack.enter_context((output/'resources.jsonl').open('w', buffering=1))
                started = time.monotonic()
                process = subprocess.Popen(command, cwd=ROOT, env=env, start_new_session=True,
                                           stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT)
                def expire():
                    timed_out.set()
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                timer = threading.Timer(max(0, started+wall_s-time.monotonic()), expire)
                timer.daemon = True
                timer.start()
                (output/'owned_pid.json').write_text(json.dumps({'pid': process.pid}))
                deadline = started + wall_s
                warning_deadline = deadline
                while True:
                    now = time.monotonic()
                    if now >= min(deadline, warning_deadline):
                        reason = 'warning_shutdown_timeout' if warning else 'wall_timeout'
                        break
                    if process.poll() is not None:
                        reason = 'memory_warning_stop' if warning else 'exited'
                        break
                    try:
                        ram, vram = monitor()
                        action = runtime_decision(ram, vram)
                        errors = 0
                        sample = {'wall_s': time.monotonic()-started, 'available_ram_bytes': ram,
                                  'free_vram_bytes': vram, 'action': action}
                        samples.append(sample)
                        stream.write(json.dumps(sample)+'\n')
                    except InterruptedError:
                        raise
                    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError, StopIteration) as exc:
                        errors += 1
                        action = 'stop' if errors >= 3 else 'continue'
                        stream.write(json.dumps({'monitor_error': type(exc).__name__, 'consecutive_errors': errors})+'\n')
                    if action == 'stop':
                        reason = 'monitor_errors' if errors >= 3 else 'hard_memory_stop'
                        break
                    if action == 'checkpoint_and_stop' and not warning:
                        warning = True
                        warning_deadline = min(deadline, time.monotonic()+2)
                        (output/'stop.request').write_text('Startup has no resumable state; close and restart fresh.\n')
                        os.killpg(process.pid, signal.SIGTERM)
                    time.sleep(min(.2, max(0, deadline-time.monotonic())))
        except (OSError, ValueError, RuntimeError, subprocess.SubprocessError, StopIteration, InterruptedError):
            reason = 'interrupted' if process else 'startup_unreadable'
        finally:
            if process is not None:
                stop_group(process, grace_s=2)
                if timer is not None:
                    timer.cancel()
                    timer.join()
                if timed_out.is_set():
                    reason = 'wall_timeout'
                returncode = process.returncode
                remaining = [pid for pid, state in group_members(process.pid) if state != 'Z']
            for sig, handler in previous.items():
                signal.signal(sig, handler)
            try:
                worker = json.loads((output/'worker_result.json').read_text())
            except (OSError, ValueError):
                worker = {}
            result = {'passed': reason == 'exited' and returncode == 0 and
                      worker_passed(worker, mode) and not remaining,
                      'reason': reason, 'launched': process is not None, 'child_exit_code': returncode,
                      'elapsed_wall_s': time.monotonic()-started if started else 0,
                      'remaining_live_group_members': remaining, 'warning_requested': warning,
                      'samples': len(samples), 'monitor_errors': errors,
                      'min_available_ram_bytes': min((s['available_ram_bytes'] for s in samples), default=None),
                      'min_free_vram_bytes': min((s['free_vram_bytes'] for s in samples), default=None),
                      'mode': mode, 'scope': 'Isolated diagnostic only; no robot/cutting/training validation', 'worker': worker}
            (output/'supervisor_result.json').write_text(json.dumps(result, indent=2)+'\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--mode', choices=('startup', 'bent_rebased', 'bent_origin', 'bent_sequence', 'bent_contact', 'two_joint_replay', 'two_joint_sequence', 'two_joint_contact', 'two_joint_interface', 'hinge_replay', 'hinge_sequence', 'hinge_contact', 'hinge_interface', 'anisotropic_sequence', 'near_origin_spin', *SPIN_AUDIT_MODES, 'spin_coast', 'anisotropic_contact', 'reset_replay', 'turning_sequence', 'offset_contact', 'feedback_sequence', 'contact_feedback', 'physx_proxy', 'dynamic_proxy', 'particle_scatter', 'blade_record_forces', 'blade_record_roundtrip', 'native_slab', 'analytic_forces', 'analytic_contacts', 'contact_roundtrip', 'mesh_crossings', 'direct_mesh', 'direct_mesh_centered', 'direct_mesh_double', 'coupon_initial', 'coupon_stationary_sdf', 'coupon_sdf256', 'coupon_sdf512', 'coupon_target256', 'coupon_target512', *SDF_EXPERIMENTS), default='startup')
    args = parser.parse_args()
    result = supervise(args.output, mode=args.mode)
    print(json.dumps(result, indent=2))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
