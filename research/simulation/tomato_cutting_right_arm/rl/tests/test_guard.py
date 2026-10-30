"""Safety threshold checks without allocating RAM/VRAM or starting a simulator."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from guard_benchmark import resource_action, startup_allowed, HOST_START, HOST_STOP


class ReserveTests(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(resource_action(5_000_000_000, 3*1024**3), 'continue')

    def test_host_warning(self):
        self.assertEqual(resource_action(2_900_000_000, 3*1024**3), 'checkpoint_and_stop')

    def test_gpu_warning(self):
        self.assertEqual(resource_action(5_000_000_000, 1400*1024**2), 'checkpoint_and_stop')

    def test_host_hard_stop(self):
        self.assertEqual(resource_action(1_900_000_000, 3*1024**3), 'stop')

    def test_gpu_hard_stop(self):
        self.assertEqual(resource_action(5_000_000_000, 1000*1024**2), 'stop')

    def test_monitor_failure(self):
        self.assertEqual(resource_action(5_000_000_000, 3*1024**3, 3), 'stop')

    def test_original_linux_kb_units(self):
        self.assertEqual(HOST_START, 5_000_000*1024)
        self.assertEqual(HOST_STOP, 2_000_000*1024)

    def test_original_stop_boundary(self):
        self.assertEqual(resource_action(HOST_STOP-1, 3*1024**3), 'stop')
        self.assertEqual(resource_action(HOST_STOP, 3*1024**3), 'checkpoint_and_stop')

    def test_measured_startup_ram_budget(self):
        self.assertFalse(startup_allowed(9_999_999_999, 5*1024**3))
        self.assertTrue(startup_allowed(10_000_000_000, 5*1024**3))

    def test_measured_startup_gpu_budget(self):
        self.assertFalse(startup_allowed(11_000_000_000, 4*1024**3-1))
        self.assertTrue(startup_allowed(11_000_000_000, 4*1024**3))


if __name__ == '__main__':
    unittest.main()
