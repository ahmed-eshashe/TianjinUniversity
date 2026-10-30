"""Watchdog-launched native DirectRLEnv/RSL adapter smoke test; never trains."""
import argparse
import hashlib
import json
from pathlib import Path
import time
import traceback

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--output', type=Path, required=True)
p.add_argument('--seconds', type=int, required=True)
p.add_argument('--phase3', action='store_true')
p.add_argument('--camera', action='store_true')
p.add_argument('--hand-cycle',action='store_true')
a = p.parse_args()
if a.camera:
    p.error('This native physical validation does not enable a camera; Phase 2 camera evidence is separate.')

def write(name, data):
    temp = a.output / (name+'.tmp')
    temp.write_text(json.dumps(data,indent=2))
    temp.replace(a.output/name)

app = None
try:
    root=Path(__file__).resolve().parents[1]
    paths=['rl/native_probe.py','rl/native_env.py','rl/native_contacts.py','rl/contact_evaluator.py','rl/grasp_metrics.py','rl/reset_sampler.py',
           'rl/scene/phase3.usda' if a.phase3 else 'rl/scene/minimal_benchmark.usda']
    write('run_configuration.json',{'phase3':a.phase3,'hand_cycle':a.hand_cycle,'training':False,'camera':False,
        'physics_hz':240,'action_hz':20,'env_count':1,'source_sha256':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths}})
    from isaaclab.app import AppLauncher
    launcher = AppLauncher(headless=True, device='cpu', visualizer=['none'])
    app = launcher.app
    import torch
    from native_env import NativeValidationCfg, NativeValidationEnv
    from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper
    cfg=NativeValidationCfg()
    if a.hand_cycle:cfg.episode_length_s=12.
    env = NativeValidationEnv(cfg, phase3=a.phase3)
    env.hand_cycle=a.hand_cycle
    if a.phase3:
        from native_contacts import NativeContactMonitor
        env.contact_monitor = NativeContactMonitor(env)
        from contact_evaluator import ContactEvidence
        from grasp_metrics import GraspEvaluator
        evidence=ContactEvidence(env)
    wrapper = RslRlVecEnvWrapper(env)
    start = time.monotonic(); steps = 0; max_speed = 0.; max_left = 0.; max_mimic = 0.
    real_oracle_samples=0; real_oracle_successes=0; oracle_reset=-1; actual_examples=[]
    max_hand=torch.zeros(6)
    finger_started=None;thumb_started=None
    while time.monotonic()-start < a.seconds:
        if (a.output/'checkpoint_and_stop.request').exists():
            write('validation_checkpoint.json', {'steps':steps,'resets':env.reset_count,'training':False,
                                                'resume':'restart physical validation from a fresh reset'})
            break
        with torch.inference_mode():
            obs,reward,done,extras = wrapper.step(torch.full((1,13), .1*__import__('math').sin(steps*.03)))
        assert obs['policy'].shape == (1,39) and torch.isfinite(obs['policy']).all()
        assert reward.shape == (1,) and done.shape == (1,)
        if env.last_unsafe:
            write('unsafe_detail.json',env.unsafe_detail)
            raise RuntimeError('Native safety check terminated an episode; see unsafe_detail.json')
        if a.phase3 and int(env.episode_length_buf[0])>=10:
            sample=evidence.sample()
            if oracle_reset!=env.reset_count:
                oracle=GraspEvaluator(sample['handle_height_m']);oracle_reset=env.reset_count
                actual_examples.append({'reset':env.reset_count,'sample':sample,'kind':'physical board-supported negative example'})
            metric=oracle.update(sample,.05)
            real_oracle_samples+=1;real_oracle_successes+=int(metric['success'])
            if metric['success']:raise RuntimeError('Oracle falsely accepted a knife still on the board')
        max_hand=torch.maximum(max_hand,env.robot.data.joint_pos.torch[0,env.ids[7:]].cpu())
        hand_now=env.robot.data.joint_pos.torch[0,env.ids[7:]].cpu()
        if finger_started is None and bool(torch.all(hand_now[2:]>.1)):finger_started=steps
        if thumb_started is None and hand_now[1]>.1:thumb_started=steps
        max_speed=max(max_speed,float(env.robot.data.joint_vel.torch.abs().max()))
        max_left=max(max_left,float((env.robot.data.joint_pos.torch[:,env.left_ids]-env.home[:,env.left_ids]).abs().max()))
        for name in ['index','middle','ring','pinky','thumb']:
            master='right_rh_'+(name+'_mcp_pitch' if name!='thumb' else 'thumb_cmc_pitch')
            follower='right_rh_'+(name+'_dip' if name!='thumb' else 'thumb_ip')
            q=env.robot.data.joint_pos.torch[0];names=env.robot.joint_names
            max_mimic=max(max_mimic,float(abs(q[names.index(follower)]-(1.86 if name=='thumb' else .89)*q[names.index(master)])))
        steps+=1
        if steps%20==0:
            write('progress.json',{'steps':steps,'resets':env.reset_count,'elapsed_s':time.monotonic()-start})
    hand_pass=not a.hand_cycle or bool(torch.all(max_hand[2:]>1.) and max_hand[0]>.5 and max_hand[1]>.25 and
        finger_started is not None and thumb_started is not None and finger_started<thumb_started)
    result={'passed':steps>=20 and env.reset_count>=2 and max_mimic<.02 and hand_pass and not (a.output/'checkpoint_and_stop.request').exists(),
            'native_class':type(env).__mro__[1].__module__+'.'+type(env).__mro__[1].__name__,
            'adapter':type(wrapper).__name__,'physics_backend':env.robot.__backend_name__,
            'steps':steps,'resets':env.reset_count,'elapsed_s':time.monotonic()-start,'max_speed_rad_s':max_speed,
            'max_left_drift_rad':max_left,'joint_count':len(env.robot.joint_names),'training':False,
            'max_mimic_residual_rad':max_mimic,
            'empty_hand_cycle':a.hand_cycle,'empty_hand_cycle_passed':hand_pass if a.hand_cycle else None,
            'max_hand_joint_positions_rad':max_hand.tolist(),
            'empty_hand_first_finger_motion_step':finger_started,'empty_hand_first_thumb_flexion_step':thumb_started,
            'physical_negative_oracle_samples':real_oracle_samples,'physical_negative_false_successes':real_oracle_successes,
            'phase3':a.phase3,'limitations':['Joint-interface validation only; not a learned pickup or complete Phase 3 acceptance']}
    write('result.json',result)
    if a.phase3:write('physical_negative_examples.json',actual_examples)
    wrapper.close()
except BaseException:
    write('failure.json',{'traceback':traceback.format_exc(),'training':False})
    traceback.print_exc()
finally:
    if app is not None:
        app.close()
