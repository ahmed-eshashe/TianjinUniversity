import unittest,math
from tomato_two_joint_sequence_reference import dynamics,geometry,step
from tomato_two_joint_contact_reference import expected_response
from tomato_isaac_startup_guard import worker_passed
class SequenceTests(unittest.TestCase):
    def test_initial_response(self):
        b=dict(q=[0.,0.],qd=[0.,0.],p=[.034,.004,0.],vp=[0.,0.,0.])
        a=step(b,0,.01,.005,1750.,1/2400);r=expected_response(0,a['wrench'],1/2400)
        self.assertEqual(a['after']['qd'],r['velocity'])
    def test_bent_unforced_motion_has_bias(self):
        matrix,bias,acc=dynamics([.2,.5],[1.,-.3],[0.,0.])
        self.assertNotEqual(acc,[0.,0.]);self.assertGreater(matrix[0][0]*matrix[1][1]-matrix[0][1]**2,0)
        for i in range(2):self.assertAlmostEqual(sum(matrix[i][j]*acc[j] for j in range(2))+bias[i],0)
    def test_kinematic_jacobian(self):
        q=[.2,-.4];p,j=geometry(.3,q);eps=1e-7
        for k in range(2):
            x=q.copy();x[k]+=eps;other,_=geometry(.3,x)
            for i in range(3):self.assertAlmostEqual((other[i]-p[i])/eps,j[i][k],places=7)
    def test_natural_separation(self):
        b=dict(q=[0.,0.],qd=[0.,0.],p=[.034,.004,0.],vp=[0.,0.,0.]);counts=[]
        for _ in range(32):
            a=step(b,0,.01,.005,1750.,1/2400);counts.append(a['signed_depth_m']>0);b=a['after']
        self.assertGreater(sum(counts),1);self.assertFalse(any(counts[-3:]))
    def test_guard(self):
        r=dict(shutdown_requested=True,diagnostic_passed=True,two_joint_sequence_checks_passed=True,two_joint_sequence_cases_completed=2,controlled_steps=32,newton_steps=64,cuda_state_echoes=66,min_coast_steps=3,natural_separation=True)
        self.assertTrue(worker_passed(r,'two_joint_sequence'))
        for k,v in [('controlled_steps',33),('min_coast_steps',2),('natural_separation',False)]:self.assertFalse(worker_passed(dict(r,**{k:v}),'two_joint_sequence'))
