import unittest
from tomato_supervision_protocol import MonitorProtocol

SAFE=(12_000_000_000,5*1024**3)
WARN=(2_999_999*1024,2*1024**3)
HARD=(1_000_000*1024,2*1024**3)

class ProtocolTests(unittest.TestCase):
    def make(self):return MonitorProtocol(start=10,wall_s=2,checkpoint_grace_s=.5)
    def test_safe(self):self.assertEqual(self.make().tick(10.1,sample=SAFE),'continue')
    def test_warning_once(self):
        p=self.make();self.assertEqual(p.tick(10.1,sample=WARN),'request_checkpoint_once')
        self.assertEqual(p.tick(10.2,sample=WARN),'await_checkpoint_exit')
        self.assertEqual(p.tick(10.3,sample=SAFE),'await_checkpoint_exit')
        self.assertEqual(p.tick(10.6,sample=SAFE),'stop_timeout')
    def test_hard_terminal(self):
        p=self.make();self.assertEqual(p.tick(10.1,sample=HARD),'stop_memory');self.assertEqual(p.tick(10.2,sample=SAFE),'stop')
    def test_errors_reset(self):
        p=self.make();p.tick(10.1);p.tick(10.2);p.tick(10.3,sample=SAFE)
        self.assertEqual(p.tick(10.4),'continue');self.assertEqual(p.errors,1)
    def test_three_errors(self):
        p=self.make();p.tick(10.1);p.tick(10.2,sample=(float('nan'),1))
        self.assertEqual(p.tick(10.3),'stop_monitor_errors')
    def test_bad_clock(self):
        for now in [9,float('nan'),True]:self.assertEqual(self.make().tick(now,sample=SAFE),'stop_invalid_clock')
    def test_wall_deadline(self):self.assertEqual(self.make().tick(12,sample=SAFE),'stop_timeout')
    def test_bad_budgets(self):
        for wall,grace in [(61,1),(0,1),(1,2),(1,float('inf'))]:
            with self.assertRaises(ValueError):MonitorProtocol(start=0,wall_s=wall,checkpoint_grace_s=grace)
