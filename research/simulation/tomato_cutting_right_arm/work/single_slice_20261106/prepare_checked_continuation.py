"""Prepare a gated continuation; guard refuses launch without comparison pass."""
from pathlib import Path
r=Path(__file__).resolve().parents[2];src=r/'rl'
s=(src/'tomato_coupling_timestep_comparison_extension.py').read_text()
s=s.replace("stride=int(os.environ.get('TOMATO_COMPARISON_STRIDE','1'))",'stride=4')
s=s.replace(' if maximum_steps-start_k>32:raise ValueError("Comparison restricted to 32 material intervals")\n','')
s=s.replace('  if True:\n   checkpoint_path=', '  if k%25==0:\n   checkpoint_path=')
s=s.replace('  if True:\n   display();', '  if k%2==0:\n   display();')
s=s.replace('numerical_comparison_report="exploratory_comparison_v1.json"','numerical_comparison_report="coupled_timestep_comparison.json",native_dt_s=1/2400,material_stride=4')
s=s.replace('Follow the continuous planned upward withdrawal','Follow the continuous planned horizontal withdrawal')
(src/'tomato_robot_slice_extension_v16.py').write_text(s)
s=(src/'tomato_coupling_timestep_comparison_worker.py').read_text().replace('from tomato_coupling_timestep_comparison_extension import run as run_cut','from tomato_robot_slice_extension_v16 import run as run_cut');(src/'tomato_research_cut_robot_worker_v16.py').write_text(s)
s=(src/'tomato_research_cut_guard_v15.py').read_text().replace('tomato_research_cut_robot_worker_v15.py','tomato_research_cut_robot_worker_v16.py')
s=s.replace(' a.output.mkdir(parents=True,exist_ok=False);', ''' comparison_coupled=json.loads((ROOT/'work/single_slice_20261106/coupled_timestep_comparison.json').read_text())
 if comparison_coupled.get('passed') is not True:raise ValueError('Coupled timestep comparison not passed')
 comparison_material=json.loads((ROOT/'work/single_slice_20261106/bodyward_timestep_comparison/report.json').read_text())
 if not all(c['passed'] for c in comparison_material['cases'] if c['candidate']!='original'):raise ValueError('Bodyward material comparisons not passed')
 a.output.mkdir(parents=True,exist_ok=False);''')
(src/'tomato_research_cut_guard_v16.py').write_text(s)
