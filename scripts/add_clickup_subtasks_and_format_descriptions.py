#!/usr/bin/env python3
"""
ClickUp Subtask Generator & Description Formatter
DEX-ROB Lab | School of Electrical & Automation Engineering, Tianjin University
Author: Ahmed Sameh | Research Lead Agent

Converts inline description checklists into native ClickUp subtasks across all 49 weekly tasks.
Formats every parent task description uniformly:
- Objective header & high-level context
- Target Deliverable
- Key Reference Files & Commands

Creates native, trackable subtasks assigned to Ahmed Sameh (176612914) with:
- Actionable titles
- Detailed technical descriptions and CLI commands
- Proper status ('in progress' for W1 active items, 'Open' for future items)
"""

import sys
import os
import time
import json
import urllib.request
import urllib.error

CLICKUP_TOKEN = 'pk_176612914_8AX37HX8WU54TI6HLUK2C2YVR5A5L3JB'
FOLDER_ID = '901214868317'  # Space: Tianjin University -> Folder: Research
USER_ID = 176612914         # Ahmed Sameh

HEADERS = {
    'Authorization': CLICKUP_TOKEN,
    'Content-Type': 'application/json'
}

def api_call(url, data=None, method='GET'):
    for attempt in range(5):
        try:
            req_data = json.dumps(data).encode('utf-8') if data is not None else None
            req = urllib.request.Request(url, headers=HEADERS, data=req_data, method=method)
            with urllib.request.urlopen(req) as resp:
                if resp.status == 204:
                    return None
                return json.loads(resp.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                retry_after = int(e.headers.get('Retry-After', 5))
                print(f" [Rate Limit 429] Backing off {retry_after}s...")
                time.sleep(retry_after)
                continue
            err_body = e.read().decode('utf-8', errors='ignore')
            print(f" [HTTP {e.code}] Error on {url}: {err_body}")
            raise e
        except Exception as ex:
            print(f" [Network Error] {ex}, retrying in 2s...")
            time.sleep(2)
    return None

WEEKS_DATA = {
    # -------------------------------------------------------------------------
    # SPRINT 1: Kinematics & Proprioceptive Observer (W1–W6)
    # -------------------------------------------------------------------------
    1: {
        "title": "Asset Stabilization & Verification",
        "summary": "Master the ARX AR5-L6 7-DoF manipulator and LinkerHand O6 5-finger dexterous hand OpenUSD assets in NVIDIA Isaac Sim. Verify rotor armature conditioning to resolve the 6,000:1 mass ratio ill-conditioning and ensure stable teleoperation without numerical explosions.",
        "deliverable": "Confirmed stable robot physics in NVIDIA Isaac Sim without NaNs, mesh penetrations, or joint velocity blowouts.",
        "references": "- USD Stage: `research/simulation/assets/robots/ar5_l6/usd_clean/ar5_o6_left_combined/ar5_o6_left_combined.usda`\n- Teleop Script: `research/simulation/scripts/control_ar5_teleop.py`",
        "subtasks": [
            {
                "name": "Inspect converted OpenUSD stage (ar5_o6_left_combined.usda)",
                "desc": "Verify the USDA hierarchy, joint articulation APIs, and mass properties for both the 7-DoF arm and 5-finger hand.",
                "status": "in progress"
            },
            {
                "name": "Analyze rotor armature conditioning (armature=0.05 arm, 0.005 hand)",
                "desc": "Understand why adding virtual rotor inertia diagonalizes the mass matrix and resolves PhysX PGS/TGS ill-conditioning.",
                "status": "in progress"
            },
            {
                "name": "Execute active teleoperation script in Isaac Sim",
                "desc": "Run teleoperation command:\n```bash\n/home/omen/isaac-sim/python.sh /media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/research/simulation/scripts/control_ar5_teleop.py\n```",
                "status": "in progress"
            },
            {
                "name": "Verify stance approach, finger opening, and compliant grasp closure",
                "desc": "Ensure arm and hand achieve target poses smoothly with zero NaN warnings in Isaac Sim terminal output.",
                "status": "Open"
            }
        ]
    },
    2: {
        "title": "Standalone Forward Kinematics & Manipulator Jacobian",
        "summary": "Implement and master the analytical kinematics engine translating 7-DoF joint coordinates into end-effector Cartesian poses and velocities. Verify the analytical geometric Jacobian against PyTorch autograd and implement damped least-squares pseudo-inversion for singularity robustness.",
        "deliverable": "Validated analytical kinematics and Jacobian engine (`ar5_kinematics.py`) matching autograd within machine precision ($err < 10^{-7}$).",
        "references": "- Module: `research/simulation/src/kinematics/ar5_kinematics.py`\n- Verification: `python research/simulation/src/kinematics/ar5_kinematics.py`",
        "subtasks": [
            {
                "name": "Review 7-DoF kinematic chain axes and link transforms",
                "desc": "Study the joint rotation axes (revolute Z, Y, Z, Y, Z, Y, X) and link offsets from URDF base to end-effector flange.",
                "status": "Open"
            },
            {
                "name": "Validate analytical Jacobian J(q) in R^{6x7} against PyTorch autograd",
                "desc": "Run validation script and ensure error between geometric Jacobian and forward kinematics autograd is < 1e-5.",
                "status": "Open"
            },
            {
                "name": "Implement damped least-squares pseudo-inverse J^dagger",
                "desc": "Implement: J^dagger = J^T (J J^T + lambda^2 I)^{-1} with damping lambda = 1e-4 for singularity robustness.",
                "status": "Open"
            }
        ]
    },
    3: {
        "title": "1 kHz Proprioceptive Contact Wrench Observer",
        "summary": "Build the core sensing innovation confirmed with Prof. Shan An: reconstructing external contact wrenches directly from motor joint torques without fragile tactile sensor arrays. Calibrate a 50 Hz bilinear Butterworth low-pass filter to reject motor PWM current ripple.",
        "deliverable": "1 kHz contact wrench observer (`wrench_estimator.py`) achieving $< 10^{-3}\text{ N}$ reconstruction error and robust contact regime classification.",
        "references": "- Module: `research/simulation/src/control/wrench_estimator.py`\n- Observer Equation: $\\mathbf{F}_{ext} = (\\mathbf{J}^T)^\\dagger \\boldsymbol{\\tau}_{ext}$",
        "subtasks": [
            {
                "name": "Implement transpose Jacobian wrench mapping: F_ext = (J^T)^dagger * tau_ext",
                "desc": "Map 7D measured joint torques to 6D Cartesian contact wrench using damped pseudo-inverse transpose.",
                "status": "Open"
            },
            {
                "name": "Tune 50 Hz bilinear Butterworth low-pass filter",
                "desc": "Reject 200 Hz motor current ripple and sensor noise while maintaining < 2 ms phase delay at 1 kHz sample rate.",
                "status": "Open"
            },
            {
                "name": "Implement 4-stage contact regime classifier",
                "desc": "Classify states: UNDER_GRASP_SLIP (< 1.5 N), NOMINAL_SAFE_HOLD (1.5-5.0 N), CRUSH_BARRIER_VIOLATION (> 5.0 N), EMERGENCY_OVERLOAD (> 15.0 N).",
                "status": "Open"
            },
            {
                "name": "Execute unit test self-check suite",
                "desc": "Run: `/home/omen/miniforge3/envs/tianjin-robotics/bin/python research/simulation/src/control/wrench_estimator.py`",
                "status": "Open"
            }
        ]
    },
    4: {
        "title": "LinkerHand O6 Actuator Mapping & Tendon Coupling",
        "summary": "Configure the 6 active motors and 5 passive tendon-coupled DIP joints of the LinkerHand O6 in Isaac Lab. Enforce mechanical pulley transmission ratios to prevent PD controller fighting and ensure stable multi-finger closure.",
        "deliverable": "Stable five-finger compliant closure in simulation without tendon spring snapping or PD controller fighting.",
        "references": "- Hand Asset: `research/simulation/assets/robots/linker_hand/linker_o6.usda`\n- Transmission Ratio: $\\theta_{DIP} = 1.126 \\cdot \\theta_{MCP}$",
        "subtasks": [
            {
                "name": "Map 6 active motor joints in Isaac Lab",
                "desc": "Configure thumb yaw, thumb pitch, and index/middle/ring/pinky MCP pitch joints with appropriate effort and velocity limits.",
                "status": "Open"
            },
            {
                "name": "Enforce mechanical tendon pulley ratio for 5 passive DIP joints",
                "desc": "Enforce kinematic coupling theta_dip = 1.126 * theta_mcp and remove active PD actuators from mimic joints.",
                "status": "Open"
            },
            {
                "name": "Tune actuator PD gains (Kp=30.0, Kd=3.0, armature=0.005)",
                "desc": "Verify stable contact compliance when grasping rigid and soft geometric primitives in Isaac Sim.",
                "status": "Open"
            }
        ]
    },
    5: {
        "title": "Aperdata Kitchen Scene Composition & Cutting Props",
        "summary": "Assemble the high-fidelity kitchen workstation simulation using verified Aperdata SimReady assets. Position cutting board, plate, and robot mounting fixtures at standard laboratory tabletop heights.",
        "deliverable": "Photorealistic OpenUSD kitchen workstation stage ready for tomato spawning and dual-arm interaction.",
        "references": "- Aperdata Stage: `/home/omen/isaac-sim-assests/0_Kitchen_Indoor/Indoor.usd`\n- Workspace Config: Origin $(0, 0, 0.75\text{ m})$, Left arm at $x = -0.35\text{ m}$",
        "subtasks": [
            {
                "name": "Import Aperdata Indoor Kitchen Stage into Isaac Sim",
                "desc": "Load `/home/omen/isaac-sim-assests/0_Kitchen_Indoor/Indoor.usd` and configure lighting and physics scene.",
                "status": "Open"
            },
            {
                "name": "Position cutting board and plate at world coordinate (0, 0, 0.75 m)",
                "desc": "Set rigid body collision and surface friction parameters for the cutting board surface.",
                "status": "Open"
            },
            {
                "name": "Mount Left AR5-L6 holding arm at x = -0.35 m facing origin",
                "desc": "Verify manipulator reachability envelope over the cutting board surface.",
                "status": "Open"
            }
        ]
    },
    6: {
        "title": "Sprint 1 Review & End-to-End Integration Test",
        "summary": "Conduct a rigorous end-to-end integration test of the complete single-arm holding pipeline before starting RL training. Verify zero NaNs, zero joint limit violations, and stable contact physics. Lock Milestone M2.",
        "deliverable": "Validation artifact `experiments/results/sprint1_kinematic_validation.json` and 100% completion of Milestone M2 in `project_status.yaml`.",
        "references": "- Milestone: M2 (Manipulator Jacobian & Proprioceptive Observer)\n- Artifact: `experiments/results/sprint1_kinematic_validation.json`",
        "subtasks": [
            {
                "name": "Run end-to-end approach, grasp, and wrench logging test",
                "desc": "Simulate Left arm reaching tomato proxy, forming compliant grasp, and streaming reconstructed contact forces.",
                "status": "Open"
            },
            {
                "name": "Audit simulation stability across 1,000 timesteps",
                "desc": "Verify zero NaN occurrences, zero joint limit violations, and smooth velocity profiles.",
                "status": "Open"
            },
            {
                "name": "Generate validation report JSON and lock Milestone M2",
                "desc": "Export `experiments/results/sprint1_kinematic_validation.json` and update `research_state/project_status.yaml`.",
                "status": "Open"
            }
        ]
    },

    # -------------------------------------------------------------------------
    # SPRINT 2: Decoupled Single-Arm Holding RL (W7–W14)
    # -------------------------------------------------------------------------
    7: {
        "title": "Gym Environment Scaffolding (HoldingTomatoEnvCfg)",
        "summary": "Construct `HoldingTomatoEnvCfg` inheriting from Isaac Lab's `ManagerBasedRLEnv`. Assemble the 33D observation vector and verify batch GPU vectorization on RTX 5060.",
        "deliverable": "Functional vectorized RL environment stepping 512 parallel instances at $> 2,000\text{ FPS}$ on GPU.",
        "references": "- File: `research/simulation/src/envs/holding_tomato_env.py`\n- Observation Space: 33D (14D arm, 11D hand, 3D wrench, 5D tomato pose/vel)",
        "subtasks": [
            {
                "name": "Create holding_tomato_env.py extending ManagerBasedRLEnv",
                "desc": "Define scene configuration, robot articulation, and simulation substepping (120 Hz).",
                "status": "Open"
            },
            {
                "name": "Assemble 33D continuous observation space",
                "desc": "Include arm joint pos/vel (14D), hand joint pos (11D), reconstructed contact force (3D), and tomato pose/vel (5D).",
                "status": "Open"
            },
            {
                "name": "Benchmark GPU batch stepping across 512 environments",
                "desc": "Confirm stable memory footprint (< 6.5 GB VRAM) and tensor shape consistency.",
                "status": "Open"
            }
        ]
    },
    8: {
        "title": "Synthetic Slicing Disturbance Generator",
        "summary": "Decouple holding arm development from Shahd's slicing arm by constructing a synthetic disturbance module injecting realistic sawing force vectors directly into the tomato body.",
        "deliverable": "Disturbance module injecting normal ($F_z$) and lateral ($F_x$) sawing forces replicating real knife friction.",
        "references": "- Slicing Force: $F_z(t) = 3.5 + 1.5\\sin(4\\pi t)\\text{ N}$, $F_x(t) = \\pm 4.0\\text{ N}$ at 2 Hz\n- File: `research/simulation/src/envs/disturbances.py`",
        "subtasks": [
            {
                "name": "Implement vertical pulsating knife feed disturbance Fz(t)",
                "desc": "Inject downward force profile: Fz(t) = 3.5 + 1.5*sin(4*pi*t) N representing blade pressing.",
                "status": "Open"
            },
            {
                "name": "Implement reciprocating lateral sawing shear force Fx(t)",
                "desc": "Inject reciprocating force: Fx(t) = +/- 4.0 N at 2 Hz representing slicing friction.",
                "status": "Open"
            },
            {
                "name": "Confirm open-loop baseline grasps fail within 2 seconds",
                "desc": "Verify that a fixed rigid grasp either drops the tomato or exceeds crush threshold under disturbance.",
                "status": "Open"
            }
        ]
    },
    9: {
        "title": "Multi-Objective Barrier Reward Formulation",
        "summary": "Formulate and implement the anti-crushing barrier reward function. Balance tomato holding stability against skin rupture and energy penalties.",
        "deliverable": "Mathematical barrier reward module preventing grasp crushing while suppressing tangential slip.",
        "references": "- Formulation: $R_{hold} = R_{stab} - \\lambda_1 P_{slip} - \\lambda_2 P_{crush} - \\lambda_3 P_{\\tau}$\n- Quadratic Barrier: $P_{crush} = \\max(0, F_n - 5.0\\text{ N})^2$",
        "subtasks": [
            {
                "name": "Implement quadratic anti-crush penalty P_crush",
                "desc": "Enforce strict zero penalty below 5.0 N and steep quadratic penalty P_crush = max(0, Fn - 5.0)^2 above threshold.",
                "status": "Open"
            },
            {
                "name": "Implement tangential slip penalty P_slip",
                "desc": "Penalize relative finger-to-tomato skin velocity: P_slip = ||v_rel||^2.",
                "status": "Open"
            },
            {
                "name": "Validate reward distribution across 1,000 random rollouts",
                "desc": "Ensure reward components are balanced and do not induce gradient vanishing or explosion.",
                "status": "Open"
            }
        ]
    },
    10: {
        "title": "First SkRL Vectorized PPO Training Run (512 Envs)",
        "summary": "Launch the first vectorized PPO training run in Isaac Lab with SkRL 2.1.0 on the RTX 5060 Laptop GPU. Configure WandB telemetry streaming for real-time monitoring.",
        "deliverable": "Successfully converged holding policy training run with WandB dashboard telemetry.",
        "references": "- Command: `/home/omen/isaac-sim/python.sh experiments/scripts/train_holding_ppo.py --num_envs 512 --headless`\n- Telemetry: WandB project `dexrob-tomato-holding`",
        "subtasks": [
            {
                "name": "Launch headless SkRL PPO training on RTX 5060",
                "desc": "Execute training script with 512 vectorized environments and Gaussian policy architecture.",
                "status": "Open"
            },
            {
                "name": "Configure WandB / TensorBoard metrics logging",
                "desc": "Stream reward/total, metrics/crush_rate, metrics/slip_dist, and loss curves in real time.",
                "status": "Open"
            },
            {
                "name": "Audit VRAM usage and training throughput",
                "desc": "Confirm GPU VRAM stays under 6.5 GB and throughput exceeds 2,000 FPS.",
                "status": "Open"
            }
        ]
    },
    11: {
        "title": "Reward Debugging & Eureka Automated Tuning",
        "summary": "Apply the Eureka automated reward tuning paradigm using LLM reflection loops on training telemetry to diagnose failure modes and optimize penalty coefficients.",
        "deliverable": "Optimized reward weights yielding $> 85\%$ holding success rate under continuous sawing disturbances.",
        "references": "- Script: `experiments/scripts/eureka_reward_reflector.py`\n- Target: Eliminate 'frozen grip' and 'death clamp' failure modes",
        "subtasks": [
            {
                "name": "Diagnose training failure modes from telemetry logs",
                "desc": "Identify whether policy exhibits 'frozen grip' (refusal to squeeze) or 'death clamp' (crushing).",
                "status": "Open"
            },
            {
                "name": "Run automated LLM reflection loop to refine penalty weights",
                "desc": "Iterate lambda_crush and lambda_slip using automated feedback over training curve metrics.",
                "status": "Open"
            },
            {
                "name": "Lock updated reward configuration in experiments/configs/",
                "desc": "Save Pareto-optimal reward configuration for master training runs.",
                "status": "Open"
            }
        ]
    },
    12: {
        "title": "Disturbance Frequency Sweep & Exam Buffer",
        "summary": "Evaluate policy robustness across varying sawing frequencies while allocating study and buffer time for Fall semester university examinations.",
        "deliverable": "Frequency response robustness curve ($f \\in [1.0, 5.0]\\text{ Hz}$) confirming stable grasp retention.",
        "references": "- Evaluation Script: `experiments/scripts/eval_frequency_sweep.py`\n- Metric: Max slip $\\Delta d_{slip} < 5\\text{ mm}$ across all frequencies",
        "subtasks": [
            {
                "name": "Run frequency sweep evaluation across f in [1.0, 5.0] Hz",
                "desc": "Log slip distance and peak normal force across 100 test episodes per frequency point.",
                "status": "Open"
            },
            {
                "name": "Generate frequency robustness plot",
                "desc": "Plot peak normal force and slip distance vs disturbance frequency.",
                "status": "Open"
            },
            {
                "name": "Fall semester university exam buffer",
                "desc": "Dedicate required time to academic coursework and examinations.",
                "status": "Open"
            }
        ]
    },
    13: {
        "title": "Shahd's Slicing Arm Sync & Coordinate Alignment",
        "summary": "Collaborate with Shahd to inspect her Gmsh tetrahedral tomato mesh and align world coordinates between the Left holding arm and Right slicing arm.",
        "deliverable": "Unified bimanual simulation coordinate frame and validated PhysX 5 FEM material parameters.",
        "references": "- Tomato Mesh: `research/simulation/assets/props/tomato/tomato.msh`\n- Material: Young's Modulus $E = 60\\text{ kPa}$, Poisson $\\nu = 0.45$",
        "subtasks": [
            {
                "name": "Inspect Shahd's Gmsh tetrahedral tomato mesh",
                "desc": "Verify mesh node count, element quality, and boundary surface smoothness.",
                "status": "Open"
            },
            {
                "name": "Review PhysX 5 FEM fracture toughness parameters",
                "desc": "Verify Young's modulus, Poisson ratio, and fracture energy threshold.",
                "status": "Open"
            },
            {
                "name": "Enforce world coordinate frame agreement",
                "desc": "Ensure Left holding palm faces +x and Right slicing blade feeds downward from +z.",
                "status": "Open"
            }
        ]
    },
    14: {
        "title": "Single-Arm Holding Checkpoint Lock (Milestone M3)",
        "summary": "Freeze and validate the trained single-arm holding policy checkpoint against formal research Hypothesis H1. Complete Milestone M3.",
        "deliverable": "Locked checkpoint `experiments/runs/holding_policy_v1.pt` achieving $< 5.0\\text{ N}$ normal force in $\\ge 95\\%$ of trials.",
        "references": "- Checkpoint: `experiments/runs/holding_policy_v1.pt`\n- Hypothesis H1: Grasp stability without crushing under sawing disturbances",
        "subtasks": [
            {
                "name": "Run 100-episode validation benchmark on holding_policy_v1.pt",
                "desc": "Record normal force distribution and confirm F_n < 5.0 N in >= 95% of episodes.",
                "status": "Open"
            },
            {
                "name": "Archive checkpoint weights and evaluation metrics",
                "desc": "Store checkpoint in repository and record metrics in `experiments/results/`.",
                "status": "Open"
            },
            {
                "name": "Update research_state/project_status.yaml for Milestone M3",
                "desc": "Set Milestone M3 status to completed with supporting metric pointers.",
                "status": "Open"
            }
        ]
    },

    # -------------------------------------------------------------------------
    # SPRINT 3: Winter GPU Simulation & Automated Tuning (W15–W18)
    # -------------------------------------------------------------------------
    15: {
        "title": "Headless Multi-Seed PPO Hyperparameter Sweep",
        "summary": "Execute multi-seed training sweeps across 5 independent random seeds during the winter break period. Quantify training convergence variance and stability.",
        "deliverable": "Statistical convergence metrics across seeds (42, 100, 2026, 777, 999) confirming low variance.",
        "references": "- Seeds: 42, 100, 2026, 777, 999\n- Parameter Grid: LR $\\in [10^{-4}, 5 \\times 10^{-4}]$, GAE-$\\lambda \\in [0.90, 0.98]$",
        "subtasks": [
            {
                "name": "Run 5-seed training sweep on RTX 5060",
                "desc": "Execute headless runs for seeds 42, 100, 2026, 777, and 999.",
                "status": "Open"
            },
            {
                "name": "Sweep learning rates and GAE lambda parameters",
                "desc": "Evaluate policy stability across learning rates 1e-4, 3e-4, 5e-4.",
                "status": "Open"
            },
            {
                "name": "Compile multi-seed convergence curves with shaded std error",
                "desc": "Generate publication-grade training curve data for paper Section VI.",
                "status": "Open"
            }
        ]
    },
    16: {
        "title": "Residual Action Space Implementation (ADR-004)",
        "summary": "Implement ADR-004 residual action space for the cutting arm: superimposing policy actions on a nominal sinusoidal sawing motion primitive.",
        "deliverable": "Residual policy architecture restricting exploration to safe contact manifolds around nominal sawing trajectories.",
        "references": "- ADR: `research_state/decisions.md` (ADR-004)\n- Nominal Motion: $v_{x,nom}(t) = A\\omega\\cos(\\omega t), v_{z,nom} = -v_{feed}$",
        "subtasks": [
            {
                "name": "Implement kinematic sawing trajectory generator",
                "desc": "Generate nominal reciprocating sawing velocity: vx(t) = A*omega*cos(omega*t), vz = -v_feed.",
                "status": "Open"
            },
            {
                "name": "Implement residual action adder with bounding clamp",
                "desc": "Clamp residual action Delta_a_t in [-0.02, +0.02] m/s to prevent destructive exploration.",
                "status": "Open"
            },
            {
                "name": "Verify closed-loop primitive execution in Isaac Lab",
                "desc": "Confirm smooth blade motion without abrupt velocity discontinuities.",
                "status": "Open"
            }
        ]
    },
    17: {
        "title": "Literature Deep Dive & Section II Drafting (CNY)",
        "summary": "Index latest 2026/2027 literature on tactile cutting, deformable body manipulation, and residual RL. Draft Section II (Related Work) in IEEEtran LaTeX format.",
        "deliverable": "Complete Section II draft (`paper/sections/02_related_work.tex`) and verified BibTeX references (`paper/references.bib`).",
        "references": "- Related Work: `paper/sections/02_related_work.tex`\n- Taxonomy: `literature/taxonomy.md`",
        "subtasks": [
            {
                "name": "Index latest robotic cutting and tactile manipulation literature",
                "desc": "Add DOIs and verified citations to paper/references.bib without hallucinations.",
                "status": "Open"
            },
            {
                "name": "Synthesize scientific taxonomy and research gaps",
                "desc": "Contrast existing rigid cutting methods against our proprioceptive adaptive impedance formulation.",
                "status": "Open"
            },
            {
                "name": "Draft Section II (Related Work) in IEEEtran format",
                "desc": "Author comprehensive 1.5-page Related Work section in LaTeX.",
                "status": "Open"
            }
        ]
    },
    18: {
        "title": "Automated Domain Randomization (DrEureka Bounds)",
        "summary": "Formulate automated physics parameter distributions in PhysX 5 FEM to ensure robust zero-shot sim-to-real transfer. Lock Milestone M4.",
        "deliverable": "Domain randomization configuration (`domain_rand_cfg.py`) covering Young's modulus, friction, and fracture limits.",
        "references": "- Milestone: M4 (Winter GPU Sim & Automated Tuning)\n- Randomization: $E \\in [30, 120]\\text{ kPa}$, $\\mu \\in [0.25, 0.75]$, $\\sigma_c \\pm 30\\%$",
        "subtasks": [
            {
                "name": "Randomize tomato Young's modulus E in [30, 120] kPa",
                "desc": "Cover soft/overripe to firm/unripe mechanical compliance regimes.",
                "status": "Open"
            },
            {
                "name": "Randomize contact friction and blade sharpness parameters",
                "desc": "Vary friction coefficient mu in [0.25, 0.75] and knife contact stiffness.",
                "status": "Open"
            },
            {
                "name": "Complete Milestone M4 in project_status.yaml",
                "desc": "Update milestone progress to 100% with domain randomization configuration verified.",
                "status": "Open"
            }
        ]
    },

    # -------------------------------------------------------------------------
    # SPRINT 4: Bimanual Sim & Baselines [Mid-Term] (W19–W26)
    # -------------------------------------------------------------------------
    19: {
        "title": "Bimanual Scene Assembly (BimanualTomatoCuttingEnv)",
        "summary": "Mount both ARX AR5-L6 arms in the Isaac Lab stage (Left holding arm at x=-0.35m, Right slicing arm at x=+0.35m) with cutting board and deformable tomato.",
        "deliverable": "Complete bimanual simulation scene (`bimanual_cutting_env.py`) with both arms and FEM tomato.",
        "references": "- Env: `research/simulation/src/envs/bimanual_cutting_env.py`\n- Embodiment: Dual AR5-L6 + LinkerHand O6 + Culinary Knife",
        "subtasks": [
            {
                "name": "Mount dual AR5-L6 arms in Isaac Lab world coordinates",
                "desc": "Place Left holding arm at x = -0.35 m and Right slicing arm at x = +0.35 m facing origin.",
                "status": "Open"
            },
            {
                "name": "Integrate PhysX 5 FEM deformable tomato between hand and blade",
                "desc": "Spawn tetrahedral tomato mesh at (0, 0, 0.75 m) resting on cutting board.",
                "status": "Open"
            },
            {
                "name": "Verify collision geometries and self-collision filters",
                "desc": "Ensure arm links and hand do not self-collide with the cutting board or fixtures.",
                "status": "Open"
            }
        ]
    },
    20: {
        "title": "Slicing & Holding Co-Simulation Verification",
        "summary": "Verify closed-loop bimanual interaction: Left hand establishes 3.0 N holding grasp while Right arm executes sawing cuts at 120 Hz solver substepping.",
        "deliverable": "Stable co-simulation execution without mesh distortion, penetration artifacts, or solver instability.",
        "references": "- Solver Rate: 120 Hz physics substepping, 50 Hz policy evaluation\n- Contact Target: 3.0 N nominal holding force",
        "subtasks": [
            {
                "name": "Execute simultaneous holding grasp and sawing cut",
                "desc": "Left hand holds tomato firmly while Right arm saws through top skin.",
                "status": "Open"
            },
            {
                "name": "Audit PhysX 5 FEM solver convergence at 120 Hz substepping",
                "desc": "Confirm zero inverted tetrahedra and stable contact impulse resolution.",
                "status": "Open"
            }
        ]
    },
    21: {
        "title": "Baseline Execution: Pure Kinematic (EXP-001) & Fixed Impedance (EXP-002)",
        "summary": "Execute mandatory research baselines: EXP-001 (Pure Kinematic Sawing) and EXP-002 (Fixed-Gain Impedance Control) across 5 independent seeds.",
        "deliverable": "Verifiable baseline telemetry logs in `experiments/runs/exp_001/` and `experiments/runs/exp_002/`.",
        "references": "- Baseline 1: EXP-001 (Pure Kinematic Sawing)\n- Baseline 2: EXP-002 (Fixed Task-Space Impedance)",
        "subtasks": [
            {
                "name": "Run EXP-001 across 5 seeds and record crush rate on soft tomatoes",
                "desc": "Measure pulp burst events and normal force spikes with open-loop kinematics.",
                "status": "Open"
            },
            {
                "name": "Run EXP-002 across 5 seeds and record stall rate on firm tomatoes",
                "desc": "Measure blade stalling and incomplete cuts under fixed impedance gains.",
                "status": "Open"
            },
            {
                "name": "Archive baseline telemetry in experiments/runs/",
                "desc": "Store metrics.csv and trajectory logs for each baseline run.",
                "status": "Open"
            }
        ]
    },
    22: {
        "title": "Proposed Method Execution: Tactile Residual RL (EXP-003)",
        "summary": "Execute the proposed tactile residual RL method (EXP-003) across 5 independent seeds. Verify $\\ge 90\\%$ slice completion rate and $\\ge 40\\%$ crush reduction.",
        "deliverable": "Experimental run logs confirming superior performance of proposed method over baselines.",
        "references": "- Experiment: EXP-003 (Proposed Tactile Residual RL)\n- Target: $\\ge 90\\%$ completion rate, $< 5.0\\text{ N}$ peak contact force",
        "subtasks": [
            {
                "name": "Run EXP-003 across 5 random seeds",
                "desc": "Execute proposed residual RL policy with proprioceptive wrench feedback.",
                "status": "Open"
            },
            {
                "name": "Measure slice completion rate, deformation, and pulp burst rate",
                "desc": "Quantify performance across soft, ripe, and firm tomato variations.",
                "status": "Open"
            },
            {
                "name": "Archive run data in experiments/runs/exp_003/",
                "desc": "Export metrics.csv with full force and trajectory logs.",
                "status": "Open"
            }
        ]
    },
    23: {
        "title": "Ablation Suite Execution: EXP-004, EXP-005, EXP-006",
        "summary": "Run architectural ablations: EXP-004 (End-to-End Joint Space RL), EXP-005 (End-to-End Cartesian RL), and EXP-006 (Residual over Kinematic Primitive).",
        "deliverable": "Verifiable ablation comparison confirming Hypothesis H2 ($\sim 5\\times$ sample efficiency improvement).",
        "references": "- EXP-004: 14-DoF Joint Position RL\n- EXP-005: Cartesian Velocity RL\n- EXP-006: Residual over Primitive",
        "subtasks": [
            {
                "name": "Run EXP-004: End-to-End Joint Space RL",
                "desc": "Evaluate sample efficiency and convergence speed of raw joint RL.",
                "status": "Open"
            },
            {
                "name": "Run EXP-005: End-to-End Cartesian Velocity RL",
                "desc": "Evaluate Cartesian velocity RL without nominal motion primitives.",
                "status": "Open"
            },
            {
                "name": "Run EXP-006: Residual over Kinematic Primitive RL",
                "desc": "Demonstrate 5x faster sample efficiency of residual formulation.",
                "status": "Open"
            }
        ]
    },
    24: {
        "title": "Statistical Hypothesis Testing (H1 & H2 Validation)",
        "summary": "Run Mann-Whitney U test and Welch's t-test using `analysis/statistical_tests.py`. Verify paper claims CLAIM-01, CLAIM-02, CLAIM-03 with 95% bootstrap confidence intervals.",
        "deliverable": "Statistical analysis report validating Hypotheses H1 and H2 with $p < 0.01$.",
        "references": "- Script: `analysis/statistical_tests.py`\n- Claims: `research_state/paper_claims.yaml`",
        "subtasks": [
            {
                "name": "Run Mann-Whitney U test and Welch's t-test on benchmark results",
                "desc": "Execute statistical tests comparing proposed method against baselines.",
                "status": "Open"
            },
            {
                "name": "Compute 95% bootstrap confidence intervals for success and crush rates",
                "desc": "Generate rigorous statistical error bounds across 5 seeds.",
                "status": "Open"
            },
            {
                "name": "Validate Claims CLAIM-01, CLAIM-02, CLAIM-03 in paper_claims.yaml",
                "desc": "Verify every claim is mathematically supported by experimental data.",
                "status": "Open"
            }
        ]
    },
    25: {
        "title": "★ INTERNAL MID-TERM CHECKPOINT (Simulation Manuscript Locked)",
        "summary": "Compile simulation experimental results table and convergence plots. Lock simulation manuscript draft for Prof. Shan An's mid-term evaluation. Complete Milestone M5.",
        "deliverable": "Locked simulation paper draft (Sections I–VI) and 100% completion of Milestone M5 in `project_status.yaml`.",
        "references": "- Milestone: M5 (Internal Mid-Term Checkpoint - Simulation Locked)\n- Venue Target: Internal evaluation / RA-L ready draft",
        "subtasks": [
            {
                "name": "Compile simulation experimental results Table I and convergence figures",
                "desc": "Export publication-ready LaTeX tables and high-resolution PDF plots.",
                "status": "Open"
            },
            {
                "name": "Draft simulation manuscript and submit for Prof. Shan An's review",
                "desc": "Present comprehensive mid-term research report to advisor.",
                "status": "Open"
            },
            {
                "name": "Lock Milestone M5 in research_state/project_status.yaml",
                "desc": "Mark Milestone M5 as completed.",
                "status": "Open"
            }
        ]
    },
    26: {
        "title": "Mid-Term Architecture Debrief & Consumables Procurement",
        "summary": "Incorporate advisor feedback from mid-term evaluation. Freeze simulation codebase and order physical experiment consumables (specimen fixtures, knives, test tomatoes).",
        "deliverable": "Procured physical fixtures and finalized hardware bill of materials for laboratory bench setup.",
        "references": "- Hardware BOM: Culinary knives, standardized cutting boards, specimen fixtures\n- Fruit Specimen: 50+ fresh tomatoes across 3 ripeness categories",
        "subtasks": [
            {
                "name": "Resolve outstanding simulation feedback from Prof. Shan An",
                "desc": "Incorporate advisor recommendations and freeze simulation branch.",
                "status": "Open"
            },
            {
                "name": "Procure physical testbed fixtures, knives, and cutting boards",
                "desc": "Order required mechanical hardware and culinary cutting tools.",
                "status": "Open"
            }
        ]
    },

    # -------------------------------------------------------------------------
    # SPRINT 5: Real Hardware Testbed & 1 kHz CAN Loop (W27–W34)
    # -------------------------------------------------------------------------
    27: {
        "title": "Control Workstation & PREEMPT_RT Linux Kernel Setup",
        "summary": "Install Ubuntu 22.04 LTS with PREEMPT_RT real-time patch on laboratory control PC. Verify real-time determinism with worst-case latency jitter $< 50\ \mu\text{s}$ over 1 hour.",
        "deliverable": "Certified real-time control PC running PREEMPT_RT kernel with jitter benchmark logs.",
        "references": "- OS: Ubuntu 22.04 LTS + Linux 6.1-rt\n- Benchmark: `cyclictest -p 99 -m -i 1000 -n`",
        "subtasks": [
            {
                "name": "Install PREEMPT_RT Linux kernel on control workstation",
                "desc": "Configure real-time privileges and thread priorities for control user.",
                "status": "Open"
            },
            {
                "name": "Execute 1-hour cyclictest jitter stress benchmark",
                "desc": "Run cyclictest under heavy CPU load and verify worst-case latency < 50 us.",
                "status": "Open"
            }
        ]
    },
    28: {
        "title": "Dual CAN Bus Interface (can0, can1) 1 kHz RT Loop",
        "summary": "Configure dual SocketCAN interfaces (`can0`, `can1`) at 1 Mbps. Implement deterministic 1 kHz send/receive loop with ARX AR5-L6 motor drivers.",
        "deliverable": "1 kHz deterministic CAN communication node with zero packet drops over 10 minutes.",
        "references": "- Interfaces: `can0` (Left arm), `can1` (Right arm) at 1 Mbps\n- Node: `ros2/drivers/arx_can_driver.cpp`",
        "subtasks": [
            {
                "name": "Configure dual SocketCAN interfaces at 1 Mbps baudrate",
                "desc": "Set up can0 and can1 with appropriate TX queue lengths.",
                "status": "Open"
            },
            {
                "name": "Implement 1 kHz deterministic control loop with AR5-L6 drivers",
                "desc": "Establish 1 kHz joint position/torque command and state feedback loop.",
                "status": "Open"
            },
            {
                "name": "Confirm zero packet drop rate over 10-minute continuous run",
                "desc": "Verify CAN bus load and frame arrival timing jitter.",
                "status": "Open"
            }
        ]
    },
    29: {
        "title": "Gravity & Friction Dynamics Model Calibration",
        "summary": "Calibrate physical robot dynamics: link mass parameters, center of mass, and Coulomb/viscous friction compensation. Verify smooth zero-gravity lead-through mode.",
        "deliverable": "Calibrated physical dynamics model enabling effortless manual zero-gravity arm guidance.",
        "references": "- Model: $\\boldsymbol{\\tau}_{grav}(\\mathbf{q}) + \\boldsymbol{\\tau}_{fric}(\\dot{\\mathbf{q}})$\n- Test: Zero-G lead-through verification",
        "subtasks": [
            {
                "name": "Identify link masses, centers of mass, and joint friction",
                "desc": "Fit dynamic model parameters using excitation trajectories.",
                "status": "Open"
            },
            {
                "name": "Implement friction compensation: tau_fric = fc*sgn(qdot) + fv*qdot",
                "desc": "Cancel joint Coulomb friction to improve low-force sensitivity.",
                "status": "Open"
            },
            {
                "name": "Verify smooth zero-gravity lead-through mode by hand",
                "desc": "Confirm arm remains stationary at arbitrary joint configurations without falling.",
                "status": "Open"
            }
        ]
    },
    30: {
        "title": "1 kHz External Wrench Calibration on Physical Arm",
        "summary": "Mount calibrated force gauge to LinkerHand O6 palm. Apply known static and dynamic loads (1N, 2N, 5N) and confirm wrench observer error $< 0.3\text{ N}$.",
        "deliverable": "Physical force calibration dataset confirming observer accuracy within $< 0.3\text{ N}$.",
        "references": "- Equipment: Digital force gauge / 6-axis ATI Mini40 sensor\n- Verification: Calibration curve in `experiments/results/wrench_calibration.csv`",
        "subtasks": [
            {
                "name": "Mount digital force gauge to LinkerHand O6 palm",
                "desc": "Secure calibrated load sensor for ground-truth force measurement.",
                "status": "Open"
            },
            {
                "name": "Apply known forces (1N, 2N, 5N, 10N) and compare against observer",
                "desc": "Record estimated F_ext vs ground-truth force gauge readings.",
                "status": "Open"
            },
            {
                "name": "Confirm observer reconstruction error < 0.3 N in operating regime",
                "desc": "Validate accuracy across 1.5 N to 5.0 N holding force range.",
                "status": "Open"
            }
        ]
    },
    31: {
        "title": "LinkerHand O6 Physical Driver & Tendon Calibration",
        "summary": "Bring up physical LinkerHand O6 5-finger dexterous hand. Calibrate zero-position motor encoders and passive tendon tensions across all 5 digits.",
        "deliverable": "Fully calibrated dexterous hand executing compliant grasps without tendon slippage or motor overheating.",
        "references": "- Hand Driver: `ros2/drivers/linker_hand_node.cpp`\n- Grasp Target: Multi-finger power and pinch grasp primitives",
        "subtasks": [
            {
                "name": "Bring up LinkerHand O6 motor drivers over USB/CAN",
                "desc": "Establish communication with all 6 active actuators.",
                "status": "Open"
            },
            {
                "name": "Calibrate zero-position encoders and passive tendon tensions",
                "desc": "Ensure uniform finger curl and proper return spring tension.",
                "status": "Open"
            },
            {
                "name": "Test compliant multi-finger grasp on soft fruit proxies",
                "desc": "Verify grasp compliance without motor overheating or stall shutdowns.",
                "status": "Open"
            }
        ]
    },
    32: {
        "title": "Hardware Safety Watchdog System (Torque, Cube, E-stop)",
        "summary": "Implement multi-tiered safety watchdogs: joint over-torque cutoff ($|\\tau_i| > 25\\text{ Nm}$), Cartesian work-cell bounding box cube, and hardware E-stop latching.",
        "deliverable": "Certified hardware safety watchdog subsystem preventing collisions, over-torques, and operator injury.",
        "references": "- Torque Limit: $|\\tau_i| < 25\\text{ Nm}$\n- Safety Cube: $35 \\times 35 \\times 30\\text{ cm}$ centered at cutting board",
        "subtasks": [
            {
                "name": "Implement joint torque cutoff watchdog (|tau_i| > 25 Nm)",
                "desc": "Trigger immediate motor brake engagement if any joint torque exceeds threshold.",
                "status": "Open"
            },
            {
                "name": "Implement Cartesian work-cell bounding box safety cube",
                "desc": "Restrict tool and palm motions strictly within 35x35x30 cm workspace.",
                "status": "Open"
            },
            {
                "name": "Integrate physical emergency E-stop button with hardware latching relay",
                "desc": "Verify instant power cutoff on emergency stop trigger.",
                "status": "Open"
            }
        ]
    },
    33: {
        "title": "MoveIt 2 Cartesian Sawing Trajectory Integration",
        "summary": "Configure MoveIt 2 Cartesian servo node for Right AR5-L6 slicing arm. Generate smooth sinusoidal sawing trajectory with zero jerk violations.",
        "deliverable": "MoveIt 2 Cartesian sawing controller tracking reciprocating trajectories at $f = 2\\text{ Hz}$ in free air.",
        "references": "- Package: `ros2/slicing_arm_moveit/`\n- Trajectory: $A = 25\\text{ mm}, f = 2\\text{ Hz}, v_{feed} = 3\\text{ mm/s}$",
        "subtasks": [
            {
                "name": "Configure MoveIt 2 servo node for Right AR5-L6 arm",
                "desc": "Set up kinematic solver and Cartesian velocity controllers.",
                "status": "Open"
            },
            {
                "name": "Generate sinusoidal sawing trajectory (A=25mm, f=2Hz, vfeed=3mm/s)",
                "desc": "Implement smooth feed and sawing trajectory generator.",
                "status": "Open"
            },
            {
                "name": "Test trajectory tracking in free air with zero jerk violations",
                "desc": "Confirm trajectory smoothness and tracking accuracy.",
                "status": "Open"
            }
        ]
    },
    34: {
        "title": "Bimanual Physical Teleoperation & Dry-Run Slicing (Milestone M6)",
        "summary": "Conduct coordinated physical dry runs with 3D-printed dummy tomato fixture. Confirm zero tool-hand collisions and verify blade clearance. Complete Milestone M6.",
        "deliverable": "Successful bimanual dry run on physical testbed and 100% completion of Milestone M6 in `project_status.yaml`.",
        "references": "- Milestone: M6 (Dual AR5-L6 Physical Testbed Commissioning)\n- Clearance: Minimum $20\\text{ mm}$ between culinary blade and finger links",
        "subtasks": [
            {
                "name": "Execute coordinated bimanual dry run with dummy tomato",
                "desc": "Hold dummy tomato with Left hand while Right arm executes sawing strokes.",
                "status": "Open"
            },
            {
                "name": "Verify blade-to-finger safety clearances (> 20 mm at all times)",
                "desc": "Confirm zero collision risk between knife blade and LinkerHand fingers.",
                "status": "Open"
            },
            {
                "name": "Update research_state/project_status.yaml for Milestone M6",
                "desc": "Lock Milestone M6 as completed.",
                "status": "Open"
            }
        ]
    },

    # -------------------------------------------------------------------------
    # SPRINT 6: Sim-to-Real Transfer & Physical Cutting Trials (W35–W43)
    # -------------------------------------------------------------------------
    35: {
        "title": "Policy Export to ONNX / TensorRT & Real-Time C++ Node",
        "summary": "Export trained PyTorch policy network to ONNX and build a real-time TensorRT C++ inference node evaluating at 100 Hz inside the 1 kHz PREEMPT_RT control loop.",
        "deliverable": "Real-time C++ inference node achieving $< 1.5\\text{ ms}$ evaluation latency on workstation GPU.",
        "references": "- Node: `ros2/policy_inference/src/tensorrt_policy_node.cpp`\n- Format: ONNX / TensorRT FP16 engine",
        "subtasks": [
            {
                "name": "Export trained PyTorch policy to ONNX format",
                "desc": "Verify input/output tensor shapes and numerical precision.",
                "status": "Open"
            },
            {
                "name": "Build TensorRT C++ inference engine node",
                "desc": "Compile optimized FP16 execution engine for workstation GPU.",
                "status": "Open"
            },
            {
                "name": "Verify inference execution latency < 1.5 ms at 100 Hz",
                "desc": "Confirm deterministic real-time execution within control loop budget.",
                "status": "Open"
            }
        ]
    },
    36: {
        "title": "Overhead RealSense D435i Camera Extrinsics & AprilTag Calibration",
        "summary": "Mount Intel RealSense D435i camera above the cutting workstation. Calibrate camera extrinsics via AprilTag and configure tomato height deformation tracking $\\Delta h(t)$.",
        "deliverable": "Calibrated overhead vision system streaming real-time tomato deformation measurements.",
        "references": "- Camera: Intel RealSense D435i\n- Metric: Real-time tomato deformation $\\Delta h(t)$ and burst detection",
        "subtasks": [
            {
                "name": "Mount Intel RealSense D435i overhead camera above table",
                "desc": "Position camera for unobstructed top-down view of cutting board.",
                "status": "Open"
            },
            {
                "name": "Perform hand-eye extrinsic calibration using AprilTag board",
                "desc": "Calculate transformation matrix between camera frame and robot base.",
                "status": "Open"
            },
            {
                "name": "Configure real-time tomato deformation tracking Delta_h(t)",
                "desc": "Track tomato height deformation and cross-sectional deflection.",
                "status": "Open"
            }
        ]
    },
    37: {
        "title": "Physical Cutting Trials: 10x Firm Tomatoes",
        "summary": "Conduct 10 physical cutting trials on Firm/Unripe tomatoes ($E \\approx 100\\text{ kPa}$). Record normal force profiles, skin puncture events, and cycle completion times.",
        "deliverable": "Complete dataset of 10 firm tomato slicing trials logged in `experiments/results/physical_trials/`.",
        "references": "- Specimen: 10x Firm/Unripe tomatoes ($E \\approx 100\\text{ kPa}$)\n- Focus: High skin puncture resistance and stall avoidance",
        "subtasks": [
            {
                "name": "Procure 10 standardized firm/unripe test tomatoes",
                "desc": "Measure mass, diameter, and baseline durometer hardness for each specimen.",
                "status": "Open"
            },
            {
                "name": "Execute 10 bimanual slicing trials under adaptive control",
                "desc": "Record normal contact force, blade feed rate, and cycle completion time.",
                "status": "Open"
            },
            {
                "name": "Log trial telemetry in experiments/results/physical_trials/",
                "desc": "Archive force logs, video recordings, and slice success flags.",
                "status": "Open"
            }
        ]
    },
    38: {
        "title": "Physical Cutting Trials: 10x Ripe Tomatoes (Adaptive vs Rigid)",
        "summary": "Conduct 10 physical cutting trials on Ripe/Optimal tomatoes ($E \\approx 60\\text{ kPa}$). Compare proposed adaptive policy against rigid fixed-gain impedance baseline.",
        "deliverable": "Comparative dataset demonstrating significantly lower deformation and pulp leakage with adaptive control.",
        "references": "- Specimen: 10x Ripe tomatoes ($E \\approx 60\\text{ kPa}$)\n- Comparison: 5 adaptive trials vs 5 rigid baseline trials",
        "subtasks": [
            {
                "name": "Procure 10 ripe/optimal test tomatoes",
                "desc": "Standardize specimen sizing and record initial weights.",
                "status": "Open"
            },
            {
                "name": "Execute comparative trials: 5 adaptive vs 5 rigid impedance",
                "desc": "Run cutting trials under identical nominal sawing velocities.",
                "status": "Open"
            },
            {
                "name": "Quantify pulp leakage and skin rupture between methods",
                "desc": "Measure weight difference and deformation curves.",
                "status": "Open"
            }
        ]
    },
    39: {
        "title": "Physical Cutting Trials: 10x Soft Tomatoes (Anti-Crush Verification)",
        "summary": "Conduct 10 physical cutting trials on Soft/Overripe tomatoes ($E \\approx 30\\text{ kPa}$). Verify adaptive grasp relaxation prevents structural crush. Validate Hypothesis H1.",
        "deliverable": "Empirical validation of anti-crushing barrier policy under extreme soft-body compliance.",
        "references": "- Specimen: 10x Soft/Overripe tomatoes ($E \\approx 30\\text{ kPa}$)\n- Hypothesis H1: Zero crush events under $< 5.0\\text{ N}$ contact force",
        "subtasks": [
            {
                "name": "Procure 10 soft/overripe test tomatoes",
                "desc": "Record baseline specimen softness and pulp compliance.",
                "status": "Open"
            },
            {
                "name": "Execute slicing trials with adaptive grasp relaxation",
                "desc": "Verify holding fingers adaptively relax to prevent structural crush.",
                "status": "Open"
            },
            {
                "name": "Validate Hypothesis H1 under extreme compliance",
                "desc": "Confirm zero crushing failures and normal force suppression < 5.0 N.",
                "status": "Open"
            }
        ]
    },
    40: {
        "title": "Sim-to-Real Domain Randomization Benchmark (EXP-007 vs EXP-008)",
        "summary": "Benchmark policy trained without domain randomization (EXP-007) vs policy trained with PhysX 5 FEM domain randomization (EXP-008) on physical robot. Validate Hypothesis H3.",
        "deliverable": "Physical benchmark proving Hypothesis H3 and Claim CLAIM-04 (zero-shot transfer $\\ge 80\\%$).",
        "references": "- EXP-007: Non-DR Policy on physical robot\n- EXP-008: PhysX 5 FEM DR Policy on physical robot",
        "subtasks": [
            {
                "name": "Run physical trials with non-DR policy (EXP-007)",
                "desc": "Evaluate failure rate and sim-to-real gap on physical tomatoes.",
                "status": "Open"
            },
            {
                "name": "Run physical trials with DrEureka DR policy (EXP-008)",
                "desc": "Evaluate transfer success rate across tomato variations.",
                "status": "Open"
            },
            {
                "name": "Validate Hypothesis H3 and Claim CLAIM-04 (>= 80% zero-shot success)",
                "desc": "Document statistical proof for paper Section VI.",
                "status": "Open"
            }
        ]
    },
    41: {
        "title": "Slice Uniformity, Leakage Weight & Cross-Section Macro Photography",
        "summary": "Measure physical cutting quality metrics: juice leakage weight on analytical scale ($g_{juice} / g_{total}$), slice thickness variance $\\sigma_{thickness}^2$, and capture macro cross-section photos.",
        "deliverable": "Quantitative slice quality dataset and high-resolution cross-section photography for publication figure.",
        "references": "- Equipment: Analytical balance (0.01 g precision), digital caliper\n- Output: `analysis/figures/slice_cross_sections.png`",
        "subtasks": [
            {
                "name": "Measure juice leakage weight on analytical balance",
                "desc": "Record pulp fluid loss as a percentage of total specimen mass.",
                "status": "Open"
            },
            {
                "name": "Measure slice thickness uniformity variance across slices",
                "desc": "Measure thickness at 4 cardinal points per slice with digital caliper.",
                "status": "Open"
            },
            {
                "name": "Capture high-resolution macro cross-section photographs",
                "desc": "Photograph clean slice faces vs crushed baseline cuts for Figure 4.",
                "status": "Open"
            }
        ]
    },
    42: {
        "title": "120 FPS High-Speed Video Capture & Failure Mode Taxonomy",
        "summary": "Record 120 FPS high-speed video of skin puncture and sawing phases. Construct failure mode taxonomy (skin slip, shear burst, blade binding) for paper and video.",
        "deliverable": "120 FPS video dataset and classified failure mode taxonomy table.",
        "references": "- Camera: 120 FPS high-speed capture mode\n- Taxonomy: `research_state/failure_taxonomy.md`",
        "subtasks": [
            {
                "name": "Record 120 FPS video of skin puncture and sawing phases",
                "desc": "Capture close-up macro video of blade-skin contact interface.",
                "status": "Open"
            },
            {
                "name": "Categorize physical failure modes across baseline and proposed trials",
                "desc": "Classify occurrences of skin slip, internal shear burst, and blade binding.",
                "status": "Open"
            },
            {
                "name": "Assemble annotated video clips for supplementary submission",
                "desc": "Prepare high-resolution video clips for 3-minute paper video.",
                "status": "Open"
            }
        ]
    },
    43: {
        "title": "Physical Data Archival & research_cli.py verify-claims (Milestone M7)",
        "summary": "Archive all physical trial logs into `experiments/results/physical_trials/`. Run `python scripts/research_cli.py verify-claims` to certify 100% claim backing. Lock Milestone M7.",
        "deliverable": "100% verified research state claims and completion of Milestone M7 in `project_status.yaml`.",
        "references": "- Verification CLI: `python scripts/research_cli.py verify-claims`\n- Milestone: M7 (Physical Trials & Sim-to-Real Benchmark)",
        "subtasks": [
            {
                "name": "Archive all raw physical trial telemetry into experiments/results/",
                "desc": "Store structured CSV logs and metadata for all 30 tomato trials.",
                "status": "Open"
            },
            {
                "name": "Execute python scripts/research_cli.py verify-claims",
                "desc": "Ensure every claim in paper_claims.yaml points to existing verified run files.",
                "status": "Open"
            },
            {
                "name": "Update research_state/project_status.yaml for Milestone M7",
                "desc": "Lock Milestone M7 as completed.",
                "status": "Open"
            }
        ]
    },

    # -------------------------------------------------------------------------
    # SPRINT 7: IEEE Manuscript Authorship & ICRA Submission (W44–W49)
    # -------------------------------------------------------------------------
    44: {
        "title": "Publication Vector Figures (Fig 1, Fig 2, Fig 3, Fig 4)",
        "summary": "Generate publication-grade vector figures: Fig 1 (System Architecture), Fig 2 (4-phase contact force curves), Fig 3 (training convergence curves), Fig 4 (physical trial photo strip).",
        "deliverable": "High-resolution vector PDF figures in `paper/figures/` meeting IEEE ICRA publication standards.",
        "references": "- Figures Dir: `paper/figures/`\n- Format: Vector PDF / 300+ DPI TIFF",
        "subtasks": [
            {
                "name": "Render Fig 1: Bimanual robot embodiment & control architecture",
                "desc": "Diagram dual AR5-L6 setup, wrench observer, and residual RL control flow.",
                "status": "Open"
            },
            {
                "name": "Plot Fig 2: 4-phase contact force curves with shaded error bands",
                "desc": "Compare normal force and feed force between proposed method and baselines.",
                "status": "Open"
            },
            {
                "name": "Plot Fig 3: Simulation convergence curves and ablation efficiency",
                "desc": "Illustrate 5x sample efficiency speedup of residual policy.",
                "status": "Open"
            },
            {
                "name": "Assemble Fig 4: Physical trial photo-strip across 3 ripeness categories",
                "desc": "Show sequential time-lapse of clean tomato slicing across firmness stages.",
                "status": "Open"
            }
        ]
    },
    45: {
        "title": "Draft Section III (System Formulation), IV (Residual RL), V (Experimental Setup)",
        "summary": "Author core technical sections in IEEEtran LaTeX format: Section III (Kinematics & Wrench Observer), Section IV (Residual RL Formulation), Section V (Simulation & Physical Setup).",
        "deliverable": "Complete, mathematically rigorous LaTeX source files for Sections III, IV, and V.",
        "references": "- Section III: `paper/sections/03_system_modeling.tex`\n- Section IV: `paper/sections/04_methodology.tex`\n- Section V: `paper/sections/05_experiments.tex`",
        "subtasks": [
            {
                "name": "Draft Section III: Kinematics, wrench observer, and tomato dynamics",
                "desc": "Detail mathematical derivation of (J^T)^dagger tau_ext observer and filter.",
                "status": "Open"
            },
            {
                "name": "Draft Section IV: Residual RL MDP and barrier reward formulation",
                "desc": "Detail 33D state, 6D residual action space, and quadratic crush barrier.",
                "status": "Open"
            },
            {
                "name": "Draft Section V: Simulation setup, DrEureka DR, and dual AR5 testbed",
                "desc": "Describe Isaac Lab environment, sensor parameters, and real-time loop.",
                "status": "Open"
            }
        ]
    },
    46: {
        "title": "Draft Section VI (Results & Ablation Tables I & II), I (Introduction), VII (Conclusion)",
        "summary": "Compile Table I (Simulation Baselines) and Table II (Physical Trials). Draft Section VI (Results & Discussion), Section I (Introduction & Contributions), Section VII (Conclusion).",
        "deliverable": "Complete 6-page IEEEtran manuscript draft with zero placeholder text.",
        "references": "- Results: `paper/sections/06_results.tex`\n- Main Manuscript: `paper/main.tex`",
        "subtasks": [
            {
                "name": "Compile benchmark Table I (Simulation) and Table II (Physical Trials)",
                "desc": "Populate verified success rates, crush rates, and sample steps.",
                "status": "Open"
            },
            {
                "name": "Draft Section VI: Results, hypothesis validation, and ablation study",
                "desc": "Analyze statistical findings and discuss why proprioceptive adaptation succeeds.",
                "status": "Open"
            },
            {
                "name": "Draft Section I (Introduction) and Section VII (Conclusion & Future Work)",
                "desc": "State core scientific contributions and future research extensions.",
                "status": "Open"
            }
        ]
    },
    47: {
        "title": "3-Minute Narrated Supplementary Video Production",
        "summary": "Produce 3-minute narrated video following IEEE guidelines: voiceover explanation of system architecture, 1 kHz observer, Isaac Sim training, and physical tomato cutting trials.",
        "deliverable": "High-definition MP4 video (< 50 MB, H.264) compliant with IEEE conference submission rules.",
        "references": "- File: `paper/video/icra2028_bimanual_slicing.mp4`\n- Duration: Exactly 3:00 minutes with clear English narration",
        "subtasks": [
            {
                "name": "Script voiceover explaining bimanual coordination and wrench observer",
                "desc": "Write concise, professional audio narration script.",
                "status": "Open"
            },
            {
                "name": "Edit video combining Isaac Sim simulations and physical trials",
                "desc": "Include title cards, force curve overlays, and high-speed cutting footage.",
                "status": "Open"
            },
            {
                "name": "Encode final MP4 video to IEEE specifications (< 50 MB, 1080p)",
                "desc": "Verify audio-visual sync and file size compliance.",
                "status": "Open"
            }
        ]
    },
    48: {
        "title": "Formal Paper Review & IEEEtran Compliance Polish with Prof. Shan An",
        "summary": "Conduct line-by-line manuscript review with Prof. Shan An. Verify IEEEtran formatting, page length (6 pages + references), and citation traceability via `paper/references.bib`.",
        "deliverable": "Camera-ready PDF manuscript fully approved by advisor Prof. Shan An.",
        "references": "- Advisor: Prof. Shan An (安山)\n- Validation: `python scripts/research_cli.py validate`",
        "subtasks": [
            {
                "name": "Conduct line-by-line mathematical review with Prof. Shan An",
                "desc": "Incorporate advisor revisions and polish scientific terminology.",
                "status": "Open"
            },
            {
                "name": "Verify IEEEtran formatting, 6-page layout, and BibTeX citations",
                "desc": "Ensure zero formatting violations, overflow margins, or broken references.",
                "status": "Open"
            },
            {
                "name": "Run automated repository validation suite",
                "desc": "Execute: `python scripts/research_cli.py validate` and ensure all schemas pass.",
                "status": "Open"
            }
        ]
    },
    49: {
        "title": "★ FIRST PUBLICATION DEADLINE: Submit to IEEE ICRA 2028 Portal (Milestone M8)",
        "summary": "Upload final PDF manuscript, supplementary video, and paper metadata to PaperCept submission portal before deadline. Tag repository release and complete Milestone M8.",
        "deliverable": "Confirmed IEEE ICRA 2028 submission receipt and completion of Milestone M8 in `project_status.yaml`.",
        "references": "- Portal: PaperCept ICRA 2028 Submission\n- Deadline: September 15, 2027\n- Milestone: M8 (First Publication Submission)",
        "subtasks": [
            {
                "name": "Upload final PDF manuscript and video to PaperCept submission portal",
                "desc": "Submit camera-ready PDF, supplementary video, and author metadata.",
                "status": "Open"
            },
            {
                "name": "Create repository Git release tag v1.0-icra2028-submission",
                "desc": "Tag master branch and preserve frozen artifacts for peer review.",
                "status": "Open"
            },
            {
                "name": "Lock Milestone M8 in research_state/project_status.yaml",
                "desc": "Celebrate completion of Paper 1 milestone with DEX-ROB Lab team!",
                "status": "Open"
            }
        ]
    }
}

def main():
    print("=" * 65)
    print("CLICKUP SUBTASK CREATION & DESCRIPTION UNIFICATION")
    print("=" * 65)

    # 1. Fetch all sprint lists
    print("1. Fetching sprint lists under Folder 'Research'...")
    folder_resp = api_call(f"https://api.clickup.com/api/v2/folder/{FOLDER_ID}/list")
    if not folder_resp or 'lists' not in folder_resp:
        print("Failed to retrieve lists!")
        sys.exit(1)

    sprint_lists = [l for l in folder_resp['lists'] if 'Sprint' in l['name']]
    sprint_lists.sort(key=lambda x: x['name'])
    print(f"Found {len(sprint_lists)} sprint lists.")

    # 2. Map existing parent tasks
    print("\n2. Scanning existing parent tasks and subtasks...")
    parent_tasks = {} # week_num -> task_dict
    existing_subtask_names = set() # (parent_id, subtask_name)

    for sl in sprint_lists:
        tasks_resp = api_call(f"https://api.clickup.com/api/v2/list/{sl['id']}/task?subtasks=true")
        if not tasks_resp or 'tasks' not in tasks_resp:
            continue
        for t in tasks_resp['tasks']:
            name = t['name']
            if ': W' in name:
                try:
                    w_str = name.split(': W')[1].split(']')[0].strip()
                    w_num = int(w_str)
                    parent_tasks[w_num] = t
                except Exception:
                    pass
            if t.get('parent'):
                existing_subtask_names.add((t['parent'], t['name'].strip()))

    print(f"Mapped {len(parent_tasks)} parent tasks across 7 sprints.")
    print(f"Found {len(existing_subtask_names)} existing subtasks.")

    # 3. Process each week: Update description & create subtasks
    print("\n3. Processing all 49 weeks...")
    total_subtasks_created = 0
    total_desc_updated = 0

    for w_num in range(1, 50):
        if w_num not in parent_tasks:
            print(f" [!] Warning: Parent task for Week {w_num} not found!")
            continue

        parent = parent_tasks[w_num]
        parent_id = parent['id']
        list_id = parent['list']['id']
        w_data = WEEKS_DATA[w_num]

        # Uniform description format
        formatted_desc = f"""### Week {w_num} Objective: {w_data['title']}
{w_data['summary']}

#### Target Deliverable:
{w_data['deliverable']}

#### Key Reference Files & Commands:
{w_data['references']}
"""

        # Update parent task description
        desc_payload = {
            'description': formatted_desc
        }
        api_call(f"https://api.clickup.com/api/v2/task/{parent_id}", data=desc_payload, method='PUT')
        total_desc_updated += 1
        time.sleep(0.3)

        # Create subtasks
        for sub in w_data['subtasks']:
            sub_name = sub['name'].strip()
            if (parent_id, sub_name) in existing_subtask_names:
                # Already exists
                continue

            # Parse priority integer (1=urgent, 2=high, 3=normal, 4=low)
            p_int = 3
            if parent.get('priority') and isinstance(parent['priority'], dict):
                try:
                    p_int = int(parent['priority'].get('id', 3))
                except Exception:
                    p_int = 3

            sub_payload = {
                'name': sub_name,
                'parent': parent_id,
                'assignees': [USER_ID],
                'status': sub['status'],
                'priority': p_int,
                'description': sub.get('desc', '')
            }

            created_sub = api_call(f"https://api.clickup.com/api/v2/list/{list_id}/task", data=sub_payload, method='POST')
            if created_sub and 'id' in created_sub:
                total_subtasks_created += 1
                existing_subtask_names.add((parent_id, sub_name))
            time.sleep(0.35)

        print(f" [W{w_num:02d}] Updated description & synced {len(w_data['subtasks'])} subtasks for {parent['name'][:40]}...")

    print("\n" + "=" * 65)
    print("COMPLETED!")
    print(f"Total task descriptions updated: {total_desc_updated}/49")
    print(f"Total native subtasks created: {total_subtasks_created}")
    print("=" * 65)

if __name__ == '__main__':
    main()
