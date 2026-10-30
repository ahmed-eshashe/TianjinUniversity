"""Guarded native knife-only settling fixture; whole-robot self-collision is a separate gate."""
import argparse
import json
from pathlib import Path
import time
import traceback

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--seconds',type=int,required=True)
a=p.parse_args()

def write(name,data):
    t=a.output/(name+'.tmp');t.write_text(json.dumps(data,indent=2));t.replace(a.output/name)

app=None
try:
    from isaaclab.app import AppLauncher
    app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
    import numpy as np
    import torch
    from pxr import UsdGeom
    from scipy.spatial.transform import Rotation
    from isaaclab.envs import DirectRLEnv
    from isaaclab.assets import RigidObject,RigidObjectCfg
    from isaaclab_physx.physics import PhysxManager
    from native_env import NativeValidationCfg
    from native_contacts import numpy
    from reset_sampler import FlatResetSampler
    from grasp_metrics import GraspEvaluator

    class KnifeFixture(DirectRLEnv):
        def __init__(self,cfg):
            self.meta=json.loads((ROOT/'rl/scene/manifest.json').read_text())
            self.results=[];self.count=0
            super().__init__(cfg)
            self.sampler=FlatResetSampler(self.points,self.meta['board_world_bounds'])
            centre=np.mean(self.meta['board_world_bounds'],axis=0)[:2]
            centre_cases=[self.sampler.at(centre,yaw) for yaw in np.linspace(-np.pi,np.pi,16,endpoint=False)]
            self.cases=[x for x in centre_cases if x['valid']]+self.sampler.sample(24)
            from isaaclab.app.settings_manager import get_settings_manager
            get_settings_manager().set_bool('/physics/disableContactProcessing',False)
            self.cv=PhysxManager.get_physics_sim_view().create_rigid_contact_view(
                [self.meta['knife_path']],filter_patterns=[[self.meta['board_path'],self.meta['counter_path']]],max_contact_data_count=128)
        def _setup_scene(self):
            self.sim.stage.GetRootLayer().subLayerPaths.append(str(ROOT/'rl/scene/phase3.usda'))
            # Explicitly isolated fixture; never reported as a full robot collision pass.
            self.sim.stage.GetPrimAtPath('/dual_ar5_o6').SetActive(False)
            self.points=np.array(UsdGeom.Mesh(self.sim.stage.GetPrimAtPath(self.meta['knife_path'])).GetPointsAttr().Get())
            self.knife=RigidObject(RigidObjectCfg(prim_path=self.meta['knife_path'],spawn=None))
            self.scene.rigid_objects['knife']=self.knife
        def _pre_physics_step(self,actions):pass
        def _apply_action(self):pass
        def _get_observations(self):
            return {'policy':torch.cat([self.knife.data.root_link_pose_w.torch,self.knife.data.root_link_vel_w.torch],dim=-1)}
        def _get_rewards(self):return torch.zeros(1,device=self.device)
        def _get_dones(self):
            return torch.zeros(1,dtype=torch.bool,device=self.device),self.episode_length_buf>=self.max_episode_length-1
        def _reset_idx(self,ids):
            super()._reset_idx(ids)
            self.case=self.cases[self.count%len(self.cases)]
            self.knife.write_root_pose_to_sim_index(root_pose=torch.tensor([self.case['pose_xyzw']],dtype=torch.float32),env_ids=ids)
            self.knife.write_root_velocity_to_sim_index(root_velocity=torch.zeros(1,6),env_ids=ids)
            self.count+=1

    cfg=NativeValidationCfg();cfg.action_space=1;cfg.observation_space=13;cfg.episode_length_s=2.
    env=KnifeFixture(cfg);env.reset()
    start=time.monotonic();steps=0;settled=[];sampled_episodes=set();last_checkpoint=start
    while time.monotonic()-start<a.seconds and len(settled)<len(env.cases):
        if (a.output/'checkpoint_and_stop.request').exists():break
        # Capture immediately BEFORE step's automatic reset of a completed episode.
        if int(env.episode_length_buf[0])==36 and env.count not in sampled_episodes:
            pose=env.knife.data.root_link_pose_w.torch[0].numpy().copy()
            vel=env.knife.data.root_link_vel_w.torch[0].numpy().copy()
            world=env.points@Rotation.from_quat(pose[3:]).as_matrix().T+pose[:3]
            lo,hi=np.array(env.meta['board_world_bounds'])
            force=numpy(env.cv.get_contact_force_matrix(dt=1/240))
            board_force=float(np.linalg.norm(force[0,0]));counter_force=float(np.linalg.norm(force[0,1]))
            gap=float(world[:,2].min()-hi[2])
            fully_inside=bool(np.all(world.min(0)[:2]>=lo[:2]+.015) and np.all(world.max(0)[:2]<=hi[:2]-.015))
            passed=bool(np.linalg.norm(vel[:3])<.01 and np.linalg.norm(vel[3:])<.1 and abs(gap)<.003 and fully_inside and 1.5<board_force<3.5 and counter_force<.05)
            settled.append({'case':env.case,'pose_xyzw':pose.tolist(),'velocity':vel.tolist(),'board_force_n':board_force,
                'counter_force_n':counter_force,'bottom_gap_m':gap,'fully_inside_board':fully_inside,'passed':passed})
            sampled_episodes.add(env.count)
            write('settled_cases.json',settled)
        env.step(torch.zeros(1,1));steps+=1
        if time.monotonic()-last_checkpoint>15:
            write('validation_checkpoint.json',{'completed_cases':settled,'training':False,'resume':'fresh reset'})
            last_checkpoint=time.monotonic()
    write('result.json',{'passed':len(settled)==len(env.cases) and all(x['passed'] for x in settled),
        'native_class':'DirectRLEnv','scope':'Knife-only fixture; robot inactive; NOT whole-task or grasp acceptance',
        'steps':steps,'elapsed_s':time.monotonic()-start,'settled_cases':len(settled),'requested_cases':len(env.cases),
        'all_settled':all(x['passed'] for x in settled),'training':False,'self_collision_gate':'separate and unresolved'})
    write('runtime_dynamics.json',{'mass_kg':numpy(env.knife.root_view.get_masses()).tolist(),
                                 'com_pose':numpy(env.knife.root_view.get_coms()).tolist(),
                                 'inertia':numpy(env.knife.root_view.get_inertias()).tolist()})
    env.close()
except BaseException:
    write('failure.json',{'traceback':traceback.format_exc()});traceback.print_exc()
finally:
    if app is not None:app.close()
