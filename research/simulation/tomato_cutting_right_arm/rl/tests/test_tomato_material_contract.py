import unittest,copy
from tomato_material_contract import validate_registry
from tomato_isaac_startup_guard import worker_passed
class MaterialContractTests(unittest.TestCase):
 def valid(self):return [[[0,1]],[[.001,0.,0.]],[[[100.,0.,0.],[0.,40.,0.],[0.,0.,30.]]],[[100.,.001,.004]],[[0.,0.]],[1],[0,1],2]
 def test_valid(self):self.assertTrue(validate_registry(*self.valid()))
 def test_wrong_colors_and_duplicate_patch_rejected(self):
  a=self.valid();a[6]=[0,0]
  with self.assertRaises(ValueError):validate_registry(*a)
  a=self.valid()
  for i in range(6):a[i]=a[i]*2
  with self.assertRaises(ValueError):validate_registry(*a)
 def test_bad_history_law_and_matrix_rejected(self):
  for index,value in [(4,[[0.,1.1]]),(3,[[100.,.004,.001]]),(2,[[[100.,5.,0.],[0.,40.,0.],[0.,0.,30.]]])]:
   a=self.valid();a[index]=value
   with self.assertRaises(ValueError):validate_registry(*a)
 def test_native_count_contracts(self):
  m=dict(shutdown_requested=True,diagnostic_passed=True,material_checks_passed=True,material_cases_completed=6,newton_steps=6,controlled_steps=6,constitutive_probes=7)
  self.assertTrue(worker_passed(m,'material_operator'))
  self.assertFalse(worker_passed(dict(m,newton_steps=7),'material_operator'))
  c=dict(shutdown_requested=True,diagnostic_passed=True,coupon_checks_passed=True,coupon_cases_completed=5,newton_steps=4,controlled_steps=4,opening_probes=802)
  self.assertTrue(worker_passed(c,'material_coupon'))
  self.assertFalse(worker_passed(dict(c,opening_probes=801),'material_coupon'))

 def test_group_and_contact_count_contracts(self):
  g=dict(shutdown_requested=True,diagnostic_passed=True,group_checks_passed=True,group_cases_completed=6,newton_steps=1,controlled_steps=1,group_probes=4)
  self.assertTrue(worker_passed(g,'group_material'))
  self.assertFalse(worker_passed(dict(g,group_probes=3),'group_material'))
  c=dict(shutdown_requested=True,diagnostic_passed=True,material_contact_passed=True,material_contact_cases=2,newton_steps=2,controlled_steps=2)
  self.assertTrue(worker_passed(c,'material_contact'))
  self.assertFalse(worker_passed(dict(c,material_contact_cases=1),'material_contact'))

 def test_volume_count_contract(self):
  v=dict(shutdown_requested=True,diagnostic_passed=True,volume_coupon_passed=True,volume_coupon_cases=4,newton_steps=3,controlled_steps=3,opening_probes=401)
  self.assertTrue(worker_passed(v,'volume_coupon'))
  for key,value in [('opening_probes',400),('newton_steps',4),('volume_coupon_cases',3)]:
   self.assertFalse(worker_passed(dict(v,**{key:value}),'volume_coupon'))

 def test_actual_model_and_coupling_contracts(self):
  m=dict(shutdown_requested=True,diagnostic_passed=True,full_model_passed=True,full_model_cases=4,newton_steps=9,controlled_steps=9,material_probes=4)
  self.assertTrue(worker_passed(m,'full_model'));self.assertFalse(worker_passed(dict(m,material_probes=3),'full_model'))
  c=dict(shutdown_requested=True,diagnostic_passed=True,full_coupling_passed=True,newton_steps=8,controlled_steps=8,cuda_state_echoes=9)
  self.assertTrue(worker_passed(c,'full_coupling'));self.assertFalse(worker_passed(dict(c,cuda_state_echoes=8),'full_coupling'))
 def test_authored_blade_and_geometry_contracts(self):
  m=dict(shutdown_requested=True,diagnostic_passed=True,full_blade_passed=True,newton_steps=17,controlled_steps=17,cuda_state_echoes=20,full_blade_intervals=16)
  self.assertTrue(worker_passed(m,'full_blade'));self.assertFalse(worker_passed(dict(m,controlled_steps=16),'full_blade'))
  g=dict(shutdown_requested=True,diagnostic_passed=True,exact_blade_geometry_passed=True,newton_steps=0,controlled_steps=0,exact_blade_cases=6,blade_field_queries=128)
  self.assertTrue(worker_passed(g,'exact_blade_geometry'));self.assertFalse(worker_passed(dict(g,newton_steps=1),'exact_blade_geometry'))

 def test_full_damage_fixture_contract(self):
  m=dict(shutdown_requested=True,diagnostic_passed=True,full_damage_passed=True,newton_steps=8,controlled_steps=8,full_damage_intervals=8)
  self.assertTrue(worker_passed(m,'full_damage'));self.assertFalse(worker_passed(dict(m,full_damage_intervals=7),'full_damage'))
