"""One-environment native Isaac Lab validation task. No optimizer or training runner."""
import json
from pathlib import Path

import numpy as np
import torch
from scipy.spatial.transform import Rotation
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import Articulation, ArticulationCfg, RigidObject, RigidObjectCfg
from isaaclab.envs import DirectRLEnv, DirectRLEnvCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sim import SimulationCfg
from isaaclab.utils import configclass
from isaaclab_physx.physics import PhysxCfg

ROOT = Path(__file__).resolve().parents[1]


@configclass
class NativeValidationCfg(DirectRLEnvCfg):
    seed = 731
    decimation = 12
    episode_length_s = 4.0
    action_space = 13
    observation_space = 39
    state_space = 0
    sim = SimulationCfg(device='cpu', dt=1/240, render_interval=12, physics=PhysxCfg(),
                        use_fabric=False, use_newton_actuators=False)
    scene = InteractiveSceneCfg(num_envs=1, env_spacing=4., replicate_physics=False)


class NativeValidationEnv(DirectRLEnv):
    """Bounded joint interface probe, deliberately distinct from the future 12-D pickup task."""

    def __init__(self, cfg, phase3=False):
        self.phase3 = phase3
        self.manifest = json.loads((ROOT / 'rl/scene/manifest.json').read_text())
        if phase3:
            self.manifest['home_rad']=json.loads((ROOT/'docs/rl/phase3_physics.json').read_text())['home_rad']
        self.reset_count = 0
        self.rng = np.random.default_rng(731)
        super().__init__(cfg)
        names = self.robot.joint_names
        audit = json.loads((ROOT / 'docs/rl/phase1_inventory.json').read_text())
        self.independent_names = audit['right_arm_independent'] + audit['right_hand_independent']
        self.ids = [names.index(n) for n in self.independent_names]
        self.left_ids = [i for i,n in enumerate(names) if n.startswith('left_')]
        self.home = torch.tensor([[self.manifest['home_rad'][n] for n in names]], device=self.device)
        self.target = self.home.clone()
        self.previous = torch.zeros((1,13), device=self.device)
        self.initial_knife = self.knife.data.default_root_pose.torch.clone()
        if self.phase3:
            from pxr import UsdGeom
            from reset_sampler import FlatResetSampler
            points=np.array(UsdGeom.Mesh(self.sim.stage.GetPrimAtPath(self.manifest['knife_path'])).GetPointsAttr().Get())
            self.sampler=FlatResetSampler(points,self.manifest['board_world_bounds'])
            self.reset_cases=self.sampler.sample(32)
            self.reset_history=[]

    def _setup_scene(self):
        # A single existing scene is composed without replacing any original asset.
        scene_file = ROOT / ('rl/scene/phase3.usda' if self.phase3 else 'rl/scene/minimal_benchmark.usda')
        scene_file=getattr(self,'scene_file_override',scene_file)
        self.sim.stage.GetRootLayer().subLayerPaths.append(str(scene_file))
        m = self.manifest
        matrix = np.array(m['robot_root_world_matrix'])
        robot_cfg = ArticulationCfg(
            prim_path='/dual_ar5_o6', spawn=None,
            init_state=ArticulationCfg.InitialStateCfg(pos=tuple(matrix[:3,3]),
                rot=tuple(Rotation.from_matrix(matrix[:3,:3]).as_quat()), joint_pos=m['home_rad']),
            actuators={
                'arm': ImplicitActuatorCfg(joint_names_expr=['.*_AR5_.*'],stiffness=2500.,damping=150.,effort_limit_sim=80.),
                'hand': ImplicitActuatorCfg(joint_names_expr=['.*_(mcp_pitch|cmc_yaw|cmc_pitch)'],stiffness=3.,damping=.15),
                'followers': ImplicitActuatorCfg(joint_names_expr=['.*_(dip|thumb_ip)'],stiffness=0.,damping=0.,effort_limit_sim=0.)})
        self.robot = Articulation(robot_cfg)
        self.knife = RigidObject(RigidObjectCfg(prim_path=m['knife_path'], spawn=None))
        # Preserve the authored knife pose, including its mesh scale. Asset defaults are explicit xyzw.
        from pxr import UsdGeom
        km = np.array(UsdGeom.XformCache().GetLocalToWorldTransform(self.sim.stage.GetPrimAtPath(m['knife_path']))).T
        self.knife.cfg.init_state.pos = tuple(km[:3,3])
        self.knife.cfg.init_state.rot = tuple(Rotation.from_matrix(km[:3,:3] / np.linalg.norm(km[:3,0])).as_quat())
        self.scene.articulations['robot'] = self.robot
        self.scene.rigid_objects['knife'] = self.knife

    def _pre_physics_step(self, actions):
        if actions.shape != (1,13) or not torch.isfinite(actions).all():
            raise ValueError('Invalid validation action')
        self.previous = actions.clamp(-1,1).clone()
        goal = self.home[:,self.ids] + self.previous * .015
        self.target[:,self.ids] += (goal-self.target[:,self.ids]).clamp(-.002,.002)
        if self.phase3 and getattr(self,'hand_cycle',False):
            phase=int(self.episode_length_buf[0])
            # Empty-hand diagnostic only. Fingers move before thumb; never a pickup controller.
            hand_goal=torch.tensor([[.8 if phase>=130 else 0.,.4 if phase>=130 else 0.,1.2,1.2,1.2,1.2]],device=self.device)
            self.target[:,self.ids[7:]] += (hand_goal-self.target[:,self.ids[7:]]).clamp(-.01,.01)
        limits = self.robot.data.soft_joint_pos_limits.torch
        self.target = torch.maximum(torch.minimum(self.target, limits[:,:,1]), limits[:,:,0])

    def _apply_action(self):
        self.robot.set_joint_position_target_index(target=self.target)

    def _get_observations(self):
        q = self.robot.data.joint_pos.torch
        qd = self.robot.data.joint_vel.torch
        return {'policy': torch.cat((q[:,self.ids]-self.home[:,self.ids],qd[:,self.ids],self.previous),dim=-1)}

    def _get_rewards(self):
        # API validation only. No task reward or learner is implemented here.
        return torch.zeros(1, device=self.device)

    def _get_dones(self):
        q = self.robot.data.joint_pos.torch
        qd = self.robot.data.joint_vel.torch
        invalid = ~torch.isfinite(q).all(dim=-1) | ~torch.isfinite(qd).all(dim=-1)
        unsafe = (qd.abs().max(dim=-1).values > 3) | ((q[:,self.left_ids]-self.home[:,self.left_ids]).abs().max(dim=-1).values > .05236)
        self.last_unsafe = bool((invalid | unsafe).any())
        if hasattr(self,'contact_monitor'):
            self.last_unsafe |= any(x['force_n']>50 and x['body'].startswith('/dual_ar5_o6') for x in self.contact_monitor.summary())
        if self.last_unsafe:
            self.unsafe_detail = {'max_speed_rad_s':float(qd.abs().max()),
                'max_left_drift_rad':float((q[:,self.left_ids]-self.home[:,self.left_ids]).abs().max()),
                'speeds':dict(zip(self.robot.joint_names,qd[0].tolist()))}
            if hasattr(self,'contact_monitor'):
                self.unsafe_detail['contacts']=self.contact_monitor.summary()
        return invalid | unsafe, self.episode_length_buf >= self.max_episode_length-1

    def _reset_idx(self, env_ids):
        super()._reset_idx(env_ids)
        self.robot.write_joint_position_to_sim_index(position=self.home, env_ids=env_ids)
        self.robot.write_joint_velocity_to_sim_index(velocity=torch.zeros_like(self.home), env_ids=env_ids)
        self.target[:] = self.home
        self.previous.zero_()
        pose=self.initial_knife
        if self.phase3:
            case=self.reset_cases[self.reset_count%len(self.reset_cases)]
            pose=torch.tensor([case['pose_xyzw']],dtype=torch.float32,device=self.device)
            self.reset_history.append(case)
        self.knife.write_root_pose_to_sim_index(root_pose=pose, env_ids=env_ids)
        self.knife.write_root_velocity_to_sim_index(root_velocity=torch.zeros((1,6),device=self.device), env_ids=env_ids)
        self.reset_count += 1
