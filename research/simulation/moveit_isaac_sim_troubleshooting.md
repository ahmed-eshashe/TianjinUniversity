# AR5-L6 & LinkerHand O6 Setup: Troubleshooting & Solutions

This document logs all critical errors encountered and solved during the end-to-end setup of the **AR5-L6** arm and **LinkerHand O6** dexterous hand in ROS 2 Jazzy and Isaac Sim 2023.1.1.

---

## Part 1: Isaac Sim Physics & URDF Import

### 1. The "Exploding Robot" (Mass Ratio & Inertia Collapse)
**Error:** Upon hitting "Play" in Isaac Sim for the first time, the imported URDF robot instantly flew apart, vibrated violently, collapsed into a pile, or disappeared (due to NaN velocities).
**Cause:** The PhysX 5 solver struggles mathematically when connected rigid bodies have extreme mass differences. The AR5 arm links weigh several kilograms, while the LinkerHand O6 finger links weigh only a few grams (a mass ratio exceeding 1:1000). This causes the internal physics solver to diverge and explode.
**Solution:**
- **Armature Injection:** We applied `physxJoint:armature = 0.05` to all joints in the USD. Armature adds "virtual mass/inertia" specifically to the motor joints without making the robot physically heavier, stabilizing the solver immensely.
- **Position Drive Enforcement:** We added `drive:angular:physics:stiffness = 400.0` and `damping = 40.0` to all joints. Without stiffness, the joints are completely limp and gravity rips the heavy structure apart.

### 2. Articulation Root Hierarchy Issues
**Error:** The robot either fell through the floor or the joints refused to be controlled simultaneously.
**Cause:** PhysX requires a single, unified mathematical tree to solve joint constraints properly. If the `PhysicsArticulationRoot` API is placed incorrectly, or multiple roots exist, the robot breaks into disconnected physics islands.
**Solution:** 
- Ensured the `PhysicsArticulationRoot` API was placed exactly on the top-level parent prim (`ar5_o6_left_combined`).
- Verified that the base link (`AR5_5_07L_W4C4A2_base`) had its physics rigidly fixed to the world frame, preventing the heavy arm from plummeting under gravity.

---

## Part 2: MoveIt 2 Configuration (ROS 2 Jazzy)

### 3. MoveGroup Node Instant Crash (`InvalidParameterTypeException`)
**Error:** `ros2 launch ahmed_moveit demo.launch.py` crashed immediately with an exception stating `parameter 'joint_limits.max_velocity' has invalid type: expected double, got integer`.
**Cause:** The MoveIt Setup Assistant generated `joint_limits.yaml` with whole numbers (e.g., `1`). ROS 2 C++ parameters are strictly typed and reject integers when expecting floats.
**Solution:** Edited `joint_limits.yaml` to ensure all numerical values use decimal points (e.g., changed `1` to `1.0`).

### 4. RViz Planning Failure (`Time parameterization failed`)
**Error:** RViz could plan the geometric path (showing the orange ghost), but hitting "Plan & Execute" resulted in a failure message because time parameterization failed.
**Cause:** MoveIt's default Time Optimal Trajectory Generation (TOTG) algorithm requires acceleration limits to calculate smooth velocity profiles, but none were provided in the configuration.
**Solution:** Added `has_acceleration_limits: true` and `max_acceleration: 5.0` to all joints in `joint_limits.yaml`.

### 5. Hand Controller Crash (`GripperCommand`)
**Error:** MoveIt crashed on startup when trying to load the `hand_controller`.
**Cause:** The MoveIt Setup Assistant incorrectly assigned the `GripperCommand` controller type to the 6-DoF dexterous hand. `GripperCommand` is strictly designed for 1-DoF parallel jaw grippers.
**Solution:** Rewrote `moveit_controllers.yaml` to classify both the arm and the dexterous hand as `FollowJointTrajectory` controllers. Added `action_ns: follow_joint_trajectory` and `default: true` to both.

---

## Part 3: Isaac Sim & ROS 2 Bridge Integration

### 6. The Tutorial Dependency Trap (`topic_based_ros2_control`)
**Error:** Following a popular YouTube tutorial resulted in MoveIt execution failures ("Failed" in RViz). 
**Cause:** The tutorial relied on `topic_based_ros2_control`, a custom plugin that is **not natively available in ROS 2 Jazzy via apt**. Attempting to build it from source failed because the Linux host was missing multiple C++ developer libraries (`console_bridge`, `TinyXML2`, `urdfdom`).
**Solution:** Bypassed the custom plugin entirely. Reverted `ros2_control.xacro` back to the default `mock_components/GenericSystem` (fake hardware). This natively broadcasts real-time joint states to the standard `/joint_states` topic without needing external plugins.

### 7. Isaac Sim Not Responding to MoveIt (Action Graph Traps)
**Error:** RViz executed paths perfectly, but the physical robot in Isaac Sim refused to mirror the movements.
**Causes & Solutions:**
We discovered several classic Isaac Sim visual scripting UI traps:
1. **Topic Mismatch & UI Reversions:** The `ROS2 Subscribe Joint State` node was listening to the wrong topic. *Fix:* Changed `topicName` to `/joint_states`. *Crucial Tip:* In Isaac Sim, you must hit the **Enter** key after typing in the Property Panel, or the UI will silently discard your input and revert to the old value.
2. **Missing Target Prim:** The `Articulation Controller` node drops all commands if it doesn't know what to control. *Fix:* Clicked "Add Target" in the Articulation Controller properties and selected the robot's root (`ar5_o6_left_combined`).
3. **Execution Wire Race Conditions:** The white execution wires were routed in parallel, causing the controller to fire *before* the subscriber updated the data. *Fix:* Rewired the graph sequentially: `Tick` $\rightarrow$ `ROS2 Subscribe Joint State (Exec Out)` $\rightarrow$ `Articulation Controller (Exec In)`.
4. **Playback State:** The Action Graph `On Playback Tick` node only receives data if the simulation is actively **Playing** (Spacebar), not paused.
---

## Part 4: Dexterous Hand Specific Challenges (LinkerHand O6)

### 8. The Mimic Joint Planning Crash
**Error:** Attempting to plan for the dexterous hand instantly failed.
**Cause:** The LinkerHand O6 URDF contains passive `mimic` joints (e.g., `lh_thumb_ip` mimics `lh_thumb_cmc_pitch`). During the MoveIt Setup Assistant phase, a mimic joint was accidentally included as an active joint in the `hand` planning group. MoveIt's mathematical solvers cannot generate trajectories for passive, mechanically constrained joints and will instantly abort.
**Solution:** Removed the `lh_thumb_ip` joint from the `hand` planning group and from all predefined group states in `ar5_o6_left.srdf`.

### 9. The Dexterous Hand Self-Collision Abort
**Error:** MoveIt instantly aborted planning for the hand with `Found a contact between...` or `Start state in collision`.
**Cause:** Dexterous hands have extremely dense collision meshes. When closing the fingers into a fist (like the `thumps` pose), the finger bounding boxes mathematically intersect with the palm or adjacent fingers. MoveIt's default safety system detects this as a crash and refuses to plan.
**Solution:** Programmatically disabled self-collisions across the entire robot (hand-vs-hand, arm-vs-arm, hand-vs-arm) in the `ar5_o6_left.srdf` by injecting `<disable_collisions>` tags for all link pairs.

### 10. The Execution Synchronization Failure (`Action client not connected`)
**Error:** RViz logged `Starting trajectory execution ...` (meaning planning succeeded!), but then immediately threw `Completed trajectory execution with status ABORTED` and `Action client not connected to action server: hand_controller/follow_joint_trajectory`.
**Cause:** We updated `moveit_controllers.yaml` to expect a full `FollowJointTrajectory` action server, but we forgot to update `ros2_controllers.yaml` (which still told the ROS 2 hardware manager to spawn a single-joint `GripperActionController`).
**Crucial Trap:** Even after fixing the source file, RViz kept failing. **Why?** ROS 2 `launch` reads configuration files from the `install/` directory, not the source directory. 
**Solution:** 
1. Fixed `ros2_controllers.yaml` to configure `hand_controller` as a `joint_trajectory_controller/JointTrajectoryController` listing all 6 active finger joints.
2. Navigated to the workspace and ran `colcon build` to sync the fixed files to the `install/` directory before restarting RViz.

### 11. The Stiff Fingers Visual Bug (Mimic Joints in Fake Hardware)
**Error:** In both RViz and Isaac Sim, commanding the fingers to curl resulted in the base knuckles (MCP) rotating, but the middle and tip joints (DIP) remained perfectly straight like stiff wooden boards.
**Cause:** The fake hardware simulation (`mock_components/GenericSystem`) only calculates and publishes the angles of explicitly defined active joints. Because the passive tip joints were never broadcast to the `/joint_states` topic, both RViz and Isaac Sim assumed their angles were strictly `0.0`.
**Solution:** Injected the mathematical `<mimic>` parameters directly into the hardware interface definition in `ros2_control.xacro` (e.g., `<param name="mimic">lh_index_mcp_pitch</param>` and `<param name="multiplier">0.89</param>`). This forces the mock hardware manager to compute the unpowered tip angles in real-time and broadcast the full pose.
