import ast
import math
from pathlib import Path
import sys
import unittest
from tomato_native_coupon import coupon_description,validate_blade_export,build_native_candidate


class NativeCouponSourceTests(unittest.TestCase):
    def test_positive_finite_spring_lengths_and_distinct_sides(self):
        c=coupon_description();self.assertEqual(len(c['springs']),6)
        for a,b in c['springs']:
            self.assertGreater(math.dist(c['positions_m'][a],c['positions_m'][b]),0)

    def test_no_damage_or_calibration_claim(self):
        c=coupon_description()
        for k in ['damage_enabled','material_calibrated','tomato_equivalence','native_runtime_validated']:
            self.assertFalse(c[k])
        self.assertEqual(c['triangle_elastic_stiffness'],0.)

    def test_default_native_call_refuses_before_import(self):
        with self.assertRaises(PermissionError):build_native_candidate({})
        self.assertFalse(any(x.split('.')[0] in {'newton','warp','torch','pxr'} for x in sys.modules))

    def test_source_compiles_without_importing_engine(self):
        p=Path(__file__).resolve().parents[1]/'tomato_native_coupon.py'
        tree=ast.parse(p.read_text());compile(tree,str(p),'exec')
        self.assertFalse(any(isinstance(n,(ast.Import,ast.ImportFrom)) and
            ('newton' in ast.unparse(n) or 'warp' in ast.unparse(n)) for n in tree.body))

    def test_unknown_blade_units_or_missing_geometry_refused(self):
        for b in [{},{'units':'mm','frame':'blade_local'}, {'units':'m','frame':'blade_local','source_sha256':'0'*64}]:
            with self.assertRaises(ValueError):validate_blade_export(b)

    def test_valid_synthetic_mesh_only_validates_schema(self):
        c=coupon_description()
        b=dict(units='m',frame='blade_local',source_sha256='0'*64,
               vertices=c['positions_m'],triangles=c['triangles'])
        self.assertIs(validate_blade_export(b),b)
