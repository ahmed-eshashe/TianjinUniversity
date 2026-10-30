import unittest,tempfile,json,sys
from pathlib import Path
from unittest.mock import patch
from tomato_native_worker import run,preview,validate_inputs

class WorkerSourceTests(unittest.TestCase):
    def test_native_factory_always_disabled(self):
        for flag in (False,True):
            with self.assertRaises(PermissionError):run(None,None,None,native_execution_authorized=flag)
        self.assertNotIn('newton',sys.modules);self.assertNotIn('warp',sys.modules)
    def test_invalid_scope_before_files(self):
        with self.assertRaises(ValueError):validate_inputs('/unused',{'purpose':'robot','native_execution_enabled':False})
    def test_enabled_configuration_refused(self):
        with self.assertRaises(ValueError):validate_inputs('/unused',{'purpose':'single_blade_coupon','native_execution_enabled':True})
    def test_preview_exact_command_no_process(self):
        with tempfile.TemporaryDirectory() as tmp,patch('tomato_native_worker.validate_inputs',return_value={}),patch('subprocess.Popen') as popen:
            out=Path(tmp)/'new';r=preview(tmp,{'_config_path':'/config.json'},out)
            self.assertIn('tomato_native_worker.py',r['command'][1]);self.assertIn('--output',r['command']);self.assertFalse(r['execution_enabled']);popen.assert_not_called();self.assertFalse(out.exists())
    def test_existing_output_refused(self):
        with tempfile.TemporaryDirectory() as tmp,patch('tomato_native_worker.validate_inputs',return_value={}):
            with self.assertRaises(ValueError):preview(tmp,{'_config_path':'/config.json'},tmp)
