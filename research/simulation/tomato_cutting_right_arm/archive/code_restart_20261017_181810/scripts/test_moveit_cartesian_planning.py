#!/usr/bin/env python3
"""
Headless verification script for MoveIt 2 Cartesian trajectory planning.
Targets ROKAE AR5 right arm with LinkerHand O6 for tomato slicing knife motions.
"""

import sys
import os
import time
import subprocess
import signal
import rclpy
from rclpy.node import Node
from moveit_msgs.srv import GetPositionFK, GetCartesianPath
from geometry_msgs.msg import Pose

def main():
    print("=" * 60)
    print(" MoveIt 2 Cartesian Planning Verification Test")
    print(" Robot: ROKAE AR5 + LinkerHand O6 (Right Arm)")
    print("=" * 60)

    # Launch move_group in headless mode if not already running
    launch_proc = None
    cmd_check = "ros2 node list 2>/dev/null | grep move_group || true"
    check_out = subprocess.check_output(cmd_check, shell=True, text=True)
    
    if "move_group" not in check_out:
        print("[TEST] Starting move_group launch in background...")
        launch_cmd = [
            "ros2", "launch", "ar5_o6_right_moveit_config", "move_group.launch.py"
        ]
        launch_proc = subprocess.Popen(
            launch_cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            preexec_fn=os.setsid
        )
        print("[TEST] Waiting for MoveIt 2 services to initialize...")
        time.sleep(5.0)

    rclpy.init()
    node = Node("test_moveit_cartesian_verifier")

    try:
        # Step 1: Query Forward Kinematics (FK) for reference starting posture
        fk_cli = node.create_client(GetPositionFK, "/compute_fk")
        print("[TEST] Connecting to /compute_fk service...")
        if not fk_cli.wait_for_service(timeout_sec=10.0):
            raise RuntimeError("Timed out waiting for /compute_fk service")

        fk_req = GetPositionFK.Request()
        fk_req.header.frame_id = "AR5_5_07R_W4C4A2_base"
        fk_req.fk_link_names = ["AR5_5_07R_W4C4A2_tcp"]
        # Use 'ready' configuration (non-singular posture for slicing)
        fk_req.robot_state.joint_state.name = [
            f"AR5_5_07R_W4C4A2_joint_{i}" for i in range(1, 8)
        ]
        fk_req.robot_state.joint_state.position = [0.0, -0.5, 0.0, 1.2, 0.0, 0.7, 0.0]

        future_fk = fk_cli.call_async(fk_req)
        rclpy.spin_until_future_complete(node, future_fk, timeout_sec=5.0)
        fk_res = future_fk.result()
        if not fk_res or not fk_res.pose_stamped:
            raise RuntimeError("Failed to compute forward kinematics for start state")

        start_pose = fk_res.pose_stamped[0].pose
        print(f"[TEST] Computed Start TCP Pose: x={start_pose.position.x:.4f}m, "
              f"y={start_pose.position.y:.4f}m, z={start_pose.position.z:.4f}m")

        # Step 2: Formulate Cartesian trajectory waypoints for tomato cutting
        # Slicing trajectory: downward descent into tomato + reciprocating stroke
        cart_cli = node.create_client(GetCartesianPath, "/compute_cartesian_path")
        print("[TEST] Connecting to /compute_cartesian_path service...")
        if not cart_cli.wait_for_service(timeout_sec=10.0):
            raise RuntimeError("Timed out waiting for /compute_cartesian_path service")

        cart_req = GetCartesianPath.Request()
        cart_req.header.frame_id = "AR5_5_07R_W4C4A2_base"
        cart_req.group_name = "arm"
        cart_req.link_name = "AR5_5_07R_W4C4A2_tcp"
        cart_req.start_state = fk_req.robot_state
        cart_req.max_step = 0.01  # 1 cm step resolution
        cart_req.jump_threshold = 0.0
        cart_req.avoid_collisions = False

        # Waypoint 1: Initial touch (descend 2.5 cm along -Z)
        wp1 = Pose()
        wp1.position.x = start_pose.position.x
        wp1.position.y = start_pose.position.y
        wp1.position.z = start_pose.position.z - 0.025
        wp1.orientation = start_pose.orientation

        # Waypoint 2: Slicing forward stroke (+3.0 cm in X, -4.0 cm in Z)
        wp2 = Pose()
        wp2.position.x = start_pose.position.x + 0.03
        wp2.position.y = start_pose.position.y
        wp2.position.z = start_pose.position.z - 0.040
        wp2.orientation = start_pose.orientation

        # Waypoint 3: Slicing backward stroke (-3.0 cm in X, -4.5 cm in Z)
        wp3 = Pose()
        wp3.position.x = start_pose.position.x - 0.03
        wp3.position.y = start_pose.position.y
        wp3.position.z = start_pose.position.z - 0.045
        wp3.orientation = start_pose.orientation

        cart_req.waypoints = [wp1, wp2, wp3]

        print("[TEST] Sending Cartesian planning request for 3 cutting waypoints...")
        future_cart = cart_cli.call_async(cart_req)
        rclpy.spin_until_future_complete(node, future_cart, timeout_sec=5.0)
        cart_res = future_cart.result()

        if not cart_res:
            raise RuntimeError("No response received from Cartesian planning service")

        fraction = cart_res.fraction
        points = cart_res.solution.joint_trajectory.points
        print(f"[TEST] Plan Result:")
        print(f"       Fraction completed: {fraction * 100:.2f}%")
        print(f"       Trajectory points:  {len(points)}")
        print(f"       Error code:         {cart_res.error_code.val}")

        if fraction < 0.95 or len(points) == 0:
            raise ValueError(f"Cartesian planning failed acceptance threshold! (fraction={fraction:.2f})")

        print("=" * 60)
        print(" [PASSED] MoveIt 2 Cartesian Path Planning Verified Successfully!")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"[FAILED] Error during MoveIt 2 Cartesian planning test: {e}", file=sys.stderr)
        return 1
    finally:
        node.destroy_node()
        rclpy.shutdown()
        if launch_proc:
            print("[TEST] Stopping background move_group launch...")
            try:
                os.killpg(os.getpgid(launch_proc.pid), signal.SIGTERM)
                launch_proc.wait(timeout=5)
            except Exception:
                pass

if __name__ == "__main__":
    sys.exit(main())
