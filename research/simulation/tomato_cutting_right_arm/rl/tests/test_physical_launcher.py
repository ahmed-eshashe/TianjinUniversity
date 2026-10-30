"""Invalid physical-test modes must be rejected before simulation/resource allocation."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]

class PhysicalLauncherTests(unittest.TestCase):
    def rejected(self,flags):
        with tempfile.TemporaryDirectory() as temporary:
            output=Path(temporary)/'must_not_launch'
            result=subprocess.run([sys.executable,str(ROOT/'rl/guard_benchmark.py'),
                '--output',str(output),'--seconds','10',*flags],capture_output=True,text=True)
            self.assertEqual(result.returncode,2,result.stderr)
            self.assertFalse(output.exists())

    def test_physical_and_native_modes_are_exclusive(self):
        self.rejected(['--phase3-grasp','--native'])

    def test_coordinated_seating_requires_tilt_mode(self):
        self.rejected(['--phase3-grasp','--seating-mode','coordinated'])

    def test_tilt_requires_physical_grasp_mode(self):
        self.rejected(['--in-place-tilt','pitch'])

    def test_physical_mode_does_not_accept_learner_resume(self):
        self.rejected(['--phase3-grasp','--resume','untrusted.pt'])

if __name__=='__main__':unittest.main()
