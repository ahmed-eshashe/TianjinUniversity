import ast,unittest
from tomato_source_binding_audit import function,check_call
class SourceBindingTests(unittest.TestCase):
    def target(self):return function('class A:\n def f(self,x,*,y=1):pass\n','A','f')
    def call(self,s):return ast.parse(s).body[0].value
    def test_keyword_and_positional(self):self.assertFalse(check_call(self.target(),self.call('a.f(2,y=3)'))['runtime_types_validated'])
    def test_unknown_keyword(self):
        with self.assertRaises(ValueError):check_call(self.target(),self.call('a.f(2,z=3)'))
    def test_arity(self):
        with self.assertRaises(ValueError):check_call(self.target(),self.call('a.f(2,3)'))
    def test_unresolved_expansion(self):
        with self.assertRaises(ValueError):check_call(self.target(),self.call('a.f(2,**options)'))
    def test_resolved_expansion(self):self.assertEqual(check_call(self.target(),self.call('a.f(2,**options)'),expanded_keywords=['y'])['explicit_keywords_checked'],['y'])

    def test_missing_required_positional(self):
        with self.assertRaises(ValueError):check_call(self.target(),self.call('a.f(y=3)'))
    def test_missing_keyword_only(self):
        target=function('class A:\n def f(self,*,required):pass\n','A','f')
        with self.assertRaises(ValueError):check_call(target,self.call('a.f()'))
    def test_duplicate_positional_keyword(self):
        with self.assertRaises(ValueError):check_call(self.target(),self.call('a.f(2,x=3)'))
