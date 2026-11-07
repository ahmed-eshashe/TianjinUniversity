"""Read-only archival of matching published material states and tool poses."""
import json, time, shutil, io, zipfile
from pathlib import Path
import numpy as np

folder = Path(__file__).parent / 'robot_cut07'
archive = folder / 'material_states'
archive.mkdir(exist_ok=True)
while True:
    try:
        before = (folder/'cutting_status.json').read_bytes()
        status = json.loads(before)
        dest = archive/f"step_{status['step']:06d}.npz"
        if not dest.exists():
            blob = (folder/'latest_material.npz').read_bytes()
            after = (folder/'cutting_status.json').read_bytes()
            if before == after and (folder/'latest_material.npz').stat().st_mtime_ns <= (folder/'cutting_status.json').stat().st_mtime_ns:
                with np.load(io.BytesIO(blob)) as state:
                    matches = np.array_equal(state['actual_tool_pose'], status['actual_tool_pose_canonical'])
                if matches:
                    pending = dest.with_suffix('.pending')
                    pending.write_bytes(blob)
                    pending.replace(dest)
                    dest.with_suffix('.json').write_bytes(before)
    except (OSError, ValueError, KeyError, EOFError, zipfile.BadZipFile):
        pass
    if (folder/'worker_result.json').exists():
        break
    time.sleep(1.)
(archive/'scope.json').write_text(json.dumps(dict(
    physical_material_states=True, actual_tool_poses=True,
    complete_joint_trajectory=False, video_recorded=False,
    count=len(list(archive.glob('step_*.npz')))), indent=2))
