import ast
from pathlib import Path
import sys
import unittest
from tomato_native_step import StepCadence,EVENTS,step_native_once


class NativeStepSourceTests(unittest.TestCase):
    def test_complete_cadence_has_one_collision_solve_observe_commit(self):
        c=StepCadence(0,0,.01)
        for e in EVENTS:c.mark(e)
        self.assertEqual(c.complete()['events'],list(EVENTS))

    def test_missing_duplicate_and_early_commit_refused(self):
        for events in [('pose','collide'),('pose','pose'),('commit',)]:
            c=StepCadence(0,0,.01)
            with self.assertRaises(ValueError):
                for e in events:c.mark(e)
        with self.assertRaises(ValueError):StepCadence(0,0,.01).complete()

    def test_extra_event_after_commit_refused(self):
        c=StepCadence(0,0,.01)
        for e in EVENTS:c.mark(e)
        with self.assertRaises(ValueError):c.mark('observe')

    def test_metadata_fails_closed(self):
        for x in [(True,0,.01),(-1,0,.01),(0,-1,.01),(0,0,0),(0,0,float('nan'))]:
            with self.assertRaises(ValueError):StepCadence(*x)

    def test_step_default_refuses_before_native_import(self):
        with self.assertRaises(PermissionError):step_native_once({}, {},step=0,start_s=0,dt_s=.01,observer_kernel=None)
        self.assertFalse(any(x.split('.')[0] in {'warp','newton','torch','pxr'} for x in sys.modules))

    def test_source_compilation_is_explicitly_not_native_evaluation(self):
        p=Path(__file__).resolve().parents[1]/'tomato_native_step.py';tree=ast.parse(p.read_text())
        compile(tree,str(p),'exec')
        self.assertFalse(any(isinstance(n,(ast.Import,ast.ImportFrom)) and 'warp' in ast.unparse(n) for n in tree.body))
