#!/usr/bin/env python3
import urllib.request
import json

CLICKUP_TOKEN = 'pk_176612914_8AX37HX8WU54TI6HLUK2C2YVR5A5L3JB'
task_id = '869fd1f2u'

test_desc = """## 🎯 Objective: Asset Stabilization & Verification
Master the ARX AR5-L6 7-DoF manipulator and LinkerHand O6 5-finger dexterous hand OpenUSD assets in NVIDIA Isaac Sim. Verify rotor armature conditioning to resolve the 6,000:1 mass ratio ill-conditioning and ensure stable teleoperation without numerical explosions.

---

### 📦 Target Deliverable
Confirmed stable robot physics in NVIDIA Isaac Sim without NaNs, mesh penetrations, or joint velocity blowouts.

---

### 🛠️ Technical References & CLI Commands
- **OpenUSD Stage:** `research/simulation/assets/robots/ar5_l6/usd_clean/ar5_o6_left_combined/ar5_o6_left_combined.usda`
- **Teleoperation Script:** `research/simulation/scripts/control_ar5_teleop.py`
- **Launch Command:**
```bash
/home/omen/isaac-sim/python.sh /media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/research/simulation/scripts/control_ar5_teleop.py
```
"""

payload = {
    'description': test_desc,
    'markdown_description': test_desc
}

req = urllib.request.Request(
    f'https://api.clickup.com/api/v2/task/{task_id}',
    headers={'Authorization': CLICKUP_TOKEN, 'Content-Type': 'application/json'},
    data=json.dumps(payload).encode('utf-8'),
    method='PUT'
)
with urllib.request.urlopen(req) as resp:
    res = json.loads(resp.read().decode())
    print('SUCCESS! W1 updated.')
    print('Description length:', len(res.get('description', '')))
    print('Markdown Description length:', len(res.get('markdown_description', '')))
