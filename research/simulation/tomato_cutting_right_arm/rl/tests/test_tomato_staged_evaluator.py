import unittest,copy
from tomato_staged_evaluator import evaluate,STAGES,AUDITS


def records():
    rows=[]
    for i,s in enumerate(STAGES):
        rows.append({'stage':s,'episode_id':'one','start_s':float(i),'end_s':float(i+1),
          'outcome':'completed','audits':{k:{'scope':'native_mechanics','evidence_id':s+'_'+k,'outcome':'passed'} for k in AUDITS}})
    rows[-1].update(topology={'materially_disconnected':True,'all_patches_failed':True,'cross_bulk_couplings':0,'active_cohesive_patches':0,'components':2},blade_absent=True,fixture_bridges_interface=False,continuous_observation=True,independent_motion_verified=True,no_healing=True)
    return rows

class StagedTests(unittest.TestCase):
    def test_candidate_never_native_validation(self):
        r=evaluate(records());self.assertEqual(r['status'],'release_evidence_candidate');self.assertFalse(r['native_runtime_validated'])
    def test_timeout_cannot_advance(self):
        r=records()[:3];r[-1]['outcome']='timeout'
        out=evaluate(r);self.assertEqual(out['next_stage'],'draw_down');self.assertEqual(out['status'],'inconclusive')
    def test_no_depth_success(self):
        r=records();r[-1]['depth_m']=100;r[-1]['topology']['materially_disconnected']=False
        self.assertEqual(evaluate(r)['status'],'partial_attached')
    def test_no_history_splice(self):
        r=records();r[-1]['episode_id']='withdrawal_branch'
        with self.assertRaises(ValueError):evaluate(r)
    def test_no_skips(self):
        with self.assertRaises(ValueError):evaluate(records()[1:])
    def test_no_time_gaps(self):
        r=records();r[1]['start_s']=1.1
        with self.assertRaises(ValueError):evaluate(r)
    def test_short_release(self):
        r=records();r[-1]['end_s']=5.9;self.assertEqual(evaluate(r)['status'],'inconclusive')
    def test_audit_failures_stop_for_review(self):
        for kind in AUDITS:
            r=records();r[2]['audits'][kind]['outcome']='failed'
            self.assertEqual(evaluate(r)['status'],'review_required')
    def test_missing_audit(self):
        r=records();del r[1]['audits']['energy'];self.assertEqual(evaluate(r)['status'],'inconclusive')
    def test_reused_audit(self):
        r=records()
        for a in r[0]['audits'].values():a['evidence_id']='same'
        self.assertEqual(evaluate(r)['status'],'inconclusive')
    def test_no_dynamic_release_from_static_graph(self):
        for key,value in [('independent_motion_verified',False),('no_healing',False),('blade_absent',False),('fixture_bridges_interface',True)]:
            r=records();r[-1][key]=value;self.assertEqual(evaluate(r)['status'],'detached_unverified')
    def test_invalid_time(self):
        r=records();r[0]['end_s']=float('nan')
        with self.assertRaises(ValueError):evaluate(r)
