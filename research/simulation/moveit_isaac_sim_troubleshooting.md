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
