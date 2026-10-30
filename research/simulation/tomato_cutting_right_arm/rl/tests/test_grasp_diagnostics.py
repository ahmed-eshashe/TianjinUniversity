import ast
from collections import deque
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np
import torch
from pxr import Usd
from scipy.spatial import ConvexHull

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'rl'))
from grasp_diagnostics import raw_contact_snapshot,friction_snapshot,command_motion_diagnostic
from contact_path_control import synchronized_increment
from plan_contact_seating import HandGeometry
from offline_controller_replay import point_motion


class DiagnosticTests(unittest.TestCase):
    def test_subthreshold_points_and_wrench_are_retained_with_hard_budget(self):
        body='/dual_ar5_o6/right_rh_index_distal';knife='/Knife'
        d=raw_contact_snapshot(np.array([[.02],[1.]]),np.array([[0,1.,0],[0,2.,0]]),
            np.array([[1.,0,0],[1.,0,0]]),np.array([[.001],[-.001]]),np.array([[2]]),np.array([[0]]),
            [body],[knife],knife,[],[0,0,0],1/240,max_points=1)
        self.assertTrue(d['points_truncated']);self.assertEqual(d['total_relevant_points'],2)
        self.assertFalse(d['raw_points'][0]['retained_by_oracle_force_filter'])
        self.assertEqual(d['pairs'][0]['below_oracle_threshold_count'],1)
        np.testing.assert_allclose(d['pairs'][0]['normal_vector_sum_backend_n'],[1.02,0,0])
        np.testing.assert_allclose(d['pairs'][0]['normal_moment_about_knife_com_backend_nm'],[0,0,-2.02])
        self.assertFalse(d['shape_feature_identity_available'])

    def test_backend_indices_outside_capacity_are_refused(self):
        with self.assertRaises(ValueError):
            raw_contact_snapshot(np.zeros((1,1)),np.zeros((1,3)),np.zeros((1,3)),np.zeros((1,1)),
                np.array([[2]]),np.array([[0]]),['/dual_ar5_o6/right_rh_index_distal'],['/Knife'],
                '/Knife',[],[0,0,0],1/240)

    def test_friction_has_separate_points_and_explicit_truncation(self):
        d=friction_snapshot(np.ones((2,3)),np.zeros((2,3)),np.array([[2]]),np.array([[0]]),
            ['/dual_ar5_o6/right_rh_index_distal'],['/Knife'],'/Knife',max_points=1)
        self.assertTrue(d['truncated']);self.assertFalse(d['normal_point_correspondence_available'])

    def test_command_fk_matches_independent_stored_replay(self):
        stage=Usd.Stage.Open(str(ROOT/'rl/scene/phase3_grasp.usda'));model=HandGeometry(stage)
        records=json.loads((ROOT/'runs/rl/phase3/contact_transfer_05/trajectory.json').read_text())
        a,b=records[-2:];q=np.array(a['q_rad']);root=model.kin.transforms(q[:7])[model.root];link=model.transforms(q[7:])['right_rh_index_distal']
        contact=next(c for c in a['contacts'] if c['part']=='index')
        br=root[:3,:3]@link[:3,:3];bp=root[:3,3]+root[:3,:3]@link[:3,3]
        local=br.T@(np.array(contact['point_world_m'])-bp)
        anchors=[{'body':'right_rh_index_distal','point_local':local.tolist()}]
        d=command_motion_diagnostic(model.kin,model,anchors,a['command_q_rad'],b['desired_q_rad'],b['command_q_rad'],q,np.eye(3))
        expected=point_motion(model,a['command_q_rad'],b['command_q_rad'],[{'body':'right_rh_index_distal','local':local}],np.eye(3))
        np.testing.assert_allclose(d['saved_target_increment_points_knife_m'],expected,atol=1e-12)

    def test_contact_oracle_evidence_is_unchanged_by_raw_logging(self):
        # Execute the real ContactEvidence.sample against an in-memory USD and a
        # fake backend. No Isaac imports or simulator are needed.
        native=SimpleNamespace(numpy=lambda a:a)
        spec=importlib.util.spec_from_file_location('isolated_contact_evaluator',ROOT/'rl/contact_evaluator.py')
        module=importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules,{'native_contacts':native}):spec.loader.exec_module(module)
        knife='/Knife';body='/dual_ar5_o6/right_rh_index_distal'
        counts=np.array([[2,0,0],[0,0,0]]);starts=np.zeros((2,3),dtype=int)
        def contacts(dt):
            counts[0,0]=2
            return np.array([[.02],[1.]]),np.zeros((2,3)),np.array([[0,1.,0],[0,1.,0]]),np.zeros((2,1)),counts,starts
        def frictions(dt):
            # Installed backend reuses count/start buffers for friction data.
            counts[:]=0
            return np.zeros((2,3)),np.zeros((2,3)),counts,starts
        view=SimpleNamespace(get_contact_data=contacts,get_contact_force_matrix=lambda dt:np.zeros((2,3,3)),get_friction_data=frictions)
        pose=torch.tensor([[0.,0,0,0,0,0,1.]])
        robot=SimpleNamespace(body_names=['right_rh_index_distal','right_rh_hand_base_link'],joint_names=['right_rh_index_mcp_pitch','right_rh_index_dip'],
            root_view=SimpleNamespace(get_link_transforms=lambda:np.array([pose.tolist()[0:1]+pose.tolist()[0:1]])),
            data=SimpleNamespace(joint_pos=SimpleNamespace(torch=torch.tensor([[1.2,1.068]])),
                soft_joint_pos_limits=SimpleNamespace(torch=torch.tensor([[[-10.,10],[-10.,10]]]))))
        env=SimpleNamespace(robot=robot,contact_monitor=SimpleNamespace(view=view,bodies=[body,knife],filters=[knife,'/Board','/Counter'],summary=lambda:[]),
            knife=SimpleNamespace(data=SimpleNamespace(root_link_pose_w=SimpleNamespace(torch=pose))),sim=SimpleNamespace(stage=Usd.Stage.CreateInMemory()),
            knife_com_local_m=[0,0,0],physics_dt=1/240)
        e=module.ContactEvidence.__new__(module.ContactEvidence);e.env=env;e.meta={'knife_path':knife,'board_path':'/Board','counter_path':'/Counter'}
        cube=np.array(list(__import__('itertools').product([-.02,.02],repeat=3)))
        e.handle_hull=ConvexHull(cube).equations;e.blade_hull=ConvexHull(cube+1).equations
        e.centre=np.zeros(3);e.cross_axes=np.eye(3)[1:];e.knife_points=cube
        e.board_lo=e.counter_lo=np.array([100,100,0]);e.board_hi=e.counter_hi=np.array([101,101,0])
        e.tips={'right_rh_index_distal':(np.array([0,0,1.]),.04)}
        baseline=e.sample(record_friction=True);diagnostic=e.sample(record_friction=True,record_raw=True)
        for key,value in baseline.items():self.assertEqual(value,diagnostic[key],key)
        self.assertEqual(len(diagnostic['contacts']),1)
        self.assertEqual(diagnostic['raw_contact_diagnostic']['total_relevant_points'],2)


class CommandPipelinePreservationTests(unittest.TestCase):
    def method(self,path):
        source=ast.parse(path.read_text())
        node=next(n for n in ast.walk(source) if isinstance(n,ast.FunctionDef) and n.name=='_pre_physics_step')
        tree=ast.Module(body=[node],type_ignores=[]);ast.fix_missing_locations(tree)
        namespace={'np':np,'torch':torch,'deque':deque,'controls':123,'phase':'contact_preserving_seating',
                   'synchronized_increment':synchronized_increment,'command_motion_diagnostic':lambda *a:{'checked':True}}
        exec(compile(tree,str(path),'exec'),namespace)
        return namespace['_pre_physics_step'],namespace

    def test_logging_preserves_targets_in_both_modes_including_limits(self):
        original,old_globals=self.method(ROOT/'runs/offline/grasp_refinement_01/source_before/rl/central_grasp.py')
        modified,new_globals=self.method(ROOT/'rl/central_grasp.py')
        for phase in ['contact_preserving_seating','approach']:
            for target,desired in [(0.,.2),(.9999,2.),(-.9999,-2.)]:
                old_globals['phase']=new_globals['phase']=phase
                def env():
                    return SimpleNamespace(ids=list(range(13)),target=torch.full((1,13),target),desired=torch.full((1,13),desired),
                        rolling_diagnostic_context={'kin':None,'model':None,'anchors':[],'knife_rotation':None,'projection':{}},
                        robot=SimpleNamespace(data=SimpleNamespace(joint_pos=SimpleNamespace(torch=torch.zeros(1,13)),
                            soft_joint_pos_limits=SimpleNamespace(torch=torch.tensor([[[-1.,1.]]*13])))))
                a,b=env(),env();original(a,torch.zeros(1,13));modified(b,torch.zeros(1,13))
                torch.testing.assert_close(a.target,b.target,rtol=0,atol=0)
                if phase=='contact_preserving_seating':
                    self.assertEqual(b.command_trace[-1]['limit_clipping_applied'],abs(target)>.99)
                    self.assertEqual(b.command_trace[-1]['applied_q_rad'],b.target[0].tolist())
                    for _ in range(110):modified(b,torch.zeros(1,13))
                    self.assertEqual(len(b.command_trace),96)


if __name__=='__main__':unittest.main()
