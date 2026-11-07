import math,unittest
from tomato_float32_coast_replay import replay,f32

class Float32CoastTests(unittest.TestCase):
    def test_observed_large_origin_rounding_scale(self):
        x=f32(.05);v=f32(-.01);frames=16;dt=1/1200
        final=replay([0.,x,0.],[0.,v,0.],dt,frames)[-1]
        self.assertGreater(abs(final[1]-(x+frames*dt*v)),1e-7)
    def test_near_origin_error_is_smaller(self):
        v=f32(-.01);dt=1/1200
        a=replay([0.,0.,0.],[0.,v,0.],dt,16)[-1][1]
        self.assertLess(abs(a-16*dt*v),1e-9)
    def test_repeated_binary32_additions(self):
        v=[f32(.02),0.,0.];dt=1/1200;expected=f32(0.)
        for _ in range(16):expected=f32(expected+f32(f32(f32(dt)/16)*v[0]))
        self.assertEqual(replay([0.]*3,v,dt,1)[0][0],expected)
    def test_invalid_packets(self):
        with self.assertRaises(ValueError):replay([0.]*3,[0.]*3,0.,16)
        with self.assertRaises(ValueError):replay([0.]*3,[0.]*3,.01,0)
