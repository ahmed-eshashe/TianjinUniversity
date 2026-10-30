import unittest
from tomato_load_samples import decode_sample, validate_pair, validate_sequence

I=((1,0,0),(0,1,0),(0,0,1))


class LoadSampleTests(unittest.TestCase):
    def sample(self, **kw):
        args=dict(body='blade',step=0,start_s=0,dt_s=.01,
                  spatial=(0,10,0,0,0,0),convention='force_then_moment',
                  quantity='force_N_moment_Nm',frame_rotation=I,
                  source_origin_world_m=(.1,0,0),target_origin_world_m=(0,0,0),
                  interaction='blade_tomato_contact')
        args.update(kw)
        return decode_sample(**args)

    def test_newton_world_com_moment_shift(self):
        s=self.sample();self.assertEqual(s.force_n,(0,10,0));self.assertEqual(s.moment_nm,(0,0,1))

    def test_declared_reverse_layout(self):
        a=self.sample();b=self.sample(spatial=(0,0,0,0,10,0),convention='moment_then_force')
        self.assertEqual(a,b)

    def test_impulse_converted_once_to_average_force(self):
        s=self.sample(spatial=(0,.1,0,0,0,0),quantity='impulse_Ns_moment_Nms')
        self.assertEqual(s.force_n,(0,10,0));self.assertEqual(s.moment_nm,(0,0,1))

    def test_unknown_units_and_conventions_rejected(self):
        for kw in [dict(quantity='Nmm'),dict(quantity=''),dict(convention='guess')]:
            with self.assertRaises(ValueError):self.sample(**kw)

    def test_invalid_time_rejected(self):
        for dt in [0,-.1,float('nan'),float('inf')]:
            with self.assertRaises(ValueError):self.sample(dt_s=dt)

    def test_pair_rejects_stale_and_other_interaction(self):
        for kw in [dict(step=1),dict(start_s=.01),dict(dt_s=.02),dict(interaction='gravity'),dict(target_origin_world_m=(1,0,0))]:
            with self.assertRaises(ValueError):validate_pair(self.sample(),self.sample(body='tomato',**kw))

    def test_pair_requires_different_bodies(self):
        with self.assertRaises(ValueError):validate_pair(self.sample(),self.sample())
        validate_pair(self.sample(),self.sample(body='tomato'))

    def test_missing_duplicate_or_overlapping_trace_rejected(self):
        for kw in [dict(step=2,start_s=.01),dict(step=0,start_s=.01),dict(step=1,start_s=0),dict(step=1,start_s=.02)]:
            with self.assertRaises(ValueError):validate_sequence([self.sample(),self.sample(**kw)])

    def test_contiguous_variable_dt_trace(self):
        validate_sequence([self.sample(),self.sample(step=1,start_s=.01,dt_s=.02),self.sample(step=2,start_s=.03)])

    def test_empty_trace_and_nonfinite_loads_rejected(self):
        with self.assertRaises(ValueError):validate_sequence([])
        with self.assertRaises(ValueError):self.sample(spatial=(0,float('nan'),0,0,0,0))
