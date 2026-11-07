from pathlib import Path
import hashlib,json,shutil
from tomato_physx_bridge_reference import reference_packet
root=Path.cwd();run=root/'runs/source_review/physx_newton_bridge_interfaces_20261031';out=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs')
isaac=Path('/home/omen/IsaacLab/source');newton=Path('/home/omen/miniconda3/envs/isaaclab_6/lib/python3.12/site-packages/newton/_src')
files={
 'physx_rigid_object':isaac/'isaaclab_physx/isaaclab_physx/assets/rigid_object/rigid_object.py',
 'base_rigid_object':isaac/'isaaclab/isaaclab/assets/rigid_object/base_rigid_object.py',
 'base_rigid_data':isaac/'isaaclab/isaaclab/assets/rigid_object/base_rigid_object_data.py',
 'wrench_composer':isaac/'isaaclab/isaaclab/utils/wrench_composer.py',
 'simulation_context':isaac/'isaaclab/isaaclab/sim/simulation_context.py',
 'isaac_newton_coupler':isaac/'isaaclab_contrib/isaaclab_contrib/coupling/coupler.py',
 'isaac_coupler_config':isaac/'isaaclab_contrib/isaaclab_contrib/coupling/coupler_cfg.py',
 'newton_model':newton/'sim/model.py','vbd_solver':newton/'solvers/vbd/solver_vbd.py',
 'vbd_coupling':newton/'solvers/vbd/vbd_coupling_kernels.py','coupling_interface':newton/'solvers/coupled/interface.py',
 'bridge_reference':root/'rl/tomato_physx_bridge_reference.py','bridge_tests':root/'rl/tests/test_tomato_physx_bridge_reference.py'}
targets=('def write_root_pose_to_sim_index','def write_root_com_velocity_to_sim_index','def write_data_to_sim',
 'def root_link_pose_w','def root_com_vel_w','def add_forces_and_torques_index','def set_external_force_and_torque',
 'def coupling_harvest_proxy_wrenches','def _harvest_vbd_body_particle_contact_forces_on_proxy_bodies_kernel',
 'integrate_with_external_rigid_solver','class CouplerEntryCfg','def step(')
evidence={}
for label,p in files.items():
 source=p.read_text();lines=source.splitlines();matches=[]
 for i,line in enumerate(lines):
  if any(target in line for target in targets):matches.append({'line':i+1,'excerpt':'\n'.join(lines[max(0,i-2):i+20])})
 evidence[label]={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'matches':matches}
 dest=run/'source_snapshot'/label/p.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
frozen=json.loads((root/'runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json').read_text())['source_sha256'];assert all(hashlib.sha256((root/n).read_bytes()).hexdigest()==h for n,h in frozen.items())
example=reference_packet([1.,2.,3.,0.,0.,0.,1.],[1.,2.,3.,0.,0.,2.],[.5,0.,0.],[0.,0.,-3.],[1.5,3.,3.])
a={'result':'Installed state/wrench interfaces inspected; host reference contract passes 5 tests. Runtime bridge is not implemented or validated.',
 'conventions':{'pose':'xyz + quaternion xyzw on both selected installed APIs; no legacy quaternion reorder.',
 'velocity':'World COM linear velocity xyz, then world angular velocity xyz.',
 'newton_pose':'Rigid body actor/link frame; COM offset remains body-local and is transformed to world for moment/point velocity.',
 'reaction':'World force = -soft contact force. World torque about COM = (contact_world - com_world) cross reaction.',
 'physx_delivery':'Instantaneous wrench composer, is_global=True, positions=None when torque already includes contact moment; call write_data_to_sim before physics step.',
 'units':'m, s, kg, N, N m; a force packet is not pre-multiplied by dt.'},
 'source_findings':['Current pose index APIs and data getters use xyzw and COM-world velocities.',
 'PhysX instantaneous composer is cleared after write_data_to_sim; permanent composer persists. Deprecated set_external_force_and_torque targets the permanent composer.',
 'SolverVBD external-rigid mode does not integrate rigid bodies; its harvest falls back to proxy momentum change. Unchanged proxy velocity can therefore yield zero despite soft contact.',
 'VBD explicit contact-force harvest in internal-rigid mode reads dynamic-body adjacency; prescribed kinematic bodies can have no such adjacency. A global-stream reference collector does not automatically become a validated runtime bridge.',
 'The inspected IsaacLab coupled configuration targets Newton ModelViews/NewtonManager; it does not demonstrate a ready CPU PhysX adapter. A PhysX shadow Newton model used for visualization is not force feedback.'],
 'ownership_decision':'PhysX remains authoritative for rigid motion. Newton proxy receives state; Newton advances only soft state in external-rigid mode. Reactions must be explicitly collected and applied once to PhysX. Never advance and copy back a second Newton rigid trajectory.',
 'planned_interval':['Read PhysX link pose, COM velocity, COM offset and body mapping at t_n; record episode/step/time/dt.',
 'Synchronize CPU PhysX state to the CUDA Newton proxy using an explicit, verified transfer; preserve quaternion and COM conventions.',
 'Run the declared Newton soft substep schedule with a documented proxy trajectory policy; collect contact-only reaction and the interval over which it acts.',
 'Apply one world COM wrench through the instantaneous composer, then write_data_to_sim and advance PhysX for the same declared interval.',
 'Refresh PhysX data, copy back state for the next interval, invalidate stale contact/snapshot generations and reject duplicate or mismatched-time deliveries.'],
 'timing_limit':'This is a partitioned time-stepping design, not monolithic Newton backward Euler. Must test impulse/work for the actual schedule and expose lag; the previous free-pair reference is not automatically the coupled reference.',
 'next_bounded_test':'Isolated CPU PhysX proxy pose/velocity echo plus one-shot wrench impulse and zero-next-step check, including rotated/nonzero-COM case. No robot or blade; no Newton contact feedback yet.',
 'tests_passed':5,'native_launches':0,'physics_steps':0,'robot_modified':False,'installed_sources_modified':False,
 'original_pinned_sources_unchanged':True,'item_15_complete':False,'reference_example':example,
 'sources':{k:{'path':v['path'],'sha256':v['sha256']} for k,v in evidence.items()}}
(run/'source_evidence.json').write_text(json.dumps(evidence,indent=2)+'\n');(run/'assessment.json').write_text(json.dumps(a,indent=2)+'\n');(out/'newton-physx-bridge-interface-review-20261031.json').write_text(json.dumps(a,indent=2)+'\n')
(out/'newton-physx-bridge-interface-review-20261031.txt').write_text('''Newton–Isaac/PhysX bridge interface review — 31 October 2026

Source inspection and host reference arithmetic complete. Five frame/wrench tests passed. No native engines were launched, no physics steps occurred, and no installed library, robot/controller or frozen production file was changed. The runtime bridge remains unimplemented/unvalidated.

Selected installed interfaces
• PhysX rigid-object data: root_link_pose_w and root_com_vel_w; articulated robot link mapping must be checked separately later.
• Pose index APIs use xyz + quaternion xyzw. Newton transforms also use xyzw. Do not apply an old wxyz conversion to these APIs.
• Velocities are world-frame COM linear xyz followed by world angular xyz. Link-origin linear velocity is a different quantity.
• World COM is link position plus rotated local COM offset. Contact velocity is COM velocity plus omega cross (contact - COM).
• Reaction force is minus soft contact force. Torque is about the COM: (contact - COM) cross reaction.
• Deliver an instantaneous world-frame force/COM torque with positions=None when the contact moment is already included. Supplying the contact position again would count its moment twice. The composer converts world inputs into the body frame before the PhysX call.
• write_data_to_sim sends the wrench before stepping and clears the instantaneous composer. The deprecated external-force setter targets the persistent composer and is unsuitable as an assumed one-step contact-force API. Actual backend force clearing still needs a runtime test.

Important coupling limits
Newton's external-rigid flag supplies one-way rigid-to-soft motion by itself. In that mode the default feedback harvest is based on proxy momentum change, so an unchanged proxy velocity can report zero reaction despite soft contact. The internal-rigid explicit harvest instead uses dynamic-body adjacency; kinematic prescribed proxies can have no entries there. Neither route is automatically a validated CPU PhysX bridge.

The inspected IsaacLab coupler works through Newton models/solver views. The reviewed shadow Newton state used for PhysX visualization is not two-way physical coupling. No ready CPU PhysX adapter was established by this inspection.

Proposed ownership and timing
PhysX owns rigid motion. Newton receives proxy state and advances soft state; it must not also advance and write back an independent rigid trajectory. Record body mapping, episode, step, time and dt. Explicitly synchronize CPU/CUDA transfers. Collect contact-only world reactions and deliver them exactly once through the instantaneous composer before the corresponding PhysX step. Refresh state and invalidate stale contact/snapshot identities afterward.

The precise proxy trajectory and substep schedule must be declared and tested. This partitioned scheme is not the monolithic Newton free-pair step tested earlier; its impulse/work reference must account for lag and the selected time integration.

Next bounded test
Create one isolated CPU PhysX proxy and verify pose/COM-velocity echo, a known one-step wrench impulse, and no stale force on the following zero-input step. Include rotation and nonzero COM to check frame/moment handling. No robot, blade, Newton contact feedback or backend migration is needed for that interface test.

Checklist item 15 remains open. The full real-blade collision path (item 12) is also still open.
''')
print('Inspected',len(files),'sources; source snapshots and bridge reference report saved.')
