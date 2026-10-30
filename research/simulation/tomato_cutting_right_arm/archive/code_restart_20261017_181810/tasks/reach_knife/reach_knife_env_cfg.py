import math
from dataclasses import MISSING
import isaaclab.envs.mdp as mdp
import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import ArticulationCfg, AssetBaseCfg, RigidObjectCfg
from isaaclab.envs import ManagerBasedRLEnvCfg
from isaaclab.managers import (
    ActionTermCfg,
    CurriculumTermCfg,
    EventTermCfg,
    ObservationGroupCfg,
    ObservationTermCfg,
    RewardTermCfg,
    SceneEntityCfg,
    TerminationTermCfg,
)
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.utils import configclass


@configclass
class ReachKnifeSceneCfg(InteractiveSceneCfg):
    """Configuration for the knife reach scene."""
    # Ground plane
    ground = AssetBaseCfg(
        prim_path="/World/ground",
        spawn=sim_utils.GroundPlaneCfg(),
    )
    
    # Kitchen & Robot Combined Scene
    robot = ArticulationCfg(
        prim_path="{ENV_REGEX_NS}/Robot",
        spawn=sim_utils.UsdFileCfg(
            usd_path="/home/omen/teamwork_projects/tomato_cutting_right_arm/assets/robots/Collected_whole_robot_updated/Collected_whole_robot/Collected_whole_robot_2/whole_robot_2.usd",
        ),
        init_state=ArticulationCfg.InitialStateCfg(
            pos=(0.0, 0.0, 0.0),
        ),
        actuators={
            "arm": ImplicitActuatorCfg(
                joint_names_expr=["right_AR5.*"],
                effort_limit=100.0,
                velocity_limit=5.0,
                stiffness=80.0,
                damping=4.0,
            ),
        },
    )


@configclass
class CommandsCfg:
    """Command terms for the MDP."""
    pass


@configclass
class ActionsCfg:
    """Action specifications for the MDP."""
    arm_action = mdp.JointPositionActionCfg(
        asset_name="robot",
        joint_names=["right_AR5.*"],
        scale=0.5,
        use_default_offset=True,
    )


@configclass
class ObservationsCfg:
    """Observation specifications for the MDP."""
    @configclass
    class PolicyCfg(ObservationGroupCfg):
        joint_pos = ObservationTermCfg(func=mdp.joint_pos_rel, params={"asset_cfg": SceneEntityCfg("robot")})
        joint_vel = ObservationTermCfg(func=mdp.joint_vel_rel, params={"asset_cfg": SceneEntityCfg("robot")})
        last_action = ObservationTermCfg(func=mdp.last_action)

        def __post_init__(self):
            self.enable_corruption = False
            self.concatenate_terms = True

    policy: PolicyCfg = PolicyCfg()


@configclass
class EventCfg:
    """Configuration for events."""
    reset_robot = EventTermCfg(
        func=mdp.reset_joints_by_scale,
        mode="reset",
        params={
            "position_range": (1.0, 1.0),
            "velocity_range": (0.0, 0.0),
            "asset_cfg": SceneEntityCfg("robot"),
        },
    )


@configclass
class RewardsCfg:
    """Reward terms for the MDP."""
    action_rate = RewardTermCfg(func=mdp.action_rate_l2, weight=-0.001)
    joint_acc = RewardTermCfg(
        func=mdp.joint_acc_l2,
        weight=-1.0e-5,
        params={"asset_cfg": SceneEntityCfg("robot")},
    )


@configclass
class TerminationsCfg:
    """Termination terms for the MDP."""
    time_out = TerminationTermCfg(func=mdp.time_out, time_out=True)


@configclass
class ReachKnifeEnvCfg(ManagerBasedRLEnvCfg):
    """Configuration for the knife reach environment."""
    scene: ReachKnifeSceneCfg = ReachKnifeSceneCfg(num_envs=64, env_spacing=2.5)
    observations: ObservationsCfg = ObservationsCfg()
    actions: ActionsCfg = ActionsCfg()
    commands: CommandsCfg = CommandsCfg()
    rewards: RewardsCfg = RewardsCfg()
    terminations: TerminationsCfg = TerminationsCfg()
    events: EventCfg = EventCfg()

    def __post_init__(self):
        """Post initialization."""
        self.decimation = 2
        self.episode_length_s = 5.0
        self.sim.dt = 1.0 / 60.0
        self.sim.render_interval = self.decimation
