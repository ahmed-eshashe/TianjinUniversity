"""Guarded central physical pickup experiment. Scripted feasibility check, never training."""
import argparse
from collections import deque
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
p.add_argument('--grasp-plan',choices=['initial','alternatives','seated','pad-aware'],default='initial')
p.add_argument('--in-place-tilt',choices=['pitch','roll-positive','roll-negative'])
p.add_argument('--seating-mode',choices=['legacy','coordinated','adaptive','mesh-guided','contact-path'],default='legacy')
a=p.parse_args()
if a.seating_mode!='legacy' and not a.in_place_tilt:p.error('Coordinated seating requires --in-place-tilt')

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
    from rolling_contact_control import project_contact_motion
    from contact_path_control import synchronized_increment,validated_waypoints,balanced_contact_goals,anchor_translation_correction
    from hand_fk_check import check_hand_frames
    from seating_control import seating_hand_goals,SupportedPinchMonitor
    from in_place_motion import tilt_path,knife_motion,relative_command_pose
    sys.path.insert(0,str(ROOT/'scripts'))
    from reach_kinematics import ArmKinematics,PALM_OFFSET

    class PhysicalGraspEnv(NativeValidationEnv):
        scene_file_override=ROOT/'rl/scene/phase3_grasp.usda'
        def _apply_action(self):
            super()._apply_action()
            if not hasattr(self,'grasp_evidence'):return
            if a.seating_mode!='legacy':
                thumb_pitch=float(self.robot.data.joint_pos.torch[0,self.ids[8]])
                if thumb_pitch>.32:
                    self.substep_event={'thumb_pitch_rad':thumb_pitch,'experimental_posture_limit_rad':.32}
                    raise RuntimeError('Experimental thumb/palm clearance posture stop')
            # Read the previous physics substep, so brief blade contacts cannot disappear between control samples.
            contacts=self.contact_monitor.summary()
            if phase=='contact_preserving_seating':
                if not hasattr(self,'seating_trace'):self.seating_trace=deque(maxlen=96)
                trace=self.grasp_evidence.sample(record_friction=True)
                trace.update(control_step=controls,substep_in_control=len([x for x in self.seating_trace if x['control_step']==controls]),
                    knife_pose_xyzw=self.knife.data.root_link_pose_w.torch[0].tolist(),
                    knife_velocity=self.knife.data.root_link_vel_w.torch[0].tolist(),
                    q_rad=self.robot.data.joint_pos.torch[0,self.ids].tolist(),command_q_rad=self.target[0,self.ids].tolist())
                self.seating_trace.append(trace)
            if any(c['body'].startswith('/dual_ar5_o6') and c['other']==self.manifest['knife_path'] for c in contacts):
                s=self.grasp_evidence.sample()
                if s['blade_contact'] or s['unsafe_contact'] or s['contact_buffer_full']:
                    self.substep_event=s
                    raise RuntimeError('Physics-substep knife contact safety stop')
            if any(c['body'].startswith('/dual_ar5_o6') and c['force_n']>50 for c in contacts):
                self.substep_event={'contacts':contacts}
                raise RuntimeError('Physics-substep excessive robot contact stop')
            for c in contacts:
                if c['body'].startswith('/dual_ar5_o6') and c['other'] in [self.manifest['board_path'],self.manifest['counter_path']]:
                    if c['force_n']>(10. if '/right_rh_' in c['body'] else 5.):
                        self.substep_event={'contacts':contacts}
                        raise RuntimeError('Physics-substep supporting-surface contact stop')

        def _pre_physics_step(self,actions):
            self.previous=actions.clone()
            arm=self.ids[:7];hand=self.ids[7:]
            if phase=='contact_preserving_seating':
                delta=(self.desired[0,self.ids]-self.target[0,self.ids]).numpy()
                increment=synchronized_increment(delta,[.001]*7+[.003]*6)
                self.target[0,self.ids]+=torch.tensor(increment,dtype=self.target.dtype)
            else:
                self.target[:,arm]+=(self.desired[:,arm]-self.target[:,arm]).clamp(-.008,.008)
                self.target[:,hand]+=(self.desired[:,hand]-self.target[:,hand]).clamp(-.01,.01)
            limits=self.robot.data.soft_joint_pos_limits.torch
            self.target=torch.maximum(torch.minimum(self.target,limits[:,:,1]),limits[:,:,0])

    planfile={'initial':'flat_grasp_geometry.json','alternatives':'flat_grasp_alternatives.json','seated':'flat_grasp_seated.json','pad-aware':'flat_grasp_pad_aware.json'}[a.grasp_plan]
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
    start=time.monotonic();controls=0;max_robot_contact=0.;last_save=start;oracle=None;initial_knife_pose=None;contact_reference=None;transfer_streak=0
    write('run_configuration.json',{'training':False,'controller':'scripted bounded native feasibility experiment',
        'in_place_tilt':a.in_place_tilt,'seating_mode':a.seating_mode,'candidate':candidate,'reset':reset,'self_collision':True,'attachments':False,
        'source_hashes':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in ['rl/central_grasp.py','rl/native_env.py','rl/contact_evaluator.py','rl/grasp_metrics.py','rl/in_place_motion.py','rl/seating_control.py','rl/hand_fk_check.py','rl/contact_path_control.py','rl/rolling_contact_control.py','rl/plan_contact_seating.py','rl/scene/phase3.usda','rl/scene/phase3_grasp.usda']}})
    for f in ['rl/central_grasp.py','rl/native_env.py','rl/contact_evaluator.py','rl/grasp_metrics.py','rl/scene/phase3.usda','rl/scene/phase3_grasp.usda','rl/in_place_motion.py','rl/seating_control.py','rl/hand_fk_check.py','rl/contact_path_control.py','rl/rolling_contact_control.py','rl/plan_contact_seating.py','rl/guard_benchmark.py','docs/rl/phase3_grasp_criteria.json',f'docs/rl/{planfile}']:
        snapshot=a.output/'source_snapshot'/f;snapshot.parent.mkdir(parents=True,exist_ok=True);snapshot.write_bytes((ROOT/f).read_bytes())

    mesh_proposal=None;contact_path_plan=None
    if a.seating_mode=='mesh-guided':
        f='docs/rl/refined_supported_wrap.json';snapshot=a.output/'source_snapshot'/f
        data=(ROOT/f).read_bytes();snapshot.parent.mkdir(parents=True,exist_ok=True);snapshot.write_bytes(data);mesh_proposal=json.loads(data)

    if a.seating_mode=='contact-path':
        f='docs/rl/contact_seating_plan.json';snapshot=a.output/'source_snapshot'/f
        data=(ROOT/f).read_bytes();snapshot.parent.mkdir(parents=True,exist_ok=True);snapshot.write_bytes(data);contact_path_plan=json.loads(data)

    def palm_pose():
        t=numpy(env.robot.root_view.get_link_transforms())[0,env.robot.body_names.index('right_rh_hand_base_link')]
        r=Rotation.from_quat(t[3:]).as_matrix()
        return t[:3]+r@PALM_OFFSET,r

    def step():
        global controls,last_save,max_robot_contact,transfer_streak
        if time.monotonic()-start>a.seconds:raise RuntimeError('Bounded experiment wall limit reached')
        if (a.output/'checkpoint_and_stop.request').exists():raise RuntimeError('Memory/manual safe stop requested')
        env.step(torch.zeros(1,13));controls+=1
        if env.last_unsafe:
            write('unsafe_detail.json',env.unsafe_detail)
            raise RuntimeError('Physical motion/contact safeguard stopped the attempt')
        sample=evidence.sample(record_friction=True)
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
            q_rad=env.robot.data.joint_pos.torch[0,env.ids].tolist(),
            command_q_rad=env.target[0,env.ids].tolist(),desired_q_rad=env.desired[0,env.ids].tolist(),palm_world_m=palm_pose()[0].tolist(),
            knife_pose_xyzw=env.knife.data.root_link_pose_w.torch[0].tolist())
        if a.in_place_tilt and initial_knife_pose is not None:
            sample['in_place_motion']=knife_motion(evidence.knife_points,initial_knife_pose,
                np.array(sample['knife_pose_xyzw']),evidence.board_lo,evidence.board_hi)
            if not sample['in_place_motion']['within_bounds']:
                write('motion_limit_event.json',sample)
                raise RuntimeError('Knife left bounded central footprint/3 cm translation/20 degree rotation limit')
        if phase=='contact_preserving_seating' and contact_reference is not None:
            transforms=numpy(env.robot.root_view.get_link_transforms())[0];errors=[];point_errors=[]
            for anchor in contact_reference['anchors']:
                body=transforms[env.robot.body_names.index(anchor['body'])]
                point=Rotation.from_quat(body[3:]).apply(anchor['point_local'])+body[:3]
                expected=contact_reference['rotation']@np.array(anchor['point_knife'])+contact_reference['pose'][:3]
                errors.append(float(np.linalg.norm(point-expected)));point_errors.append(expected-point)
            pose=np.array(sample['knife_pose_xyzw']);centroid=Rotation.from_quat(pose[3:]).apply(evidence.knife_points.mean(0))+pose[:3]
            drift=float(np.linalg.norm(centroid[:2]-contact_reference['centroid'][:2]))
            sample['contact_path_tracking']={'max_material_point_error_m':max(errors),'seating_lateral_drift_m':drift,'reference_error_vectors_m':[e.tolist() for e in point_errors]}
            if max(errors)>.003 or drift>.002:
                write('contact_path_tracking_stop.json',sample)
                raise RuntimeError('Contact-path material-point/knife drift stop')
            if contact_reference.get('feedback_enabled'):
                forces={f:sum(c['force_n'] for c in sample['contacts'] if c['part']==f and c['on_handle']) for f in ['thumb','index']}
                if all(v>.3 for v in forces.values()):
                    delta=anchor_translation_correction(point_errors);contact_reference['feedback_total']+=delta
                    if np.linalg.norm(contact_reference['feedback_total'])>.003:raise RuntimeError('Bounded contact feedback displacement exhausted')
                    if np.linalg.norm(delta)>0:
                        command_p,command_r=kin.pose(env.desired[0,env.ids[:7]].numpy())
                        q,error,angle=kin.solve(command_p+delta,command_r,env.desired[0,env.ids[:7]].numpy())
                        if error>.001 or angle>.01:raise RuntimeError('Contact feedback IK precision stop')
                        env.desired[0,env.ids[:7]]=torch.tensor(q,dtype=env.desired.dtype)
                    sample['contact_feedback_delta_m']=delta.tolist()
        q=env.robot.data.joint_pos.torch[0,env.ids[7:]];qd=env.robot.data.joint_vel.torch[0,env.ids[7:]]
        sample['estimated_hand_drive_torque_nm']=(3*(env.target[0,env.ids[7:]]-q)-.15*qd).tolist()
        if oracle is not None:sample['metric']=oracle.update(sample,.05)
        records.append(sample)
        if phase=='contact_preserving_seating':
            forces={f:sum(c['force_n'] for c in sample['contacts'] if c['part']==f and c['on_handle']) for f in ['thumb','index','middle','ring']}
            transfer_streak=transfer_streak+1 if all(v>.3 for v in forces.values()) else 0
            sample['contact_transfer']={'force_n':forces,'continuous_support_s':transfer_streak*.05}
            if transfer_streak==10:write('contact_transfer_ready.json',sample)
        if controls%10==0:write('progress.json',{'phase':phase,'controls':controls,'elapsed_wall_s':time.monotonic()-start,
                                               'handle_height_m':sample['handle_height_m'],'handle_in_palm_m':sample['handle_in_palm_m'],
                                               'motion':sample.get('in_place_motion'),'contacts':sample['contacts']})
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

    def move(target,orientation,feedback=None,settle_steps=10):
        origin,initial_rotation=palm_pose();distance=np.linalg.norm(target-origin)
        angle=Rotation.from_matrix(orientation@initial_rotation.T).magnitude()
        count=max(2,int(np.ceil(distance/.004)),int(np.ceil(angle/.025)))
        rotations=Slerp([0,1],Rotation.from_matrix([initial_rotation,orientation]))
        q=env.robot.data.joint_pos.torch[0,env.ids[:7]].numpy().copy()
        compensate=a.in_place_tilt and phase not in ['descent','approach']
        if compensate:
            q=env.target[0,env.ids[:7]].numpy().copy()
            command_position,command_rotation=kin.pose(q)
            if np.linalg.norm(command_position-origin)>.02:
                raise RuntimeError('Contact command tracking offset exceeds 2 cm')
        for alpha in np.linspace(0,1,count+1)[1:]:
            pos=origin+alpha*(target-origin);rot=rotations(alpha).as_matrix()
            if compensate:
                pos,rot=relative_command_pose(origin,initial_rotation,command_position,command_rotation,pos,rot)
            q,error,rotation_error=kin.solve(pos,rot,q)
            if error>.005 or rotation_error>.04:raise RuntimeError('IK route does not meet pose tolerance')
            env.desired[:,env.ids[:7]]=torch.from_numpy(q.astype(np.float32)).unsqueeze(0)
            wait_targets(100)
            if feedback is not None:feedback(records[-1])
        for _ in range(settle_steps):
            sample=step()
            if feedback is not None:feedback(sample)
        if np.linalg.norm(palm_pose()[0]-target)>.02:raise RuntimeError('Palm tracking error exceeds 2 cm')

    thumb_pitch_limit=.38 if a.seating_mode!='legacy' else np.deg2rad(32.5)
    pinch_monitor=None
    phase='settling'
    for _ in range(30):sample=step()
    initial_height=sample['handle_height_m'];oracle=GraspEvaluator(initial_height)
    initial_knife_pose=np.array(sample['knife_pose_xyzw'])
    handle_pose=env.knife.data.root_link_pose_w.torch[0].numpy();kr=Rotation.from_quat(handle_pose[3:]).as_matrix()
    handle=kr@evidence.centre+handle_pose[:3]
    orientation=np.array(candidate['hand_rotation_world'])
    target=handle-orientation@(np.array(candidate['handle_in_hand_m'])-PALM_OFFSET)
    phase='preshape_above_board'
    thumb_yaw=min(np.deg2rad(candidate['thumb_yaw_deg']),.87)
    set_hand(np.deg2rad(candidate['finger_deg']),thumb_yaw,0.)
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
    phase='finger_contact_feedback'
    for _ in range(120):
        sample=records[-1];supported=[]
        for i,finger in enumerate(['index','middle','ring','pinky']):
            force=sum(c['force_n'] for c in sample['contacts'] if c['part']==finger and c['on_handle'])
            if force>=1. and sample['estimated_hand_drive_torque_nm'][i+2]>.003:supported.append(finger)
            else:env.desired[0,env.ids[i+9]]=min(float(env.desired[0,env.ids[i+9]])+.004,np.deg2rad(85))
        if len(supported)>=2:break
        step()
    phase='fingers_then_thumb'
    env.desired[0,env.ids[7]]=thumb_yaw
    env.desired[0,env.ids[8]]=np.deg2rad(candidate['thumb_pitch_deg'])
    wait_targets()
    for _ in range(20):sample=step()
    # Increment only the thumb's independent drives until actual handle support appears.
    phase='thumb_contact_feedback'
    for _ in range(160):
        thumb_force=sum(c['force_n'] for c in sample['contacts'] if c['part']=='thumb' and c['on_handle'])
        if thumb_force>=3.:break
        current=float(env.desired[0,env.ids[8]])
        if current<thumb_pitch_limit:env.desired[0,env.ids[8]]=min(current+.003,thumb_pitch_limit)
        else:env.desired[0,env.ids[7]]=min(float(env.desired[0,env.ids[7]])+.001,.90)
        sample=step()
    write('before_lift.json',sample)
    support={c['part'] for c in sample['contacts'] if c['on_handle'] and c['force_n']>.05}
    loaded_fingers={finger for i,finger in enumerate(['index','middle','ring','pinky'])
                    if finger in support and sample['estimated_hand_drive_torque_nm'][i+2]>.003}
    # A temporary pinch can precede a fully curled wrap. Do not apply final curl criteria to that initial contact.
    thumb_normals=[np.array(c['normal_world']) for c in sample['contacts'] if c['part']=='thumb' and c['on_handle']]
    finger_normals=[np.array(c['normal_world']) for c in sample['contacts'] if c['part'] in loaded_fingers and c['on_handle']]
    pinch_opposed=any(float(t@f)<-.5 for t in thumb_normals for f in finger_normals)
    if 'thumb' not in support or not loaded_fingers or not pinch_opposed:
        raise RuntimeError('Opposed physical finger/handle support absent; lift refused')
    phase='pinch_force_feedback'
    finger_preload=2. if a.in_place_tilt else 3.
    thumb_preload=3. if a.in_place_tilt else 4.
    for _ in range(80):
        all_loaded=True
        for finger in loaded_fingers:
            i=['index','middle','ring','pinky'].index(finger)
            force=sum(c['force_n'] for c in sample['contacts'] if c['part']==finger and c['on_handle'])
            if force<finger_preload:
                env.desired[0,env.ids[i+9]]=min(float(env.desired[0,env.ids[i+9]])+.002,np.deg2rad(85));all_loaded=False
        thumb_force=sum(c['force_n'] for c in sample['contacts'] if c['part']=='thumb' and c['on_handle'])
        if thumb_force<thumb_preload:
            env.desired[0,env.ids[8]]=min(float(env.desired[0,env.ids[8]])+.002,thumb_pitch_limit);all_loaded=False
        if all_loaded:break
        sample=step()
    write('provisional_pinch.json',{'support_parts':sorted(support),'final_grasp_accepted':False,
                                  'note':'An initial opposed pinch may provide clearance; final palm/three-finger criteria remain mandatory'})
    write('before_lift.json',sample)
    def maintain_pinch(sample):
        if pinch_monitor is not None:pinch_monitor.update(sample)
        for finger in loaded_fingers:
            i=['index','middle','ring','pinky'].index(finger)
            force=sum(c['force_n'] for c in sample['contacts'] if c['part']==finger and c['on_handle'])
            if force<finger_preload:
                env.desired[0,env.ids[i+9]]=min(float(env.desired[0,env.ids[i+9]])+.002,np.deg2rad(85))
        force=sum(c['force_n'] for c in sample['contacts'] if c['part']=='thumb' and c['on_handle'])
        if force<thumb_preload:env.desired[0,env.ids[8]]=min(float(env.desired[0,env.ids[8]])+.002,thumb_pitch_limit)

    if a.in_place_tilt:
        phase='tilt_hand_clearance_3mm'
        palm,rotation=palm_pose()
        move(palm+np.array([0.,0.,.003]),rotation,maintain_pinch)
        phase='supported_in_place_tilt'
        if a.seating_mode!='legacy':pinch_monitor=SupportedPinchMonitor()
        palm,rotation=palm_pose()
        pose=env.knife.data.root_link_pose_w.torch[0].numpy().copy()
        roll={'pitch':0.,'roll-positive':12.,'roll-negative':-12.}[a.in_place_tilt]
        for next_target,next_rotation in tilt_path(palm,rotation,pose,evidence.centre,evidence.blade,roll,tip_pivot=a.seating_mode=='coordinated'):
            move(next_target,next_rotation,maintain_pinch)
            clearance_goal=.035 if a.seating_mode=='coordinated' else .010
            if records[-1]['handle_height_m']-initial_height>=clearance_goal:break
        sample=records[-1]
        write('after_tilt.json',sample)
        minimum_clearance=.030 if a.seating_mode=='coordinated' else .008
        if sample['handle_height_m']-initial_height<minimum_clearance:
            raise RuntimeError(f'Knife handle did not reach {minimum_clearance*1000:.0f} mm supported clearance; seating/lift refused')
        if a.seating_mode in ['adaptive','mesh-guided','contact-path']:
            phase='adaptive_supported_clearance'
            pose=np.array(records[-1]['knife_pose_xyzw']);kr=Rotation.from_quat(pose[3:]).as_matrix()
            _,hand_r=palm_pose();hand_in_knife=kr.T@hand_r
            centre_in_hand=np.array(records[-1]['handle_in_palm_m'])
            for _ in range(30):
                sample=records[-1]
                if sample['handle_height_m']-initial_height>=.035:break
                pose=np.array(sample['knife_pose_xyzw']);kr=Rotation.from_quat(pose[3:]).as_matrix()
                handle=kr@evidence.centre+pose[:3]
                tip=evidence.blade[evidence.blade[:,0].argmin()]
                pivot=kr@tip+pose[:3];pivot[2]=evidence.board_hi[2]
                axis=np.cross(handle-pivot,[0.,0.,1.]);axis/=np.linalg.norm(axis)
                delta=Rotation.from_rotvec(axis*np.deg2rad(.4)).as_matrix()
                orientation=delta@kr@hand_in_knife
                next_handle=pivot+delta@(handle-pivot)
                target=next_handle-orientation@(centre_in_hand-PALM_OFFSET)
                move(target,orientation,maintain_pinch,settle_steps=2)
            write('after_adaptive_clearance.json',records[-1])
            if records[-1]['handle_height_m']-initial_height<.030:
                raise RuntimeError('Adaptive supported clearance remained below 30 mm; palm seating refused')
        if a.seating_mode!='legacy':
            audit=check_hand_frames(env,kin);write('hand_frame_audit.json',audit)
            if audit['max_position_error_m']>.001 or audit['max_angle_error_rad']>.02:
                raise RuntimeError('Native hand frames do not match geometric model; seating refused')
            phase='coordinated_palm_seating'
            missing_support=[0]
            def seat_feedback(sample):
                parts={c['part'] for c in sample['contacts'] if c['on_handle'] and c['force_n']>.2}
                missing_support[0]=0 if 'thumb' in parts and any(f in parts for f in ['index','middle','ring','pinky']) else missing_support[0]+1
                if missing_support[0]>=3 or sample['handle_height_m']-initial_height<.006:
                    raise RuntimeError('Supported clearance/opposed pinch lost during seating; motion stopped early')
                goals=env.desired[0,env.ids[7:]].numpy()
                updated=seating_hand_goals(sample,goals)
                env.desired[0,env.ids[7:]]=torch.tensor(updated,dtype=env.desired.dtype)
            seating_start,orientation=palm_pose()
            if a.seating_mode=='contact-path':
                path=contact_path_plan;waypoints=validated_waypoints(path)
                if 'preshape_joint_rad' in path:
                    phase='contact_path_preshape'
                    for part in path.get('preshape_parts',['pinky']):
                        index=['thumb_yaw','thumb_pitch','index','middle','ring','pinky'].index(part)
                        env.desired[0,env.ids[7+index]]=float(path['preshape_joint_rad'][index])
                    wait_targets(100)
                    for _ in range(8):step()
                reference_pose=np.array(records[-1]['knife_pose_xyzw']);reference_rotation=Rotation.from_quat(reference_pose[3:]).as_matrix()
                contact_reference={'pose':reference_pose,'rotation':reference_rotation,'anchors':path['reference_anchors'],
                    'centroid':reference_rotation@evidence.knife_points.mean(0)+reference_pose[:3],
                    'feedback_enabled':path.get('anchor_translation_feedback',False),'feedback_total':np.zeros(3)}
                initial_joints=env.robot.data.joint_pos.torch[0,env.ids[7:]].numpy().copy()
                preload=env.desired[0,env.ids[7:]].numpy().copy()-initial_joints;correction=np.zeros(6)
                phase='contact_preserving_seating'
                if path.get('rolling_contact'):
                    from plan_contact_seating import HandGeometry
                    model=HandGeometry(env.sim.stage);parts=['index','middle','ring','pinky']
                    goal=path['target'];original=path['reference_sample']
                    goal_r=Rotation.from_quat(original['knife_pose_xyzw'][3:]).as_matrix().T@np.array(goal['hand_rotation_world'])
                    goal_t=evidence.centre-goal_r@np.array(goal['handle_in_hand_m']);initial_distance=None
                    for roll_index in range(400):
                        sample=records[-1];pose=np.array(sample['knife_pose_xyzw']);kr=Rotation.from_quat(pose[3:]).as_matrix()
                        transforms=numpy(env.robot.root_view.get_link_transforms())[0]
                        root_pose=transforms[env.robot.body_names.index('right_rh_hand_base_link')]
                        root_r=Rotation.from_quat(root_pose[3:]).as_matrix();r=kr.T@root_r;t=kr.T@(root_pose[:3]-pose[:3])
                        handq=np.array(sample['q_rad'][7:]);links=model.transforms(handq);anchors=[]
                        forces={f:sum(c['force_n'] for c in sample['contacts'] if c['part']==f and c['on_handle']) for f in ['thumb',*parts]}
                        if forces['thumb']<.3 or max(forces[f] for f in parts)<.3:raise RuntimeError('Rolling contact lost opposed support')
                        for part in ['thumb',*parts]:
                            available=[c for c in sample['contacts'] if c['part']==part and c['on_handle'] and c['force_n']>.3]
                            if not available:continue
                            c=max(available,key=lambda c:c['force_n']);body=transforms[env.robot.body_names.index(c['body'])]
                            br=Rotation.from_quat(body[3:]).as_matrix();local=br.T@(np.array(c['point_world_m'])-body[:3])
                            anchors.append({'body':c['body'],'point_local':local.tolist(),'point_knife':(kr.T@(np.array(c['point_world_m'])-pose[:3])).tolist()})
                        def points(dt,omega,dq):
                            rr=Rotation.from_rotvec(omega).as_matrix()@r;tr=model.transforms(handq+dq)
                            return np.concatenate([t+dt+rr@(tr[c['body']][:3,:3]@np.array(c['point_local'])+tr[c['body']][:3,3]) for c in anchors])
                        zero=np.zeros(12);base=points(zero[:3],zero[3:6],zero[6:]);jac=[]
                        for j in range(12):
                            z=zero.copy();eps=1e-5 if j<3 else 1e-4;z[j]=eps
                            jac.append((points(z[:3],z[3:6],z[6:])-base)/eps)
                        jac=np.array(jac).T;distance=np.linalg.norm(goal_t-t)
                        if initial_distance is None:initial_distance=max(distance,.001)
                        fraction=float(np.clip(1-distance/initial_distance,0,1))
                        qgoal=np.deg2rad([goal['thumb_yaw_deg'],goal['thumb_pitch_deg'],70,52.5+17.5*np.clip((fraction-.3)/.7,0,1),70,85])
                        desired=np.r_[goal_t-t,Rotation.from_matrix(goal_r@r.T).as_rotvec(),qgoal-handq]
                        delta=project_contact_motion(jac,desired,[.00015]*3+[.001]*3+[.001]*6)
                        nextq=handq+delta[6:]
                        if np.any(nextq<0) or np.any(nextq>np.array([.90,.315,*[np.deg2rad(85)]*4])):raise RuntimeError('Rolling candidate hand posture limit')
                        nr=Rotation.from_rotvec(delta[3:6]).as_matrix()@r;nt=t+delta[:3]
                        # Predict only supporting-surface clearance; force/blade/self-contact guards remain authoritative.
                        next_links=model.transforms(nextq)
                        bottom=min(float(((v@(nr@next_links[name][:3,:3]).T+nt+nr@next_links[name][:3,3])@reference_rotation.T+reference_pose[:3])[:,2].min()) for name,(v,eq) in model.meshes.items())
                        if bottom<evidence.board_hi[2]+.002:raise RuntimeError('Rolling candidate supporting-surface clearance stop')
                        orientation=reference_rotation@nr;target=reference_rotation@(nt+nr@PALM_OFFSET)+reference_pose[:3]
                        actual_p,actual_r=palm_pose();command_p,command_r=kin.pose(env.target[0,env.ids[:7]].numpy())
                        solve_p,solve_r=relative_command_pose(actual_p,actual_r,command_p,command_r,target,orientation)
                        arm,error,angle=kin.solve(solve_p,solve_r,env.target[0,env.ids[:7]].numpy())
                        if error>.001 or angle>.01:raise RuntimeError('Rolling arm IK precision stop')
                        held=env.target[0,env.ids[7:]].numpy()-handq
                        commanded=balanced_contact_goals(sample,nextq+held,nextq+held,3.)
                        commanded=np.clip(commanded,0,[.90,.38,*[np.deg2rad(85)]*4])
                        env.desired[0,env.ids[:7]]=torch.tensor(arm,dtype=env.desired.dtype)
                        env.desired[0,env.ids[7:]]=torch.tensor(commanded,dtype=env.desired.dtype)
                        contact_reference['anchors']=anchors;contact_reference['feedback_enabled']=False
                        step();pinch_monitor.update(records[-1])
                        if roll_index%10==0:write('rolling_progress.json',{'iteration':roll_index,'fraction':fraction,'goal_distance_m':float(distance),'sample':records[-1],'linear_contact_velocity_residual_m':float(np.linalg.norm(jac@delta))})
                        contacts={c['part'] for c in records[-1]['contacts'] if c['on_handle'] and c['force_n']>.1}
                        if 'palm' in contacts and 'thumb' in contacts and len(contacts.intersection(parts))>=3:break
                else:
                    for waypoint in waypoints[1:]:
                        relative_r=np.array(waypoint['hand_rotation_in_knife']);orientation=reference_rotation@relative_r
                        target=reference_rotation@(np.array(waypoint['hand_root_in_knife_m'])+relative_r@PALM_OFFSET)+reference_pose[:3]
                        actual_p,actual_r=palm_pose();command_p,command_r=kin.pose(env.target[0,env.ids[:7]].numpy())
                        solve_p,solve_r=relative_command_pose(actual_p,actual_r,command_p,command_r,target,orientation)
                        q,error,angle=kin.solve(solve_p,solve_r,env.target[0,env.ids[:7]].numpy())
                        if error>.005 or angle>.04:raise RuntimeError('Contact-preserving arm IK route failed')
                        write('current_contact_waypoint.json',waypoint)
                        nominal=np.array(waypoint['joint_rad']);commanded=np.clip(nominal+preload+correction,0,[.90,.38,*[np.deg2rad(85)]*4])
                        env.desired[0,env.ids[:7]]=torch.tensor(q,dtype=env.desired.dtype)
                        env.desired[0,env.ids[7:]]=torch.tensor(commanded,dtype=env.desired.dtype)
                        wait_targets(240)
                        for _ in range(6):
                            sample=step();pinch_monitor.update(sample)
                            updated=balanced_contact_goals(sample,env.desired[0,env.ids[7:]].numpy(),nominal+preload,path.get('index_force_target_n',2.))
                            for part in path.get('preshape_parts',['pinky']):
                                index=['thumb_yaw','thumb_pitch','index','middle','ring','pinky'].index(part)
                                updated[index]=nominal[index]+preload[index]
                            env.desired[0,env.ids[7:]]=torch.tensor(updated,dtype=env.desired.dtype)
                        correction=np.clip(env.desired[0,env.ids[7:]].numpy()-nominal-preload,-.08,.08)
                        write('seating_progress.json',{'fraction':waypoint['fraction'],'waypoint':waypoint,'sample':records[-1],
                            'offline_path_status':path['status']})
            elif a.seating_mode=='mesh-guided':
                proposal=mesh_proposal
                goal=proposal['candidates'][0]
                if not goal['predicted_simultaneous_contacts']:
                    raise RuntimeError('No geometrically valid near-contact proposal; guided seating refused')
                reference_kr=Rotation.from_quat(proposal['supported_sample']['knife_pose_xyzw'][3:]).as_matrix()
                final_relative=reference_kr.T@np.array(goal['hand_rotation_world'])
                pose=np.array(records[-1]['knife_pose_xyzw']);kr=Rotation.from_quat(pose[3:]).as_matrix()
                initial_relative=kr.T@orientation
                relative_path=Slerp([0.,1.],Rotation.from_matrix([initial_relative,final_relative]))
                initial_centre=np.array(records[-1]['handle_in_palm_m']);final_centre=np.array(goal['handle_in_hand_m'])
                initial_joints=env.robot.data.joint_pos.torch[0,env.ids[7:]].numpy().copy()
                final_joints=np.deg2rad([goal['thumb_yaw_deg'],goal['thumb_pitch_deg'],*[goal['finger_degrees'][f] for f in ['index','middle','ring','pinky']]])
                preload=env.desired[0,env.ids[7:]].numpy().copy()-initial_joints
                correction=np.zeros(6)
                phase='mesh_guided_palm_seating'
                for fraction in np.linspace(0,1,81)[1:]:
                    sample=records[-1];pose=np.array(sample['knife_pose_xyzw']);kr=Rotation.from_quat(pose[3:]).as_matrix()
                    orientation=kr@relative_path(float(fraction)).as_matrix()
                    relative_centre=initial_centre+fraction*(final_centre-initial_centre)
                    handle=kr@evidence.centre+pose[:3]
                    target=handle-orientation@(relative_centre-PALM_OFFSET)
                    nominal=initial_joints+fraction*(final_joints-initial_joints)
                    commanded=nominal+preload+correction
                    commanded=np.clip(commanded,0.,[.90,thumb_pitch_limit,*[np.deg2rad(85)]*4])
                    env.desired[0,env.ids[7:]]=torch.tensor(commanded,dtype=env.desired.dtype)
                    move(target,orientation,seat_feedback,settle_steps=2)
                    correction=np.clip(env.desired[0,env.ids[7:]].numpy()-nominal-preload,-.08,.08)
                    write('seating_progress.json',{'fraction':float(fraction),'proposal':goal,'sample':records[-1]})
            else:
                for seat_index in range(140):
                    sample=records[-1]
                    parts={c['part'] for c in sample['contacts'] if c['on_handle'] and c['force_n']>.1}
                    if 'palm' in parts and 'thumb' in parts and len(parts.intersection(['index','middle','ring','pinky']))>=3:break
                    # Correct measured whole-object lateral drift with the hand, without commanding the knife.
                    pose=np.array(sample['knife_pose_xyzw'])
                    centroid=Rotation.from_quat(pose[3:]).apply(evidence.knife_points.mean(0))+pose[:3]
                    initial_centroid=Rotation.from_quat(initial_knife_pose[3:]).apply(evidence.knife_points.mean(0))+initial_knife_pose[:3]
                    drift=centroid[:2]-initial_centroid[:2]
                    # Rolling the loaded pads toward the proximal links requires coordinated curl,
                    # rather than holding the initial fingertip angles while the palm descends.
                    for i,finger in enumerate(['index','middle','ring','pinky']):
                        if finger in parts:
                            env.desired[0,env.ids[i+9]]=min(float(env.desired[0,env.ids[i+9]])+.009,np.deg2rad(85))
                    seat_feedback(sample)
                    current,_=palm_pose()
                    # Descend vertically rather than dragging the knife toward a fixed stale pose.
                    target=current+np.array([0.,0.,-.0005])
                    if np.linalg.norm(drift)>.020:target[:2]-=.00025*drift/np.linalg.norm(drift)
                    move(target,orientation,seat_feedback,settle_steps=2)
                    write('seating_progress.json',{'iteration':seat_index,'descent_m':float(seating_start[2]-palm_pose()[0][2]),
                        'sample':records[-1]})
            write('after_seating.json',records[-1])
            parts={c['part'] for c in records[-1]['contacts'] if c['on_handle'] and c['force_n']>.1}
            if 'palm' not in parts or len(parts.intersection(['index','middle','ring','pinky']))<3:
                raise RuntimeError('Coordinated seating did not establish palm/three-finger contact; lift refused')
            target=palm_pose()[0]
        else:
            phase='early_wrap_after_tilt'
            for _ in range(100):
                sample=records[-1];loaded=[]
                for i,finger in enumerate(['index','middle','ring','pinky']):
                    force=sum(c['force_n'] for c in sample['contacts'] if c['part']==finger and c['on_handle'])
                    if force>.5 and sample['estimated_hand_drive_torque_nm'][i+2]>.003:loaded.append(finger)
                    elif finger not in loaded_fingers:
                        env.desired[0,env.ids[i+9]]=min(float(env.desired[0,env.ids[i+9]])+.004,np.deg2rad(85))
                if len(loaded)>=3:break
                maintain_pinch(sample);step()
            # A partial seating move may lower the hand by at most 3 mm at this small clearance.
            phase='seat_handle_after_tilt'
            pose=np.array(sample['knife_pose_xyzw']);handle=Rotation.from_quat(pose[3:]).apply(evidence.centre)+pose[:3]
            _,orientation=palm_pose()
            seated=np.array(candidate['handle_in_hand_m']).copy();seated[0]-=.015;seated[2]-=.015
            target=handle-orientation@(seated-PALM_OFFSET)
            current=palm_pose()[0];delta=target-current
            if delta[2]<-.003:target=current+delta*(.003/-delta[2])
            move(target,orientation,maintain_pinch)
        phase='clearance_lift_after_tilt'
        move(target+np.array([0,0,.015]),orientation,maintain_pinch)
        target=palm_pose()[0]-np.array([0,0,.035])
    else:
        phase='clearance_lift'
        move(target+np.array([0,0,.035]),orientation)
    sample=records[-1]
    if sample['dropped'] or sample['handle_height_m']-initial_height<.015:
        raise RuntimeError('Knife did not follow the physical clearance lift; wrap/lift refused')
    phase='complete_wrap'
    if a.seating_mode not in ['mesh-guided','contact-path']:
        set_hand(np.deg2rad(85),float(env.desired[0,env.ids[7]]),float(env.desired[0,env.ids[8]]))
    phase='lift'
    move(target+np.array([0,0,.075]),orientation)
    phase='hold'
    for _ in range(80):
        sample=step();metric=sample['metric']
        if sample['dropped']:raise RuntimeError('Knife dropped during hold')
        if a.seating_mode=='mesh-guided':seat_feedback(sample)
        if metric['success']:passed=True;break
    write('grasp_metric.json',metric)
    write('result.json',{'passed':passed,'training':False,'initial_handle_height_m':initial_height,
        'final_handle_height_m':sample['handle_height_m'],'lift_m':sample['handle_height_m']-initial_height,
        'metric':metric,'max_robot_contact_n':max_robot_contact,'controls':controls,'phase':phase,
        'initial_reset':reset,'knife_teleports_during_episode':0,'attachment_created':False})
except BaseException:
    error=traceback.format_exc()
    write('failure.json',{'phase':phase,'traceback':error,'training':False,
        'last_sample':records[-1] if records else None,'substep_event':getattr(env,'substep_event',None)})
    write('result.json',{'passed':False,'phase':phase,'training':False,'reason':error.strip().splitlines()[-1],
                        'controls':len(records),'knife_teleports_during_episode':0,'attachment_created':False})
    traceback.print_exc()
finally:
    try:
        write('trajectory.json',records)
        if env is not None and hasattr(env,'seating_trace'):write('seating_substeps.json',list(env.seating_trace))
    finally:
        try:
            if env is not None:env.close()
        finally:
            if app is not None:app.close()
