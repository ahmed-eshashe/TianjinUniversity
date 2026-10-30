import ast
from pathlib import Path
import sys
import unittest
from tomato_soft_contact_observer import check_contact_layout,make_native_observer


class SoftObserverTests(unittest.TestCase):
    def check(self,**kw):
        a=dict(total_count=3,total_capacity=16,body_counts=[2,1],body_capacity=8,
               body_indices=[[0,2],[1]],record_bodies=[0,1,0])
        a.update(kw);return check_contact_layout(**a)

    def test_matching_retained_stream_does_not_prove_candidates(self):
        r=self.check();self.assertTrue(r['retained_stream_matches_adjacency'])
        self.assertFalse(r['broad_phase_completeness_proven'])
        self.assertFalse(r['independent_candidate_completeness_supplied'])

    def test_total_and_body_saturation_refused(self):
        for kw in [dict(total_capacity=3),dict(body_capacity=2),dict(total_count=17)]:
            with self.assertRaises(ValueError):self.check(**kw)

    def test_missing_duplicate_or_wrong_body_adjacency_refused(self):
        for ix in [[[0],[1]],[[0,0],[1]],[[0,1],[2]]]:
            with self.assertRaises(ValueError):self.check(body_indices=ix)

    def test_independent_reference_mismatch_refused(self):
        with self.assertRaises(ValueError):self.check(independent_reference_counts=[3,1])
        with self.assertRaises(ValueError):self.check(independent_reference_counts=[True,1])
        self.assertTrue(self.check(independent_reference_counts=[2,1])['independent_candidate_completeness_supplied'])

    def test_zero_contact_trace_needs_unsaturated_capacity(self):
        r=check_contact_layout(total_count=0,total_capacity=16,body_counts=[0],body_capacity=8,body_indices=[[]],record_bodies=[])
        self.assertFalse(r['broad_phase_completeness_proven'])

    def test_invalid_count_and_body_mapping_refused(self):
        for kw in [dict(total_count=True),dict(body_counts=[-1,1]),dict(record_bodies=[0,1,3])]:
            with self.assertRaises(ValueError):self.check(**kw)

    def test_factory_refuses_before_import(self):
        with self.assertRaises(PermissionError):make_native_observer(expected_helper_sha256='')
        self.assertFalse(any(x.split('.')[0] in {'warp','newton'} for x in sys.modules))

    def test_source_compiles_without_native_evaluation(self):
        p=Path(__file__).resolve().parents[1]/'tomato_soft_contact_observer.py'
        tree=ast.parse(p.read_text());compile(tree,str(p),'exec')
        self.assertFalse(any(isinstance(n,(ast.Import,ast.ImportFrom)) and 'warp' in ast.unparse(n) for n in tree.body))
