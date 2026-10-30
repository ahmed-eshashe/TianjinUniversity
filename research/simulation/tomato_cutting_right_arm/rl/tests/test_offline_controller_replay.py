"""Stored simulator targets provide an independent check on the offline replay."""
import json
from pathlib import Path
import sys
import unittest

from pxr import Usd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from offline_controller_replay import ROOT, HandGeometry, replay


class StoredControllerReplayTests(unittest.TestCase):
    def test_saved_target_is_reproduced_before_and_near_contact_loss(self):
        stage = Usd.Stage.Open(str(ROOT / 'rl/scene/phase3_grasp.usda'))
        model = HandGeometry(stage)
        folder = ROOT / 'runs/rl/phase3/contact_transfer_05'
        records = json.loads((folder / 'trajectory.json').read_text())
        plan = json.loads((folder / 'source_snapshot/docs/rl/contact_seating_plan.json').read_text())
        for control in [661, 761]:
            with self.subTest(control=control):
                result = replay(stage, model, records, plan, control)
                self.assertLess(result['offline_next_target_vs_saved_max_joint_error_rad'], 1e-5)
                self.assertLess(result['offline_desired_vs_saved_max_joint_error_rad'], 1e-5)
                self.assertLess(result['projected_linear_residual_m'], 1e-12)
                self.assertGreater(max(result['saved_command_point_motion_m']), 1e-6)


if __name__ == '__main__':
    unittest.main()
