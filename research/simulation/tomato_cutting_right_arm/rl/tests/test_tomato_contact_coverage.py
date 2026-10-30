import unittest
from tomato_contact_coverage import *
class CoverageTests(unittest.TestCase):
    def report(self,**kw):
        d=dict(candidate_pairs=[('vertex',0,0),('face',0,0)],emitted_pairs=[('vertex',0,0),('face',0,0)],reference_active_pairs=[('face',0,0)],attempted_count=2,record_capacity=8,body_counts=[2],body_capacity=8,independent_reference_reviewed=True);d.update(kw);return coverage_report(**d)
    def test_matching_still_not_physics(self):self.assertFalse(self.report()['native_contact_validated'])
    def test_vertex_contacts_do_not_cover_face(self):self.assertEqual(self.report(emitted_pairs=[('vertex',0,0)])['status'],'failed_missing_pairs')
    def test_missing_candidate(self):self.assertEqual(self.report(candidate_pairs=[('vertex',0,0)],emitted_pairs=[('vertex',0,0)])['missing_candidate_pairs'],[['face',0,0]])
    def test_saturation_both_levels(self):
        self.assertEqual(self.report(record_capacity=2)['status'],'refused_saturated');self.assertEqual(self.report(body_capacity=2)['status'],'refused_saturated')
    def test_missing_or_unreviewed_reference(self):
        self.assertEqual(self.report(reference_active_pairs=None)['status'],'inconclusive');self.assertEqual(self.report(independent_reference_reviewed=False)['status'],'inconclusive_reference_unreviewed')
    def test_duplicate_identity(self):
        with self.assertRaises(ValueError):self.report(emitted_pairs=[('face',0,0),('face',0,0)])
    def test_challenges_disabled(self):
        self.assertEqual(len(challenge_registry()),10);self.assertTrue(all(not r['execution_enabled'] for r in challenge_registry()))
    def metrics(self,load,work):return {'physical_config_sha256':'a'*64,'peak_load_n':load,'cutting_work_j':work}
    def test_refinement(self):self.assertTrue(refinement_report(self.metrics(1,1),self.metrics(1.01,1.01))['within_provisional_budget'])
    def test_changed_physics_refused(self):
        fine=self.metrics(1,1);fine['physical_config_sha256']='b'*64
        with self.assertRaises(ValueError):refinement_report(self.metrics(1,1),fine)
    def test_no_loosened_target(self):
        with self.assertRaises(ValueError):refinement_report(self.metrics(1,1),self.metrics(1,1),relative_budget=.2)
