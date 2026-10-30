"""False-success regressions for the offline full-cut qualification."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tomato_full_cut_checks import material_components,cap_contact_witness,separation_status

class FullCutChecks(unittest.TestCase):
    def model(self):
        d={'nodes':[{'side':s} for s in ['slice','slice','remainder','remainder']],
           'bonds':[{'nodes':[0,1]},{'nodes':[2,3]}]}
        a=[{'bond_ids':[0,1],'integration_cells_global_ids':[]}]
        return d,a
    def test_one_tiny_remaining_bridge_prevents_separation(self):
        d,a=self.model();s=material_components(d,a,[[0]],[1.-1e-12],[[1,2]])
        self.assertFalse(s['materially_disconnected']);self.assertEqual(s['components'],1)
    def test_complete_damage_yields_two_material_pieces(self):
        d,a=self.model();s=material_components(d,a,[[0]],[1.],[[1,2]])
        self.assertTrue(s['materially_disconnected']);self.assertEqual(s['components'],2)
    def test_bulk_bridge_prevents_false_success(self):
        d,a=self.model();d['bonds'].append({'nodes':[1,2]});a[0]['bond_ids'].append(2)
        self.assertFalse(material_components(d,a,[[0]],[1.],[[1,2]])['materially_disconnected'])
    def test_volume_coupling_cannot_be_ignored(self):
        d,a=self.model();a[0]['integration_cells_global_ids']=[[0,1,2,3]]
        self.assertFalse(material_components(d,a,[[0]],[1.],[[1,2]])['materially_disconnected'])
    def test_vertex_feasibility_does_not_prove_capped_triangle_clearance(self):
        self.assertAlmostEqual(cap_contact_witness([0.,1.,1.],0.,1.,.5),.125)
    def test_uncapped_or_constant_width_has_no_cap_witness(self):
        self.assertEqual(cap_contact_witness([0.,.1,.2],0.,1.,.5),0.)
        self.assertEqual(cap_contact_witness([1.,2.,3.],0.,1.,.5),0.)
    def test_detachment_is_not_independent_release(self):
        topology={'materially_disconnected':True,'all_patches_failed':True}
        kw={'blade_absent':True,'minimum_gap_m':.001,'relative_translation_verified':True,'no_healing':True}
        self.assertTrue(separation_status(topology,**kw))
        for key,value in [('blade_absent',False),('minimum_gap_m',0.),('relative_translation_verified',False),('no_healing',False)]:
            self.assertFalse(separation_status(topology,**{**kw,key:value}))
        self.assertFalse(separation_status({**topology,'all_patches_failed':False},**kw))
if __name__=='__main__':unittest.main()
