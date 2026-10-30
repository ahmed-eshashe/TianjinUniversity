import unittest,tempfile,json,copy
from pathlib import Path
from tomato_native_launch_contract import *

class LaunchContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        (self.root/'worker.py').write_text('pass\n')
        (self.root/'config.json').write_text(json.dumps({'purpose':'two_piece_coupon','native_execution_enabled':False}))
        self.req={'purpose':'two_piece_coupon','training':False,'robot_coupling':False,
            'wall_budget_s':60,'not_before_utc':'2026-10-28T09:00:00Z','expires_utc':'2026-10-28T09:02:00Z',
            'source_sha256':{'worker.py':digest(self.root/'worker.py')},
            'config_path':'config.json','config_sha256':digest(self.root/'config.json')}
    def check(self,r=None,now='2026-10-28T09:00:00Z'):
        return validate_request(self.root,r or self.req,now_utc=now)
    def test_valid_still_disabled(self):self.assertFalse(self.check()['execution_enabled'])
    def test_expiry_margin(self):
        with self.assertRaises(ValueError):self.check(now='2026-10-28T09:01:01Z')
    def test_premature(self):
        with self.assertRaises(ValueError):self.check(now='2026-10-28T08:59:59Z')
    def test_source_tamper(self):
        (self.root/'worker.py').write_text('changed')
        with self.assertRaises(ValueError):self.check()
    def test_config_tamper(self):
        (self.root/'config.json').write_text('{}')
        with self.assertRaises(ValueError):self.check()
    def test_scope_and_budget(self):
        for key,value in [('training',True),('robot_coupling',True),('wall_budget_s',61),('wall_budget_s',float('nan'))]:
            r=copy.deepcopy(self.req);r[key]=value
            with self.assertRaises(ValueError):self.check(r)
    def test_no_symlink_or_traversal(self):
        (self.root/'link').symlink_to(self.root/'worker.py')
        for p in ['link','../worker.py',str(self.root/'worker.py')]:
            with self.assertRaises(ValueError):owned_file(self.root,p)
    def test_checkpoint_binding(self):
        req=checkpoint_request(run_id='a',step=3,source_sha256=self.req['source_sha256'])
        (self.root/'state.json').write_text('{}')
        ack={'run_id':'a','committed_step':3,'source_sha256':req['source_sha256'],
             'state_path':'state.json','state_sha256':digest(self.root/'state.json'),'worker_stopped':True}
        self.assertFalse(verify_checkpoint(self.root,req,ack)['native_state_complete'])
        for key,value in [('run_id','b'),('committed_step',2),('worker_stopped',False),('state_sha256','x')]:
            bad=copy.deepcopy(ack);bad[key]=value
            with self.assertRaises(ValueError):verify_checkpoint(self.root,req,bad)
    def test_resource_validation(self):
        self.assertTrue(sample_resources(host_reader=lambda:11e9,gpu_reader=lambda:(0,5*1024**3))['startup_allowed'])
        with self.assertRaises(ValueError):sample_resources(host_reader=lambda:11e9,gpu_reader=lambda:(2,1))
    def test_utc_explicit(self):
        with self.assertRaises(ValueError):utc('2026-10-28T09:00:00')
    def test_actual_adapter_bounded_read_only(self):
        from unittest.mock import patch
        with patch('subprocess.check_output',return_value='100, 8192\n') as query:
            result=actual_resources()
            self.assertEqual(result['free_vram_bytes'],8092*1024**2)
            self.assertEqual(query.call_args.kwargs['timeout'],2)
            self.assertEqual(query.call_args.args[0][0],'nvidia-smi')
    def test_actual_adapter_ambiguous_gpu_refuses(self):
        from unittest.mock import patch
        with patch('subprocess.check_output',return_value='100,8192\n100,8192\n'):
            with self.assertRaises(ValueError):actual_resources()
