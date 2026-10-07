#!/usr/bin/env python3
"""
ClickUp Sprint Restructuring Script
DEX-ROB Lab | School of Electrical & Automation Engineering, Tianjin University
Author: Ahmed (Holding Arm & Sim-to-Real Control) | Research Lead Agent

Restructures the ClickUp Research workspace into clean Agile Sprint Lists:
1. Cleans the flat duplicate tasks from the old 'Tasks' list.
2. Renames 'Tasks' to '📝 General Backlog & Lab Notes'.
3. Creates 7 dedicated Sprint Lists (Sprint 1 through Sprint 7) under Folder 'Research'.
4. Creates '🎯 Milestones & Hypotheses Tracker' list.
5. Populates each Sprint list with its corresponding weekly tasks (Weeks 1 to 49).
"""

import urllib.request
import urllib.error
import json
import time
import os
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from scripts.sync_clickup_roadmap import TASKS_DEF, to_millis, hours_to_millis, START_DATE, USER_ID, CLICKUP_TOKEN

FOLDER_ID = '901214868317'  # Folder: Research
OLD_LIST_ID = '901222387244' # Current flat Tasks list

HEADERS = {
    'Authorization': CLICKUP_TOKEN,
    'Content-Type': 'application/json'
}

SPRINT_LISTS_DEF = [
    {
        "name": "🚀 Sprint 1: Kinematics & Proprioceptive Observer (W1–W6)",
        "weeks": list(range(1, 7)),
        "color": "#4B0082" # Indigo
    },
    {
        "name": "🤖 Sprint 2: Decoupled Holding RL & Sawing Disturbance (W7–W14)",
        "weeks": list(range(7, 15)),
        "color": "#1E90FF" # Dodger Blue
    },
    {
        "name": "❄️ Sprint 3: Winter GPU Simulation & Automated Tuning (W15–W18)",
        "weeks": list(range(15, 19)),
        "color": "#00CED1" # Dark Turquoise
    },
    {
        "name": "⚔️ Sprint 4: Bimanual Sim & Baselines [Mid-Term] (W19–W26)",
        "weeks": list(range(19, 27)),
        "color": "#FFA500" # Orange
    },
    {
        "name": "🦾 Sprint 5: Real Hardware Testbed & 1 kHz CAN Loop (W27–W34)",
        "weeks": list(range(27, 35)),
        "color": "#9370DB" # Medium Purple
    },
    {
        "name": "🍅 Sprint 6: Sim-to-Real Transfer & 30-Tomato Trials (W35–W43)",
        "weeks": list(range(35, 44)),
        "color": "#FF4500" # Orange Red
    },
    {
        "name": "📄 Sprint 7: IEEE Manuscript Authorship & ICRA Sub (W44–W49)",
        "weeks": list(range(44, 50)),
        "color": "#2E8B57" # Sea Green
    }
]

MILESTONES_DEF = [
    {
        "name": "🎯 [Milestone M1] Robot Asset Stabilization & Kinematic Verification",
        "description": "Clean OpenUSD asset conversion of ARX AR5-L6 and LinkerHand O6. Rotor armature conditioning (0.05/0.005) verified with zero physics divergence.",
        "status": "Closed",
        "priority": 1,
        "due_date": datetime(2026, 10, 13, 20, 0, 0),
        "tags": ["Milestone", "M1", "Sprint 1", "COMPLETED"]
    },
    {
        "name": "🎯 [Milestone M2] Manipulator Jacobian & 1 kHz Contact Wrench Observer",
        "description": "Analytical Jacobian J(q) verified against PyTorch autograd (err < 1e-5). 1 kHz external wrench observer F_ext = (J^T)^\\dagger tau_ext with 50 Hz low-pass filter.",
        "status": "in progress",
        "priority": 1,
        "due_date": datetime(2026, 11, 17, 20, 0, 0),
        "tags": ["Milestone", "M2", "Sprint 1", "IN_PROGRESS"]
    },
    {
        "name": "🎯 [Milestone M3] Decoupled Single-Arm Holding RL under Sawing Disturbance",
        "description": "PPO policy in Isaac Lab stabilizes soft tomato against synthetic sawing shear (+/-4N) and normal forces, suppressing crush damage below 5.0 N in >=95% of rollouts.",
        "status": "Open",
        "priority": 1,
        "due_date": datetime(2027, 1, 12, 20, 0, 0),
        "tags": ["Milestone", "M3", "Sprint 2", "H1"]
    },
    {
        "name": "🎯 [Milestone M4] Winter GPU Simulation Sprint & Eureka Automated Tuning",
        "description": "Multi-seed headless training sweeps, DrEureka domain randomization formulation, and ADR-004 residual action space implementation.",
        "status": "Open",
        "priority": 1,
        "due_date": datetime(2027, 2, 16, 20, 0, 0),
        "tags": ["Milestone", "M4", "Sprint 3", "Eureka"]
    },
    {
        "name": "🎯 [Milestone M5] Bimanual Sim & Baselines (EXP-001..006) [Mid-Term Checkpoint]",
        "description": "★ INTERNAL MID-TERM LAB CHECKPOINT: Bimanual cell co-simulation in Isaac Lab. All baselines EXP-001 through EXP-006 executed. Simulation manuscript locked for Prof. Shan An's review.",
        "status": "Open",
        "priority": 1,
        "due_date": datetime(2027, 3, 31, 20, 0, 0),
        "tags": ["Milestone", "M5", "Sprint 4", "GATE_1"]
    },
    {
        "name": "🎯 [Milestone M6] Dual AR5-L6 Real-Time Testbed & 1 kHz CAN Bus Commissioning",
        "description": "PREEMPT_RT kernel (<50 us jitter), dual CAN-FD at 1 Mbps, physical torque calibration, MoveIt 2 Cartesian planning, and physical dry-run slicing.",
        "status": "Open",
        "priority": 1,
        "due_date": datetime(2027, 6, 8, 20, 0, 0),
        "tags": ["Milestone", "M6", "Sprint 5", "Hardware"]
    },
    {
        "name": "🎯 [Milestone M7] Sim-to-Real Domain Randomization & 30-Tomato Trials (EXP-007..008)",
        "description": "Zero-shot physical cutting trials on 30 commercial tomatoes across 3 ripeness categories. 1 kHz CSV telemetry logged, proving Claim CLAIM-04 (>=80% success).",
        "status": "Open",
        "priority": 1,
        "due_date": datetime(2027, 8, 10, 20, 0, 0),
        "tags": ["Milestone", "M7", "Sprint 6", "Physical-Trials"]
    },
    {
        "name": "🎯 [Milestone M8] IEEE ICRA 2028 Camera-Ready Manuscript & Video Submission",
        "description": "★ FIRST PUBLICATION DEADLINE: Final submission to IEEE ICRA 2028 conference portal with 8-page IEEEtran paper, 4 publication figures, and 3-minute narrated video.",
        "status": "Open",
        "priority": 1,
        "due_date": datetime(2027, 9, 15, 20, 0, 0),
        "tags": ["Milestone", "M8", "Sprint 7", "ICRA 2028", "FIRST_DEADLINE"]
    },
    {
        "name": "🔬 [Hypothesis H1] Tactile-Driven Impedance Adaptation Prevents Crushing",
        "description": "Modulating knife-contact normal and tangential impedance via high-rate tactile/torque feedback reduces volumetric tomato crush deformation by >= 40% vs fixed-stiffness position control.",
        "status": "Open",
        "priority": 2,
        "due_date": datetime(2027, 3, 31, 20, 0, 0),
        "tags": ["Hypothesis", "H1", "Theory"]
    },
    {
        "name": "🔬 [Hypothesis H2] Residual Policy Decoupling Accelerates Training Convergence (5x)",
        "description": "Formulating cutting policy as residual Cartesian delta over nominal kinematic sawing primitive converges in 5x fewer environment steps than end-to-end 14-DoF joint RL.",
        "status": "Open",
        "priority": 2,
        "due_date": datetime(2027, 3, 31, 20, 0, 0),
        "tags": ["Hypothesis", "H2", "Theory"]
    },
    {
        "name": "🔬 [Hypothesis H3] PhysX 5 FEM Fracture Domain Randomization Enables Zero-Shot Transfer",
        "description": "Training in Isaac Lab with PhysX 5 FEM parameter randomization (+-40% Young's modulus, +-30% toughness) produces policy capable of zero-shot real-world transfer with >= 80% success.",
        "status": "Open",
        "priority": 2,
        "due_date": datetime(2027, 8, 10, 20, 0, 0),
        "tags": ["Hypothesis", "H3", "Theory"]
    }
]


def clean_flat_tasks():
    """Removes the 49 flat tasks previously added to the old Tasks list."""
    print("1. Cleaning flat roadmap tasks from old list...")
    req = urllib.request.Request(f'https://api.clickup.com/api/v2/list/{OLD_LIST_ID}/task?archived=false&page=0', headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        tasks = data.get('tasks', [])

    deleted_count = 0
    for t in tasks:
        if t['name'].startswith('[Sprint '):
            del_req = urllib.request.Request(f"https://api.clickup.com/api/v2/task/{t['id']}", headers=HEADERS, method='DELETE')
            try:
                with urllib.request.urlopen(del_req) as del_resp:
                    deleted_count += 1
            except Exception as e:
                print(f"Error deleting {t['id']}: {e}")
            time.sleep(0.3)
    print(f"   Deleted {deleted_count} flat tasks from old list.")


def rename_old_list():
    """Renames old list to '📝 General Backlog & Lab Notes'."""
    print("2. Renaming old list to '📝 General Backlog & Lab Notes'...")
    req = urllib.request.Request(
        f'https://api.clickup.com/api/v2/list/{OLD_LIST_ID}',
        data=json.dumps({'name': '📝 General Backlog & Lab Notes'}).encode('utf-8'),
        headers=HEADERS,
        method='PUT'
    )
    try:
        with urllib.request.urlopen(req) as resp:
            print("   List renamed successfully.")
    except Exception as e:
        print(f"   Error renaming list: {e}")


def create_list(folder_id: str, name: str) -> str:
    """Creates a new list inside a folder."""
    req = urllib.request.Request(
        f'https://api.clickup.com/api/v2/folder/{folder_id}/list',
        data=json.dumps({'name': name}).encode('utf-8'),
        headers=HEADERS,
        method='POST'
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        return data['id']


def create_task_in_list(list_id: str, task_def: dict, week_num: int):
    """Creates a task in a specific list."""
    start_dt = START_DATE + timedelta(weeks=week_num - 1)
    due_dt = start_dt + timedelta(days=6, hours=14)

    payload = {
        "name": task_def["name"],
        "description": task_def["description"],
        "assignees": [USER_ID],
        "tags": task_def.get("tags", []),
        "status": task_def.get("status", "Open"),
        "priority": task_def["priority"],
        "start_date": to_millis(start_dt),
        "due_date": to_millis(due_dt),
        "time_estimate": hours_to_millis(task_def["hours"])
    }

    req = urllib.request.Request(
        f'https://api.clickup.com/api/v2/list/{list_id}/task',
        data=json.dumps(payload).encode('utf-8'),
        headers=HEADERS,
        method='POST'
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))


def main():
    print("============================================================")
    print("CLICKUP AGILE SPRINT RESTRUCTURING FOR RESEARCH WORKSPACE")
    print("============================================================")

    # Step 1: Clean old flat tasks
    clean_flat_tasks()

    # Step 2: Rename old list
    rename_old_list()

    # Build week-to-task mapping from TASKS_DEF
    tasks_by_week = {t["week"]: t for t in TASKS_DEF}

    # Step 3: Create Sprint lists and populate tasks
    print("\n3. Creating 7 Dedicated Sprint Lists & Populating Weekly Tasks...")
    for sprint in SPRINT_LISTS_DEF:
        print(f"\n---> Creating List: {sprint['name']}")
        list_id = create_list(FOLDER_ID, sprint['name'])
        time.sleep(0.5)

        for w in sprint['weeks']:
            task_def = tasks_by_week[w]
            res = create_task_in_list(list_id, task_def, w)
            print(f"     [W{w}] Added: {res.get('name')} (ID: {res.get('id')})")
            time.sleep(0.5)

    # Step 4: Create Milestones & Hypotheses Tracker List
    print("\n4. Creating '🎯 Research Milestones & Hypotheses Tracker' List...")
    milestone_list_id = create_list(FOLDER_ID, "🎯 Research Milestones & Hypotheses Tracker")
    time.sleep(0.5)

    for m in MILESTONES_DEF:
        payload = {
            "name": m["name"],
            "description": m["description"],
            "assignees": [USER_ID],
            "tags": m["tags"],
            "status": m["status"],
            "priority": m["priority"],
            "due_date": to_millis(m["due_date"])
        }
        req = urllib.request.Request(
            f'https://api.clickup.com/api/v2/list/{milestone_list_id}/task',
            data=json.dumps(payload).encode('utf-8'),
            headers=HEADERS,
            method='POST'
        )
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                print(f"     [M/H] Added: {data.get('name')} (ID: {data.get('id')})")
        except Exception as e:
            print(f"     Error adding milestone {m['name']}: {e}")
        time.sleep(0.5)

    print("\n============================================================")
    print("CLICKUP SPRINT RESTRUCTURING COMPLETE!")
    print("============================================================")


if __name__ == "__main__":
    main()
