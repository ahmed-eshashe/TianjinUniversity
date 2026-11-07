"""Create isolated, bounded test sources; no production files modified."""
from pathlib import Path
r=Path(__file__).resolve().parents[2];src=r/'rl'
s=(src/'tomato_robot_slice_extension_v15.py').read_text()
s=s.replace(' from tomato_master_remap_slice_engine_exploratory_v1 import subcycled_engine as live_engine', ''' import os,importlib
 stride=int(os.environ.get('TOMATO_COMPARISON_STRIDE','1'))
 if stride not in (1,2,4):raise ValueError('Invalid bounded comparison stride')
 live_engine=importlib.import_module({1:'tomato_master_remap_slice_engine_exploratory_v1',2:'tomato_master_remap_slice_engine_exploratory_v2',4:'tomato_master_remap_slice_engine_exploratory_v3'}[stride]).subcycled_engine''')
s=s.replace('dt=1/2400;set_dt(dt)','dt=stride/2400;set_dt(1/2400)')
s=s.replace("  advance(target,'research_'+phase,velocity_target)",'''  # Preserve native physics and collision observation at 2400 Hz.
  # The instantaneous composer is consumed by each call to advance.
  for native_substep in range(stride):
   if native_substep:
    if tool.instantaneous_wrench_composer.active:raise ValueError('Unconsumed substep wrench')
    tool.instantaneous_wrench_composer.set_forces_and_torques_index(forces=torch.tensor(wrench[:3][None,None],dtype=torch.float32),torques=torch.tensor(wrench[3:][None,None],dtype=torch.float32),positions=None,is_global=True)
   advance(target,'research_'+phase,velocity_target)''')
s=s.replace('if k%25==0:', 'if True:').replace('if k%10==0:\n   display()', 'if True:\n   display()')
s=s.replace(' for k in range(start_k,maximum_steps):',' if maximum_steps-start_k>32:raise ValueError("Comparison restricted to 32 material intervals")\n for k in range(start_k,maximum_steps):')
(src/'tomato_coupling_timestep_comparison_extension.py').write_text(s)
s=(src/'tomato_research_cut_robot_worker_v15.py').read_text().replace('from tomato_robot_slice_extension_v15 import run as run_cut','from tomato_coupling_timestep_comparison_extension import run as run_cut')
(src/'tomato_coupling_timestep_comparison_worker.py').write_text(s)
s=(src/'tomato_research_cut_guard_v15.py').read_text().replace('tomato_research_cut_robot_worker_v15.py','tomato_coupling_timestep_comparison_worker.py')
(src/'tomato_coupling_timestep_comparison_guard.py').write_text(s)
