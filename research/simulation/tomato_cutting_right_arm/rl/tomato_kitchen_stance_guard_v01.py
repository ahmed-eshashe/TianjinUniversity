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
FULL_DAMAGE_WORKER = ROOT / 'rl/tomato_full_damage_worker.py'
FULL_BLADE_WORKER = ROOT / 'rl/tomato_full_blade_worker.py'
EXACT_BLADE_WORKER = ROOT / 'rl/tomato_exact_blade_worker.py'
FULL_COUPLING_WORKER = ROOT / 'rl/tomato_full_coupling_worker.py'
FULL_MODEL_WORKER = ROOT / 'rl/tomato_full_model_worker.py'
VOLUME_COUPON_WORKER = ROOT / 'rl/tomato_volumetric_coupon_worker.py'
MATERIAL_CONTACT_WORKER = ROOT / 'rl/tomato_material_contact_worker.py'
GROUP_MATERIAL_WORKER = ROOT / 'rl/tomato_group_material_worker.py'
MATERIAL_COUPON_WORKER = ROOT / 'rl/tomato_material_coupon_worker.py'
MATERIAL_OPERATOR_WORKER = ROOT / 'rl/tomato_material_operator_worker.py'
BENT_REPLAY_WORKER = ROOT / 'rl/tomato_bent_replay_worker.py'
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


TANGENT_TIME_REFINEMENTS = {'tangent_fine_short':2,'tangent_fine_duration':2,'tangent_finest_short':4,'tangent_finest_duration':4,'tangent_refined8_short':8,'tangent_refined8_duration':8,'tangent_refined16_short':16,'tangent_refined16_duration':16}

GLOBAL_HOLD_MODES = {'global_hold_preview':(1,True),'global_hold_preview_r8':(8,True),'global_hold_preview_r16':(16,True),'global_hold':(1,False),'global_hold_r8':(8,False),'global_hold_r16':(16,False)}

LOADED_SCENE_MODES = {'load_clear_screen':('clear',True),'load_down_screen':('down',True),'load_twist_screen':('lateral_twist',True),'load_reverse_screen':('reversed',True),'load_down':('down',False),'load_twist':('lateral_twist',False),'load_reverse':('reversed',False)}

PREPARED_SCENE_MODES = {'prepared_scene_device_screen':('screen',.01,24,2),'prepared_scene_device_preview':('preview',.25,600,1),'prepared_scene_device_hold':('sustained',10.,24000,2),'prepared_scene_screen':('screen',.01,24,2),'prepared_scene_preview':('preview',.25,600,1),'prepared_scene_hold':('sustained',10.,24000,2)}

GLOBAL_SCREEN_REFINEMENTS = {'fraction_screen1':1,'fraction_screen8':8,'fraction_screen16':16,'fraction_screen32':32,'fraction_screen64':64}

MOUNTED_V06_REFINEMENTS = {f'mounted_target_v06_r{r}':r for r in [4,8,16,32,64,128,256]}

MOUNTED_COM_REFINEMENTS = {f'mounted_target_com_r{r}':r for r in [64,128,256]}

MOVING_CONTACT_MODES = {f'moving_contact_c{r}_{direction}':(r,direction) for r in [1,2,4] for direction in ['down','up']}

def assert_experiment_route(mode, worker_path, command):
    if mode == 'demo_grip':
        expected = ROOT / 'rl/tomato_kitchen_stance_worker_v01.py'
        suffix = ['--interactive'] if os.environ.get('TOMATO_PICKUP_INTERACTIVE') == '1' else []
    elif mode == 'effort_split':
        expected = ROOT / 'rl/tomato_effort_split_worker.py'
        suffix = []
    elif mode == 'motor_effort_capture':
        expected = ROOT / 'rl/tomato_motor_effort_capture_worker.py'
        suffix = []
    elif mode == 'corrected_exchange_clear':
        expected = ROOT / 'rl/tomato_corrected_exchange_clear_worker.py'
        suffix = []
    elif mode == 'corrected_exchange_operator':
        expected = ROOT / 'rl/tomato_corrected_exchange_operator_worker.py'
        suffix = []
    elif mode == 'live_clear_assembly':
        expected = ROOT / 'rl/tomato_live_clear_assembly_worker.py'
        suffix = []
    elif mode == 'near_approach':
        expected = ROOT / 'rl/tomato_near_approach_worker.py'
        suffix = []
    elif mode == 'dry_tracking_v02':
        expected = ROOT / 'rl/tomato_dry_tracking_worker_v02.py'
        suffix = []
    elif mode == 'dry_scene_inspection_v02':
        expected = ROOT / 'rl/tomato_dry_motion_inspection_worker_v02.py'
        suffix = []
    elif mode == 'dry_scene_inspection':
        expected = ROOT / 'rl/tomato_dry_motion_inspection_worker.py'
        suffix = []
    elif mode == 'visible_dry_motion':
        expected = ROOT / 'rl/tomato_visible_dry_motion_worker.py'
        suffix = []
    elif mode == 'robot_body_parameters':
        expected = ROOT / 'rl/tomato_robot_body_parameters_worker.py'
        suffix = []
    elif mode == 'joint_state_interface_pgs':
        expected = ROOT / 'rl/tomato_joint_state_interface_worker_pgs.py'
        suffix = []
    elif mode == 'joint_recenter_pgs':
        expected = ROOT / 'rl/tomato_joint_recenter_worker_pgs.py'
        suffix = []
    elif mode == 'robot_kinematic_binding':
        expected = ROOT / 'rl/tomato_robot_kinematic_binding_worker.py'
        suffix = []
    elif mode == 'joint_state_interface':
        expected = ROOT / 'rl/tomato_joint_state_interface_worker.py'
        suffix = []
    elif mode == 'joint_recenter_v03':
        expected = ROOT / 'rl/tomato_joint_recenter_worker_v03.py'
        suffix = []
    elif mode == 'joint_recenter_v02':
        expected = ROOT / 'rl/tomato_joint_recenter_worker_v02.py'
        suffix = []
    elif mode == 'joint_recenter':
        expected = ROOT / 'rl/tomato_joint_recenter_worker.py'
        suffix = []
    elif mode in MOVING_CONTACT_MODES:
        refinement,direction = MOVING_CONTACT_MODES[mode]
        expected = ROOT / 'rl/tomato_moving_contact_worker.py'
        suffix = ['--coupling-refinement', str(refinement), '--direction', direction]
    elif mode == 'robot_wrench_trace':
        expected = ROOT / 'rl/tomato_robot_wrench_calibration_worker.py'
        suffix = []
    elif mode == 'robot_wrench_com_trace':
        expected = ROOT / 'rl/tomato_robot_wrench_calibration_com_worker.py'
        suffix = []
    elif mode in MOUNTED_COM_REFINEMENTS:
        expected = ROOT / 'rl/tomato_mounted_target_com_worker.py'
        suffix = ['--refinement', str(MOUNTED_COM_REFINEMENTS[mode])]
    elif mode in MOUNTED_V06_REFINEMENTS:
        expected = ROOT / ('rl/tomato_mounted_target_screen_worker_v06_extended.py' if MOUNTED_V06_REFINEMENTS[mode]>=128 else 'rl/tomato_mounted_target_screen_worker_v06.py')
        suffix = ['--refinement', str(MOUNTED_V06_REFINEMENTS[mode])]
    else:
        return
    if Path(worker_path) != expected or command[:3] != [str(PYTHON), str(expected), '--output'] or command[4:] != suffix:
        raise ValueError('Experiment mode/worker/argument route mismatch before launch: '+mode)

def worker_passed(worker, mode):
    if worker.get('shutdown_requested') is not True:
        return False
    if mode == 'demo_grip':
        return worker.get('demo_grip_passed') is True and worker.get('controlled_steps') == 4448 and worker.get('training') is False
    if mode == 'effort_split':
        return (worker.get('diagnostic_passed') is True and worker.get('effort_split_passed') is True
                and worker.get('controlled_steps') == 75 and worker.get('executed_steps') == 72
                and worker.get('setup_physx_steps') == 3 and worker.get('cases_completed') == 3
                and worker.get('deformable_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('training') is False and worker.get('motor_work_qualified') is False)
    if mode == 'motor_effort_capture':
        return (worker.get('diagnostic_passed') is True and worker.get('motor_effort_capture_passed') is True
                and worker.get('controlled_steps') == 4448 and worker.get('executed_steps') == 120
                and worker.get('setup_physx_steps') == 3 and worker.get('deformable_steps') == 0
                and worker.get('newton_steps') == 0 and worker.get('training') is False
                and worker.get('motor_work_qualified') is False)
    if mode == 'corrected_exchange_clear':
        return (worker.get('diagnostic_passed') is True and worker.get('corrected_exchange_clear_passed') is True
                and worker.get('controlled_steps') == 27 and worker.get('deformable_steps') == 240
                and worker.get('matched_physx_steps') == 24 and worker.get('setup_physx_steps') == 3
                and worker.get('exchange_blocks') == 24 and worker.get('newton_steps') == 0
                and worker.get('training') is False)
    if mode == 'corrected_exchange_operator':
        return (worker.get('diagnostic_passed') is True and worker.get('corrected_exchange_operator_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('deformable_steps') == 0
                and worker.get('newton_steps') == 0 and worker.get('cases_completed') == 3
                and worker.get('queued_requests') == 2 and worker.get('training') is False)
    if mode == 'live_clear_assembly':
        return (worker.get('diagnostic_passed') is True and worker.get('live_clear_assembly_passed') is True
                and worker.get('controlled_steps') == 27 and worker.get('deformable_steps') == 240
                and worker.get('matched_physx_steps') == 24 and worker.get('setup_physx_steps') == 3
                and worker.get('newton_steps') == 0 and worker.get('training') is False)
    if mode == 'near_approach':
        return (worker.get('diagnostic_passed') is True and worker.get('near_approach_passed') is True
                and worker.get('controlled_steps') == 4091 and worker.get('newton_steps') == 0
                and worker.get('episodes_completed') == 1 and worker.get('training') is False)
    if mode == 'dry_tracking_v02':
        return (worker.get('diagnostic_passed') is True and worker.get('dry_tracking_corrected_passed') is True
                and worker.get('controlled_steps') == 4091 and worker.get('newton_steps') == 0
                and worker.get('episodes_completed') == 1 and worker.get('training') is False)
    if mode in ('dry_scene_inspection','dry_scene_inspection_v02'):
        return (worker.get('diagnostic_passed') is True and worker.get('dry_scene_inspection_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('training') is False)
    if mode == 'visible_dry_motion':
        return (worker.get('diagnostic_passed') is True and worker.get('visible_dry_motion_passed') is True
                and worker.get('controlled_steps') == 4091 and worker.get('newton_steps') == 0
                and worker.get('episodes_completed') == 1 and worker.get('training') is False)
    if mode == 'robot_body_parameters':
        return (worker.get('diagnostic_passed') is True and worker.get('robot_body_parameters_captured') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == 0 and worker.get('cases_completed') == 46)
    if mode == 'joint_state_interface_pgs':
        return (worker.get('diagnostic_passed') is True and worker.get('joint_state_interface_pgs_component_passed') is True
                and worker.get('controlled_steps') == 192 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == 0 and worker.get('cases_completed') == 6)
    if mode == 'joint_recenter_pgs':
        return (worker.get('diagnostic_passed') is True and worker.get('joint_recenter_pgs_component_passed') is True
                and worker.get('controlled_steps') == 264 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == 0 and worker.get('cases_completed') == 21)
    if mode == 'robot_kinematic_binding':
        return (worker.get('diagnostic_passed') is True and worker.get('robot_kinematic_binding_captured') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == 0 and worker.get('cases_completed') == 2)
    if mode == 'joint_state_interface':
        return (worker.get('diagnostic_passed') is True and worker.get('joint_state_interface_component_passed') is True
                and worker.get('controlled_steps') == 192 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == 0 and worker.get('cases_completed') == 6)
    if mode == 'joint_recenter_v03':
        return (worker.get('diagnostic_passed') is True and worker.get('joint_recenter_v03_component_passed') is True
                and worker.get('controlled_steps') == 264 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == 0 and worker.get('cases_completed') == 21)
    if mode == 'joint_recenter_v02':
        return (worker.get('diagnostic_passed') is True and worker.get('joint_recenter_v02_component_passed') is True
                and worker.get('controlled_steps') == 264 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == 0 and worker.get('cases_completed') == 21)
    if mode == 'joint_recenter':
        return (worker.get('diagnostic_passed') is True and worker.get('joint_recenter_component_passed') is True
                and worker.get('controlled_steps') == 264 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == 0 and worker.get('cases_completed') == 21)
    if mode in MOVING_CONTACT_MODES:
        refinement,direction = MOVING_CONTACT_MODES[mode]
        return (worker.get('diagnostic_passed') is True and worker.get('moving_contact_component_passed') is True
                and worker.get('moving_contact_work_qualified') is False
                and worker.get('coupling_refinement') == refinement and worker.get('direction') == direction
                and worker.get('controlled_steps') == 32*refinement and worker.get('matched_physx_steps') == 32*refinement
                and worker.get('deformable_steps') == 4096 and worker.get('newton_steps') == 0
                and worker.get('cases_completed') == 4)
    if mode in MOUNTED_COM_REFINEMENTS:
        refinement=MOUNTED_COM_REFINEMENTS[mode]
        return (worker.get('diagnostic_passed') is True and worker.get('mounted_target_com_component_passed') is True
                and worker.get('mounted_target_work_qualified') is False and worker.get('refinement') == refinement
                and worker.get('controlled_steps') == 32*refinement and worker.get('matched_physx_steps') == 32*refinement
                and worker.get('deformable_steps') == 32*refinement and worker.get('newton_steps') == 0
                and worker.get('cases_completed') == 4)
    if mode == 'robot_wrench_com_trace':
        return (worker.get('diagnostic_passed') is True and worker.get('robot_wrench_com_trace_passed') is True
                and worker.get('controlled_steps') == 136 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == 0 and worker.get('cases_completed') == 17)
    if mode == 'robot_wrench_trace':
        return (worker.get('diagnostic_passed') is True and worker.get('robot_wrench_trace_passed') is True
                and worker.get('controlled_steps') == 136 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == 0 and worker.get('cases_completed') == 17)
    if mode in MOUNTED_V06_REFINEMENTS:
        refinement=MOUNTED_V06_REFINEMENTS[mode]
        return (worker.get('diagnostic_passed') is True and worker.get('mounted_target_feedback_v06_component_passed') is True
                and worker.get('mounted_target_work_qualified') is False and worker.get('refinement') == refinement
                and worker.get('controlled_steps') == 32*refinement and worker.get('matched_physx_steps') == 32*refinement
                and worker.get('deformable_steps') == 32*refinement and worker.get('newton_steps') == 0
                and worker.get('cases_completed') == 4)
    if mode == 'sustained_support':
        return (worker.get('diagnostic_passed') is True and worker.get('sustained_support_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 48002
                and worker.get('episodes_completed') == 2)
    if mode == 'objective_operator':
        return (worker.get('diagnostic_passed') is True and worker.get('objective_operator_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('cases_completed') == 6)
    if mode == 'checked_volume':
        return (worker.get('diagnostic_passed') is True and worker.get('checked_volume_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('cases_completed') == 4)
    if mode == 'objective_force':
        return (worker.get('diagnostic_passed') is True and worker.get('objective_force_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('cases_completed') == 6 and worker.get('hessian_columns') == 54)
    if mode == 'objective_model':
        return (worker.get('diagnostic_passed') is True and worker.get('objective_model_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 4
                and worker.get('episodes_completed') == 2)
    if mode == 'external_load_operator':
        return (worker.get('diagnostic_passed') is True and worker.get('external_load_operator_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == 0 and worker.get('physical_time_advanced_s') == 0.
                and worker.get('cases_completed') == 4)
    if mode == 'robot_energy_operator_v03':
        return (worker.get('diagnostic_passed') is True and worker.get('robot_energy_operator_v03_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == 0 and worker.get('physical_time_advanced_s') == 0.
                and worker.get('cases_completed') == 2)
    if mode in ('mounted_target_screen_v05_fine','mounted_target_screen_v05_finest'):
        refinement=4 if mode.endswith('finest') else 2
        return (worker.get('diagnostic_passed') is True and worker.get('mounted_target_feedback_v05_component_passed') is True
                and worker.get('mounted_target_work_qualified') is False and worker.get('refinement') == refinement
                and worker.get('controlled_steps') == 32*refinement and worker.get('matched_physx_steps') == 32*refinement
                and worker.get('deformable_steps') == 32*refinement and worker.get('newton_steps') == 0
                and worker.get('cases_completed') == 4)
    if mode == 'mounted_target_screen_v05':
        return (worker.get('diagnostic_passed') is True and worker.get('mounted_target_feedback_v05_component_passed') is True
                and worker.get('mounted_target_work_qualified') is False and worker.get('refinement') == 1
                and worker.get('controlled_steps') == 32 and worker.get('matched_physx_steps') == 32
                and worker.get('deformable_steps') == 32 and worker.get('newton_steps') == 0
                and worker.get('cases_completed') == 4)
    if mode == 'mounted_target_screen_v04':
        return (worker.get('diagnostic_passed') is True and worker.get('mounted_target_feedback_v04_component_passed') is True
                and worker.get('mounted_target_work_qualified') is False and worker.get('refinement') == 1
                and worker.get('controlled_steps') == 32 and worker.get('matched_physx_steps') == 32
                and worker.get('deformable_steps') == 32 and worker.get('newton_steps') == 0
                and worker.get('cases_completed') == 4)
    if mode == 'mounted_target_screen_v03':
        return (worker.get('diagnostic_passed') is True and worker.get('mounted_target_feedback_v03_component_passed') is True
                and worker.get('mounted_target_work_qualified') is False and worker.get('refinement') == 1
                and worker.get('controlled_steps') == 32 and worker.get('matched_physx_steps') == 32
                and worker.get('deformable_steps') == 32 and worker.get('newton_steps') == 0
                and worker.get('cases_completed') == 4)
    if mode == 'robot_energy_operator_v02':
        return (worker.get('diagnostic_passed') is True and worker.get('robot_energy_operator_v02_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == 0 and worker.get('physical_time_advanced_s') == 0.
                and worker.get('cases_completed') == 2)
    if mode == 'mounted_target_screen_v02':
        return (worker.get('diagnostic_passed') is True and worker.get('mounted_target_feedback_v02_component_passed') is True
                and worker.get('mounted_target_work_qualified') is False and worker.get('refinement') == 1
                and worker.get('controlled_steps') == 32 and worker.get('matched_physx_steps') == 32
                and worker.get('deformable_steps') == 32 and worker.get('newton_steps') == 0
                and worker.get('cases_completed') == 4)
    if mode == 'robot_energy_operator':
        return (worker.get('diagnostic_passed') is True and worker.get('robot_energy_operator_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == 0 and worker.get('physical_time_advanced_s') == 0.
                and worker.get('cases_completed') == 2)
    if mode == 'mounted_target_screen':
        return (worker.get('diagnostic_passed') is True and worker.get('mounted_target_feedback_component_passed') is True
                and worker.get('mounted_target_work_qualified') is False and worker.get('refinement') == 1
                and worker.get('controlled_steps') == 32 and worker.get('matched_physx_steps') == 32
                and worker.get('deformable_steps') == 32 and worker.get('newton_steps') == 0
                and worker.get('cases_completed') == 4)
    if mode == 'cad_pressure_operator':
        return (worker.get('diagnostic_passed') is True and worker.get('cad_pressure_operator_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == 0 and worker.get('physical_time_advanced_s') == 0.
                and worker.get('cases_completed') == 6)
    if mode == 'global_pressure_operator':
        return (worker.get('diagnostic_passed') is True and worker.get('global_pressure_operator_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == 0 and worker.get('physical_time_advanced_s') == 0.
                and worker.get('cases_completed') == 3)
    if mode == 'cached_static_operator':
        return (worker.get('diagnostic_passed') is True and worker.get('cached_static_operator_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == 0 and worker.get('physical_time_advanced_s') == 0.
                and worker.get('cases_completed') == 4)
    if mode == 'static_preparation_cached':
        return (worker.get('diagnostic_passed') is True and worker.get('cached_static_preparation_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == 0 and worker.get('physical_time_advanced_s') == 0.
                and worker.get('load_stages_completed') == 6 and worker.get('residual_evaluations',0) > 0)
    if mode == 'direct_static_operator':
        return (worker.get('diagnostic_passed') is True and worker.get('direct_static_operator_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == 0 and worker.get('physical_time_advanced_s') == 0.
                and worker.get('cases_completed') == 3)
    if mode == 'static_preparation_direct':
        return (worker.get('diagnostic_passed') is True and worker.get('direct_static_preparation_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == 0 and worker.get('physical_time_advanced_s') == 0.
                and worker.get('load_stages_completed') == 6 and worker.get('residual_evaluations',0) > 0)
    if mode == 'loaded_force':
        return (worker.get('diagnostic_passed') is True and worker.get('loaded_force_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == 0 and worker.get('physical_time_advanced_s') == 0.
                and worker.get('cases_completed') == 2)
    if mode == 'static_preparation_safeguarded':
        return (worker.get('diagnostic_passed') is True and worker.get('safeguarded_static_preparation_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == 0 and worker.get('physical_time_advanced_s') == 0.
                and worker.get('load_stages_completed') == 6 and worker.get('residual_evaluations',0) > 0)
    if mode == 'static_preparation_iterative':
        return (worker.get('diagnostic_passed') is True and worker.get('iterative_static_preparation_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == 0 and worker.get('physical_time_advanced_s') == 0.
                and worker.get('load_stages_completed') == 6 and worker.get('residual_evaluations',0) > 0)
    if mode == 'static_preparation_regularized':
        return (worker.get('diagnostic_passed') is True and worker.get('regularized_static_preparation_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == 0 and worker.get('physical_time_advanced_s') == 0.
                and worker.get('load_stages_completed') == 6 and worker.get('residual_evaluations',0) > 0)
    if mode == 'static_operator':
        return (worker.get('diagnostic_passed') is True and worker.get('static_operator_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == 0 and worker.get('physical_time_advanced_s') == 0.
                and worker.get('cases_completed') == 3)
    if mode == 'static_preparation':
        return (worker.get('diagnostic_passed') is True and worker.get('static_preparation_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == 0 and worker.get('physical_time_advanced_s') == 0.
                and worker.get('load_stages_completed') == 6 and worker.get('residual_evaluations',0) > 0)
    if mode == 'failed_safe_global_operator':
        return (worker.get('diagnostic_passed') is True and worker.get('failed_safe_global_operator_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0 and worker.get('cases_completed') == 3)
    if mode == 'failed_safe_integrator':
        return (worker.get('diagnostic_passed') is True and worker.get('failed_safe_integrator_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == 16 and worker.get('cases_completed') == 3)
    if mode in LOADED_SCENE_MODES:
        load_case, screen = LOADED_SCENE_MODES[mode]
        steps = 48 if screen else 5280
        return (worker.get('diagnostic_passed') is True and worker.get('loaded_scene_screen_passed' if screen else 'loaded_scene_challenge_passed') is True
                and worker.get('load_case') == load_case and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == steps and worker.get('matched_physx_steps') == steps
                and worker.get('controlled_steps') == steps+3 and worker.get('setup_physx_steps') == 3
                and worker.get('refinement') == 1 and worker.get('duration_s') == (.01 if screen else 1.1)
                and worker.get('episodes_completed') == 2)
    if mode in PREPARED_SCENE_MODES:
        phase, duration, per_episode, episodes = PREPARED_SCENE_MODES[mode]
        steps = per_episode*episodes
        return (worker.get('diagnostic_passed') is True and worker.get(('prepared_scene_device_' if '_device_' in mode else 'prepared_scene_')+phase+'_passed') is True
                and worker.get('newton_steps') == 0 and worker.get('deformable_steps') == steps
                and worker.get('controlled_steps') == steps+3 and worker.get('matched_physx_steps') == steps
                and worker.get('setup_physx_steps') == 3 and worker.get('refinement') == 1
                and worker.get('duration_s') == duration and worker.get('episodes_completed') == episodes)
    if mode in GLOBAL_SCREEN_REFINEMENTS:
        refinement = GLOBAL_SCREEN_REFINEMENTS[mode]
        return (worker.get('diagnostic_passed') is True and worker.get('screen_dynamics_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == 48*refinement and worker.get('refinement') == refinement
                and worker.get('duration_s') == .01 and worker.get('episodes_completed') == 2)
    if mode in GLOBAL_HOLD_MODES:
        refinement, preview = GLOBAL_HOLD_MODES[mode]
        flag = 'hold_preview_passed' if preview else 'sustained_global_passed'
        return (worker.get('diagnostic_passed') is True and worker.get(flag) is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == (600 if preview else 48000)*refinement
                and worker.get('refinement') == refinement and worker.get('duration_s') == (.25 if preview else 10.)
                and worker.get('episodes_completed') == (1 if preview else 2))
    if mode in TANGENT_TIME_REFINEMENTS:
        refinement = TANGENT_TIME_REFINEMENTS[mode]
        duration = .1 if mode.endswith('duration') else .01
        steps = (480 if duration == .1 else 48)*refinement
        return (worker.get('diagnostic_passed') is True and worker.get('tangent_timestep_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == steps and worker.get('duration_s') == duration
                and worker.get('refinement') == refinement and worker.get('episodes_completed') == 2)
    if mode in ('timestep_fine_short','timestep_fine_duration','timestep_finest_short','timestep_finest_duration'):
        refinement = 4 if 'finest' in mode else 2
        duration = .1 if mode.endswith('duration') else .01
        steps = (480 if duration == .1 else 48)*refinement
        return (worker.get('diagnostic_passed') is True and worker.get('timestep_preflight_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == steps and worker.get('duration_s') == duration
                and worker.get('refinement') == refinement and worker.get('episodes_completed') == 2)
    if mode == 'fraction_operator':
        return (worker.get('diagnostic_passed') is True and worker.get('fraction_operator_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('cases_completed') == 5)
    if mode == 'fraction_integrator':
        return (worker.get('diagnostic_passed') is True and worker.get('fraction_integrator_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == 16 and worker.get('cases_completed') == 3)
    if mode in ('fraction_short','fraction_duration'):
        steps, duration = (48,.01) if mode == 'fraction_short' else (480,.1)
        return (worker.get('diagnostic_passed') is True and worker.get('fraction_preflight_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == steps and worker.get('duration_s') == duration
                and worker.get('episodes_completed') == 2)
    if mode == 'tangent_operator':
        return (worker.get('diagnostic_passed') is True and worker.get('tangent_operator_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('cases_completed') == 3)
    if mode == 'tangent_integrator':
        return (worker.get('diagnostic_passed') is True and worker.get('tangent_integrator_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == 16 and worker.get('cases_completed') == 3)
    if mode in ('tangent_short','tangent_duration'):
        steps, duration = (48,.01) if mode == 'tangent_short' else (480,.1)
        return (worker.get('diagnostic_passed') is True and worker.get('tangent_preflight_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == steps and worker.get('duration_s') == duration
                and worker.get('episodes_completed') == 2)
    if mode == 'tight_linear':
        return (worker.get('diagnostic_passed') is True and worker.get('tight_linear_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('cases_completed') == 3)
    if mode == 'tight_integrator':
        return (worker.get('diagnostic_passed') is True and worker.get('tight_integrator_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == 16 and worker.get('cases_completed') == 3)
    if mode in ('tight_short','tight_duration'):
        steps, duration = (48,.01) if mode == 'tight_short' else (480,.1)
        return (worker.get('diagnostic_passed') is True and worker.get('tight_preflight_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == steps and worker.get('duration_s') == duration
                and worker.get('episodes_completed') == 2)
    if mode in ('block_preconditioner','failed_frame'):
        flag = 'block_preconditioner_passed' if mode == 'block_preconditioner' else 'failed_frame_passed'
        return (worker.get('diagnostic_passed') is True and worker.get(flag) is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('cases_completed') == (3 if mode == 'block_preconditioner' else 6))
    if mode == 'block_integrator':
        return (worker.get('diagnostic_passed') is True and worker.get('block_integrator_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == 16 and worker.get('cases_completed') == 3)
    if mode in ('block_short','block_duration'):
        steps, duration = (48,.01) if mode == 'block_short' else (480,.1)
        return (worker.get('diagnostic_passed') is True and worker.get('block_preflight_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == steps and worker.get('duration_s') == duration
                and worker.get('episodes_completed') == 2)
    if mode == 'lbfgs_operator':
        return (worker.get('diagnostic_passed') is True and worker.get('lbfgs_operator_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('cases_completed') == 3)
    if mode == 'lbfgs_integrator':
        return (worker.get('diagnostic_passed') is True and worker.get('lbfgs_integrator_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == 16 and worker.get('cases_completed') == 3)
    if mode in ('lbfgs_short','lbfgs_duration'):
        steps, duration = (48,.01) if mode == 'lbfgs_short' else (480,.1)
        return (worker.get('diagnostic_passed') is True and worker.get('lbfgs_preflight_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == steps and worker.get('duration_s') == duration
                and worker.get('episodes_completed') == 2)
    if mode in ('local_short','local_duration'):
        steps, duration = (48,.01) if mode == 'local_short' else (480,.1)
        return (worker.get('diagnostic_passed') is True and worker.get('local_preflight_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == steps and worker.get('duration_s') == duration
                and worker.get('episodes_completed') == 2)
    if mode == 'local_frame':
        return (worker.get('diagnostic_passed') is True and worker.get('local_frame_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('cases_completed') == 3)
    if mode in ('global_short','global_duration'):
        steps, duration = (48,.01) if mode == 'global_short' else (480,.1)
        return (worker.get('diagnostic_passed') is True and worker.get('global_preflight_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == steps and worker.get('duration_s') == duration
                and worker.get('episodes_completed') == 2)
    if mode == 'global_integrator':
        return (worker.get('diagnostic_passed') is True and worker.get('global_integrator_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('deformable_steps') == 16 and worker.get('cases_completed') == 3)
    if mode == 'global_energy':
        return (worker.get('diagnostic_passed') is True and worker.get('global_energy_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('cases_completed') == 3)
    if mode == 'global_gn_operator':
        return (worker.get('diagnostic_passed') is True and worker.get('global_gn_operator_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('cases_completed') == 3)
    if mode == 'local_ledger':
        return (worker.get('diagnostic_passed') is True and worker.get('local_ledger_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('cases_completed') == 3)
    if mode == 'rebased_local_preflight':
        return (worker.get('diagnostic_passed') is True and worker.get('rebased_local_preflight_passed') is True
                and worker.get('storage') == 'rebased' and worker.get('controlled_steps') == 0
                and worker.get('newton_steps') == 962 and worker.get('settings_completed') == 1)
    if mode == 'rebased_operator':
        return (worker.get('diagnostic_passed') is True and worker.get('rebased_operator_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('cases_completed') == 6)
    if mode == 'rebased_preflight':
        return (worker.get('diagnostic_passed') is True and worker.get('rebased_preflight_passed') is True
                and worker.get('storage') == 'rebased' and worker.get('controlled_steps') == 0
                and worker.get('newton_steps') == 962 and worker.get('settings_completed') == 1)
    if mode == 'physical_pressure':
        return (worker.get('diagnostic_passed') is True and worker.get('physical_pressure_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('cases_completed') == 3)
    if mode == 'relative_extended':
        return (worker.get('diagnostic_passed') is True and worker.get('sensitivity_complete') is True
                and worker.get('storage') == 'rest-relative' and worker.get('study') == 'extended'
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 9224
                and worker.get('settings_completed') == 4)
    if mode in ('relative_fast_equivalence','relative_preflight'):
        flag, steps = ('fast_equivalence_passed',98) if mode == 'relative_fast_equivalence' else ('relative_preflight_passed',962)
        return (worker.get('diagnostic_passed') is True and worker.get(flag) is True
                and worker.get('storage') == 'rest-relative' and worker.get('controlled_steps') == 0
                and worker.get('newton_steps') == steps and worker.get('settings_completed') == 1)
    if mode == 'cohesive_color':
        return (worker.get('diagnostic_passed') is True and worker.get('cohesive_color_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('cases_completed') == 11)
    if mode == 'relative_finest':
        return (worker.get('diagnostic_passed') is True and worker.get('sensitivity_complete') is True
                and worker.get('storage') == 'rest-relative' and worker.get('study') == 'finest'
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 1540
                and worker.get('settings_completed') == 2)
    if mode == 'relative_fine':
        return (worker.get('diagnostic_passed') is True and worker.get('sensitivity_complete') is True
                and worker.get('storage') == 'rest-relative' and worker.get('controlled_steps') == 0
                and worker.get('newton_steps') == 1160 and worker.get('settings_completed') == 4)
    if mode == 'relative_sensitivity':
        return (worker.get('diagnostic_passed') is True and worker.get('sensitivity_complete') is True
                and worker.get('storage') == 'rest-relative' and worker.get('controlled_steps') == 0
                and worker.get('newton_steps') == 684 and worker.get('settings_completed') == 6)
    if mode == 'relative_operator':
        return (worker.get('diagnostic_passed') is True and worker.get('relative_operator_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('cases_completed') == 6)
    if mode == 'position_precision':
        return (worker.get('diagnostic_passed') is True and worker.get('position_precision_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 624
                and worker.get('cases_completed') == 6)
    if mode == 'objective_gn_extended':
        return (worker.get('diagnostic_passed') is True and worker.get('objective_gn_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('cases_completed') == 8)
    if mode == 'integration_sensitivity_fine':
        return (worker.get('diagnostic_passed') is True and worker.get('sensitivity_complete') is True and worker.get('storage') is None
                and worker.get('study') == 'fine' and worker.get('controlled_steps') == 0
                and worker.get('newton_steps') == 1740 and worker.get('settings_completed') == 6)
    if mode == 'integration_sensitivity':
        return (worker.get('diagnostic_passed') is True and worker.get('sensitivity_complete') is True and worker.get('storage') is None
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 684
                and worker.get('settings_completed') == 6)
    if mode == 'material_history':
        return (worker.get('diagnostic_passed') is True and worker.get('material_history_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('cases_completed') == 6)
    if mode == 'contact_geometry':
        return (worker.get('diagnostic_passed') is True and worker.get('contact_geometry_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('cases_completed') == 4)
    if mode == 'objective_gn':
        return (worker.get('diagnostic_passed') is True and worker.get('objective_gn_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('cases_completed') == 6)
    if mode == 'contact_preflight':
        return (worker.get('diagnostic_passed') is True and worker.get('contact_dynamics_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 482
                and worker.get('episodes_completed') == 2 and worker.get('steps_per_episode') == 240
                and worker.get('objective_material') is True)
    if mode == 'contact_dynamics':
        return (worker.get('diagnostic_passed') is True and worker.get('contact_dynamics_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 48
                and worker.get('episodes_completed') == 2 and worker.get('steps_per_episode') == 24
                and worker.get('objective_material') is True)
    if mode == 'embedding_contact':
        return (worker.get('diagnostic_passed') is True and worker.get('embedding_contact_passed') is True
                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 0
                and worker.get('cases_completed') == 18)
    if mode == 'mounted_contact':
        return (worker.get('diagnostic_passed') is True and worker.get('mounted_contact_passed') is True
                and worker.get('controlled_steps') == 24 and worker.get('newton_steps') == 24
                and worker.get('cases_completed') == 6)
    if mode == 'fixed_mount':
        return (worker.get('diagnostic_passed') is True and worker.get('fixed_mount_passed') is True
                and worker.get('controlled_steps') == 3851 and worker.get('newton_steps') == 30
                and worker.get('episodes_completed') == 2)
    if mode == 'robot_scene_frames':
        return (worker.get('diagnostic_passed') is True and worker.get('robot_scene_frames_passed') is True
                and worker.get('controlled_steps') == 2 and worker.get('newton_steps') == 6)
    if mode == 'startup':
        return worker.get('startup_step_passed') is True and worker.get('steps') == 1
    if mode == 'full_damage':
        return (worker.get('diagnostic_passed') is True and worker.get('full_damage_passed') is True
                and worker.get('newton_steps') == 8 and worker.get('controlled_steps') == 8
                and worker.get('full_damage_intervals') == 8)
    if mode == 'full_blade':
        return (worker.get('diagnostic_passed') is True and worker.get('full_blade_passed') is True
                and worker.get('newton_steps') == 17 and worker.get('controlled_steps') == 17
                and worker.get('cuda_state_echoes') == 20 and worker.get('full_blade_intervals') == 16)
    if mode == 'exact_blade_geometry':
        return (worker.get('diagnostic_passed') is True and worker.get('exact_blade_geometry_passed') is True
                and worker.get('newton_steps') == 0 and worker.get('controlled_steps') == 0
                and worker.get('exact_blade_cases') == 6 and worker.get('blade_field_queries') == 128)
    if mode == 'exact_blade':
        return (worker.get('diagnostic_passed') is True and worker.get('exact_blade_passed') is True
                and worker.get('newton_steps') == 6 and worker.get('controlled_steps') == 6
                and worker.get('exact_blade_cases') == 6 and worker.get('blade_field_queries') == 128)
    if mode == 'full_coupling':
        return (worker.get('diagnostic_passed') is True and worker.get('full_coupling_passed') is True
                and worker.get('newton_steps') == 8 and worker.get('controlled_steps') == 8
                and worker.get('cuda_state_echoes') == 9)
    if mode == 'full_model':
        return (worker.get('diagnostic_passed') is True and worker.get('full_model_passed') is True
                and worker.get('full_model_cases') == 4 and worker.get('newton_steps') == 9
                and worker.get('controlled_steps') == 9 and worker.get('material_probes') == 4)
    if mode == 'volume_coupon':
        return (worker.get('diagnostic_passed') is True and worker.get('volume_coupon_passed') is True
                and worker.get('volume_coupon_cases') == 4 and worker.get('newton_steps') == 3
                and worker.get('controlled_steps') == 3 and worker.get('opening_probes') == 401)
    if mode == 'material_contact':
        return (worker.get('diagnostic_passed') is True and worker.get('material_contact_passed') is True
                and worker.get('material_contact_cases') == 2 and worker.get('newton_steps') == 2
                and worker.get('controlled_steps') == 2)
    if mode == 'group_material':
        return (worker.get('diagnostic_passed') is True and worker.get('group_checks_passed') is True
                and worker.get('group_cases_completed') == 6 and worker.get('newton_steps') == 1
                and worker.get('controlled_steps') == 1 and worker.get('group_probes') == 4)
    if mode == 'material_coupon':
        return (worker.get('diagnostic_passed') is True and worker.get('coupon_checks_passed') is True
                and worker.get('coupon_cases_completed') == 5 and worker.get('newton_steps') == 4
                and worker.get('controlled_steps') == 4 and worker.get('opening_probes') == 802)
    if mode == 'material_operator':
        return (worker.get('diagnostic_passed') is True and worker.get('material_checks_passed') is True
                and worker.get('material_cases_completed') == 6 and worker.get('newton_steps') == 6
                and worker.get('controlled_steps') == 6 and worker.get('constitutive_probes') == 7)
    if mode == 'bent_replay':
        return (worker.get('diagnostic_passed') is True and worker.get('bent_replay_checks_passed') is True
                and worker.get('bent_replay_cases_completed') == 2 and worker.get('controlled_steps') == 66
                and worker.get('newton_steps') == 132 and worker.get('cuda_state_echoes') == 138
                and worker.get('reset_cycles_completed') == 2 and worker.get('dirty_wrench_resets') == 4
                and worker.get('replay_comparisons') == 4)
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


def supervise(output, *, monitor=hardware_sample, wall_s=None, mode='startup', _fixture_command=None):
    """Only CLI route is the fixed startup worker; fixture injection is for stdlib tests."""
    maximum_wall_s = 600 if mode == 'demo_grip' else 900 if mode in ('corrected_exchange_clear','corrected_exchange_operator','live_clear_assembly','near_approach','dry_tracking_v02','dry_scene_inspection_v02','dry_scene_inspection','visible_dry_motion','joint_recenter','joint_recenter_v02','joint_recenter_v03','joint_state_interface','robot_kinematic_binding','joint_recenter_pgs','joint_state_interface_pgs','robot_body_parameters') else 3600 if mode in MOVING_CONTACT_MODES else 3600 if mode in MOUNTED_COM_REFINEMENTS else 900 if mode == 'robot_wrench_com_trace' else 3600 if mode in MOUNTED_V06_REFINEMENTS else (900 if LOADED_SCENE_MODES[mode][1] else 10800) if mode in LOADED_SCENE_MODES else (43200 if PREPARED_SCENE_MODES[mode][0]=='sustained' else 3600 if PREPARED_SCENE_MODES[mode][0]=='preview' else 900) if mode in PREPARED_SCENE_MODES else 7200 if mode in ('static_preparation_direct','static_preparation_cached') else 900 if mode in ('static_operator','loaded_force','direct_static_operator','cached_static_operator','global_pressure_operator','external_load_operator','cad_pressure_operator','robot_energy_operator','mounted_target_screen','robot_energy_operator_v02','mounted_target_screen_v02','robot_energy_operator_v03','mounted_target_screen_v03','mounted_target_screen_v04','mounted_target_screen_v05','mounted_target_screen_v05_fine','mounted_target_screen_v05_finest','robot_wrench_trace') else 1800 if mode in ('static_preparation','static_preparation_regularized','static_preparation_iterative','static_preparation_safeguarded') else 900 if mode == 'failed_safe_global_operator' else 1800 if mode == 'failed_safe_integrator' else 1800 if mode in GLOBAL_SCREEN_REFINEMENTS else (3600 if GLOBAL_HOLD_MODES[mode][1] else 43200) if mode in GLOBAL_HOLD_MODES else 3600 if mode in ('global_duration','local_duration','lbfgs_duration','block_duration','tight_duration','tangent_duration','fraction_duration','timestep_fine_duration','timestep_finest_duration','tangent_fine_duration','tangent_finest_duration','tangent_refined8_duration','tangent_refined16_duration') else 1800 if mode in ('global_integrator','global_short','local_short','lbfgs_short','lbfgs_integrator','block_short','block_integrator','tight_short','tight_integrator','tangent_short','tangent_integrator','fraction_short','fraction_integrator','timestep_fine_short','timestep_finest_short','tangent_fine_short','tangent_finest_short','tangent_refined8_short','tangent_refined16_short') else 900 if mode in ('fraction_operator','tangent_operator','tight_linear','block_preconditioner','failed_frame','lbfgs_operator','local_frame','global_gn_operator','global_energy') else 3600 if mode in ('relative_extended','rebased_local_preflight') else 1800 if mode in ('rebased_preflight','relative_preflight','relative_fine','relative_finest') else 1200 if mode in ('integration_sensitivity_fine','relative_sensitivity') else 600 if mode in ('rebased_operator','relative_fast_equivalence','cohesive_color','relative_operator','integration_sensitivity','contact_preflight','objective_gn','objective_gn_extended') else 7200 if mode == 'sustained_support' else 300 if mode == 'full_blade' else 180
    wall_s = maximum_wall_s if wall_s is None else wall_s
    if not 0 < wall_s <= maximum_wall_s:
        raise ValueError(f'Worker budget must be at most {maximum_wall_s} seconds for {mode}')
    if mode not in ('demo_grip','effort_split','motor_effort_capture','corrected_exchange_clear','corrected_exchange_operator','live_clear_assembly','near_approach','dry_tracking_v02','dry_scene_inspection_v02','dry_scene_inspection','visible_dry_motion', 'startup', 'robot_body_parameters', 'joint_state_interface_pgs', 'joint_recenter_pgs', 'robot_kinematic_binding', 'joint_state_interface', 'joint_recenter', 'joint_recenter_v02', 'joint_recenter_v03', 'robot_wrench_com_trace', 'robot_wrench_trace', 'mounted_target_screen_v05_fine', 'mounted_target_screen_v05_finest', 'mounted_target_screen_v05', 'mounted_target_screen_v04', 'mounted_target_screen_v03', 'robot_energy_operator_v03', 'mounted_target_screen_v02', 'robot_energy_operator_v02', 'mounted_target_screen', 'robot_energy_operator', 'cad_pressure_operator', 'external_load_operator', 'global_pressure_operator', 'cached_static_operator', 'static_preparation_cached', 'direct_static_operator', 'static_preparation_direct', 'loaded_force', 'static_preparation_safeguarded', 'static_preparation_iterative', 'static_preparation_regularized', 'static_operator', 'static_preparation', 'failed_safe_global_operator', 'failed_safe_integrator', 'tangent_refined8_short', 'tangent_refined8_duration', 'tangent_refined16_short', 'tangent_refined16_duration', 'fraction_operator', 'fraction_integrator', 'fraction_short', 'fraction_duration', 'tangent_fine_short', 'tangent_fine_duration', 'tangent_finest_short', 'tangent_finest_duration', 'tangent_operator', 'tangent_integrator', 'tangent_short', 'tangent_duration', 'timestep_fine_short', 'timestep_fine_duration', 'timestep_finest_short', 'timestep_finest_duration', 'tight_linear', 'tight_integrator', 'tight_short', 'tight_duration', 'block_preconditioner', 'failed_frame', 'block_integrator', 'block_short', 'block_duration', 'lbfgs_operator', 'lbfgs_integrator', 'lbfgs_short', 'lbfgs_duration', 'local_short', 'local_duration', 'local_frame', 'global_short', 'global_duration', 'global_integrator', 'global_energy', 'global_gn_operator', 'local_ledger', 'rebased_local_preflight', 'rebased_operator', 'rebased_preflight', 'physical_pressure', 'relative_extended', 'relative_preflight', 'relative_fast_equivalence', 'cohesive_color', 'relative_finest', 'relative_fine', 'relative_sensitivity', 'relative_operator', 'position_precision', 'objective_gn_extended', 'integration_sensitivity_fine', 'integration_sensitivity', 'material_history', 'contact_geometry', 'objective_gn', 'contact_preflight', 'contact_dynamics', 'embedding_contact', 'objective_model', 'objective_force', 'checked_volume', 'objective_operator', 'sustained_support', 'mounted_contact', 'fixed_mount', 'robot_scene_frames', 'full_damage', 'exact_blade_geometry', 'full_blade', 'exact_blade', 'full_coupling', 'full_model', 'volume_coupon', 'material_contact', 'group_material', 'material_coupon', 'material_operator', 'bent_replay', 'bent_rebased', 'bent_origin', 'bent_sequence', 'bent_contact', 'two_joint_replay', 'two_joint_sequence', 'two_joint_contact', 'two_joint_interface', 'hinge_replay', 'hinge_sequence', 'hinge_contact', 'hinge_interface', 'anisotropic_sequence', 'near_origin_spin', *SPIN_AUDIT_MODES, 'spin_coast', 'anisotropic_contact', 'reset_replay', 'turning_sequence', 'offset_contact', 'feedback_sequence', 'contact_feedback', 'physx_proxy', 'dynamic_proxy', 'particle_scatter', 'blade_record_forces', 'blade_record_roundtrip', 'native_slab', 'analytic_forces', 'analytic_contacts', 'contact_roundtrip', 'mesh_crossings', 'direct_mesh', 'direct_mesh_centered', 'direct_mesh_double', 'coupon_initial', 'coupon_stationary_sdf', 'coupon_sdf256', 'coupon_sdf512', 'coupon_target256', 'coupon_target512') and mode not in MOVING_CONTACT_MODES and mode not in MOUNTED_COM_REFINEMENTS and mode not in MOUNTED_V06_REFINEMENTS and mode not in LOADED_SCENE_MODES and mode not in PREPARED_SCENE_MODES and mode not in GLOBAL_HOLD_MODES and mode not in GLOBAL_SCREEN_REFINEMENTS and mode not in SDF_EXPERIMENTS:
        raise ValueError('Only fixed startup or stationary coupon diagnostic allowed')
    worker_path = WORKER if mode == 'startup' else COUPON_WORKER
    if mode == 'demo_grip':worker_path = ROOT / 'rl/tomato_kitchen_stance_worker_v01.py'
    if mode == 'effort_split':
        worker_path = ROOT / 'rl/tomato_effort_split_worker.py'
    if mode == 'motor_effort_capture':
        worker_path = ROOT / 'rl/tomato_motor_effort_capture_worker.py'
    if mode == 'corrected_exchange_clear':
        worker_path = ROOT / 'rl/tomato_corrected_exchange_clear_worker.py'
    if mode == 'corrected_exchange_operator':
        worker_path = ROOT / 'rl/tomato_corrected_exchange_operator_worker.py'
    if mode == 'live_clear_assembly':
        worker_path = ROOT / 'rl/tomato_live_clear_assembly_worker.py'
    if mode == 'near_approach':
        worker_path = ROOT / 'rl/tomato_near_approach_worker.py'
    if mode == 'dry_tracking_v02':
        worker_path = ROOT / 'rl/tomato_dry_tracking_worker_v02.py'
    if mode == 'dry_scene_inspection_v02':
        worker_path = ROOT / 'rl/tomato_dry_motion_inspection_worker_v02.py'
    if mode == 'dry_scene_inspection':
        worker_path = ROOT / 'rl/tomato_dry_motion_inspection_worker.py'
    if mode == 'visible_dry_motion':
        worker_path = ROOT / 'rl/tomato_visible_dry_motion_worker.py'
    if mode == 'robot_body_parameters':
        worker_path = ROOT / 'rl/tomato_robot_body_parameters_worker.py'
    if mode == 'joint_state_interface_pgs':
        worker_path = ROOT / 'rl/tomato_joint_state_interface_worker_pgs.py'
    if mode == 'joint_recenter_pgs':
        worker_path = ROOT / 'rl/tomato_joint_recenter_worker_pgs.py'
    if mode == 'robot_kinematic_binding':
        worker_path = ROOT / 'rl/tomato_robot_kinematic_binding_worker.py'
    if mode == 'joint_state_interface':
        worker_path = ROOT / 'rl/tomato_joint_state_interface_worker.py'
    if mode == 'joint_recenter_v03':
        worker_path = ROOT / 'rl/tomato_joint_recenter_worker_v03.py'
    if mode == 'joint_recenter_v02':
        worker_path = ROOT / 'rl/tomato_joint_recenter_worker_v02.py'
    if mode == 'joint_recenter':
        worker_path = ROOT / 'rl/tomato_joint_recenter_worker.py'
    if mode in MOVING_CONTACT_MODES:
        worker_path = ROOT / 'rl/tomato_moving_contact_worker.py'
    if mode in MOUNTED_COM_REFINEMENTS:
        worker_path = ROOT / 'rl/tomato_mounted_target_com_worker.py'
    if mode == 'robot_wrench_com_trace':
        worker_path = ROOT / 'rl/tomato_robot_wrench_calibration_com_worker.py'
    if mode == 'robot_wrench_trace':
        worker_path = ROOT / 'rl/tomato_robot_wrench_calibration_worker.py'
    if mode in MOUNTED_V06_REFINEMENTS:
        worker_path = ROOT / 'rl/tomato_mounted_target_screen_worker_v06.py'
    if mode in LOADED_SCENE_MODES:
        worker_path = ROOT / 'rl/tomato_loaded_scene_planning_worker.py'
    if mode in PREPARED_SCENE_MODES:
        worker_path = ROOT / ('rl/tomato_prepared_scene_clock_worker.py' if '_device_' in mode else 'rl/tomato_prepared_scene_hold_worker.py')
    if mode == 'sustained_support':
        worker_path = ROOT / 'rl/tomato_sustained_support_worker.py'
    if mode == 'objective_operator':
        worker_path = ROOT / 'rl/tomato_objective_operator_worker.py'
    if mode == 'checked_volume':
        worker_path = ROOT / 'rl/tomato_checked_volume_worker.py'
    if mode == 'objective_force':
        worker_path = ROOT / 'rl/tomato_objective_force_worker.py'
    if mode == 'objective_model':
        worker_path = ROOT / 'rl/tomato_objective_model_worker.py'
    if mode in ('timestep_fine_short','timestep_fine_duration','timestep_finest_short','timestep_finest_duration'):
        worker_path = ROOT / 'rl/tomato_timestep_preflight_worker.py'
    if mode in TANGENT_TIME_REFINEMENTS:
        worker_path = ROOT / 'rl/tomato_tangent_timestep_worker.py'
    if mode == 'external_load_operator':
        worker_path = ROOT / 'rl/tomato_external_load_worker.py'
    if mode == 'robot_energy_operator_v03':
        worker_path = ROOT / 'rl/tomato_robot_energy_worker_v03.py'
    if mode in ('mounted_target_screen_v05_fine','mounted_target_screen_v05_finest'):
        worker_path = ROOT / 'rl/tomato_mounted_target_screen_worker_v05.py'
    if mode == 'mounted_target_screen_v05':
        worker_path = ROOT / 'rl/tomato_mounted_target_screen_worker_v05.py'
    if mode == 'mounted_target_screen_v04':
        worker_path = ROOT / 'rl/tomato_mounted_target_screen_worker_v04.py'
    if mode == 'mounted_target_screen_v03':
        worker_path = ROOT / 'rl/tomato_mounted_target_screen_worker_v03.py'
    if mode == 'robot_energy_operator_v02':
        worker_path = ROOT / 'rl/tomato_robot_energy_worker_v02.py'
    if mode == 'mounted_target_screen_v02':
        worker_path = ROOT / 'rl/tomato_mounted_target_screen_worker_v02.py'
    if mode == 'robot_energy_operator':
        worker_path = ROOT / 'rl/tomato_robot_energy_worker.py'
    if mode == 'mounted_target_screen':
        worker_path = ROOT / 'rl/tomato_mounted_target_screen_worker.py'
    if mode == 'cad_pressure_operator':
        worker_path = ROOT / 'rl/tomato_cad_pressure_worker.py'
    if mode == 'global_pressure_operator':
        worker_path = ROOT / 'rl/tomato_global_pressure_worker.py'
    if mode == 'cached_static_operator':
        worker_path = ROOT / 'rl/tomato_cached_static_operator_worker.py'
    if mode == 'static_preparation_cached':
        worker_path = ROOT / 'rl/tomato_static_cached_worker.py'
    if mode == 'direct_static_operator':
        worker_path = ROOT / 'rl/tomato_direct_static_operator_worker.py'
    if mode == 'static_preparation_direct':
        worker_path = ROOT / 'rl/tomato_static_direct_worker.py'
    if mode == 'loaded_force':
        worker_path = ROOT / 'rl/tomato_loaded_force_worker.py'
    if mode == 'static_preparation_safeguarded':
        worker_path = ROOT / 'rl/tomato_static_safeguarded_worker.py'
    if mode == 'static_preparation_iterative':
        worker_path = ROOT / 'rl/tomato_static_iterative_worker.py'
    if mode == 'static_preparation_regularized':
        worker_path = ROOT / 'rl/tomato_static_regularized_worker.py'
    if mode == 'static_operator':
        worker_path = ROOT / 'rl/tomato_static_operator_worker.py'
    if mode == 'static_preparation':
        worker_path = ROOT / 'rl/tomato_static_preparation_worker.py'
    if mode == 'failed_safe_global_operator':
        worker_path = ROOT / 'rl/tomato_failed_safe_global_operator_worker.py'
    if mode == 'failed_safe_integrator':
        worker_path = ROOT / 'rl/tomato_failed_safe_integrator_worker.py'
    if mode in GLOBAL_SCREEN_REFINEMENTS:
        worker_path = ROOT / 'rl/tomato_streamed_hold_worker.py'
    if mode in GLOBAL_HOLD_MODES:
        worker_path = ROOT / 'rl/tomato_streamed_hold_worker.py'
    if mode == 'fraction_operator':
        worker_path = ROOT / 'rl/tomato_fraction_operator_worker.py'
    if mode == 'fraction_integrator':
        worker_path = ROOT / 'rl/tomato_fraction_integrator_worker.py'
    if mode in ('fraction_short','fraction_duration'):
        worker_path = ROOT / 'rl/tomato_fraction_preflight_worker.py'
    if mode == 'tangent_operator':
        worker_path = ROOT / 'rl/tomato_tangent_operator_worker.py'
    if mode == 'tangent_integrator':
        worker_path = ROOT / 'rl/tomato_tangent_integrator_worker.py'
    if mode in ('tangent_short','tangent_duration'):
        worker_path = ROOT / 'rl/tomato_tangent_preflight_worker.py'
    if mode == 'tight_linear':
        worker_path = ROOT / 'rl/tomato_tight_linear_worker.py'
    if mode == 'tight_integrator':
        worker_path = ROOT / 'rl/tomato_tight_integrator_worker.py'
    if mode in ('tight_short','tight_duration'):
        worker_path = ROOT / 'rl/tomato_tight_preflight_worker.py'
    if mode == 'block_preconditioner':
        worker_path = ROOT / 'rl/tomato_block_preconditioner_worker.py'
    if mode == 'failed_frame':
        worker_path = ROOT / 'rl/tomato_failed_frame_worker.py'
    if mode == 'block_integrator':
        worker_path = ROOT / 'rl/tomato_block_integrator_worker.py'
    if mode in ('block_short','block_duration'):
        worker_path = ROOT / 'rl/tomato_block_preflight_worker.py'
    if mode == 'lbfgs_operator':
        worker_path = ROOT / 'rl/tomato_lbfgs_operator_worker.py'
    if mode == 'lbfgs_integrator':
        worker_path = ROOT / 'rl/tomato_lbfgs_integrator_worker.py'
    if mode in ('lbfgs_short','lbfgs_duration'):
        worker_path = ROOT / 'rl/tomato_lbfgs_preflight_worker.py'
    if mode in ('local_short','local_duration'):
        worker_path = ROOT / 'rl/tomato_local_preflight_worker.py'
    if mode == 'local_frame':
        worker_path = ROOT / 'rl/tomato_local_frame_worker.py'
    if mode in ('global_short','global_duration'):
        worker_path = ROOT / 'rl/tomato_global_preflight_worker.py'
    if mode == 'global_integrator':
        worker_path = ROOT / 'rl/tomato_global_integrator_worker.py'
    if mode == 'global_energy':
        worker_path = ROOT / 'rl/tomato_global_energy_worker.py'
    if mode == 'global_gn_operator':
        worker_path = ROOT / 'rl/tomato_global_gn_operator_worker.py'
    if mode == 'local_ledger':
        worker_path = ROOT / 'rl/tomato_local_ledger_worker.py'
    if mode == 'rebased_local_preflight':
        worker_path = ROOT / 'rl/tomato_rebased_local_preflight_worker.py'
    if mode == 'rebased_operator':
        worker_path = ROOT / 'rl/tomato_rebased_operator_worker.py'
    if mode == 'rebased_preflight':
        worker_path = ROOT / 'rl/tomato_rebased_preflight_worker.py'
    if mode == 'physical_pressure':
        worker_path = ROOT / 'rl/tomato_physical_pressure_worker.py'
    if mode == 'relative_extended':
        worker_path = ROOT / 'rl/tomato_relative_extended_worker.py'
    if mode == 'relative_fast_equivalence':
        worker_path = ROOT / 'rl/tomato_relative_fast_equivalence_worker.py'
    if mode == 'relative_preflight':
        worker_path = ROOT / 'rl/tomato_relative_preflight_worker.py'
    if mode == 'cohesive_color':
        worker_path = ROOT / 'rl/tomato_cohesive_color_worker.py'
    if mode == 'relative_finest':
        worker_path = ROOT / 'rl/tomato_relative_finest_worker.py'
    if mode == 'relative_fine':
        worker_path = ROOT / 'rl/tomato_relative_fine_worker.py'
    if mode == 'relative_sensitivity':
        worker_path = ROOT / 'rl/tomato_relative_sensitivity_worker.py'
    if mode == 'relative_operator':
        worker_path = ROOT / 'rl/tomato_relative_operator_worker.py'
    if mode == 'position_precision':
        worker_path = ROOT / 'rl/tomato_position_precision_worker.py'
    if mode == 'objective_gn_extended':
        worker_path = ROOT / 'rl/tomato_objective_gn_worker.py'
    if mode == 'integration_sensitivity_fine':
        worker_path = ROOT / 'rl/tomato_integration_fine_worker.py'
    if mode == 'integration_sensitivity':
        worker_path = ROOT / 'rl/tomato_integration_sensitivity_worker.py'
    if mode == 'material_history':
        worker_path = ROOT / 'rl/tomato_material_history_worker.py'
    if mode == 'contact_geometry':
        worker_path = ROOT / 'rl/tomato_contact_geometry_worker.py'
    if mode == 'objective_gn':
        worker_path = ROOT / 'rl/tomato_objective_gn_worker.py'
    if mode in ('contact_dynamics','contact_preflight'):
        worker_path = ROOT / 'rl/tomato_contact_dynamics_worker.py'
    if mode == 'embedding_contact':
        worker_path = ROOT / 'rl/tomato_embedding_contact_worker.py'
    if mode == 'mounted_contact':
        worker_path = ROOT / 'rl/tomato_mounted_contact_worker.py'
    if mode == 'fixed_mount':
        worker_path = ROOT / 'rl/tomato_fixed_mount_worker.py'
    if mode == 'robot_scene_frames':
        worker_path = ROOT / 'rl/tomato_robot_scene_frames_worker.py'
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
    if mode == 'full_damage':
        worker_path = FULL_DAMAGE_WORKER
    if mode == 'full_blade':
        worker_path = FULL_BLADE_WORKER
    if mode in ('exact_blade','exact_blade_geometry'):
        worker_path = EXACT_BLADE_WORKER
    if mode == 'full_coupling':
        worker_path = FULL_COUPLING_WORKER
    if mode == 'full_model':
        worker_path = FULL_MODEL_WORKER
    if mode == 'volume_coupon':
        worker_path = VOLUME_COUPON_WORKER
    if mode == 'material_contact':
        worker_path = MATERIAL_CONTACT_WORKER
    if mode == 'group_material':
        worker_path = GROUP_MATERIAL_WORKER
    if mode == 'material_coupon':
        worker_path = MATERIAL_COUPON_WORKER
    if mode == 'material_operator':
        worker_path = MATERIAL_OPERATOR_WORKER
    if mode == 'bent_replay':
        worker_path = BENT_REPLAY_WORKER
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
    if mode in MOUNTED_V06_REFINEMENTS and MOUNTED_V06_REFINEMENTS[mode]>=128:
        worker_path = ROOT / 'rl/tomato_mounted_target_screen_worker_v06_extended.py'
    command = _fixture_command or [str(PYTHON), str(worker_path), '--output', str(output)]
    if mode == 'demo_grip' and os.environ.get('TOMATO_PICKUP_INTERACTIVE') == '1':command.append('--interactive')
    if mode in MOVING_CONTACT_MODES:
        refinement,direction = MOVING_CONTACT_MODES[mode]
        command += ['--coupling-refinement', str(refinement), '--direction', direction]
    if mode in MOUNTED_COM_REFINEMENTS:
        command += ['--refinement', str(MOUNTED_COM_REFINEMENTS[mode])]
    if mode in MOUNTED_V06_REFINEMENTS:
        command += ['--refinement', str(MOUNTED_V06_REFINEMENTS[mode])]
    if mode in ('mounted_target_screen_v05_fine','mounted_target_screen_v05_finest'):
        command += ['--refinement', '4' if mode.endswith('finest') else '2']
    if mode in ('global_duration','local_duration','lbfgs_duration','block_duration','tight_duration','tangent_duration','fraction_duration','timestep_fine_duration','timestep_finest_duration','tangent_fine_duration','tangent_finest_duration','tangent_refined8_duration','tangent_refined16_duration') and not _fixture_command:
        command.append('--long')
    if mode in ('timestep_fine_short','timestep_fine_duration','timestep_finest_short','timestep_finest_duration') and not _fixture_command:
        command += ['--refinement', '4' if 'finest' in mode else '2']
    if mode in TANGENT_TIME_REFINEMENTS and not _fixture_command:
        command += ['--refinement', str(TANGENT_TIME_REFINEMENTS[mode])]
    if mode in LOADED_SCENE_MODES and not _fixture_command:
        load_case, screen = LOADED_SCENE_MODES[mode]
        command += ['--load-case',load_case]
        if screen:command.append('--screen')
    if mode in PREPARED_SCENE_MODES and not _fixture_command:
        phase = PREPARED_SCENE_MODES[mode][0]
        if phase in ('screen','preview'):command.append('--'+phase)
    if mode in GLOBAL_HOLD_MODES and not _fixture_command:
        refinement, preview = GLOBAL_HOLD_MODES[mode]
        command += ['--refinement', str(refinement)]
        if preview:command.append('--preview')
    if mode in GLOBAL_SCREEN_REFINEMENTS and not _fixture_command:
        command += ['--refinement', str(GLOBAL_SCREEN_REFINEMENTS[mode]), '--screen']
    if mode == 'exact_blade_geometry' and not _fixture_command:
        command.append('--geometry-only')
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

    if not _fixture_command:
        assert_experiment_route(mode, worker_path, command)

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
                                                ({ROOT/'rl/tomato_two_joint_replay_reference.py', ROOT/'rl/tomato_bent_rebased_reference.py', ROOT/'rl/tomato_bent_origin_reference.py', ROOT/'rl/tomato_two_joint_sequence_reference.py', ROOT/'rl/tomato_half_step_reaction.py', ROOT/'rl/tomato_offset_contact_reference.py', ROOT/'rl/tomato_reaction_metadata.py', ROOT/'rl/tomato_wrench_contract.py'} if mode == 'bent_replay' else set()) |
                                                ({ROOT/'rl/tomato_material_contract.py', ROOT/'rl/tomato_native_cohesive_operator.py', ROOT/'rl/tomato_bonds.py', ROOT/'rl/tomato_cohesive_adapter_reference.py', ROOT/'rl/tomato_cohesive_evolution_reference.py'} if mode == 'material_operator' else set()) |
                                                ({ROOT/'rl/tomato_material_contract.py', ROOT/'rl/tomato_native_cohesive_operator.py', ROOT/'rl/tomato_bonds.py', ROOT/'rl/tomato_half_step_reaction.py'} if mode == 'material_coupon' else set()) |
                                                ({ROOT/'rl/tomato_native_group_cohesion.py', ROOT/'rl/tomato_bonds.py', ROOT/'rl/tomato_cohesive_adapter_reference.py', ROOT/'rl/tomato_cohesive_evolution_reference.py'} if mode == 'group_material' else set()) |
                                                ({ROOT/'rl/tomato_native_cohesive_operator.py', ROOT/'rl/tomato_material_contract.py', ROOT/'rl/tomato_half_step_reaction.py'} if mode == 'material_contact' else set()) |
                                                ({ROOT/'rl/tomato_deterministic_contact_solver.py', ROOT/'rl/tomato_blade_quadrature.py', ROOT/'rl/tomato_exact_blade_coverage.py', ROOT/'rl/tomato_exact_blade_queries.py', ROOT/'rl/tomato_mesh_weighted_contact.py', ROOT/'work/exact_blade_cells.json'} if mode in ('exact_blade','exact_blade_geometry','full_blade') else set()) |
                                                ({ROOT/'rl/tomato_native_volume_steps.py', ROOT/'rl/tomato_native_full_gather.py', ROOT/'rl/tomato_native_full_model.py', ROOT/'rl/tomato_native_group_cohesion.py', ROOT/'rl/tomato_surface_cohesion.py', ROOT/'rl/tomato_volume_protection.py'} if mode in ('full_model','full_coupling','full_blade','full_damage') else set()) |
                                                ({ROOT/'rl/tomato_native_group_cohesion.py'} if mode == 'volume_coupon' else set()) |
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
    parser.add_argument('--mode', choices=('demo_grip','effort_split','motor_effort_capture','corrected_exchange_clear','corrected_exchange_operator','live_clear_assembly','near_approach','dry_tracking_v02','dry_scene_inspection_v02','dry_scene_inspection','visible_dry_motion', 'robot_body_parameters', 'joint_state_interface_pgs', 'joint_recenter_pgs', 'robot_kinematic_binding', 'joint_state_interface', 'joint_recenter', 'joint_recenter_v02', 'joint_recenter_v03', *MOVING_CONTACT_MODES, *MOUNTED_COM_REFINEMENTS, *MOUNTED_V06_REFINEMENTS, *LOADED_SCENE_MODES, *PREPARED_SCENE_MODES, *GLOBAL_SCREEN_REFINEMENTS, *GLOBAL_HOLD_MODES, 'robot_wrench_com_trace', 'robot_wrench_trace', 'mounted_target_screen_v05_fine', 'mounted_target_screen_v05_finest', 'mounted_target_screen_v05', 'mounted_target_screen_v04', 'mounted_target_screen_v03', 'robot_energy_operator_v03', 'mounted_target_screen_v02', 'robot_energy_operator_v02', 'mounted_target_screen', 'robot_energy_operator', 'cad_pressure_operator', 'external_load_operator', 'global_pressure_operator', 'cached_static_operator', 'static_preparation_cached', 'direct_static_operator', 'static_preparation_direct', 'loaded_force', 'static_preparation_safeguarded', 'static_preparation_iterative', 'static_preparation_regularized', 'static_operator', 'static_preparation', 'failed_safe_global_operator', 'failed_safe_integrator', 'startup', 'tangent_refined8_short', 'tangent_refined8_duration', 'tangent_refined16_short', 'tangent_refined16_duration', 'fraction_operator', 'fraction_integrator', 'fraction_short', 'fraction_duration', 'tangent_fine_short', 'tangent_fine_duration', 'tangent_finest_short', 'tangent_finest_duration', 'tangent_operator', 'tangent_integrator', 'tangent_short', 'tangent_duration', 'timestep_fine_short', 'timestep_fine_duration', 'timestep_finest_short', 'timestep_finest_duration', 'tight_linear', 'tight_integrator', 'tight_short', 'tight_duration', 'block_preconditioner', 'failed_frame', 'block_integrator', 'block_short', 'block_duration', 'lbfgs_operator', 'lbfgs_integrator', 'lbfgs_short', 'lbfgs_duration', 'local_short', 'local_duration', 'local_frame', 'global_short', 'global_duration', 'global_integrator', 'global_energy', 'global_gn_operator', 'local_ledger', 'rebased_local_preflight', 'rebased_operator', 'rebased_preflight', 'physical_pressure', 'relative_extended', 'relative_preflight', 'relative_fast_equivalence', 'cohesive_color', 'relative_finest', 'relative_fine', 'relative_sensitivity', 'relative_operator', 'position_precision', 'objective_gn_extended', 'integration_sensitivity_fine', 'integration_sensitivity', 'material_history', 'contact_geometry', 'objective_gn', 'contact_preflight', 'contact_dynamics', 'embedding_contact', 'objective_model', 'objective_force', 'checked_volume', 'objective_operator', 'sustained_support', 'mounted_contact', 'fixed_mount', 'robot_scene_frames', 'full_damage', 'exact_blade_geometry', 'full_blade', 'exact_blade', 'full_coupling', 'full_model', 'volume_coupon', 'material_contact', 'group_material', 'material_coupon', 'material_operator', 'bent_replay', 'bent_rebased', 'bent_origin', 'bent_sequence', 'bent_contact', 'two_joint_replay', 'two_joint_sequence', 'two_joint_contact', 'two_joint_interface', 'hinge_replay', 'hinge_sequence', 'hinge_contact', 'hinge_interface', 'anisotropic_sequence', 'near_origin_spin', *SPIN_AUDIT_MODES, 'spin_coast', 'anisotropic_contact', 'reset_replay', 'turning_sequence', 'offset_contact', 'feedback_sequence', 'contact_feedback', 'physx_proxy', 'dynamic_proxy', 'particle_scatter', 'blade_record_forces', 'blade_record_roundtrip', 'native_slab', 'analytic_forces', 'analytic_contacts', 'contact_roundtrip', 'mesh_crossings', 'direct_mesh', 'direct_mesh_centered', 'direct_mesh_double', 'coupon_initial', 'coupon_stationary_sdf', 'coupon_sdf256', 'coupon_sdf512', 'coupon_target256', 'coupon_target512', *SDF_EXPERIMENTS), default='startup')
    args = parser.parse_args()
    result = supervise(args.output, mode=args.mode)
    print(json.dumps(result, indent=2))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
