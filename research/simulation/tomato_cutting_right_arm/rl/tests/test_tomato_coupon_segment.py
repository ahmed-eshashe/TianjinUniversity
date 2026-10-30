import unittest,tempfile,json
from pathlib import Path
from tomato_coupon_segment import *

class SegmentTests(unittest.TestCase):
    def journal(self,root):return SegmentJournal(Path(root)/'segment',run_id='r',episode_id='e',source_sha256={'worker':'a'*64})
    def test_chain_and_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            j=self.journal(tmp);h=j.commit({'step':0,'force_n':[0,0,0]});j.commit({'step':1})
            row=json.loads((j.root/'step000001.json').read_text());self.assertEqual(row['previous_record_sha256'],h);self.assertEqual(row['episode_id'],'e');self.assertFalse(row['native_physics_pass'])
    def test_output_reuse_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.journal(tmp)
            with self.assertRaises(FileExistsError):self.journal(tmp)
    def test_skip_and_duplicate(self):
        with tempfile.TemporaryDirectory() as tmp:
            j=self.journal(tmp)
            with self.assertRaises(ValueError):j.commit({'step':1})
            j.commit({'step':0})
            with self.assertRaises(ValueError):j.commit({'step':0})
    def test_nonfinite_not_committed(self):
        with tempfile.TemporaryDirectory() as tmp:
            j=self.journal(tmp)
            with self.assertRaises(ValueError):j.commit({'step':0,'force':float('nan')})
            self.assertEqual(j.next_step,0);self.assertFalse((j.root/'step000000.json').exists())
    def test_checkpoint_honest_partial_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            j=self.journal(tmp);j.commit({'step':0});j.checkpoint({'x':[1]})
            c=json.loads((j.root/'checkpoint000001.json').read_text());self.assertFalse(c['restart_supported']);self.assertFalse(c['native_state_registry_complete'])
    def test_default_refusal_before_runtime(self):
        import sys
        with self.assertRaises(PermissionError):run_native_segment(None,None,None,None,None)
        self.assertNotIn('warp',sys.modules);self.assertNotIn('newton',sys.modules)
    def test_segment_caps_and_disabled_config(self):
        self.assertEqual(validate_segment({'native_execution_enabled':False,'max_steps':12,'dt_s':.001}),(12,.001))
        for n in [0,13,True]:
            with self.assertRaises(ValueError):validate_segment({'native_execution_enabled':False,'max_steps':n,'dt_s':.001})
    def test_static_binding_syntax(self):
        import ast
        ast.parse(Path(__import__('tomato_coupon_segment').__file__).read_text())
