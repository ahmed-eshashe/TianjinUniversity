import copy
import unittest
from tomato_episode_contract import validate_export, expected_reset, assert_reset_matches, assert_irreversible


def fixture():
    registry=['body_q_prev','particle_q_prev','contact_warm_start','coupling_snapshot']
    return dict(episode_id='old',seed=7,backend_state_fields=registry,state=dict(
        positions_m=[[0.,0.,0.]],velocities_m_s=[[0.,0.,0.]],
        damage_states=[dict(damage=.2,kappa_m=.001)],edge_hits=[False],
        contact_state=dict(multipliers=[0.],active_ids=[],eligibility=[False]),
        solver_history={k:[] for k in registry},
        work_ledger=dict(tool=0.,fracture=0.),phase_clock_s=0.,previous_action=[0.],
        random_state=dict(seed=7,counter=0),topology_state=dict(active_patches=[0])))


class EpisodeContractTests(unittest.TestCase):
    def test_reset_expected_export_has_no_aliases(self):
        b=fixture();e=expected_reset(b,new_episode_id='new',seed=7)
        e['state']['positions_m'][0][0]=1
        self.assertEqual(b['state']['positions_m'][0][0],0)

    def test_full_matching_reset_export(self):
        e=expected_reset(fixture(),new_episode_id='new',seed=7)
        assert_reset_matches(copy.deepcopy(e),e)

    def test_each_stale_state_field_breaks_reset(self):
        e=expected_reset(fixture(),new_episode_id='new',seed=7)
        for key in e['state']:
            a=copy.deepcopy(e)
            if key=='phase_clock_s':a['state'][key]=1.
            elif key=='damage_states':a['state'][key][0]['damage']=.3
            elif key=='contact_state':a['state'][key]['active_ids']=[0]
            elif key=='solver_history':a['state'][key]['body_q_prev']=[1]
            elif type(a['state'][key]) is dict:a['state'][key]['stale']=1
            else:a['state'][key].append(1)
            with self.subTest(key=key), self.assertRaises(ValueError):assert_reset_matches(a,e)

    def test_missing_and_unknown_fields_rejected(self):
        for key in fixture()['state']:
            a=fixture();del a['state'][key]
            with self.assertRaises(ValueError):validate_export(a)
        a=fixture();a['state']['undeclared_buffer']=[]
        with self.assertRaises(ValueError):validate_export(a)

    def test_missing_backend_buffer_and_new_buffer_require_registry(self):
        a=fixture();del a['state']['solver_history']['coupling_snapshot']
        with self.assertRaises(ValueError):validate_export(a)
        a=fixture();a['state']['solver_history']['extra']=[]
        with self.assertRaises(ValueError):validate_export(a)
        a['backend_state_fields'].append('extra');validate_export(a)

    def test_seed_and_episode_cannot_be_relabelled(self):
        for kw in [dict(new_episode_id='old',seed=7),dict(new_episode_id='new',seed=8)]:
            with self.assertRaises(ValueError):expected_reset(fixture(),**kw)

    def test_eligible_loading_history_can_increase(self):
        a=fixture();b=copy.deepcopy(a);b['state']['damage_states'][0]=dict(damage=.3,kappa_m=.002)
        assert_irreversible(a,b,eligible_patch_ids=[0],phase='loading')

    def test_no_contact_and_withdrawal_cannot_grow_damage(self):
        a=fixture();b=copy.deepcopy(a);b['state']['damage_states'][0]['damage']=.3
        for ids,phase in [([], 'loading'),([0],'withdrawal'),([0],'reclosure')]:
            with self.assertRaises(ValueError):assert_irreversible(a,b,eligible_patch_ids=ids,phase=phase)

    def test_no_healing_of_damage_or_kappa(self):
        for key in ['damage','kappa_m']:
            a=fixture();b=copy.deepcopy(a);b['state']['damage_states'][0][key]=0
            with self.assertRaises(ValueError):assert_irreversible(a,b,eligible_patch_ids=[0],phase='loading')

    def test_cross_episode_transition_rejected(self):
        a=fixture();b=copy.deepcopy(a);b['episode_id']='another'
        with self.assertRaises(ValueError):assert_irreversible(a,b,eligible_patch_ids=[],phase='hold')

    def test_nonfinite_history_and_opaque_state_rejected(self):
        a=fixture();a['state']['damage_states'][0]['kappa_m']=float('inf')
        with self.assertRaises(ValueError):validate_export(a)
        a=fixture();a['state']['random_state']=object()
        with self.assertRaises(ValueError):validate_export(a)
