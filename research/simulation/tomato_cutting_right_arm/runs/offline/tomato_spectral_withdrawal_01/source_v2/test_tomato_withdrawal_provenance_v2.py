import unittest,tempfile,hashlib
from pathlib import Path
from tomato_withdrawal_provenance_v2 import validate_transition,verify_files,unchanged_history,withdrawal_anchor,warm_active_rows

class ProvenanceTests(unittest.TestCase):
    def test_compressed_contact_row_mapping(self):
        self.assertEqual(warm_active_rows([True,False,True,False,True],[.2,0,.3,0,.4]),[0,1,2])
    def test_withdrawn_rows_not_warmed(self):
        self.assertEqual(warm_active_rows([True,False,True],[0.,.5,.7]),[1])
    def test_mapping_size_mismatch(self):
        with self.assertRaises(ValueError):warm_active_rows([True],[0,1])
    def anchor(self):return {'passed':True,'backend':'triangle_spectral_evolving_v1','depth_mm':8.,'source_hashes':{'physical':'a'},'damage_states':[{'damage':1.,'kappa_m':.004}], 'energy_j':.1,'fracture_dissipation_j':.2,'cumulative_blade_work_j':.3}
    def test_same_pose_source_transition(self):validate_transition(self.anchor(),{'physical':'a','new':'b'},8.)
    def test_transition_must_hold(self):
        with self.assertRaises(ValueError):validate_transition(self.anchor(),{'physical':'a'},7.99)
    def test_unsupported_and_rejected(self):
        for change in [{'backend':'triangle_evolving_v1'},{'passed':False}]:
            a=self.anchor();a.update(change)
            with self.assertRaises(ValueError):validate_transition(a,{'physical':'a'},8.)
    def test_source_mismatch(self):
        with self.assertRaises(ValueError):validate_transition(self.anchor(),{'physical':'changed'},8.)
    def test_withdrawal_step_range(self):
        a=self.anchor();a['backend']='triangle_spectral_withdrawal_v1'
        validate_transition(a,a['source_hashes'],7.75)
        for depth in [8.001,7.7,float('nan')]:
            with self.assertRaises(ValueError):validate_transition(a,a['source_hashes'],depth)
    def test_withdrawal_sources_exact(self):
        a=self.anchor();a['backend']='triangle_spectral_withdrawal_v1'
        with self.assertRaises(ValueError):validate_transition(a,dict(a['source_hashes'],new='x'),7.9)
    def test_saved_file_hashes(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);(p/'source').write_text('s');(p/'state').write_text('x')
            state={'source_hashes':{'source':hashlib.sha256(b's').hexdigest()},'state_hashes':{'state':hashlib.sha256(b'x').hexdigest()}}
            verify_files(p,p,state)
            (p/'state').write_text('changed')
            with self.assertRaises(ValueError):verify_files(p,p,state)
            (p/'state').write_text('x');(p/'source').write_text('changed')
            with self.assertRaises(ValueError):verify_files(p,p,state)
    def test_no_healing_or_new_damage(self):
        a=self.anchor();b=self.anchor();self.assertTrue(unchanged_history(a,b))
        b['damage_states'][0]['damage']=.9;self.assertFalse(unchanged_history(a,b))
        b=self.anchor();b['damage_states'][0]['kappa_m']=.005;self.assertFalse(unchanged_history(a,b))
    def test_independent_ledger_anchor(self):
        a=self.anchor();anchor=withdrawal_anchor('forward',a,'digest')
        self.assertEqual(anchor['checkpoint'],'forward');self.assertEqual(anchor['cumulative_blade_work_j'],.3)
        a['backend']='triangle_spectral_withdrawal_v1';a['withdrawal_anchor']=anchor;a['energy_j']=.09
        b=withdrawal_anchor('later',a,'other');self.assertEqual(b,anchor);self.assertIsNot(b,anchor)

if __name__=='__main__':unittest.main()
