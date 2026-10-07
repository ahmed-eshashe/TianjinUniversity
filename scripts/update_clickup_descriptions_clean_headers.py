#!/usr/bin/env python3
"""
ClickUp Description Formatter - Clean Visual Headers
DEX-ROB Lab | School of Electrical & Automation Engineering, Tianjin University
Author: Ahmed Sameh | Research Lead Agent

Updates all 49 weekly task descriptions to use clean, beautiful ClickUp native headers:
- '## 🎯 Week N Objective: ...' (H2 heading)
- '---' (Visual Divider)
- '### 📦 Target Deliverable' (H3 heading)
- '---' (Visual Divider)
- '### 🛠️ Key Technical References & CLI' (H3 heading)

Eliminates all '####' markers completely.
Preserves all native ClickUp subtasks.
"""

import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import json
import urllib.request
import urllib.error

# Import data dictionary
from scripts.add_clickup_subtasks_and_format_descriptions import WEEKS_DATA, CLICKUP_TOKEN, FOLDER_ID, api_call

def main():
    print("=" * 65)
    print("UPDATING CLICKUP DESCRIPTIONS WITH CLEAN HEADERS (NO '####')")
    print("=" * 65)

    # 1. Fetch sprint lists
    print("1. Fetching sprint lists under Folder 'Research'...")
    folder_resp = api_call(f"https://api.clickup.com/api/v2/folder/{FOLDER_ID}/list")
    if not folder_resp or 'lists' not in folder_resp:
        print("Failed to retrieve lists!")
        sys.exit(1)

    sprint_lists = [l for l in folder_resp['lists'] if 'Sprint' in l['name']]
    sprint_lists.sort(key=lambda x: x['name'])
    print(f"Found {len(sprint_lists)} sprint lists.")

    # 2. Map existing parent tasks
    print("\n2. Scanning parent tasks across sprints...")
    parent_tasks = {}

    for sl in sprint_lists:
        tasks_resp = api_call(f"https://api.clickup.com/api/v2/list/{sl['id']}/task?subtasks=false")
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

    print(f"Mapped {len(parent_tasks)} parent tasks.")

    # 3. Update descriptions for all 49 tasks
    print("\n3. Updating descriptions with clean H2/H3 headers and dividers...")
    updated_count = 0

    for w_num in range(1, 50):
        if w_num not in parent_tasks:
            print(f" [!] Warning: Parent task for Week {w_num} not found!")
            continue

        parent = parent_tasks[w_num]
        parent_id = parent['id']
        w_data = WEEKS_DATA[w_num]

        clean_desc = f"""## 🎯 Week {w_num} Objective: {w_data['title']}
{w_data['summary']}

---

### 📦 Target Deliverable
{w_data['deliverable']}

---

### 🛠️ Key Technical References & CLI
{w_data['references']}
"""

        payload = {
            'description': clean_desc,
            'markdown_description': clean_desc
        }

        api_call(f"https://api.clickup.com/api/v2/task/{parent_id}", data=payload, method='PUT')
        updated_count += 1
        print(f" [W{w_num:02d}] Updated description for {parent['name'][:42]}...")
        time.sleep(0.3)

    print("\n" + "=" * 65)
    print("COMPLETED!")
    print(f"Successfully updated clean descriptions on {updated_count}/49 tasks.")
    print("=" * 65)

if __name__ == '__main__':
    main()
