# Copyright (c) 2022-2026, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Configuration for the AR5_L6 7-DoF Manipulator and LinkerHand O6 Dexterous Robot.

The following configurations are available:

* :obj:`AR5_L6_LEFT_CFG`: 7-DoF left arm alone
* :obj:`AR5_L6_RIGHT_CFG`: 7-DoF right arm alone
* :obj:`AR5_O6_LEFT_COMBINED_CFG`: 7-DoF left arm with LinkerHand O6 5-finger dexterous hand
"""

import os
from isaaclab_newton.sim.schemas import NewtonArticulationCfg
from isaaclab_physx.sim.schemas import PhysxArticulationCfg, PhysxRigidBodyCfg

import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets.articulation import ArticulationCfg

# Base directory for the robot assets
ROBOT_ASSET_DIR = os.path.dirname(os.path.abspath(__file__))

##
# 1. AR5_L6 Left Arm (7-DoF Arm Only)
##

AR5_L6_LEFT_CFG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(
        usd_path=os.path.join(ROBOT_ASSET_DIR, "usd/urdf_output/AR5_L6_left/AR5_L6_left.usda"),
        rigid_props=PhysxRigidBodyCfg(disable_gravity=False, max_depenetration_velocity=5.0),
        activate_contact_sensors=False,
        articulation_props=[
            PhysxArticulationCfg(
                enabled_self_collisions=True,
                solver_position_iteration_count=8,
                solver_velocity_iteration_count=0,
            ),
            NewtonArticulationCfg(self_collision_enabled=True),
        ],
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        joint_pos={
            "AR5_5_07L_W4C4A2_joint_1": 0.0,
            "AR5_5_07L_W4C4A2_joint_2": -0.523,
            "AR5_5_07L_W4C4A2_joint_3": 0.0,
            "AR5_5_07L_W4C4A2_joint_4": 1.571,
            "AR5_5_07L_W4C4A2_joint_5": 0.0,
            "AR5_5_07L_W4C4A2_joint_6": 1.047,
            "AR5_5_07L_W4C4A2_joint_7": 0.0,
            "lh_.*": 0.0,
        },
    ),
    actuators={
        "arm": ImplicitActuatorCfg(
            joint_names_expr=["AR5_5_07L_W4C4A2_joint_[1-7]"],
            joint_effort_limit=108.0,
            stiffness=800.0,
            damping=40.0,
        ),
        "hand": ImplicitActuatorCfg(
            joint_names_expr=["lh_.*"],
            joint_effort_limit=20.0,
            stiffness=50.0,
            damping=2.0,
        ),
    },
)

##
# 2. AR5_L6 Right Arm (7-DoF Arm + Right Hand)
##

AR5_L6_RIGHT_CFG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(
        usd_path=os.path.join(ROBOT_ASSET_DIR, "usd/urdf_output/AR5_L6_right/AR5_L6_right.usda"),
        rigid_props=PhysxRigidBodyCfg(disable_gravity=False, max_depenetration_velocity=5.0),
        activate_contact_sensors=True,
        articulation_props=[
            PhysxArticulationCfg(
                enabled_self_collisions=True,
                solver_position_iteration_count=8,
                solver_velocity_iteration_count=0,
            ),
            NewtonArticulationCfg(self_collision_enabled=True),
        ],
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        joint_pos={
            "AR5_5_07R_W4C4A2_joint_1": 0.0,
            "AR5_5_07R_W4C4A2_joint_2": -0.523,
            "AR5_5_07R_W4C4A2_joint_3": 0.0,
            "AR5_5_07R_W4C4A2_joint_4": 1.571,
            "AR5_5_07R_W4C4A2_joint_5": 0.0,
            "AR5_5_07R_W4C4A2_joint_6": 1.047,
            "AR5_5_07R_W4C4A2_joint_7": 0.0,
            "rh_.*": 0.0,
        },
    ),
    actuators={
        "arm": ImplicitActuatorCfg(
            joint_names_expr=["AR5_5_07R_W4C4A2_joint_[1-7]"],
            joint_effort_limit=108.0,
            stiffness=800.0,
            damping=40.0,
        ),
        "hand": ImplicitActuatorCfg(
            joint_names_expr=["rh_.*"],
            joint_effort_limit=20.0,
            stiffness=50.0,
            damping=2.0,
        ),
    },
)

##
# 3. AR5_O6 Left Combined (7-DoF Arm + LinkerHand O6 Dexterous Hand)
##

AR5_O6_LEFT_COMBINED_CFG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(
        usd_path=os.path.join(ROBOT_ASSET_DIR, "usd/urdf_output/ar5_o6_left_combined/ar5_o6_left_combined.usda"),
        rigid_props=PhysxRigidBodyCfg(disable_gravity=False, max_depenetration_velocity=5.0),
        activate_contact_sensors=True,
        articulation_props=[
            PhysxArticulationCfg(
                enabled_self_collisions=True,
                solver_position_iteration_count=8,
                solver_velocity_iteration_count=0,
            ),
            NewtonArticulationCfg(self_collision_enabled=True),
        ],
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        joint_pos={
            "AR5_5_07L_W4C4A2_joint_1": 0.0,
            "AR5_5_07L_W4C4A2_joint_2": -0.523,
            "AR5_5_07L_W4C4A2_joint_3": 0.0,
            "AR5_5_07L_W4C4A2_joint_4": 1.571,
            "AR5_5_07L_W4C4A2_joint_5": 0.0,
            "AR5_5_07L_W4C4A2_joint_6": 1.047,
            "AR5_5_07L_W4C4A2_joint_7": 0.0,
            "lh_.*": 0.0,
        },
    ),
    actuators={
        "arm": ImplicitActuatorCfg(
            joint_names_expr=["AR5_5_07L_W4C4A2_joint_[1-7]"],
            joint_effort_limit=108.0,
            stiffness=800.0,
            damping=40.0,
        ),
        "hand": ImplicitActuatorCfg(
            joint_names_expr=["lh_.*"],
            joint_effort_limit=20.0,
            stiffness=50.0,
            damping=2.0,
        ),
    },
)
