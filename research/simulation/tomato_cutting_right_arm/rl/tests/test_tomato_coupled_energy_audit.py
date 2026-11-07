import unittest,json,copy,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'work'))
from audit_coupled_energy import audit_case
class EnergyAuditTests(unittest.TestCase):
 def case(self):return json.loads((ROOT/'runs/native/bent_replay_20261101_01/bent_replay_measurements.json').read_text())['episodes'][0][0]
 def test_saved_native_work_ledger(self):self.assertTrue(audit_case(self.case())['passed'])
 def test_wrong_particle_force_sign_rejected(self):
  c=self.case()
  for s in c['steps']:s['force_n']=[-x for x in s['force_n']]
  with self.assertRaises(ValueError):audit_case(c)
