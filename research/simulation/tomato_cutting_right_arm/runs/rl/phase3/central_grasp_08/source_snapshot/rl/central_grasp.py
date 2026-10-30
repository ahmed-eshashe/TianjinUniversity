"""Guarded central physical pickup experiment. Scripted feasibility check, never training."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
import traceback

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--seconds',type=int,required=True)
p.add_argument('--candidate',type=int,default=0)
p.add_argument('--grasp-plan',choices=['initial','alternatives'],default='initial')
a=p.parse_args()

def write(name,data):
    t=a.output/(name+'.tmp');t.write_text(json.dumps(data,indent=2));t.replace(a.output/name)

app=None;env=None;records=[];phase='startup';passed=False
try:
    from isaaclab.app import AppLauncher
    app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
    import numpy as np
    import torch
    from scipy.spatial.transform import Rotation,Slerp
    from native_env import NativeValidationCfg,NativeValidationEnv
    from native_contacts import NativeContactMonitor,numpy
    from contact_evaluator import ContactEvidence
    from grasp_metrics import GraspEvaluator
    sys.path.insert(0,str(ROOT/'scripts'))
    from reach_kinematics import ArmKinematics,PALM_OFFSET

    class PhysicalGraspEnv(NativeValidationEnv):
        def _apply_action(self):
            super()._apply_action()
            if not hasattr(self,'grasp_evidence'):return
            # Read the previous physics substep, so brief blade contacts cannot disappear between control samples.
            contacts=self.contact_monitor.summary()
            if any(c['body'].startswith('/dual_ar5_o6') and c['other']==self.manifest['knife_path'] for c in contacts):
                s=self.grasp_evidence.sample()
                if s['blade_contact'] or s['unsafe_contact'] or s['contact_buffer_full']:
                    self.substep_event=s
                    raise RuntimeError('Physics-substep knife contact safety stop')
            if any(c['body'].startswith('/dual_ar5_o6') and c['force_n']>50 for c in contacts):
                self.substep_event={'contacts':contacts}
                raise RuntimeError('Physics-substep excessive robot contact stop')

        def _pre_physics_step(self,actions):
            self.previous=actions.clone()
            arm=self.ids[:7];hand=self.ids[7:]
            self.target[:,arm]+=(self.desired[:,arm]-self.target[:,arm]).clamp(-.008,.008)
            self.target[:,hand]+=(self.desired[:,hand]-self.target[:,hand]).clamp(-.01,.01)
            limits=self.robot.data.soft_joint_pos_limits.torch
            self.target=torch.maximum(torch.minimum(self.target,limits[:,:,1]),limits[:,:,0])

    planfile='flat_grasp_alternatives.json' if a.grasp_plan=='alternatives' else 'flat_grasp_geometry.json'
    plan=json.loads((ROOT/'docs/rl'/planfile).read_text())
    candidate=plan['candidates'][a.candidate]
    reset=candidate.get('reset',plan['reset'])
    if candidate['ik_position_error_m']>.005 or candidate['ik_angle_error_rad']>.04:
        raise RuntimeError('Candidate is not kinematically reachable')
    cfg=NativeValidationCfg();cfg.episode_length_s=1000.
    env=PhysicalGraspEnv(cfg,phase3=True)
    env.reset_cases=[reset];env.reset()
    env.desired=env.home.clone()
    env.contact_monitor=NativeContactMonitor(env);evidence=ContactEvidence(env);env.grasp_evidence=evidence
    kin=ArmKinematics(env.sim.stage)
    start=time.monotonic();controls=0;max_robot_contact=0.;last_save=start;oracle=None
    write('run_configuration.json',{'training':False,'controller':'scripted bounded native feasibility experiment',
        'candidate':candidate,'reset':reset,'self_collision':True,'attachments':False,
        'source_hashes':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in ['rl/central_grasp.py','rl/native_env.py','rl/contact_evaluator.py','rl/grasp_metrics.py','rl/scene/phase3.usda']}})
    for f in ['rl/central_grasp.py','rl/native_env.py','rl/contact_evaluator.py','rl/grasp_metrics.py','rl/scene/phase3.usda','docs/rl/phase3_grasp_criteria.json',f'docs/rl/{planfile}']:
        snapshot=a.output/'source_snapshot'/f;snapshot.parent.mkdir(parents=True,exist_ok=True);snapshot.write_bytes((ROOT/f).read_bytes())

    def palm_pose():
        t=numpy(env.robot.root_view.get_link_transforms())[0,env.robot.body_names.index('right_rh_hand_base_link')]
        r=Rotation.from_quat(t[3:]).as_matrix()
        return t[:3]+r@PALM_OFFSET,r

    def step():
        global controls,last_save,max_robot_contact
        if time.monotonic()-start>a.seconds:raise RuntimeError('Bounded experiment wall limit reached')
        if (a.output/'checkpoint_and_stop.request').exists():raise RuntimeError('Memory/manual safe stop requested')
        env.step(torch.zeros(1,13));controls+=1
        if env.last_unsafe:
            write('unsafe_detail.json',env.unsafe_detail)
            raise RuntimeError('Physical motion/contact safeguard stopped the attempt')
        sample=evidence.sample()
        if sample['blade_contact'] or sample['unsafe_contact'] or sample['attachment'] or sample['contact_buffer_full'] or sample['joint_limit_violation']:
            raise RuntimeError('Blade/attachment/contact-buffer/joint-limit safeguard stopped the attempt')
        contacts=env.contact_monitor.summary()
        for c in contacts:
            if not c['body'].startswith('/dual_ar5_o6'):continue
            max_robot_contact=max(max_robot_contact,c['force_n'])
            if c['other'] in [env.manifest['board_path'],env.manifest['counter_path']]:
                threshold=10. if '/right_rh_' in c['body'] else 5.
                if c['force_n']>threshold:
                    write('unsafe_contacts.json',contacts)
                    raise RuntimeError('Excessive hand/arm contact with supporting surface')
        sample.update(phase=phase,control_step=controls,sim_s=controls*.05,
            q_rad=env.robot.data.joint_pos.torch[0,env.ids].tolist(),palm_world_m=palm_pose()[0].tolist(),
            knife_pose_xyzw=env.knife.data.root_link_pose_w.torch[0].tolist())
        if oracle is not None:sample['metric']=oracle.update(sample,.05)
        records.append(sample)
        if controls%10==0:write('progress.json',{'phase':phase,'controls':controls,'elapsed_wall_s':time.monotonic()-start,
                                               'handle_height_m':sample['handle_height_m'],'contacts':sample['contacts']})
        if time.monotonic()-last_save>15:
            write('validation_checkpoint.json',{'phase':phase,'controls':controls,'records':records[-20:],
                'training':False,'resume':'fresh physical reset required'})
            last_save=time.monotonic()
        return sample

    def wait_targets(max_steps=240):
        for _ in range(max_steps):
            step()
            if float((env.target-env.desired).abs().max())<.001:break
        else:raise RuntimeError('Bounded target interpolation could not converge')

    def set_hand(fingers,thumb_yaw,thumb_pitch):
        values=[thumb_yaw,thumb_pitch,fingers,fingers,fingers,fingers]
        env.desired[:,env.ids[7:]]=torch.tensor([values],dtype=env.desired.dtype,device=env.device)
        wait_targets()

    def move(target,orientation):
        origin,initial_rotation=palm_pose();distance=np.linalg.norm(target-origin)
        angle=Rotation.from_matrix(orientation@initial_rotation.T).magnitude()
        count=max(2,int(np.ceil(distance/.004)),int(np.ceil(angle/.025)))
        rotations=Slerp([0,1],Rotation.from_matrix([initial_rotation,orientation]))
        q=env.robot.data.joint_pos.torch[0,env.ids[:7]].numpy().copy()
        for alpha in np.linspace(0,1,count+1)[1:]:
            pos=origin+alpha*(target-origin);rot=rotations(alpha).as_matrix()
            q,error,rotation_error=kin.solve(pos,rot,q)
            if error>.005 or rotation_error>.04:raise RuntimeError('IK route does not meet pose tolerance')
            env.desired[:,env.ids[:7]]=torch.from_numpy(q.astype(np.float32)).unsqueeze(0)
            wait_targets(100)
        for _ in range(10):step()
        if np.linalg.norm(palm_pose()[0]-target)>.02:raise RuntimeError('Palm tracking error exceeds 2 cm')

    phase='settling'
    for _ in range(30):sample=step()
    initial_height=sample['handle_height_m'];oracle=GraspEvaluator(initial_height)
    handle_pose=env.knife.data.root_link_pose_w.torch[0].numpy();kr=Rotation.from_quat(handle_pose[3:]).as_matrix()
    handle=kr@evidence.centre+handle_pose[:3]
    orientation=np.array(candidate['hand_rotation_world'])
    target=handle-orientation@(np.array(candidate['handle_in_hand_m'])-PALM_OFFSET)
    phase='preshape_above_board'
    set_hand(np.deg2rad(candidate['finger_deg']),np.deg2rad(candidate['thumb_yaw_deg']),0.)
    phase='approach'
    # A joint-space route to the pregrasp avoids a wrist-folding branch of the straight pose interpolation.
    pregrasp=target+np.array([0,0,.08])
    q,error,angle=kin.solve(pregrasp,orientation,np.array(candidate['q_rad']))
    if error>.005 or angle>.04:raise RuntimeError('Pregrasp IK is not reachable within tolerance')
    env.desired[:,env.ids[:7]]=torch.from_numpy(q.astype(np.float32)).unsqueeze(0)
    wait_targets(600)
    for _ in range(20):step()
    if np.linalg.norm(palm_pose()[0]-pregrasp)>.02:raise RuntimeError('Pregrasp tracking error')
    phase='descent'
    move(target,orientation)
    phase='fingers_then_thumb'
    set_hand(np.deg2rad(candidate['finger_deg']),np.deg2rad(candidate['thumb_yaw_deg']),np.deg2rad(candidate['thumb_pitch_deg']))
    for _ in range(20):sample=step()
    # Increment only the thumb's independent drives until actual handle support appears.
    phase='thumb_contact_feedback'
    for _ in range(160):
        thumb_force=sum(c['force_n'] for c in sample['contacts'] if c['part']=='thumb' and c['on_handle'])
        if thumb_force>=3.:break
        current=float(env.desired[0,env.ids[8]])
        if current<np.deg2rad(32.5):env.desired[0,env.ids[8]]+=.003
        else:env.desired[0,env.ids[7]]=min(float(env.desired[0,env.ids[7]])+.003,np.deg2rad(77.5))
        sample=step()
    write('before_lift.json',sample)
    support={c['part'] for c in sample['contacts'] if c['on_handle'] and c['force_n']>.05}
    if 'thumb' not in support or not support&{'index','middle','ring','pinky'} or not sample['metric']['opposed']:
        raise RuntimeError('Opposed physical finger/handle support absent; lift refused')
    write('provisional_pinch.json',{'support_parts':sorted(support),'final_grasp_accepted':False,
                                  'note':'An initial opposed pinch may provide clearance; final palm/three-finger criteria remain mandatory'})
    phase='clearance_lift'
    move(target+np.array([0,0,.035]),orientation)
    sample=records[-1]
    if sample['dropped'] or sample['handle_height_m']-initial_height<.015:
        raise RuntimeError('Knife did not follow the physical clearance lift; wrap/lift refused')
    phase='complete_wrap'
    set_hand(np.deg2rad(85),float(env.desired[0,env.ids[7]]),float(env.desired[0,env.ids[8]]))
    phase='lift'
    move(target+np.array([0,0,.075]),orientation)
    phase='hold'
    for _ in range(80):
        sample=step();metric=sample['metric']
        if sample['dropped']:raise RuntimeError('Knife dropped during hold')
        if metric['success']:passed=True;break
    write('grasp_metric.json',metric)
    write('result.json',{'passed':passed,'training':False,'initial_handle_height_m':initial_height,
        'final_handle_height_m':sample['handle_height_m'],'lift_m':sample['handle_height_m']-initial_height,
        'metric':metric,'max_robot_contact_n':max_robot_contact,'controls':controls,'phase':phase,
        'initial_reset':reset,'knife_teleports_during_episode':0,'attachment_created':False})
except BaseException:
    write('failure.json',{'phase':phase,'traceback':traceback.format_exc(),'training':False,
        'last_sample':records[-1] if records else None,'substep_event':getattr(env,'substep_event',None)})
    traceback.print_exc()
finally:
    try:
        write('trajectory.json',records)
    finally:
        try:
            if env is not None:env.close()
        finally:
            if app is not None:app.close()
