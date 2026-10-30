import copy
import unittest
from tomato_geometry_transfer import inspect_geometry, contact_allowed


def fixture():
    d=dict(nodes=[dict(id=i,side=s,position_m=[i*.01,0,0]) for i,s in enumerate(['slice','slice','remainder','remainder'])],
           bonds=[dict(id=0,nodes=[0,1],rest_length_m=.01,kind='slice'),dict(id=1,nodes=[2,3],rest_length_m=.01,kind='remainder'),dict(id=2,nodes=[1,2],rest_length_m=.01,kind='interface')],
           interface_patches=[dict(area_m2=.001,bond_ids=[2])],pieces=[],fixture=dict(node_ids=[3]),numerical_rest_gap_m=0.)
    a=[dict(global_node_ids=[0,1,2,3],node_mass_kg=[.01]*4,bond_ids=[0,1],integration_cells_global_ids=[])]
    return d,a


class GeometryTransferTests(unittest.TestCase):
    def test_registry_preserves_mass_and_interface_identity(self):
        d,a=fixture();r=inspect_geometry(d,a)
        self.assertEqual(r['total_mass_kg'],.04);self.assertEqual(r['interface_bonds'],1)
        self.assertFalse(r['native_constitutive_equivalence'])

    def test_cross_cut_contact_never_excluded_by_adjacency(self):
        self.assertTrue(contact_allowed('slice','remainder'))
        with self.assertRaises(ValueError):contact_allowed('slice','remainder',adjacent_same_side=True)
        self.assertFalse(contact_allowed('slice','slice',adjacent_same_side=True))

    def test_external_contact_not_silently_removed(self):
        for body in ['blade','board','fixture']:
            self.assertTrue(contact_allowed('slice',body));self.assertTrue(contact_allowed('remainder',body))

    def test_fixture_cannot_hold_slice(self):
        d,a=fixture();d['fixture']['node_ids']=[0]
        with self.assertRaises(ValueError):inspect_geometry(d,a)

    def test_mass_missing_or_double_counted_rejected(self):
        for ids in [[0,1,2],[0,1,2,2]]:
            d,a=fixture();a[0]['global_node_ids']=ids;a[0]['node_mass_kg']=[.01]*len(ids)
            with self.assertRaises(ValueError):inspect_geometry(d,a)

    def test_bulk_or_volume_hidden_bridge_rejected(self):
        d,a=fixture();a[0]['bond_ids'].append(2)
        with self.assertRaises(ValueError):inspect_geometry(d,a)
        d,a=fixture();a[0]['integration_cells_global_ids']=[[0,1,2,3]]
        with self.assertRaises(ValueError):inspect_geometry(d,a)

    def test_missing_interface_patch_mapping_rejected(self):
        d,a=fixture();d['interface_patches'][0]['bond_ids']=[]
        with self.assertRaises(ValueError):inspect_geometry(d,a)

    def test_zero_rest_length_rejected(self):
        d,a=fixture();d['bonds'][0]['rest_length_m']=0
        with self.assertRaises(ValueError):inspect_geometry(d,a)
