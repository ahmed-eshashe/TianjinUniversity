import unittest,datetime as dt
from tomato_preparation_runner import quota_receipt_ok,GROUPS
class RunnerContractTests(unittest.TestCase):
    def setUp(self):self.now=dt.datetime(2026,10,27,20,tzinfo=dt.timezone.utc)
    def receipt(self,age=0,used=19):return {'checked_utc':(self.now-dt.timedelta(seconds=age)).isoformat(),'windows':[{'usedPercent':used}]}
    def test_fresh_receipt(self):self.assertTrue(quota_receipt_ok(self.receipt(),self.now))
    def test_stale_and_future_refused(self):
        for age in (31,-1):
            with self.assertRaises(ValueError):quota_receipt_ok(self.receipt(age),self.now)
    def test_threshold_and_all_windows(self):
        r=self.receipt();r['windows'].append({'usedPercent':45})
        with self.assertRaises(ValueError):quota_receipt_ok(r,self.now)
    def test_unknown_window_refused(self):
        r=self.receipt();r['windows']=[]
        with self.assertRaises(ValueError):quota_receipt_ok(r,self.now)
    def test_fixed_call_budgets(self):self.assertTrue(all(0<=calls<=12 for _,calls in GROUPS.values()))
