import unittest,tempfile,json,ast
from pathlib import Path
from tomato_coupon_segment import SegmentJournal,record_diagnostic_step
from tomato_reaction_metadata import endpoint_metadata
class SegmentMetadataTests(unittest.TestCase):
    def row(self):return {'step':0,'start_s':0.,'dt_s':.1,'force_convention':'force_then_moment','spatial_wrench_world_about_com':[[1.,0.,0.,0.,0.,0.]]}
    def meta(self,row):return endpoint_metadata(row,body_pose_xyzw=[0.,0.,0.,0.,0.,0.,1.],body_com_local_m=[0.,0.,0.],body_spatial_velocity=[1.,0.,0.,0.,0.,0.],target_origin_world_m=[0.,0.,0.])
    def test_saved_metadata_and_estimate(self):
        with tempfile.TemporaryDirectory() as tmp:
            j=SegmentJournal(Path(tmp)/'record',run_id='r',episode_id='e',source_sha256={'s':'a'*64});r=self.row();record_diagnostic_step(j,r,self.meta(r));d=json.loads((j.root/'step000000.json').read_text())['diagnostic']
            self.assertEqual(d['endpoint_work_estimate']['estimated_contact_work_on_blade_j'],.1);self.assertFalse(d['endpoint_reaction_metadata']['work_ledger_admissible']);self.assertFalse(d['endpoint_work_estimate']['exact_step_work'])
    def test_mismatched_step_refused_before_commit(self):
        class NeverCommit:
            def commit(self,row):raise AssertionError('must refuse before commit')
        r=self.row();m=self.meta(r);m['step']=1
        with self.assertRaises(ValueError):record_diagnostic_step(NeverCommit(),r,m)
    def test_mislabeled_average_refused(self):
        r=self.row();m=self.meta(r);m['work_ledger_admissible']=True
        with self.assertRaises(ValueError):record_diagnostic_step(None,r,m)
    def test_source_capture_before_commit(self):
        import tomato_coupon_segment
        tree=ast.parse(Path(tomato_coupon_segment.__file__).read_text())
        f=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='run_native_segment')
        calls=[n for n in ast.walk(f) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name)]
        capture=next(n.lineno for n in calls if n.func.id=='capture_metadata');commit=next(n.lineno for n in calls if n.func.id=='record_diagnostic_step')
        self.assertLess(capture,commit)
