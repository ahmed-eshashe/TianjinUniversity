import unittest,copy,json
from tomato_patch_registry import validate_registry
class PatchRegistryTests(unittest.TestCase):
    def data(self):
        return {'version':1,'frame_scope':'fixed_material_normal_x','units':{'position':'m','stiffness':'N/m','area':'m2','fracture_budget':'J'},'source_sha256':{'s':'a'*64},'positions_m':[[0.,0.,0.],[0.,0.,0.]],'node_sides':['slice','remainder'],'pairs':[[0,1]],'reference_gaps_m':[[0.,0.,0.]],'patches':[{'id':'p','original_patch_index':0,'area_m2':.01,'pair_indices':[0],'weights':[1.],'stiffness_n_m':[[100.,0.,0.],[0.,40.,0.],[0.,0.,30.]],'law':{'stiffness_n_m':100.,'area_m2':.01,'peak_traction_pa':10.,'fracture_energy_j_m2':.02,'damping_n_s_m':0.},'fracture_budget_j':.01*.02}],'native_runtime_validated':False,'native_spring_replacement_allowed':False}
    def test_zero_thickness_surface_not_spring(self):self.assertFalse(validate_registry(self.data())['native_spring_replacement_allowed'])
    def test_json_roundtrip(self):self.assertEqual(validate_registry(self.data()),validate_registry(json.loads(json.dumps(self.data()))))
    def test_area_double_count_refused(self):
        d=self.data();d['patches'][0]['fracture_budget_j']*=.01
        with self.assertRaises(ValueError):validate_registry(d)
    def test_weight_scaling_refused(self):
        d=self.data();d['patches'][0]['weights']=[2.]
        with self.assertRaises(ValueError):validate_registry(d)
    def test_pair_side_refused(self):
        d=self.data();d['node_sides'][1]='slice'
        with self.assertRaises(ValueError):validate_registry(d)
    def test_reference_gap_refused(self):
        d=self.data();d['reference_gaps_m'][0][0]=.1
        with self.assertRaises(ValueError):validate_registry(d)
    def test_duplicate_patch_refused(self):
        d=self.data();d['patches'].append(copy.deepcopy(d['patches'][0]))
        with self.assertRaises(ValueError):validate_registry(d)
