from pathlib import Path
r=Path(__file__).resolve().parents[2];p=r/'rl/tomato_relative_finest_worker.py';s=p.read_text().replace('SETTINGS=[(16,16),(16,32)]','SETTINGS=[(32,8),(32,16),(64,8),(64,16)]').replace('total_expected_steps=1540','total_expected_steps=9224').replace('steps!=1540','steps!=9224')
s=s.replace('from tomato_relative_full_model import RelativeObjectiveVBD,build_relative_model,configure_relative','from tomato_relative_full_model import build_relative_model,configure_relative\n  from tomato_relative_fast_model import RelativeFastObjectiveVBD as RelativeObjectiveVBD')
s=s.replace("relative_fine_20261102_01/final_f8_i64_e0.npz","relative_finest_20261102_01/final_f16_i32_e0.npz").replace("relative_fine_20261102_01/source_closure.json","relative_finest_20261102_01/source_closure.json")
s=s.replace("reference=np.load(out/'final_f16_i32_e0.npz')","reference=np.load(out/'final_f64_i16_e0.npz')")
a=s.index("  a=np.load(out/'final_f16_i16_e0.npz')");b=s.index("   pe=float(abs(left['x']-right['x']).max())",a)
s=s[:a]+'''  a=np.load(out/'final_f32_i8_e0.npz');b=np.load(out/'final_f32_i16_e0.npz');c=np.load(out/'final_f64_i8_e0.npz');d=np.load(out/'final_f64_i16_e0.npz');prior_state=np.load(ROOT/'runs/native/relative_finest_20261102_01/final_f16_i32_e0.npz');comparisons=[]
  for label,left,right in [('iteration_f32',a,b),('iteration_f64',c,d),('time_f16_f32',prior_state,b),('time_two_finest',b,d)]:
'''+s[b:]
s=s.replace("study='finest'","study='extended'")
(r/'rl/tomato_relative_extended_worker.py').write_text(s)
