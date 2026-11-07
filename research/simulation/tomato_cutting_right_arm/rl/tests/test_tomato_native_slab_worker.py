import unittest
from tomato_native_slab_worker import fixture_cases,expected_minimum
from tomato_isaac_startup_guard import worker_passed


class NativeSlabReferenceTests(unittest.TestCase):
    def test_fixed_fixture_count_and_reversals(self):
        cases=fixture_cases();self.assertEqual(len(cases),16)
        for i in range(0,16,2):
            a,b=cases[i:i+2]
            self.assertEqual(a['a'],b['b']);self.assertEqual(a['b'],b['a'])
            self.assertEqual(expected_minimum(a['a'],a['b'],.002),expected_minimum(b['a'],b['b'],.002))

    def test_crossings_have_exact_medial_plane_minimum(self):
        for c in fixture_cases():
            if c['minimum_normal_ambiguous']:
                self.assertEqual(expected_minimum(c['a'],c['b'],.002),-.002)

    def test_unique_and_clear_controls(self):
        self.assertEqual(expected_minimum([0.,0.,.001],[0.,0.,.001],.002),-.001)
        self.assertEqual(expected_minimum([0.,0.,.003],[0.,0.,.003],.002),.001)

    def test_guard_requires_exact_query_scope(self):
        result={'diagnostic_passed':True,'shutdown_requested':True,'slab_optimizer_cases_completed':16,
                'slab_queries_completed':19,'mechanical_steps':0,'force_evaluations':0}
        self.assertTrue(worker_passed(result,'native_slab'))
        for key,value in [('slab_queries_completed',20),('mechanical_steps',1),('force_evaluations',1)]:
            self.assertFalse(worker_passed(dict(result,**{key:value}),'native_slab'))
        self.assertFalse(worker_passed(result,'analytic_forces'))


if __name__=='__main__':unittest.main()
