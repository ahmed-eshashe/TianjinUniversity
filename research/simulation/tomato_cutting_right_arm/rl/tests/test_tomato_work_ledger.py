import unittest
from dataclasses import replace
from tomato_load_samples import decode_sample
from tomato_work_ledger import StepMotion, integrate_work, energy_balance

I=((1,0,0),(0,1,0),(0,0,1))


class WorkLedgerTests(unittest.TestCase):
    def sample(self, step=0, start=0, dt=.1):
        return decode_sample(body='blade',step=step,start_s=start,dt_s=dt,
            spatial=(2,0,0,0,0,3),convention='force_then_moment',
            quantity='force_N_moment_Nm',frame_rotation=I,
            source_origin_world_m=(0,0,0),target_origin_world_m=(0,0,0),
            interaction='actuator_on_blade')

    def motion(self, step=0, start=0, dt=.1):
        return StepMotion(step,start,dt,'blade',(0,0,0),(.5,0,0),(0,0,2))

    def integrate(self, samples, motions):
        return integrate_work(samples,motions,convention='step_average_load_constant_twist')

    def balance(self, **kw):
        args=dict(initial_energy_j=dict(elastic=0,kinetic=0,gravitational=0),
                  final_energy_j=dict(elastic=.5,kinetic=.1,gravitational=.1),
                  external_work_j=dict(tool=1,fixture=0,other_external=0),
                  dissipation_j=dict(fracture=.2,friction=.1,damping=0),
                  relative_tolerance=.01,absolute_tolerance_j=1e-12)
        args.update(kw);return energy_balance(**args)

    def test_translation_and_rotation_work_have_known_total(self):
        r=self.integrate([self.sample()],[self.motion()])
        self.assertAlmostEqual(r['work_j'],.7);self.assertFalse(r['runtime_physics_validated'])

    def test_reverse_motion_returns_work(self):
        m=replace(self.motion(),velocity_world_m_s=(-.5,0,0),angular_velocity_world_rad_s=(0,0,-2))
        self.assertAlmostEqual(self.integrate([self.sample()],[m])['work_j'],-.7)

    def test_variable_dt_trace_integrated_once(self):
        samples=[self.sample(),self.sample(1,.1,.2)]
        motions=[self.motion(),self.motion(1,.1,.2)]
        self.assertAlmostEqual(self.integrate(samples,motions)['work_j'],2.1)

    def test_missing_motion_and_stale_origin_rejected(self):
        with self.assertRaises(ValueError):self.integrate([self.sample()],[])
        with self.assertRaises(ValueError):self.integrate([self.sample()],[replace(self.motion(),origin_world_m=(1,0,0))])

    def test_unknown_sampling_rule_rejected(self):
        with self.assertRaises(ValueError):integrate_work([self.sample()],[self.motion()],convention='guess')

    def test_full_channel_energy_accounting_balances(self):
        r=self.balance();self.assertTrue(r['balanced']);self.assertAlmostEqual(r['residual_j'],0)

    def test_omitted_fracture_and_wrong_work_sign_fail(self):
        self.assertFalse(self.balance(dissipation_j=dict(fracture=0,friction=.1,damping=0))['balanced'])
        self.assertFalse(self.balance(external_work_j=dict(tool=-1,fixture=0,other_external=0))['balanced'])

    def test_fixture_work_is_not_silently_ignored(self):
        self.assertFalse(self.balance(external_work_j=dict(tool=1,fixture=.2,other_external=0))['balanced'])

    def test_negative_and_nonfinite_dissipation_rejected(self):
        for loss in [-.2,float('nan')]:
            with self.assertRaises(ValueError):self.balance(dissipation_j=dict(fracture=loss,friction=.1,damping=0))

    def test_missing_channels_and_double_counted_gravity_rejected(self):
        with self.assertRaises(ValueError):self.balance(external_work_j=dict(tool=1))
        with self.assertRaises(ValueError):self.balance(external_work_j=dict(tool=1,fixture=0,other_external=0,gravity=.1))

    def test_zero_trace_does_not_claim_physical_success(self):
        z=dict(elastic=0,kinetic=0,gravitational=0)
        r=self.balance(initial_energy_j=z,final_energy_j=z,external_work_j=dict(tool=0,fixture=0,other_external=0),dissipation_j=dict(fracture=0,friction=0,damping=0))
        self.assertTrue(r['balanced']);self.assertTrue(r['zero_activity']);self.assertIsNone(r['relative_residual']);self.assertFalse(r['runtime_physics_validated'])

    def test_tolerances_cannot_be_loosened(self):
        for kw in [dict(relative_tolerance=.02),dict(absolute_tolerance_j=1e-10)]:
            with self.assertRaises(ValueError):self.balance(**kw)
