import unittest,math
from tomato_two_joint_sequence_reference import step,geometry
from tomato_offset_contact_reference import world_point
from tomato_isaac_startup_guard import worker_passed
class BentSequenceTests(unittest.TestCase):
    def trace(self,yaw):
        q=[math.pi/6,-math.pi/3];pose,_=geometry(yaw,q)
        b=dict(q=q,qd=[0.,0.],p=world_point(pose,[.004,.004,0.]),vp=[0.,0.,0.]);trace=[]
        for _ in range(32):
            a=step(b,yaw,.01,.005,1750.,1/2400);trace.append(a);b=a['after']
        return trace
    def test_natural_separation_and_rotation(self):
        a=self.trace(0);b=self.trace(math.pi/2)
        for trace in (a,b):
            self.assertGreater(sum(s['signed_depth_m']>0 for s in trace),1)
            self.assertTrue(all(s['signed_depth_m']<0 and s['force']==[0.,0.,0.] for s in trace[-3:]))
        for x,y in zip(a[-1]['after']['qd'],b[-1]['after']['qd']):self.assertAlmostEqual(x,y)
    def test_contact_normal_turns(self):
        t=self.trace(0);n=[s['normal'] for s in t if s['signed_depth_m']>0]
        self.assertGreater(max(math.dist(x,n[0]) for x in n),1e-5)
    def test_guard(self):
        r=dict(shutdown_requested=True,diagnostic_passed=True,bent_sequence_checks_passed=True,bent_sequence_cases_completed=2,controlled_steps=32,newton_steps=64,cuda_state_echoes=66,min_coast_steps=3,natural_separation=True)
        self.assertTrue(worker_passed(r,'bent_sequence'))
        for k,v in [('newton_steps',63),('min_coast_steps',2),('natural_separation',False)]:self.assertFalse(worker_passed(dict(r,**{k:v}),'bent_sequence'))
