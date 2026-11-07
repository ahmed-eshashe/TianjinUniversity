from pathlib import Path
r=Path(__file__).resolve().parents[2];rl=r/'rl'
s=(rl/'tomato_relative_sensitivity_worker.py').read_text().replace('SETTINGS=[(1,32),(1,64),(2,16),(2,32),(4,8),(4,16)]','SETTINGS=[(2,32)]')
s=s.replace('from tomato_relative_full_model import RelativeObjectiveVBD,build_relative_model,configure_relative','from tomato_relative_full_model import build_relative_model,configure_relative\n  from tomato_relative_fast_model import RelativeFastObjectiveVBD as RelativeObjectiveVBD')
s=s.replace('total_expected_steps=684','total_expected_steps=98').replace('steps!=684','steps!=98')
a=s.index("  reference=np.load(out/'final_f4_i16_e0.npz')");b=s.index("  if steps!=98:",a)
s=s[:a]+'''  prior=np.load(ROOT/'runs/native/relative_sensitivity_20261102_01/final_f2_i32_e0.npz');current=np.load(out/'final_f2_i32_e0.npz');pe=float(abs(prior['x']-current['x']).max());ve=float(abs(prior['v']-current['v']).max())
  write(out,'dynamic_equivalence.json',dict(position_error_m=pe,velocity_error_m_s=ve,position_budget_m=1e-7,velocity_budget_m_s=2e-5,scope='Color-only exact-force assembly versus the saved full assembly at identical geometry, step and solver settings. No accuracy or support qualification.'))
  if pe>1e-7 or ve>2e-5:raise ValueError('Color-only assembly changed dynamic replay beyond the comparison budget')
'''+s[b:]
s=s.replace("sensitivity_complete=complete,storage=", "sensitivity_complete=complete,fast_equivalence_passed=complete,storage=")
(rl/'tomato_relative_fast_equivalence_worker.py').write_text(s)
p=rl/'tomato_relative_preflight_worker.py';s=p.read_text().replace('from tomato_relative_full_model import RelativeObjectiveVBD,build_relative_model,configure_relative','from tomato_relative_full_model import build_relative_model,configure_relative\n  from tomato_relative_fast_model import RelativeFastObjectiveVBD as RelativeObjectiveVBD');p.write_text(s)
p=rl/'tomato_isaac_startup_guard.py';s=p.read_text();at=s.index("    if mode == 'cohesive_color':")
s=s[:at]+'''    if mode in ('relative_fast_equivalence','relative_preflight'):
        flag, steps = ('fast_equivalence_passed',98) if mode == 'relative_fast_equivalence' else ('relative_preflight_passed',962)
        return (worker.get('diagnostic_passed') is True and worker.get(flag) is True
                and worker.get('storage') == 'rest-relative' and worker.get('controlled_steps') == 0
                and worker.get('newton_steps') == steps and worker.get('settings_completed') == 1)
'''+s[at:]
s=s.replace("1800 if mode in ('relative_fine','relative_finest')", "1800 if mode in ('relative_preflight','relative_fine','relative_finest')")
s=s.replace("('cohesive_color','relative_operator'", "('relative_fast_equivalence','cohesive_color','relative_operator'")
s=s.replace("('startup', 'cohesive_color'", "('startup', 'relative_preflight', 'relative_fast_equivalence', 'cohesive_color'")
at=s.index("    if mode == 'cohesive_color':",s.index('def supervise'))
s=s[:at]+'''    if mode == 'relative_fast_equivalence':
        worker_path = ROOT / 'rl/tomato_relative_fast_equivalence_worker.py'
    if mode == 'relative_preflight':
        worker_path = ROOT / 'rl/tomato_relative_preflight_worker.py'
'''+s[at:];p.write_text(s)
