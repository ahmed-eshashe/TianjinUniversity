import unittest
from pathlib import Path
from tomato_blade_export import export_authored_blade

BASE='''#usda 1.0
(metersPerUnit = 1 )
def Mesh "CollisionBlade" {
int[] faceVertexCounts = [3,3,3,3]
int[] faceVertexIndices = [0,2,1,0,1,3,0,3,2,1,2,3]
}'''
PHASE='''over "SM_kitchen_knife_02" {
matrix4d xformOp:transform:phase3 = ((1,0,0,0),(0,1,0,0),(0,0,1,0),(3,4,5,1))
uniform token[] xformOpOrder = ["xformOp:transform:phase3"]
over "CollisionBlade" {
point3f[] points = [(0,0,0),(0.1,0,0),(0,0.02,0),(0,0,0.001)]
}
}'''


class BladeExportTests(unittest.TestCase):
    def test_explicit_local_metres_do_not_include_world_pose(self):
        r=export_authored_blade(BASE,PHASE)
        self.assertEqual(r['dimensions_m'],[.1,.02,.001]);self.assertEqual(r['vertices'][0],[0,0,0])
        self.assertFalse(r['runtime_composition_verified'])

    def test_scaled_transform_and_extra_stack_refused(self):
        for text in [PHASE.replace('(1,0,0,0)','(2,0,0,0)'),PHASE.replace('["xformOp:transform:phase3"]','["xformOp:transform:phase3", "xformOp:scale"]')]:
            with self.assertRaises(ValueError):export_authored_blade(BASE,text)

    def test_wrong_units_missing_arrays_and_geometry_overrides_refused(self):
        for base,phase in [(BASE.replace('= 1 ','= 0.01 '),PHASE),(BASE.replace('faceVertexCounts','missing'),PHASE),(BASE,PHASE.replace('point3f[] points','double3 xformOp:translate = (0,0,0)\npoint3f[] points'))]:
            with self.assertRaises(ValueError):export_authored_blade(base,phase)

    def test_actual_authored_blade_dimensions_match_saved_reference(self):
        r=Path(__file__).resolve().parents[2]
        e=export_authored_blade((r/'rl/scene/minimal_benchmark.usda').read_text(),(r/'rl/scene/phase3.usda').read_text())
        expected=[.26593121886253357,.0504381824284792,.00760862766765058]
        for a,b in zip(e['dimensions_m'],expected):self.assertLess(abs(a-b),1e-8)
