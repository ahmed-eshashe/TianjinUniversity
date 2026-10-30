"""Small source-protocol regressions; no model integration or native import."""
import unittest,copy,sys,json,resource,signal,fcntl
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[3];F=Path(__file__).parent
resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55)
now=datetime.now(timezone.utc);assert now<datetime(2026,10,26,4,53,35,tzinfo=timezone.utc)
q=json.loads((R/'runs/offline/tomato_triangle_withdrawal_01/quota_lease.json').read_text());assert 0<=(now-datetime.fromisoformat(q['checked_utc'])).total_seconds()<=480 and q['maximum_reported_used_percent']<45
hs=[]
for n in ['logs/offline_overnight.lock','logs/right_arm_control.lock']:
 h=(R/n).open('a');fcntl.flock(h,fcntl.LOCK_EX|fcntl.LOCK_NB);hs.append(h)
sys.path.insert(0,str(R/'rl'))
from tomato_reclosure_provenance import validate_transition,transition_sources
class Tests(unittest.TestCase):
 def setUp(self):self.old={'passed':True,'backend':'triangle_spectral_withdrawal_v1','depth_mm':0.,'damage_states':[{}]*47,'source_hashes':{'a':'b'}};self.hashes={'a':'b','new':'c'}
 def reject(self,**kw):
  s=copy.deepcopy(self.old);s.update(kw)
  with self.assertRaises(AssertionError):validate_transition(s,self.hashes,0.,-1.)
 def test_withdrawal_valid(self):validate_transition(self.old,self.hashes,0.,-1.)
 def test_inserted_rejected(self):self.reject(depth_mm=.1)
 def test_legacy_backend_rejected(self):self.reject(backend='triangle_withdrawal_v1')
 def test_unaccepted_rejected(self):self.reject(passed=False)
 def test_missing_patch_rejected(self):self.reject(damage_states=[{}]*46)
 def test_source_change_rejected(self):self.reject(source_hashes={'a':'changed'})
 def test_nonzero_initial_drive_rejected(self):
  with self.assertRaises(AssertionError):validate_transition(self.old,self.hashes,.025,-1.)
 def test_reclosure_valid(self):
  s=self.old|{'backend':'triangle_spectral_cleared_reclosure_v1','source_hashes':self.hashes,'depth_mm':-1.,'drive_mm':0.};validate_transition(s,self.hashes,.025,-1.)
 def test_large_drive_rejected(self):
  s=self.old|{'backend':'triangle_spectral_cleared_reclosure_v1','source_hashes':self.hashes,'depth_mm':-1.,'drive_mm':0.}
  with self.assertRaises(AssertionError):validate_transition(s,self.hashes,.05,-1.)
 def test_cleared_pose_mismatch_rejected(self):
  s=self.old|{'backend':'triangle_spectral_cleared_reclosure_v1','source_hashes':self.hashes,'depth_mm':-1.,'drive_mm':0.}
  with self.assertRaises(AssertionError):validate_transition(s,self.hashes,0.,-2.)
 def test_actual_anchor_sources(self):self.assertGreater(len(transition_sources(R)),20)
 def test_worker_only_expected_edits(self):
  old=(R/'rl/offline_tomato_cleared_reclosure.py').read_text();new=(R/'rl/offline_tomato_spectral_reclosure.py').read_text()
  new=new.replace('triangle_spectral_withdrawal_v1','triangle_withdrawal_v1').replace('triangle_spectral_cleared_reclosure_v1','triangle_cleared_reclosure_v1')
  new=new.replace('from tomato_contact_spectral_search import solve_triangle_continuation\n        from tomato_reclosure_provenance import transition_sources,validate_transition','from tomato_contact_continuation import solve_triangle_continuation')
  for line in ['        files.extend([ROOT/n for n in transition_sources(ROOT)])\n','            validate_transition(old,hashes,a.drive_mm,a.depth_mm)\n',"        if [s.__dict__ for s in states]!=[s.__dict__ for s in committed]:flags.append('diagnostic_history_changed')\n"]:new=new.replace(line,'')
  self.assertEqual(old,new)
 def test_auditor_only_expected_edits(self):
  old=(R/'rl/audit_tomato_cleared_reclosure.py').read_text();new=(R/'rl/audit_tomato_spectral_reclosure.py').read_text().replace('triangle_spectral_withdrawal_v1','triangle_withdrawal_v1').replace('triangle_spectral_cleared_reclosure_v1','triangle_cleared_reclosure_v1')
  new=new.replace("        if [v.__dict__ for v in states]!=[v.__dict__ for v in committed]:flags.append('diagnostic_history_changed')\n",'');self.assertEqual(old,new)
r=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests));out={'passed':r.wasSuccessful(),'tests':r.testsRun,'failures':len(r.failures),'errors':len(r.errors),'forbidden_imports':[n for n in sys.modules if n.split('.')[0] in {'newton','warp','torch','isaaclab','isaacsim','omni','pxr'}]};assert not out['forbidden_imports'];(F/'tests.json').write_text(json.dumps(out,indent=2)+'\n');sys.exit(not r.wasSuccessful())
