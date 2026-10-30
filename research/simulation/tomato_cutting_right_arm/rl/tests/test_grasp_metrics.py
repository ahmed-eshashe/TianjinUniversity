"""Adversarial oracle fixtures. Synthetic positives do not certify a physical grasp."""
import copy
import json
import math
from pathlib import Path
import sys
import unittest
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from grasp_metrics import GraspEvaluator
from reset_sampler import FlatResetSampler


def fixture():
    contacts=[]
    for part,angle in [('palm',0),('thumb',90),('index',180),('middle',210),('ring',260)]:
        a=math.radians(angle)
        contacts.append({'part':part,'force_n':1.,'on_handle':True,'radial_vector':[math.cos(a),math.sin(a)],
                         'curl_rad':2.2,'proximal':False,'distance_from_tip_m':.025})
    return {'handle_height_m':.96,'handle_in_palm_m':[0,.02,.03],'support_force_n':0.,'support_clearance_m':.05,'contacts':contacts,
            'blade_contact':False,'unsafe_contact':False,'attachment':False,'joint_limit_violation':False,
            'contact_buffer_full':False,'dropped':False}


class DetectorTests(unittest.TestCase):
    def test_contact_result_is_json_serializable(self):
        result=GraspEvaluator(.9).update(fixture(),.05)
        self.assertIsInstance(json.loads(json.dumps(result))['enclosed'],bool)

    def run_hold(self,s):
        evaluator=GraspEvaluator(.9)
        for _ in range(60):result=evaluator.update(s,.05)
        return result

    def test_synthetic_wrap_and_rotations(self):
        for theta in np.linspace(-math.pi,math.pi,13):
            s=fixture()
            rotation=np.array([[math.cos(theta),-math.sin(theta)],[math.sin(theta),math.cos(theta)]])
            for c in s['contacts']:c['radial_vector']=(rotation@c['radial_vector']).tolist()
            self.assertTrue(self.run_hold(s)['success'])

    def test_tip_only_rejected(self):
        s=fixture()
        for c in s['contacts']:c['distance_from_tip_m']=.001
        self.assertFalse(self.run_hold(s)['success'])

    def test_support_and_drop_rejected(self):
        for key,value in [('support_force_n',2.45),('support_clearance_m',0.),('support_force_n',float('nan')),('dropped',True),('handle_height_m',.92)]:
            s=fixture();s[key]=value
            self.assertFalse(self.run_hold(s)['success'])

    def test_unsafe_event_latches(self):
        for key in ['blade_contact','unsafe_contact','attachment','joint_limit_violation','contact_buffer_full']:
            e=GraspEvaluator(.9);s=fixture();s[key]=True;e.update(s,.05)
            s[key]=False
            for _ in range(100):r=e.update(s,.05)
            self.assertFalse(r['success'])

    def test_transient_and_slip(self):
        e=GraspEvaluator(.9);s=fixture()
        for _ in range(59):r=e.update(s,.05)
        self.assertFalse(r['success'])
        s['handle_in_palm_m'][0]=.011
        self.assertFalse(e.update(s,.05)['success'])
        self.assertEqual(e.hold,0.)

    def test_one_sided_contact_rejected(self):
        s=fixture()
        for c in s['contacts']:c['radial_vector']=[1.,0.]
        self.assertFalse(self.run_hold(s)['success'])

    def test_missing_palm_or_thumb_rejected(self):
        for part in ['palm','thumb']:
            s=fixture();s['contacts']=[c for c in s['contacts'] if c['part']!=part]
            self.assertFalse(self.run_hold(s)['success'])

    def test_thumb_must_oppose_fingers(self):
        s=fixture()
        for c in s['contacts']:
            c['radial_vector']=[0.,1.] if c['part'] not in ['thumb','palm'] else ([1.,0.] if c['part']=='thumb' else [0.,-1.])
        extra=copy.deepcopy(s['contacts'][1]);extra['radial_vector']=[-1.,0.];s['contacts'].append(extra)
        self.assertFalse(self.run_hold(s)['success'])

    def test_contacts_on_blade_do_not_count(self):
        s=fixture()
        for c in s['contacts']:c['on_handle']=False
        self.assertFalse(self.run_hold(s)['success'])

    def test_seeded_reset_and_footprint(self):
        points=np.array([[x,y,z] for x in [-.2,.2] for y in [-.02,.02] for z in [-.005,.005]])
        bounds=[[-.15,-.25,0],[.15,.25,.02]]
        a=FlatResetSampler(points,bounds);b=FlatResetSampler(points,bounds)
        cases=a.sample(100)
        self.assertEqual(cases,b.sample(100))
        self.assertTrue(all(c['minimum_edge_margin_m']>=.02-1e-10 for c in cases))
        self.assertFalse(a.at([.14,0],0)['valid'])

if __name__=='__main__':unittest.main()
