"""Isolated binding negatives; mocked dependencies do not validate native runtime."""
import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from tomato_supervision_protocol import prepare

class BindingTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.cfg=self.root/'config.json'
        self.cfg.write_text(json.dumps({'source_sha256':{'worker':'a'}}))
        self.request={'config_path':'config.json','source_sha256':{'worker':'a'},'wall_budget_s':60}
        self.v=patch('tomato_supervision_protocol.validate_request');self.v.start();self.addCleanup(self.v.stop)
        self.p=patch('tomato_supervision_protocol.preview',return_value={'execution_enabled':False});self.p.start();self.addCleanup(self.p.stop)
    def call(self,out=None):return prepare(self.root,self.request,out or self.root/'new',now_utc='diagnostic_mock')
    def test_disabled(self):
        a=self.call();self.assertFalse(a['execution_enabled']);self.assertFalse(a['checkpoint_resumable'])
    def test_missing_source(self):
        self.request['source_sha256']={}
        with self.assertRaises(ValueError):self.call()
    def test_extra_source(self):
        self.request['source_sha256']['extra']='b'
        with self.assertRaises(ValueError):self.call()
    def test_outside(self):
        with self.assertRaises(ValueError):self.call(self.root.parent/'outside')
    def test_traversal(self):
        with self.assertRaises(ValueError):self.call(self.root/'x/../new')
    def test_symlink(self):
        (self.root/'alias').symlink_to(self.root,target_is_directory=True)
        with self.assertRaises(ValueError):self.call(self.root/'alias/new')
