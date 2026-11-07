import ast,unittest
from pathlib import Path
class BindingTests(unittest.TestCase):
 def test_installed_iteration_is_preserved_except_explicit_hook(self):
  root=Path(__file__).resolve().parents[2]
  installed=Path('/home/omen/miniconda3/envs/isaaclab_6/lib/python3.12/site-packages/newton/_src/solvers/vbd/solver_vbd.py')
  def method(p,classname):
   tree=ast.parse(p.read_text());c=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==classname)
   return next(n for n in c.body if isinstance(n,ast.FunctionDef) and n.name=='_solve_particle_iteration')
  original=method(installed,'SolverVBD');extension=method(root/'rl/tomato_native_cohesive_operator.py','CohesiveVBD')
  loop=next(n for n in ast.walk(extension) if isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='color')
  hook=loop.body.pop(0)
  self.assertIn('cohesive_blocks',ast.unparse(hook))
  self.assertEqual(ast.dump(original,include_attributes=False),ast.dump(extension,include_attributes=False))
  extension=method(root/'rl/tomato_native_group_cohesion.py','GroupCohesiveVBD')
  loop=next(n for n in ast.walk(extension) if isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='color')
  self.assertIn('group_blocks',ast.unparse(loop.body.pop(0)))
  self.assertEqual(ast.dump(original,include_attributes=False),ast.dump(extension,include_attributes=False))

 def test_full_model_retains_installed_iteration_outside_force_accumulation(self):
  root=Path(__file__).resolve().parents[2]
  installed=Path('/home/omen/miniconda3/envs/isaaclab_6/lib/python3.12/site-packages/newton/_src/solvers/vbd/solver_vbd.py')
  def method(path,name):
   tree=ast.parse(path.read_text());c=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==name)
   return next(n for n in c.body if isinstance(n,ast.FunctionDef) and n.name=='_solve_particle_iteration')
  original=method(installed,'SolverVBD');extension=method(root/'rl/tomato_native_full_model.py','FullTomatoVBD')
  def loop(m):return next(n for n in ast.walk(m) if isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='color')
  a=loop(original);b=loop(extension);self.assertIn('_gather_blocks',ast.unparse(b.body.pop(0)))
  spring=next(n for n in a.body if isinstance(n,ast.If) and ast.unparse(n.test)=='model.spring_count');a.body.remove(spring)
  call=next(n for n in ast.walk(extension) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='_volume_safe_update');call.func.attr='_penetration_free_truncation';call.args=call.args[1:]
  self.assertEqual(ast.dump(original,include_attributes=False),ast.dump(extension,include_attributes=False))

 def test_deterministic_contact_solver_preserves_particle_iteration(self):
  root=Path(__file__).resolve().parents[2]
  def method(filename,classname):
   tree=ast.parse((root/'rl'/filename).read_text());c=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==classname)
   return next(n for n in c.body if isinstance(n,ast.FunctionDef) and n.name=='_solve_particle_iteration')
  original=method('tomato_native_full_model.py','FullTomatoVBD');extension=method('tomato_deterministic_contact_solver.py','FullBladeVBD')
  extension.body.pop(1) # Explicit initial area-penalty hook follows the docstring.
  def loop(m):return next(n for n in ast.walk(m) if isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='color')
  a=loop(original);b=loop(extension);ac=next(n for n in a.body if isinstance(n,ast.If) and ast.unparse(n.test)=='contacts is not None');bc=next(n for n in b.body if isinstance(n,ast.If) and ast.unparse(n.test)=='contacts is not None');a.body.remove(ac);b.body.remove(bc)
  self.assertIn('_contact_gather',ast.unparse(bc));self.assertEqual(ast.dump(original,include_attributes=False),ast.dump(extension,include_attributes=False))
