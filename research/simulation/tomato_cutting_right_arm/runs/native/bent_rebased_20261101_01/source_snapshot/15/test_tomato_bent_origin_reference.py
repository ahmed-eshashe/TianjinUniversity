import unittest,math
from tomato_bent_origin_reference import origin_for,step
from tomato_two_joint_sequence_reference import geometry,step as local_step
from tomato_offset_contact_reference import world_point
from tomato_isaac_startup_guard import worker_passed
class OriginTests(unittest.TestCase):
    def test_translation_preserves_mechanics(self):
        for yaw in (0.,math.pi/2):
            q=[math.pi/6,-math.pi/3];pose,_=geometry(yaw,q);p=world_point(pose,[.004,.004,0.]);o=origin_for(yaw,q)
            b=dict(q=q,qd=[.01,-.02],p=p,vp=[.03,.04,0.]);translated=dict(b,p=[x+y for x,y in zip(p,o)])
            a=local_step(b,yaw,.01,.005,1750.,1/2400);t=step(translated,yaw,.01,.005,1750.,1/2400,o)
            for key in ('force','wrench','effort_nm'):
                for x,y in zip(a[key],t[key]):self.assertAlmostEqual(x,y,places=12)
            for key in ('q','qd','vp'):
                for x,y in zip(a['after'][key],t['after'][key]):self.assertAlmostEqual(x,y,places=12)
            for x,y,z in zip(a['after']['p'],o,t['after']['p']):self.assertAlmostEqual(x+y,z)
            self.assertLess(math.hypot(*translated['p']),1e-16)
    def test_natural_separation(self):
        q=[math.pi/6,-math.pi/3];o=origin_for(0,q);b=dict(q=q,qd=[0.,0.],p=[0.,0.,0.],vp=[0.,0.,0.]);counts=[]
        for _ in range(32):
            s=step(b,0,.01,.005,1750.,1/2400,o);counts.append(s['signed_depth_m']>0);b=s['after']
        self.assertGreater(sum(counts),1);self.assertFalse(any(counts[-3:]))
    def test_guard(self):
        r=dict(shutdown_requested=True,diagnostic_passed=True,bent_origin_checks_passed=True,bent_origin_cases_completed=2,controlled_steps=32,newton_steps=64,cuda_state_echoes=66,min_coast_steps=3,natural_separation=True)
        self.assertTrue(worker_passed(r,'bent_origin'))
        for k,v in [('controlled_steps',33),('min_coast_steps',2),('natural_separation',False)]:self.assertFalse(worker_passed(dict(r,**{k:v}),'bent_origin'))
