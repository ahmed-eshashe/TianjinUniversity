import unittest
from separation import assess_separation

class SeparationControls(unittest.TestCase):
    def test_intact_and_partial_cut_are_not_separation(self):
        for edges in [[[0,1],[1,2],[2,3]], [[0,1],[2,3],[0,3]]]:
            self.assertFalse(assess_separation([1]*4,edges,[0,0,1,1])['topological_separation'])
    def test_disconnected_pieces_conserve_registered_mass(self):
        r=assess_separation([.01,.02,.03,.04],[[0,1],[2,3]],[0,0,1,1])
        self.assertTrue(r['topological_separation'])
        self.assertAlmostEqual(sum(c['mass_kg'] for c in r['components']),.1)
        self.assertFalse(r['physics_validated'])
    def test_single_surviving_constraint_blocks_release(self):
        r=assess_separation([1]*6,[[0,1],[2,3],[4,5],[1,4]],[0,0,1,1,2,2])
        self.assertTrue(r['surviving_cross_piece_connection'])
        self.assertFalse(r['topological_separation'])
    def test_fragmentation_is_not_success(self):
        r=assess_separation([1]*4,[[0,1]],[0,0,1,1])
        self.assertTrue(r['unintended_fragmentation'])
        self.assertFalse(r['topological_separation'])
    def test_invalid_registry_rejected(self):
        for masses,edges,labels in [([1,0],[],[0,1]),([1,1],[[0,2]],[0,1]),([1,1],[[0.,1.]],[0,1])]:
            with self.assertRaises(ValueError):assess_separation(masses,edges,labels)
    def test_three_slices(self):
        self.assertTrue(assess_separation([1]*6,[[0,1],[2,3],[4,5]],[0,0,1,1,2,2])['topological_separation'])

if __name__=='__main__':unittest.main()
